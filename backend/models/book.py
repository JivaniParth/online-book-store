from database import db
from datetime import datetime
from sqlalchemy import Numeric

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(Numeric(10, 2), nullable=False)
    original_price = db.Column(Numeric(10, 2), nullable=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(Numeric(3, 2), default=0.0)
    reviews = db.Column(db.Integer, default=0)
    image = db.Column(db.String(500), nullable=True)
    isbn = db.Column(db.String(20), nullable=True, unique=True)
    publication_date = db.Column(db.Date, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(50), default='English')
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='book', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    
    def __init__(self, title, author, description, price, category_id, original_price=None, 
                 stock=0, rating=0.0, reviews=0, image=None, isbn=None, publication_date=None, 
                 pages=None, language='English', is_featured=False):
        self.title = title
        self.author = author
        self.description = description
        self.price = price
        self.original_price = original_price or price
        self.stock = stock
        self.rating = rating
        self.reviews = reviews
        self.image = image
        self.isbn = isbn
        self.publication_date = publication_date
        self.pages = pages
        self.language = language
        self.is_featured = is_featured
        self.category_id = category_id
    
    @property
    def is_on_sale(self):
        """Check if book is on sale"""
        return self.original_price and self.price < self.original_price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            return round(((self.original_price - self.price) / self.original_price) * 100, 0)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if book is in stock"""
        return self.stock > 0
    
    @property
    def availability_status(self):
        """Get availability status"""
        if self.stock > 10:
            return "In Stock"
        elif self.stock > 0:
            return "Limited Stock"
        else:
            return "Out of Stock"
    
    def update_stock(self, quantity):
        """Update stock quantity"""
        if self.stock + quantity >= 0:
            self.stock += quantity
            return True
        return False
    
    def add_review(self, rating):
        """Add a review and update average rating"""
        total_rating = (self.rating * self.reviews) + rating
        self.reviews += 1
        self.rating = total_rating / self.reviews
    
    def to_dict(self):
        """Convert book object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'price': float(self.price),
            'originalPrice': float(self.original_price) if self.original_price else float(self.price),
            'stock': self.stock,
            'rating': float(self.rating),
            'reviews': self.reviews,
            'image': self.image,
            'isbn': self.isbn,
            'publicationDate': self.publication_date.strftime('%Y-%m-%d') if self.publication_date else None,
            'pages': self.pages,
            'language': self.language,
            'isFeatured': self.is_featured,
            'isOnSale': self.is_on_sale,
            'discountPercentage': self.discount_percentage,
            'availabilityStatus': self.availability_status,
            'isInStock': self.is_in_stock,
            'category': self.category.slug if self.category else None,
            'categoryName': self.category.name if self.category else None,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def to_dict_simple(self):
        """Convert book object to simple dictionary (for cart items)"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': float(self.price),
            'image': self.image,
            'stock': self.stock
        }
    
    @classmethod
    def search(cls, query):
        """Search books by title or author"""
        return cls.query.filter(
            db.or_(
                cls.title.contains(query),
                cls.author.contains(query)
            ),
            cls.is_active == True
        )
    
    @classmethod
    def get_by_category(cls, category_id):
        """Get books by category"""
        return cls.query.filter_by(category_id=category_id, is_active=True)
    
    @classmethod
    def get_featured(cls):
        """Get featured books"""
        return cls.query.filter_by(is_featured=True, is_active=True)
    
    @classmethod
    def get_on_sale(cls):
        """Get books on sale"""
        return cls.query.filter(
            cls.price < cls.original_price,
            cls.is_active == True
        )
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'