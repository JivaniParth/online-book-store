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
        author = request.args.get("author", "")  # NEW: Filter by author
        publisher = request.args.get("publisher", "")  # NEW: Filter by publisher
        search = request.args.get("search", "")
        sort_by = request.args.get("sort", "title")
        min_price = request.args.get("min_price", type=float)  # NEW
        max_price = request.args.get("max_price", type=float)  # NEW

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

        # NEW: Filter by author
        if author:
            query = query.filter_by(author_name=author)

        # NEW: Filter by publisher
        if publisher:
            query = query.filter_by(publisher_name=publisher)

        # Filter by search term
        if search:
            query = query.filter(
                or_(
                    Book.title.contains(search),
                    Book.author_name.contains(search),
                    Book.publisher_name.contains(search),
                )
            )

        # NEW: Filter by price range
        if min_price is not None:
            query = query.filter(Book.price >= min_price)
        if max_price is not None:
            query = query.filter(Book.price <= max_price)

        # Sort books
        if sort_by == "price-low":
            query = query.order_by(Book.price.asc())
        elif sort_by == "price-high":
            query = query.order_by(Book.price.desc())
        elif sort_by == "title":
            query = query.order_by(Book.title.asc())
        elif sort_by == "author":  # NEW
            query = query.order_by(Book.author_name.asc())
        elif sort_by == "publisher":  # NEW
            query = query.order_by(Book.publisher_name.asc())
        elif sort_by == "newest":  # NEW
            query = query.order_by(Book.publication_date.desc())
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


@books_bp.route("/authors", methods=["GET"])
def get_authors():
    """Get list of all unique authors"""
    try:
        from database import db
        from models.book import Book

        # Get unique authors
        authors = (
            db.session.query(Book.author_name)
            .distinct()
            .order_by(Book.author_name)
            .all()
        )
        author_list = [author[0] for author in authors]

        return jsonify({"success": True, "authors": author_list}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching authors: {str(e)}")
        return jsonify({"error": "Failed to fetch authors", "details": str(e)}), 500


@books_bp.route("/publishers", methods=["GET"])
def get_publishers():
    """Get list of all unique publishers"""
    try:
        from database import db
        from models.book import Book

        # Get unique publishers
        publishers = (
            db.session.query(Book.publisher_name)
            .distinct()
            .order_by(Book.publisher_name)
            .all()
        )
        publisher_list = [publisher[0] for publisher in publishers]

        return jsonify({"success": True, "publishers": publisher_list}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching publishers: {str(e)}")
        return jsonify({"error": "Failed to fetch publishers", "details": str(e)}), 500


@books_bp.route("/filters", methods=["GET"])
def get_filters():
    """Get all available filters (categories, authors, publishers, price range)"""
    try:
        from database import db
        from models.book import Book
        from models.category import Category

        # Get categories
        categories = Category.query.all()
        category_list = [cat.to_dict() for cat in categories]

        # Get unique authors
        authors = (
            db.session.query(Book.author_name)
            .distinct()
            .order_by(Book.author_name)
            .all()
        )
        author_list = [author[0] for author in authors]

        # Get unique publishers
        publishers = (
            db.session.query(Book.publisher_name)
            .distinct()
            .order_by(Book.publisher_name)
            .all()
        )
        publisher_list = [publisher[0] for publisher in publishers]

        # Get price range
        price_range = db.session.query(
            db.func.min(Book.price).label("min_price"),
            db.func.max(Book.price).label("max_price"),
        ).first()

        return (
            jsonify(
                {
                    "success": True,
                    "filters": {
                        "categories": category_list,
                        "authors": author_list,
                        "publishers": publisher_list,
                        "priceRange": {
                            "min": (
                                float(price_range.min_price)
                                if price_range.min_price
                                else 0
                            ),
                            "max": (
                                float(price_range.max_price)
                                if price_range.max_price
                                else 100
                            ),
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error fetching filters: {str(e)}")
        return jsonify({"error": "Failed to fetch filters", "details": str(e)}), 500
