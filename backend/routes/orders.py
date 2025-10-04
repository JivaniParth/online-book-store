from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/", methods=["GET"])
@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    """Get all orders for current user"""
    try:
        from models.order import Order

        user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Get user's orders with pagination
        pagination = (
            Order.query.filter_by(user_id=user_id)
            .order_by(Order.order_date.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        orders = [order.to_dict_simple() for order in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "orders": orders,
                    "pagination": {
                        "page": page,
                        "pages": pagination.pages,
                        "per_page": per_page,
                        "total": pagination.total,
                        "has_next": pagination.has_next,
                        "has_prev": pagination.has_prev,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({"error": "Failed to fetch orders", "details": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["GET"])
@orders_bp.route("/<int:order_id>/", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        from models.order import Order

        user_id = int(get_jwt_identity())

        # Get order belonging to the current user
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()

        if not order:
            return jsonify({"error": "Order not found"}), 404

        return jsonify({"success": True, "order": order.to_dict()}), 200

    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch order", "details": str(e)}), 500


@orders_bp.route("/create", methods=["POST"])
@orders_bp.route("/create/", methods=["POST"])
@jwt_required()
def create_order():
    """Create new order from cart"""
    try:
        logger.info(f"\n=== Creating Order ===")

        from database import db
        from models.cart import CartItem
        from models.order import Order, OrderItem
        from models.book import Book
        from decimal import Decimal

        user_id = int(get_jwt_identity())
        logger.info(f"User ID: {user_id}")

        data = request.get_json()
        logger.info(f"Request data: {data}")

        # Validate required fields
        required_fields = [
            "firstName",
            "lastName",
            "email",
            "address",
            "city",
            "postalCode",
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # Get user's cart items
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        logger.info(f"Cart items found: {len(cart_items)}")

        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400

        # Validate stock for all items
        for cart_item in cart_items:
            book = Book.query.filter_by(isbn=cart_item.book_id).first()
            if not book:
                return jsonify({"error": f"Book not found: {cart_item.book_id}"}), 404

            if cart_item.quantity > book.stock_quantity:
                return (
                    jsonify(
                        {
                            "error": f"Insufficient stock for {book.title}. Available: {book.stock_quantity}"
                        }
                    ),
                    400,
                )

        logger.info("✅ Validation complete, creating order...")

        # Create order
        order = Order(
            user_id=user_id,
            first_name=data["firstName"],
            last_name=data["lastName"],
            email=data["email"],
            phone=data.get("phone", ""),
            address=data["address"],
            city=data["city"],
            postal_code=data["postalCode"],
            payment_method=data.get("paymentMethod", "cod"),
        )

        db.session.add(order)
        db.session.flush()  # Get order_id
        logger.info(f"✅ Order created with ID: {order.order_id}")

        # Create order items and update stock
        for cart_item in cart_items:
            book = Book.query.filter_by(isbn=cart_item.book_id).first()

            # Create order item with ISBN as book_id
            order_item = OrderItem(
                book_id=cart_item.book_id,  # This is the ISBN
                quantity=cart_item.quantity,
                price_per_item=book.price,
            )
            order.order_items.append(order_item)

            # Update book stock
            book.stock_quantity -= cart_item.quantity
            logger.info(f"✅ Added {cart_item.quantity}x {book.title}, updated stock")

        # Calculate order totals
        try:
            subtotal = sum(item.total_price for item in order.order_items)
            tax_amount = subtotal * Decimal("0.10")
            order.total_amount = subtotal + tax_amount
            logger.info(
                f"✅ Order totals calculated: subtotal={subtotal}, tax={tax_amount}, total={order.total_amount}"
            )
        except Exception as calc_error:
            logger.error(f"❌ Total calculation failed: {calc_error}")
            # Fallback calculation
            order.total_amount = (
                sum(float(item.total_price) for item in order.order_items) * 1.10
            )

        # Clear user's cart
        CartItem.query.filter_by(user_id=user_id).delete()
        logger.info("✅ Cart cleared")

        db.session.commit()
        logger.info("✅ Order committed to database")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Order created successfully",
                    "order": order.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"❌ Order creation failed: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")

        from database import db

        db.session.rollback()
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500


@orders_bp.route("/<int:order_id>/cancel", methods=["PUT"])
@orders_bp.route("/<int:order_id>/cancel/", methods=["PUT"])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    try:
        from database import db
        from models.order import Order
        from models.book import Book

        user_id = int(get_jwt_identity())

        # Get order belonging to the current user
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()

        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Check if order can be cancelled
        if not order.can_cancel():
            return (
                jsonify(
                    {
                        "error": f"Order cannot be cancelled. Current status: {order.status}"
                    }
                ),
                400,
            )

        # Restore stock for all order items
        for order_item in order.order_items:
            book = Book.query.filter_by(isbn=order_item.book_id).first()
            if book:
                book.stock_quantity += order_item.quantity
                logger.info(f"✅ Restored {order_item.quantity} units of {book.title}")

        # Cancel order
        order.cancel()
        logger.info(f"✅ Order {order_id} cancelled")

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Order cancelled successfully",
                    "order": order.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        from database import db

        db.session.rollback()
        return jsonify({"error": "Failed to cancel order", "details": str(e)}), 500


@orders_bp.route("/stats", methods=["GET"])
@orders_bp.route("/stats/", methods=["GET"])
@jwt_required()
def get_order_stats():
    """Get order statistics for current user"""
    try:
        from models.order import Order

        user_id = int(get_jwt_identity())

        # Get order statistics
        orders = Order.query.filter_by(user_id=user_id).all()

        stats = {
            "totalOrders": len(orders),
            "totalSpent": sum(float(order.total_amount) for order in orders),
            "statusBreakdown": {
                "pending": len([o for o in orders if o.status == "pending"]),
                "confirmed": len([o for o in orders if o.status == "confirmed"]),
                "processing": len([o for o in orders if o.status == "processing"]),
                "shipped": len([o for o in orders if o.status == "shipped"]),
                "delivered": len([o for o in orders if o.status == "delivered"]),
                "cancelled": len([o for o in orders if o.status == "cancelled"]),
            },
        }

        return jsonify({"success": True, "stats": stats}), 200

    except Exception as e:
        logger.error(f"Error getting order stats: {str(e)}")
        return jsonify({"error": "Failed to get order stats", "details": str(e)}), 500
