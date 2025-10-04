from database import db
from datetime import datetime
from sqlalchemy import Numeric


class Book(db.Model):
    __tablename__ = "Book_Details"  # Matches your DDL

    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author_name = db.Column(db.String(255), nullable=False, index=True)
    publisher_name = db.Column(db.String(255), nullable=False)
    category_name = db.Column(db.String(255), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    publication_date = db.Column(db.Date, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    # Foreign Keys
    # Note: Your DDL has foreign keys, but we'll handle them as strings for now
    # since you're using names instead of IDs

    # Relationships
    cart_items = db.relationship(
        "CartItem", backref="book", lazy=True, foreign_keys="CartItem.book_id"
    )
    order_items = db.relationship(
        "OrderItem", backref="book", lazy=True, foreign_keys="OrderItem.book_id"
    )
    reviews = db.relationship(
        "Review", backref="book", lazy=True, foreign_keys="Review.book_id"
    )

    # Properties for backward compatibility
    @property
    def id(self):
        """Use ISBN as ID"""
        return self.isbn

    @property
    def author(self):
        return self.author_name

    @property
    def stock(self):
        return self.stock_quantity

    @property
    def original_price(self):
        """For now, return same as price (you can add this field to DDL later)"""
        return self.price

    @property
    def rating(self):
        """Calculate average rating from reviews"""
        if self.reviews:
            return sum(r.rating for r in self.reviews) / len(self.reviews)
        return 0.0

    @property
    def review_count(self):
        """Count of reviews"""
        return len(self.reviews) if self.reviews else 0

    @property
    def is_on_sale(self):
        """Check if book is on sale"""
        return False  # No sale price in current DDL

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        return 0

    @property
    def is_in_stock(self):
        """Check if book is in stock"""
        return self.stock_quantity > 0

    @property
    def availability_status(self):
        """Get availability status"""
        if self.stock_quantity > 10:
            return "In Stock"
        elif self.stock_quantity > 0:
            return "Limited Stock"
        else:
            return "Out of Stock"

    @property
    def is_active(self):
        return True  # All books active by default

    @property
    def created_at(self):
        return self.publication_date or datetime.utcnow()

    @property
    def updated_at(self):
        return self.publication_date or datetime.utcnow()

    def update_stock(self, quantity):
        """Update stock quantity"""
        if self.stock_quantity + quantity >= 0:
            self.stock_quantity += quantity
            return True
        return False

    def to_dict(self):
        """Convert book object to dictionary"""
        return {
            "id": self.isbn,
            "title": self.title,
            "author": self.author_name,
            "description": self.description,
            "price": float(self.price),
            "originalPrice": float(self.price),
            "stock": self.stock_quantity,
            "rating": float(self.rating),
            "reviews": self.review_count,
            "image": self.image,
            "isbn": self.isbn,
            "publicationDate": (
                self.publication_date.strftime("%Y-%m-%d")
                if self.publication_date
                else None
            ),
            "pages": self.pages,
            "language": "English",
            "isFeatured": False,
            "isOnSale": self.is_on_sale,
            "discountPercentage": self.discount_percentage,
            "availabilityStatus": self.availability_status,
            "isInStock": self.is_in_stock,
            "category": self.category_name.lower().replace(" ", "-"),
            "categoryName": self.category_name,
            "createdAt": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
            ),
            "updatedAt": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
            ),
        }

    def to_dict_simple(self):
        """Convert book object to simple dictionary (for cart items)"""
        return {
            "id": self.isbn,
            "title": self.title,
            "author": self.author_name,
            "price": float(self.price),
            "image": self.image,
            "stock": self.stock_quantity,
        }

    @classmethod
    def search(cls, query):
        """Search books by title or author"""
        return cls.query.filter(
            db.or_(cls.title.contains(query), cls.author_name.contains(query))
        )

    @classmethod
    def get_by_category(cls, category_name):
        """Get books by category"""
        return cls.query.filter_by(category_name=category_name)

    def __repr__(self):
        return f"<Book {self.title} by {self.author_name}>"
