from database import db
from datetime import datetime
from sqlalchemy import ForeignKey


class CartItem(db.Model):
    __tablename__ = "cart"  # Changed to lowercase

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    book_id = db.Column(
        db.String(13),
        ForeignKey("book_details.isbn", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def id(self):
        return self.cart_id

    @property
    def created_at(self):
        return self.date_added

    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.book.price * self.quantity if self.book else 0

    @property
    def total_original_price(self):
        """Calculate total original price for this cart item"""
        original_price = self.book.price
        return original_price * self.quantity if self.book else 0

    @property
    def savings(self):
        """Calculate savings for this cart item"""
        return self.total_original_price - self.total_price

    def update_quantity(self, new_quantity):
        """Update quantity with validation"""
        if new_quantity <= 0:
            return False

        if self.book and new_quantity > self.book.stock_quantity:
            return False

        self.quantity = new_quantity
        self.date_added = datetime.utcnow()
        return True

    def to_dict(self):
        """Convert cart item to dictionary"""
        book_data = self.book.to_dict_simple() if self.book else {}

        return {
            "id": self.book_id,
            "book_id": self.book_id,
            "title": book_data.get("title", ""),
            "author": book_data.get("author", ""),
            "price": book_data.get("price", 0),
            "image": book_data.get("image", ""),
            "quantity": self.quantity,
            "totalPrice": float(self.total_price),
            "stock": book_data.get("stock", 0),
        }

    @classmethod
    def get_user_cart(cls, user_id):
        """Get all cart items for a user"""
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def clear_user_cart(cls, user_id):
        """Clear all items from user's cart"""
        cls.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    def __repr__(self):
        return f"<CartItem User:{self.user_id} Book:{self.book_id} Qty:{self.quantity}>"
