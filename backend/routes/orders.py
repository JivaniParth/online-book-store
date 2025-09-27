from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@orders_bp.route('', methods=['GET'])  # Handle both with and without trailing slash
@jwt_required()
def get_orders():
    try:
        from models.order import Order
        
        user_id = int(get_jwt_identity())  # Convert string to int
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get user's orders with pagination
        pagination = Order.query.filter_by(user_id=user_id)\
            .order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        orders = [order.to_dict_simple() for order in pagination.items]
        
        return jsonify({
            'success': True,
            'orders': orders,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch orders', 'details': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@orders_bp.route('/<int:order_id>/', methods=['GET'])  # Handle both with and without trailing slash
@jwt_required()
def get_order(order_id):
    try:
        from models.order import Order
        
        user_id = int(get_jwt_identity())  # Convert string to int
        
        # Get order belonging to the current user
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch order', 'details': str(e)}), 500

@orders_bp.route('/create', methods=['POST'])
@orders_bp.route('/create/', methods=['POST'])  # Handle both with and without trailing slash
@jwt_required()
def create_order():
    try:
        print(f"\n=== DEBUG: Creating Order ===")
        print(f"Request data: {request.get_json()}")
        
        user_id = int(get_jwt_identity())
        print(f"User ID: {user_id}")
        
        # Check if models can be imported
        try:
            from database import db
            from models.cart import CartItem
            from models.order import Order, OrderItem
            print("✅ Successfully imported models")
        except Exception as import_error:
            print(f"❌ Model import failed: {import_error}")
            raise import_error
        from database import db
        from models.cart import CartItem
        from models.order import Order, OrderItem
        
        user_id = int(get_jwt_identity())  # Convert string to int
                
        data = request.get_json()
        print(f"Parsed data: {data}")
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'address', 'city', 'postalCode']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Missing field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        print("✅ All required fields present")
        
        # Get user's cart items
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        print(f"Cart items found: {len(cart_items)}")
        
        if not cart_items:
            print("❌ Cart is empty")
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Validate stock for all items
        for cart_item in cart_items:
            # Handle case where book might not have is_in_stock attribute
            try:
                if hasattr(cart_item.book, 'is_in_stock') and not cart_item.book.is_in_stock:
                    return jsonify({'error': f'{cart_item.book.title} is out of stock'}), 400
            except:
                pass  # Skip stock check if attribute doesn't exist
            
            if hasattr(cart_item.book, 'stock') and cart_item.quantity > cart_item.book.stock:
                return jsonify({
                    'error': f'Insufficient stock for {cart_item.book.title}. Available: {cart_item.book.stock}'
                }), 400
        print("✅ Validation complete, creating order...")
        
        # Create order
        try:
            order = Order(
                user_id=user_id,
                first_name=data['firstName'],
                last_name=data['lastName'],
                email=data['email'],
                phone=data.get('phone', ''),
                address=data['address'],
                city=data['city'],
                postal_code=data['postalCode'],
                payment_method=data.get('paymentMethod', 'cod')
            )
            print("✅ Order object created")
        except Exception as order_create_error:
            print(f"❌ Order creation failed: {order_create_error}")
            raise order_create_error
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update stock
        for cart_item in cart_items:
            # Create order item
            order_item = OrderItem(
                book_id=cart_item.book_id,
                quantity=cart_item.quantity,
                price_per_item=cart_item.book.price
            )
            order.order_items.append(order_item)
            
            # Update book stock if method exists
            if hasattr(cart_item.book, 'update_stock'):
                cart_item.book.update_stock(-cart_item.quantity)
            elif hasattr(cart_item.book, 'stock'):
                cart_item.book.stock -= cart_item.quantity
        
        # Calculate order totals with Decimal fix
        try:
            if hasattr(order, 'calculate_totals'):
                # Try the original method first
                try:
                    order.calculate_totals()
                except TypeError as decimal_error:
                    print(f"⚠️  Decimal error in calculate_totals, applying fix: {decimal_error}")
                    # Manual calculation with proper Decimal handling
                    from decimal import Decimal
                    order.subtotal = sum(item.total_price for item in order.order_items)
                    order.tax_amount = order.subtotal * Decimal('0.10')
                    order.total_amount = order.subtotal + order.tax_amount
            print("✅ Order totals calculated")
        except Exception as calc_error:
            print(f"❌ Total calculation failed: {calc_error}")
            # Set default values if calculation fails
            order.subtotal = sum(float(getattr(item, 'total_price', 0)) for item in order.order_items)
            order.tax_amount = order.subtotal * 0.10
            order.total_amount = order.subtotal + order.tax_amount
        
        # Clear user's cart
        CartItem.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order.to_dict() if hasattr(order, 'to_dict') else {
                'id': order.id,
                'status': getattr(order, 'status', 'pending'),
                'total_amount': getattr(order, 'total_amount', 0)
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Order creation failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to create order', 'details': str(e)}), 500

@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@orders_bp.route('/<int:order_id>/cancel/', methods=['PUT'])  # Handle both with and without trailing slash
@jwt_required()
def cancel_order(order_id):
    try:
        from database import db
        from models.order import Order
        
        user_id = int(get_jwt_identity())  # Convert string to int
        
        # Get order belonging to the current user
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if order can be cancelled
        if hasattr(order, 'can_cancel') and not order.can_cancel():
            return jsonify({'error': f'Order cannot be cancelled. Current status: {getattr(order, "status", "unknown")}'}), 400
        
        # Cancel order and restore stock
        for order_item in order.order_items:
            if order_item.book:
                if hasattr(order_item.book, 'update_stock'):
                    order_item.book.update_stock(order_item.quantity)
                elif hasattr(order_item.book, 'stock'):
                    order_item.book.stock += order_item.quantity
        
        # Cancel order
        if hasattr(order, 'cancel'):
            order.cancel()
        else:
            # Fallback: manually set status to cancelled
            order.status = 'cancelled'
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'order': order.to_dict() if hasattr(order, 'to_dict') else {
                'id': order.id,
                'status': getattr(order, 'status', 'cancelled')
            }
        }), 200
        
    except Exception as e:
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel order', 'details': str(e)}), 500

@orders_bp.route('/stats', methods=['GET'])
@orders_bp.route('/stats/', methods=['GET'])  # Handle both with and without trailing slash
@jwt_required()
def get_order_stats():
    try:
        from models.order import Order
        
        user_id = int(get_jwt_identity())  # Convert string to int
        
        # Get order statistics
        orders = Order.query.filter_by(user_id=user_id).all()
        
        stats = {
            'totalOrders': len(orders),
            'totalSpent': sum(float(getattr(order, 'total_amount', 0)) for order in orders),
            'statusBreakdown': {
                'pending': len([o for o in orders if getattr(o, 'status', '') == 'pending']),
                'confirmed': len([o for o in orders if getattr(o, 'status', '') == 'confirmed']),
                'processing': len([o for o in orders if getattr(o, 'status', '') == 'processing']),
                'shipped': len([o for o in orders if getattr(o, 'status', '') == 'shipped']),
                'delivered': len([o for o in orders if getattr(o, 'status', '') == 'delivered']),
                'cancelled': len([o for o in orders if getattr(o, 'status', '') == 'cancelled'])
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get order stats', 'details': str(e)}), 500