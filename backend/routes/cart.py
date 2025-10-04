from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/", methods=["GET"])
@cart_bp.route("", methods=["GET"])
@jwt_required()
def get_cart():
    """Get user's cart items"""
    try:
        from models.cart import CartItem

        user_id = int(get_jwt_identity())
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        cart_data = [item.to_dict() for item in cart_items]

        return jsonify({"success": True, "cart": cart_data}), 200

    except Exception as e:
        logger.error(f"Error fetching cart: {str(e)}")
        return jsonify({"error": "Failed to fetch cart", "details": str(e)}), 500


@cart_bp.route("/add", methods=["POST"])
@cart_bp.route("/add/", methods=["POST"])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    try:
        from database import db
        from models.book import Book
        from models.cart import CartItem

        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Get book_id (could be integer or ISBN string)
        book_id = data.get("book_id")
        quantity = data.get("quantity", 1)

        if not book_id:
            return jsonify({"error": "Book ID is required"}), 400

        # Find book by ID or ISBN
        book = Book.query.filter_by(isbn=str(book_id)).first()
        if not book:
            # Try finding by integer ID if exists
            try:
                book = Book.query.get(book_id)
            except:
                pass

        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Use ISBN as book_id for cart
        book_isbn = book.isbn

        # Check stock
        if book.stock_quantity < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        # Check if item already exists in cart
        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_isbn).first()

        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if book.stock_quantity < new_quantity:
                return jsonify({"error": "Insufficient stock"}), 400
            cart_item.quantity = new_quantity
        else:
            # Create new cart item
            cart_item = CartItem(user_id=user_id, book_id=book_isbn, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Item added to cart",
                    "cart_item": cart_item.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({"error": "Failed to add to cart", "details": str(e)}), 500


@cart_bp.route("/update", methods=["PUT"])
@cart_bp.route("/update/", methods=["PUT"])
@jwt_required()
def update_cart_item():
    """Update cart item quantity"""
    try:
        from database import db
        from models.book import Book
        from models.cart import CartItem

        user_id = int(get_jwt_identity())
        data = request.get_json()

        book_id = str(data.get("book_id"))  # Convert to string (ISBN)
        quantity = data.get("quantity")

        if not book_id or quantity is None:
            return jsonify({"error": "Book ID and quantity are required"}), 400

        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()

        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404

        if quantity <= 0:
            # Remove item from cart
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({"success": True, "message": "Item removed from cart"}), 200

        # Check stock
        book = Book.query.filter_by(isbn=book_id).first()
        if book and book.stock_quantity < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        cart_item.quantity = quantity
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Cart updated",
                    "cart_item": cart_item.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating cart: {str(e)}")
        return jsonify({"error": "Failed to update cart", "details": str(e)}), 500


@cart_bp.route("/remove/<book_id>", methods=["DELETE"])
@cart_bp.route("/remove/<book_id>/", methods=["DELETE"])
@jwt_required()
def remove_from_cart(book_id):
    """Remove item from cart"""
    try:
        from database import db
        from models.cart import CartItem

        user_id = int(get_jwt_identity())
        book_id = str(book_id)  # Convert to string (ISBN)

        cart_item = CartItem.query.filter_by(user_id=user_id, book_id=book_id).first()

        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404

        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({"success": True, "message": "Item removed from cart"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error removing from cart: {str(e)}")
        return jsonify({"error": "Failed to remove from cart", "details": str(e)}), 500


@cart_bp.route("/clear", methods=["DELETE"])
@cart_bp.route("/clear/", methods=["DELETE"])
@jwt_required()
def clear_cart():
    """Clear all items from cart"""
    try:
        from database import db
        from models.cart import CartItem

        user_id = int(get_jwt_identity())

        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "Cart cleared"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error clearing cart: {str(e)}")
        return jsonify({"error": "Failed to clear cart", "details": str(e)}), 500


@cart_bp.route("/test-jwt", methods=["GET"])
@jwt_required()
def test_jwt():
    """Simple endpoint to test if JWT is working"""
    try:
        user_id = int(get_jwt_identity())
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"JWT working correctly for user {user_id}",
                    "user_id": user_id,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"JWT test failed: {str(e)}")
        return jsonify({"error": f"JWT test failed: {str(e)}"}), 500
