from database import db
from datetime import datetime
import string
import random
from sqlalchemy import Numeric
from decimal import Decimal


class Order(db.Model):
    __tablename__ = "Book_Order"  # Matches your DDL

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_status = db.Column(
        db.Enum(
            "pending", "completed", "failed", "refunded", name="payment_status_enum"
        ),
        default="pending",
    )

    # Relationships
    order_items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="OrderItem.order_id",
    )

    # Properties for backward compatibility
    @property
    def id(self):
        return self.order_id

    @property
    def order_number(self):
        """Generate order number from order_id"""
        return f"BH{self.order_id:08d}"

    @property
    def status(self):
        """Map payment_status to order status"""
        status_map = {
            "pending": "pending",
            "completed": "delivered",
            "failed": "cancelled",
            "refunded": "cancelled",
        }
        return status_map.get(self.payment_status, "pending")

    @status.setter
    def status(self, value):
        """Map order status to payment_status"""
        status_map = {
            "pending": "pending",
            "confirmed": "pending",
            "processing": "pending",
            "shipped": "completed",
            "delivered": "completed",
            "cancelled": "failed",
        }
        self.payment_status = status_map.get(value, "pending")

    @property
    def first_name(self):
        return self.customer_name.split()[0] if self.customer_name else ""

    @property
    def last_name(self):
        parts = self.customer_name.split()
        return " ".join(parts[1:]) if len(parts) > 1 else ""

    @property
    def email(self):
        return self.customer_email

    @property
    def address(self):
        return self.shipping_address

    @property
    def city(self):
        """Extract city from shipping address (last part before postal code)"""
        # This is a simple implementation, adjust based on your address format
        return ""

    @property
    def postal_code(self):
        return ""

    @property
    def created_at(self):
        return self.order_date

    @property
    def updated_at(self):
        return self.order_date

    @property
    def subtotal(self):
        """Calculate subtotal from order items"""
        return sum(item.total_price for item in self.order_items)

    @property
    def tax_amount(self):
        """Calculate tax (10%)"""
        return self.subtotal * Decimal("0.10")

    @property
    def shipping_cost(self):
        return Decimal("0.00")

    @property
    def discount_amount(self):
        return Decimal("0.00")

    def __init__(
        self,
        user_id,
        first_name,
        last_name,
        email,
        phone,
        address,
        city,
        postal_code,
        payment_method="cod",
    ):
        self.user_id = user_id
        self.customer_name = f"{first_name} {last_name}"
        self.customer_email = email
        self.phone = phone
        self.shipping_address = f"{address}, {city} {postal_code}"
        self.payment_method = payment_method
        self.total_amount = 0.00
        self.order_date = datetime.utcnow()

    def calculate_totals(self):
        """Calculate order totals"""
        # Calculate subtotal from order items
        subtotal = sum(item.total_price for item in self.order_items)

        # Calculate tax (10%)
        tax = subtotal * Decimal("0.10")

        # Calculate total
        self.total_amount = subtotal + tax

        return self.total_amount

    def add_item(self, book, quantity, price_per_item):
        """Add item to order"""
        order_item = OrderItem(
            book_id=book.isbn, quantity=quantity, unit_price=price_per_item
        )
        self.order_items.append(order_item)
        self.calculate_totals()

    def update_status(self, new_status):
        """Update order status"""
        self.status = new_status

    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.payment_status in ["pending"]

    def cancel(self):
        """Cancel order"""
        if self.can_cancel():
            self.payment_status = "failed"
            return True
        return False

    @property
    def full_name(self):
        """Get customer full name"""
        return self.customer_name

    @property
    def full_address(self):
        """Get formatted full address"""
        return self.shipping_address

    @property
    def items_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.order_items)

    def to_dict(self):
        """Convert order to dictionary"""
        return {
            "id": self.order_id,
            "orderNumber": self.order_number,
            "status": self.status,
            "customer": {
                "firstName": self.first_name,
                "lastName": self.last_name,
                "email": self.customer_email,
                "phone": self.phone,
                "fullName": self.customer_name,
            },
            "shipping": {
                "address": self.shipping_address,
                "city": self.city,
                "postalCode": self.postal_code,
                "fullAddress": self.shipping_address,
            },
            "payment": {"method": self.payment_method, "status": self.payment_status},
            "totals": {
                "subtotal": float(self.subtotal),
                "taxAmount": float(self.tax_amount),
                "shippingCost": float(self.shipping_cost),
                "discountAmount": float(self.discount_amount),
                "totalAmount": float(self.total_amount),
            },
            "items": [item.to_dict() for item in self.order_items],
            "itemsCount": self.items_count,
            "timestamps": {
                "createdAt": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "shippedAt": None,
                "deliveredAt": None,
            },
        }

    def to_dict_simple(self):
        """Convert order to simple dictionary (for order lists)"""
        return {
            "id": self.order_id,
            "orderNumber": self.order_number,
            "status": self.status,
            "totalAmount": float(self.total_amount),
            "itemsCount": self.items_count,
            "createdAt": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def get_user_orders(cls, user_id):
        """Get all orders for a user"""
        return (
            cls.query.filter_by(user_id=user_id).order_by(cls.order_date.desc()).all()
        )

    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "Order_Item"  # Matches your DDL

    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("Book_Order.order_id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id = db.Column(
        db.String(13), db.ForeignKey("Book_Details.isbn"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(Numeric(10, 2), nullable=False)

    # Property for backward compatibility
    @property
    def id(self):
        return self.order_item_id

    @property
    def price_per_item(self):
        return self.unit_price

    @property
    def created_at(self):
        return datetime.utcnow()

    def __init__(self, book_id, quantity, price_per_item):
        self.book_id = book_id
        self.quantity = quantity
        self.unit_price = price_per_item

    @property
    def total_price(self):
        """Calculate total price for this order item"""
        return self.unit_price * self.quantity

    def to_dict(self):
        """Convert order item to dictionary"""
        book_data = self.book.to_dict_simple() if self.book else {}

        return {
            "id": self.order_item_id,
            "bookId": self.book_id,
            "title": book_data.get("title", ""),
            "author": book_data.get("author", ""),
            "image": book_data.get("image", ""),
            "quantity": self.quantity,
            "pricePerItem": float(self.unit_price),
            "totalPrice": float(self.total_price),
            "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self):
        return (
            f"<OrderItem Order:{self.order_id} Book:{self.book_id} Qty:{self.quantity}>"
        )
