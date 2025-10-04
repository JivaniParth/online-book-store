from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


# Admin authorization decorator
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from models.user import User

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or user.user_type != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)

    return decorated_function


# ==================== BOOKS MANAGEMENT ====================


@admin_bp.route("/books", methods=["GET"])
@admin_required
def admin_get_books():
    """Get all books for admin management"""
    try:
        from database import db
        from models.book import Book

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")

        query = Book.query

        if search:
            query = query.filter(
                db.or_(
                    Book.title.contains(search),
                    Book.author_name.contains(search),
                    Book.isbn.contains(search),
                )
            )

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        books = [book.to_dict() for book in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "books": books,
                    "pagination": {
                        "page": page,
                        "pages": pagination.pages,
                        "total": pagination.total,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/books", methods=["POST"])
@admin_required
def admin_create_book():
    """Create new book"""
    try:
        from database import db
        from models.book import Book

        data = request.get_json()

        # Validate required fields
        required = [
            "isbn",
            "title",
            "author_name",
            "publisher_name",
            "category_name",
            "price",
            "stock_quantity",
        ]
        for field in required:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        # Check if ISBN already exists
        if Book.query.filter_by(isbn=data["isbn"]).first():
            return jsonify({"error": "Book with this ISBN already exists"}), 400

        book = Book(
            isbn=data["isbn"],
            title=data["title"],
            author_name=data["author_name"],
            publisher_name=data["publisher_name"],
            category_name=data["category_name"],
            price=data["price"],
            publication_date=data.get("publication_date"),
            pages=data.get("pages"),
            stock_quantity=data["stock_quantity"],
            description=data.get("description"),
            image=data.get("image"),
        )

        db.session.add(book)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Book created successfully",
                    "book": book.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error creating book: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/books/<isbn>", methods=["PUT"])
@admin_required
def admin_update_book(isbn):
    """Update book details"""
    try:
        from database import db
        from models.book import Book

        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404

        data = request.get_json()

        # Update fields
        if "title" in data:
            book.title = data["title"]
        if "author_name" in data:
            book.author_name = data["author_name"]
        if "publisher_name" in data:
            book.publisher_name = data["publisher_name"]
        if "category_name" in data:
            book.category_name = data["category_name"]
        if "price" in data:
            book.price = data["price"]
        if "publication_date" in data:
            book.publication_date = data["publication_date"]
        if "pages" in data:
            book.pages = data["pages"]
        if "stock_quantity" in data:
            book.stock_quantity = data["stock_quantity"]
        if "description" in data:
            book.description = data["description"]
        if "image" in data:
            book.image = data["image"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Book updated successfully",
                    "book": book.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating book: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/books/<isbn>", methods=["DELETE"])
@admin_required
def admin_delete_book(isbn):
    """Delete book"""
    try:
        from database import db
        from models.book import Book

        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404

        db.session.delete(book)
        db.session.commit()

        return jsonify({"success": True, "message": "Book deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting book: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== USERS MANAGEMENT ====================


@admin_bp.route("/users", methods=["GET"])
@admin_required
def admin_get_users():
    """Get all users"""
    try:
        from models.user import User

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = [user.to_dict() for user in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "users": users,
                    "pagination": {
                        "page": page,
                        "pages": pagination.pages,
                        "total": pagination.total,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def admin_update_user(user_id):
    """Update user details"""
    try:
        from database import db
        from models.user import User

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            # Check if email is taken
            existing = User.query.filter_by(email=data["email"]).first()
            if existing and existing.user_id != user_id:
                return jsonify({"error": "Email already in use"}), 400
            user.email = data["email"]
        if "phone" in data:
            user.phone = data["phone"]
        if "address" in data:
            user.address = data["address"]
        if "city" in data:
            user.city = data["city"]
        if "user_type" in data:
            user.user_type = data["user_type"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User updated successfully",
                    "user": user.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def admin_delete_user(user_id):
    """Delete user"""
    try:
        from database import db
        from models.user import User

        current_user_id = int(get_jwt_identity())
        if user_id == current_user_id:
            return jsonify({"error": "Cannot delete your own account"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"success": True, "message": "User deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== ORDERS MANAGEMENT ====================


@admin_bp.route("/orders", methods=["GET"])
@admin_required
def admin_get_orders():
    """Get all orders"""
    try:
        from models.order import Order

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status", "")

        query = Order.query

        if status:
            query = query.filter_by(payment_status=status)

        pagination = query.order_by(Order.order_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        orders = [order.to_dict() for order in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "orders": orders,
                    "pagination": {
                        "page": page,
                        "pages": pagination.pages,
                        "total": pagination.total,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@admin_required
def admin_get_order_details(order_id):
    """Get specific order details for admin"""
    try:
        from models.order import Order

        order = Order.query.get(order_id)

        if not order:
            return jsonify({"error": "Order not found"}), 404

        return jsonify({"success": True, "order": order.to_dict()}), 200

    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/orders/<int:order_id>", methods=["PUT"])
@admin_required
def admin_update_order(order_id):
    """Update order status"""
    try:
        from database import db
        from models.order import Order

        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        data = request.get_json()

        if "payment_status" in data:
            order.payment_status = data["payment_status"]
        if "shipping_address" in data:
            order.shipping_address = data["shipping_address"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Order updated successfully",
                    "order": order.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating order: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def admin_delete_order(order_id):
    """Delete order"""
    try:
        from database import db
        from models.order import Order

        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        db.session.delete(order)
        db.session.commit()

        return jsonify({"success": True, "message": "Order deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting order: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== AUTHORS MANAGEMENT ====================


@admin_bp.route("/authors", methods=["GET"])
@admin_required
def admin_get_authors():
    """Get all authors"""
    try:
        from database import db

        result = db.session.execute(db.text("SELECT * FROM Author"))
        authors = [dict(row._mapping) for row in result]

        return jsonify({"success": True, "authors": authors}), 200

    except Exception as e:
        logger.error(f"Error fetching authors: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/authors", methods=["POST"])
@admin_required
def admin_create_author():
    """Create new author"""
    try:
        from database import db

        data = request.get_json()

        if not data.get("author_name"):
            return jsonify({"error": "author_name is required"}), 400

        # Check if author exists
        result = db.session.execute(
            db.text("SELECT * FROM Author WHERE author_name = :name"),
            {"name": data["author_name"]},
        )
        if result.fetchone():
            return jsonify({"error": "Author already exists"}), 400

        db.session.execute(
            db.text(
                """
                INSERT INTO Author (author_name, biography, nationality)
                VALUES (:name, :bio, :nationality)
            """
            ),
            {
                "name": data["author_name"],
                "bio": data.get("biography"),
                "nationality": data.get("nationality"),
            },
        )
        db.session.commit()

        return jsonify({"success": True, "message": "Author created successfully"}), 201

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error creating author: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/authors/<author_name>", methods=["PUT"])
@admin_required
def admin_update_author(author_name):
    """Update author details"""
    try:
        from database import db

        data = request.get_json()

        db.session.execute(
            db.text(
                """
                UPDATE Author 
                SET biography = :bio, nationality = :nationality
                WHERE author_name = :name
            """
            ),
            {
                "name": author_name,
                "bio": data.get("biography"),
                "nationality": data.get("nationality"),
            },
        )
        db.session.commit()

        return jsonify({"success": True, "message": "Author updated successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating author: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/authors/<author_name>", methods=["DELETE"])
@admin_required
def admin_delete_author(author_name):
    """Delete author"""
    try:
        from database import db

        db.session.execute(
            db.text("DELETE FROM Author WHERE author_name = :name"),
            {"name": author_name},
        )
        db.session.commit()

        return jsonify({"success": True, "message": "Author deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting author: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== PUBLISHERS MANAGEMENT ====================


@admin_bp.route("/publishers", methods=["GET"])
@admin_required
def admin_get_publishers():
    """Get all publishers"""
    try:
        from database import db

        result = db.session.execute(db.text("SELECT * FROM Publisher"))
        publishers = [dict(row._mapping) for row in result]

        return jsonify({"success": True, "publishers": publishers}), 200

    except Exception as e:
        logger.error(f"Error fetching publishers: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/publishers", methods=["POST"])
@admin_required
def admin_create_publisher():
    """Create new publisher"""
    try:
        from database import db

        data = request.get_json()

        if not data.get("publisher_name"):
            return jsonify({"error": "publisher_name is required"}), 400

        db.session.execute(
            db.text(
                """
                INSERT INTO Publisher (publisher_name, address, city, phone, email, established_date)
                VALUES (:name, :address, :city, :phone, :email, :established)
            """
            ),
            {
                "name": data["publisher_name"],
                "address": data.get("address"),
                "city": data.get("city"),
                "phone": data.get("phone"),
                "email": data.get("email"),
                "established": data.get("established_date"),
            },
        )
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Publisher created successfully"}),
            201,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error creating publisher: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/publishers/<publisher_name>", methods=["PUT"])
@admin_required
def admin_update_publisher(publisher_name):
    """Update publisher details"""
    try:
        from database import db

        data = request.get_json()

        db.session.execute(
            db.text(
                """
                UPDATE Publisher 
                SET address = :address, city = :city, phone = :phone, 
                    email = :email, established_date = :established
                WHERE publisher_name = :name
            """
            ),
            {
                "name": publisher_name,
                "address": data.get("address"),
                "city": data.get("city"),
                "phone": data.get("phone"),
                "email": data.get("email"),
                "established": data.get("established_date"),
            },
        )
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Publisher updated successfully"}),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating publisher: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/publishers/<publisher_name>", methods=["DELETE"])
@admin_required
def admin_delete_publisher(publisher_name):
    """Delete publisher"""
    try:
        from database import db

        db.session.execute(
            db.text("DELETE FROM Publisher WHERE publisher_name = :name"),
            {"name": publisher_name},
        )
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Publisher deleted successfully"}),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting publisher: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== CATEGORIES MANAGEMENT ====================


@admin_bp.route("/categories", methods=["GET"])
@admin_required
def admin_get_categories():
    """Get all categories"""
    try:
        from models.category import Category

        categories = Category.query.all()

        return (
            jsonify(
                {"success": True, "categories": [cat.to_dict() for cat in categories]}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def admin_create_category():
    """Create new category"""
    try:
        from database import db
        from models.category import Category

        data = request.get_json()

        if not data.get("name"):
            return jsonify({"error": "name is required"}), 400

        # Check if exists
        if Category.query.filter_by(category_name=data["name"]).first():
            return jsonify({"error": "Category already exists"}), 400

        category = Category(name=data["name"], description=data.get("description"))

        db.session.add(category)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Category created successfully",
                    "category": category.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error creating category: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/categories/<category_name>", methods=["PUT"])
@admin_required
def admin_update_category(category_name):
    """Update category"""
    try:
        from database import db
        from models.category import Category

        category = Category.query.filter_by(category_name=category_name).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

        data = request.get_json()

        if "description" in data:
            category.description = data["description"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Category updated successfully",
                    "category": category.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating category: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/categories/<category_name>", methods=["DELETE"])
@admin_required
def admin_delete_category(category_name):
    """Delete category"""
    try:
        from database import db
        from models.category import Category

        category = Category.query.filter_by(category_name=category_name).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

        db.session.delete(category)
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Category deleted successfully"}),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== REVIEWS MANAGEMENT ====================


@admin_bp.route("/reviews", methods=["GET"])
@admin_required
def admin_get_reviews():
    """Get all reviews"""
    try:
        from models.review import Review

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        pagination = Review.query.order_by(Review.review_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        reviews = [review.to_dict() for review in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "reviews": reviews,
                    "pagination": {
                        "page": page,
                        "pages": pagination.pages,
                        "total": pagination.total,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@admin_required
def admin_delete_review(review_id):
    """Delete review"""
    try:
        from database import db
        from models.review import Review

        review = Review.query.get(review_id)
        if not review:
            return jsonify({"error": "Review not found"}), 404

        db.session.delete(review)
        db.session.commit()

        return jsonify({"success": True, "message": "Review deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting review: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== DASHBOARD STATS ====================


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def admin_get_stats():
    """Get admin dashboard statistics"""
    try:
        from models.user import User
        from models.book import Book
        from models.order import Order
        from models.category import Category
        from models.review import Review
        from database import db
        from decimal import Decimal

        # Count statistics
        total_users = User.query.filter_by(user_type="customer").count()
        total_books = Book.query.count()
        total_orders = Order.query.count()
        total_categories = Category.query.count()
        total_reviews = Review.query.count()

        # Revenue statistics
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(
            payment_status="completed"
        ).scalar() or Decimal("0")

        pending_orders = Order.query.filter_by(payment_status="pending").count()
        completed_orders = Order.query.filter_by(payment_status="completed").count()

        # Recent orders
        recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()

        # Low stock books
        low_stock_books = Book.query.filter(Book.stock_quantity < 10).all()

        return (
            jsonify(
                {
                    "success": True,
                    "stats": {
                        "totalUsers": total_users,
                        "totalBooks": total_books,
                        "totalOrders": total_orders,
                        "totalCategories": total_categories,
                        "totalReviews": total_reviews,
                        "totalRevenue": float(total_revenue),
                        "pendingOrders": pending_orders,
                        "completedOrders": completed_orders,
                    },
                    "recentOrders": [order.to_dict_simple() for order in recent_orders],
                    "lowStockBooks": [
                        book.to_dict_simple() for book in low_stock_books
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
