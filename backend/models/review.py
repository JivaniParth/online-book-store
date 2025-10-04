from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_

books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
def get_books():
    try:
        from database import db
        from models.book import Book
        from models.category import Category

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 12, type=int)
        category = request.args.get("category", "")
        search = request.args.get("search", "")
        sort_by = request.args.get("sort", "title")

        # Base query
        query = Book.query

        # Filter by category
        if category and category != "all":
            # Convert slug to category name
            category_name = category.replace("-", " ").title()
            if category == "science-fiction":
                category_name = "Science Fiction"
            elif category == "self-help":
                category_name = "Self Help"

            query = query.filter_by(category_name=category_name)

        # Filter by search term
        if search:
            query = query.filter(
                or_(Book.title.contains(search), Book.author_name.contains(search))
            )

        # Sort books
        if sort_by == "price-low":
            query = query.order_by(Book.price.asc())
        elif sort_by == "price-high":
            query = query.order_by(Book.price.desc())
        elif sort_by == "title":
            query = query.order_by(Book.title.asc())
        else:
            query = query.order_by(Book.title.asc())

        # Paginate results
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
        current_app.logger.error(f"Error fetching books: {str(e)}")
        return jsonify({"error": "Failed to fetch books", "details": str(e)}), 500


@books_bp.route("/<book_id>", methods=["GET"])
def get_book(book_id):
    try:
        from database import db
        from models.book import Book

        # book_id is the ISBN
        book = Book.query.filter_by(isbn=book_id).first()

        if not book:
            # Try as integer ID for backward compatibility
            try:
                book = Book.query.filter_by(isbn=str(book_id)).first()
            except:
                pass

        if not book:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"success": True, "book": book.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching book {book_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch book", "details": str(e)}), 500


@books_bp.route("/categories", methods=["GET"])
@books_bp.route("/categories/", methods=["GET"])
def get_categories():
    try:
        from database import db
        from models.category import Category

        categories = Category.query.all()

        # Add "All Books" category
        categories_data = [
            {
                "id": "all",
                "name": "All Books",
                "description": "Browse all available books",
            }
        ]

        # Convert categories to the format expected by frontend
        for category in categories:
            categories_data.append(category.to_dict())

        return jsonify({"success": True, "categories": categories_data}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({"error": "Failed to fetch categories", "details": str(e)}), 500
