from database import db
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, decode_token
import logging

# Add this logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)

# Add this debug function BEFORE your existing routes
@cart_bp.before_request
def debug_jwt_issues():
    """Debug JWT authentication"""
    print(f"\n=== DEBUGGING CART REQUEST ===")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    
    # Check for Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        print(f"✅ Authorization header found: {auth_header[:30]}...")
        
        # Extract token
        try:
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
                
        except Exception as token_error:
            print(f"❌ Token extraction failed: {token_error}")
    else:
        print("❌ No Authorization header found!")
    
    print("=== END DEBUG ===\n")

# Your existing routes start here (don't change these)
@cart_bp.route('/', methods=['GET'])
@cart_bp.route('', methods=['GET'])
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

# ... rest of your existing code stays the same ...

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_cart'),
    )
    
    def __init__(self, user_id, book_id, quantity=1):
        self.user_id = user_id
        self.book_id = book_id
        self.quantity = quantity
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.book.price * self.quantity if self.book else 0
    
    @property
    def total_original_price(self):
        """Calculate total original price for this cart item"""
        original_price = self.book.original_price if self.book.original_price else self.book.price
        return original_price * self.quantity if self.book else 0
    
    @property
    def savings(self):
        """Calculate savings for this cart item"""
        return self.total_original_price - self.total_price
    
    def update_quantity(self, new_quantity):
        """Update quantity with validation"""
        if new_quantity <= 0:
            return False
        
        # Check if enough stock is available
        if self.book and new_quantity > self.book.stock:
            return False
        
        self.quantity = new_quantity
        self.updated_at = datetime.utcnow()
        return True
    
    def increase_quantity(self, amount=1):
        """Increase quantity by specified amount"""
        return self.update_quantity(self.quantity + amount)
    
    def decrease_quantity(self, amount=1):
        """Decrease quantity by specified amount"""
        return self.update_quantity(self.quantity - amount)
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        book_data = self.book.to_dict_simple() if self.book else {}
        
        return {
            'id': self.book_id,  # Using book_id as id for frontend compatibility
            'book_id': self.book_id,
            'title': book_data.get('title', ''),
            'author': book_data.get('author', ''),
            'price': book_data.get('price', 0),
            'image': book_data.get('image', ''),
            'quantity': self.quantity,
            'totalPrice': float(self.total_price),
            'totalOriginalPrice': float(self.total_original_price),
            'savings': float(self.savings),
            'stock': book_data.get('stock', 0),
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def get_user_cart(cls, user_id):
        """Get all cart items for a user"""
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def get_cart_total(cls, user_id):
        """Get total price of user's cart"""
        cart_items = cls.get_user_cart(user_id)
        return sum(item.total_price for item in cart_items)
    
    @classmethod
    def get_cart_items_count(cls, user_id):
        """Get total number of items in user's cart"""
        cart_items = cls.get_user_cart(user_id)
        return sum(item.quantity for item in cart_items)
    
    @classmethod
    def clear_user_cart(cls, user_id):
        """Clear all items from user's cart"""
        cls.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    
    def __repr__(self):
        return f'<CartItem User:{self.user_id} Book:{self.book_id} Qty:{self.quantity}>'