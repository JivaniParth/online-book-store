from database import db
from datetime import datetime
from sqlalchemy import Numeric, ForeignKey


class Book(db.Model):
    __tablename__ = "book_details"  # Changed to lowercase

    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author_name = db.Column(
        db.String(255),
        ForeignKey("author.author_name", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    publisher_name = db.Column(
        db.String(255),
        ForeignKey("publisher.publisher_name", ondelete="RESTRICT"),
        nullable=False,
    )
    category_name = db.Column(
        db.String(255),
        ForeignKey("category.category_name", ondelete="RESTRICT"),
        nullable=False,
    )
    price = db.Column(Numeric(10, 2), nullable=False)
    publication_date = db.Column(db.Date, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    # Relationships
    cart_items = db.relationship(
        "CartItem",
        backref="book",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="CartItem.book_id",
    )
    order_items = db.relationship(
        "OrderItem",
        backref="book",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="OrderItem.book_id",
    )
    reviews = db.relationship(
        "Review",
        backref="book",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="Review.book_id",
    )

    @property
    def id(self):
        return self.isbn

    @property
    def author(self):
        return self.author_name

    @property
    def stock(self):
        return self.stock_quantity

    @property
    def original_price(self):
        return self.price

    @property
    def rating(self):
        if self.reviews:
            return sum(r.rating for r in self.reviews) / len(self.reviews)
        return 0.0

    @property
    def review_count(self):
        return len(self.reviews) if self.reviews else 0

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def availability_status(self):
        if self.stock_quantity > 10:
            return "In Stock"
        elif self.stock_quantity > 0:
            return "Limited Stock"
        else:
            return "Out of Stock"

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
            "publisher": self.publisher_name,
            "category": self.category_name.lower().replace(" ", "-"),
            "categoryName": self.category_name,
            "availabilityStatus": self.availability_status,
            "isInStock": self.is_in_stock,
        }

    def to_dict_simple(self):
        """Convert book object to simple dictionary"""
        return {
            "id": self.isbn,
            "title": self.title,
            "author": self.author_name,
            "price": float(self.price),
            "image": self.image,
            "stock": self.stock_quantity,
        }

    def __repr__(self):
        return f"<Book {self.title} by {self.author_name}>"
