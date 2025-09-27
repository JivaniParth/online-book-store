from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_

books_bp = Blueprint('books', __name__)

@books_bp.route('', methods=['GET'])
def get_books():
    try:
        # Import db and models inside the function
        from database import db
        from models.book import Book
        from models.category import Category
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'title')
        
        # Base query - Remove is_active filter if the field doesn't exist
        query = Book.query
        
        # Check if is_active column exists before filtering
        try:
            # Try to access is_active, if it fails, skip this filter
            query = query.filter_by(is_active=True)
        except:
            # If is_active column doesn't exist, just use all books
            pass
        
        # Filter by category
        if category and category != 'all':
            # First try to find by slug, then by name, then by ID
            category_obj = None
            
            # Try finding by slug first
            try:
                category_obj = Category.query.filter_by(slug=category).first()
            except:
                pass
            
            # If not found by slug, try by name (convert category to proper name)
            if not category_obj:
                category_name = category.replace('-', ' ').title()
                if category == 'science-fiction':
                    category_name = 'Science Fiction'
                elif category == 'self-help':
                    category_name = 'Self Help'
                
                category_obj = Category.query.filter_by(name=category_name).first()
            
            # If found, filter books by this category
            if category_obj:
                query = query.filter_by(category_id=category_obj.id)
        
        # Filter by search term
        if search:
            query = query.filter(or_(
                Book.title.contains(search),
                Book.author.contains(search)
            ))
        
        # Sort books
        if sort_by == 'price-low':
            query = query.order_by(Book.price.asc())
        elif sort_by == 'price-high':
            query = query.order_by(Book.price.desc())
        elif sort_by == 'rating':
            query = query.order_by(Book.rating.desc())
        elif sort_by == 'popularity':
            query = query.order_by(Book.reviews.desc())
        else:  # default to title
            query = query.order_by(Book.title.asc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        books = [book.to_dict() for book in pagination.items]
        
        return jsonify({
            'success': True,
            'books': books,
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
        current_app.logger.error(f"Error fetching books: {str(e)}")
        return jsonify({'error': 'Failed to fetch books', 'details': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        from database import db
        from models.book import Book
        
        # Remove is_active filter if column doesn't exist
        try:
            book = Book.query.filter_by(id=book_id, is_active=True).first()
        except:
            book = Book.query.filter_by(id=book_id).first()
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify({
            'success': True,
            'book': book.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching book {book_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch book', 'details': str(e)}), 500

@books_bp.route('/categories', methods=['GET'])
@books_bp.route('/categories/', methods=['GET'])  # Handle both with and without trailing slash
def get_categories():
    try:
        from database import db
        from models.category import Category
        
        # Remove is_active filter if column doesn't exist
        try:
            categories = Category.query.filter_by(is_active=True).all()
        except:
            categories = Category.query.all()
        
        # Add "All Books" category
        categories_data = [{'id': 'all', 'name': 'All Books'}]
        
        # Convert categories to the format expected by frontend
        for category in categories:
            category_dict = category.to_dict() if hasattr(category, 'to_dict') else {
                'id': category.name.lower().replace(' ', '-'),
                'name': category.name,
                'description': getattr(category, 'description', '')
            }
            categories_data.append(category_dict)
        
        return jsonify({
            'success': True,
            'categories': categories_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories', 'details': str(e)}), 500