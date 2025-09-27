from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)

# Debug function to troubleshoot JWT issues
@cart_bp.before_request
def debug_jwt_issues():
    """Debug JWT authentication issues"""
    print(f"\n=== DEBUGGING CART REQUEST ===")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Full URL: {request.url}")
    
    # Check for Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        print(f"✅ Authorization header found: {auth_header[:30]}...")
        
        try:
            # Extract token
            token = auth_header.split(' ')[1]
            print(f"✅ Token extracted: {token[:20]}...")
            
            # Try to verify JWT
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                print(f"✅ JWT verification SUCCESS for user: {user_id}")
            except Exception as jwt_error:
                print(f"❌ JWT verification FAILED: {jwt_error}")
                print(f"Error type: {type(jwt_error).__name__}")
                
                # Additional debugging based on error type
                if "signature" in str(jwt_error).lower():
                    print("🔍 ISSUE: JWT Secret Key mismatch between login and verification!")
                elif "expired" in str(jwt_error).lower():
                    print("🔍 ISSUE: Token has expired - try logging in again!")
                elif "invalid" in str(jwt_error).lower():
                    print("🔍 ISSUE: Invalid token format!")
                    
        except Exception as token_error:
            print(f"❌ Token extraction failed: {token_error}")
    else:
        print("❌ No Authorization header found!")
    
    print("=== END DEBUG ===\n")

@cart_bp.route('/', methods=['GET'])
@cart_bp.route('', methods=['GET'])  # Handle both with and without trailing slash
@jwt_required()
def get_cart():
    try:
        from models.cart import CartItem
        
        user_id = get_jwt_identity()
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        cart_data = [item.to_dict() for item in cart_items]
        
        return jsonify({
            'success': True,
            'cart': cart_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch cart', 'details': str(e)}), 500

@cart_bp.route('/add', methods=['POST'])
@cart_bp.route('/add/', methods=['POST'])  # Handle both with and without trailing slash
@jwt_required()
def add_to_cart():
    try:
        from database import db
        from models.book import Book
        from models.cart import CartItem
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        book_id = data.get('book_id')
        quantity = data.get('quantity', 1)
        
        if not book_id:
            return jsonify({'error': 'Book ID is required'}), 400
        
        # Check if book exists - handle missing is_active field
        try:
            book = Book.query.filter_by(id=book_id, is_active=True).first()
        except:
            # If is_active column doesn't exist, just check by ID
            book = Book.query.filter_by(id=book_id).first()
            
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check stock
        if hasattr(book, 'stock') and book.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Check if item already exists in cart
        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()
        
        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if hasattr(book, 'stock') and book.stock < new_quantity:
                return jsonify({'error': 'Insufficient stock'}), 400
            cart_item.quantity = new_quantity
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                book_id=book_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to add to cart', 'details': str(e)}), 500

@cart_bp.route('/update', methods=['PUT'])
@cart_bp.route('/update/', methods=['PUT'])  # Handle both with and without trailing slash
@jwt_required()
def update_cart_item():
    try:
        from database import db
        from models.book import Book
        from models.cart import CartItem
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        book_id = data.get('book_id')
        quantity = data.get('quantity')
        
        if not book_id or quantity is None:
            return jsonify({'error': 'Book ID and quantity are required'}), 400
        
        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        if quantity <= 0:
            # Remove item from cart
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Item removed from cart'
            }), 200
        
        # Check stock
        book = Book.query.get(book_id)
        if book and hasattr(book, 'stock') and book.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to update cart', 'details': str(e)}), 500

@cart_bp.route('/remove/<int:book_id>', methods=['DELETE'])
@cart_bp.route('/remove/<int:book_id>/', methods=['DELETE'])  # Handle both with and without trailing slash
@jwt_required()
def remove_from_cart(book_id):
    try:
        from database import db
        from models.cart import CartItem
        
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart'
        }), 200
        
    except Exception as e:
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to remove from cart', 'details': str(e)}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@cart_bp.route('/clear/', methods=['DELETE'])  # Handle both with and without trailing slash
@jwt_required()
def clear_cart():
    try:
        from database import db
        from models.cart import CartItem
        
        user_id = get_jwt_identity()
        
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        }), 200
        
    except Exception as e:
        from database import db
        db.session.rollback()
        return jsonify({'error': 'Failed to clear cart', 'details': str(e)}), 500

# Test endpoint to verify JWT is working
@cart_bp.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """Simple endpoint to test if JWT is working"""
    try:
        user_id = get_jwt_identity()
        return jsonify({
            'success': True,
            'message': f'JWT working correctly for user {user_id}',
            'user_id': user_id
        }), 200
    except Exception as e:
        return jsonify({'error': f'JWT test failed: {str(e)}'}), 500