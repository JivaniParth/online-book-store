from database import db
from datetime import datetime
import string
import random
from sqlalchemy import Numeric
from decimal import Decimal


class Order(db.Model):
    __tablename__ = "book_order"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("User.user_id", ondelete="CASCADE"), nullable=False
    )
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False, default=0)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_status = db.Column(
        db.Enum(
            "pending", "completed", "failed", "refunded", name="payment_status_enum"
        ),
        default="pending",
    )

    order_items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="OrderItem.order_id",
    )

    @property
    def id(self):
        return self.order_id

    @property
    def order_number(self):
        return f"BH{self.order_id:08d}"

    @property
    def status(self):
        status_map = {
            "pending": "pending",
            "completed": "delivered",
            "failed": "cancelled",
            "refunded": "cancelled",
        }
        return status_map.get(self.payment_status, "pending")

    @status.setter
    def status(self, value):
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
        return sum(item.total_price for item in self.order_items)

    @property
    def tax_amount(self):
        return self.subtotal * Decimal("0.08")

    @property
    def shipping_cost(self):
        return Decimal("0.00") if self.subtotal >= 50 else Decimal("5.99")

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
        self.total_amount = Decimal("0.00")
        self.order_date = datetime.utcnow()
        self.payment_status = "pending"

    def calculate_totals(self):
        subtotal = sum(item.total_price for item in self.order_items)
        tax = subtotal * Decimal("0.08")
        shipping = Decimal("0.00") if subtotal >= 50 else Decimal("5.99")
        self.total_amount = subtotal + tax + shipping
        return self.total_amount

    def add_item(self, book, quantity, price_per_item):
        order_item = OrderItem(
            book_id=book.isbn, quantity=quantity, price_per_item=price_per_item
        )
        self.order_items.append(order_item)
        self.calculate_totals()

    def update_status(self, new_status):
        self.status = new_status

    def can_cancel(self):
        return self.payment_status in ["pending"]

    def cancel(self):
        if self.can_cancel():
            self.payment_status = "failed"
            return True
        return False

    @property
    def full_name(self):
        return self.customer_name

    @property
    def full_address(self):
        return self.shipping_address

    @property
    def items_count(self):
        return sum(item.quantity for item in self.order_items)

    def to_dict(self):
        # Use stored total_amount, convert Decimal to float
        total_amount = float(self.total_amount) if self.total_amount else 0.00

        # Calculate component totals for display
        subtotal = (
            sum(item.total_price for item in self.order_items)
            if self.order_items
            else Decimal("0.00")
        )
        tax_amount = subtotal * Decimal("0.08")
        shipping_cost = Decimal("0.00") if subtotal >= 50 else Decimal("5.99")

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
                "subtotal": float(subtotal),
                "taxAmount": float(tax_amount),
                "shippingCost": float(shipping_cost),
                "discountAmount": 0.00,
                "totalAmount": total_amount,
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
        total_amount = float(self.total_amount) if self.total_amount else 0.00

        return {
            "id": self.order_id,
            "orderNumber": self.order_number,
            "status": self.status,
            "totalAmount": total_amount,
            "itemsCount": self.items_count,
            "createdAt": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def get_user_orders(cls, user_id):
        return (
            cls.query.filter_by(user_id=user_id).order_by(cls.order_date.desc()).all()
        )

    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "Order_Item"

    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("Book_Order.order_id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id = db.Column(
        db.String(13),
        db.ForeignKey("Book_Details.isbn", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(Numeric(10, 2), nullable=False)

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
        self.unit_price = Decimal(str(price_per_item))

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def to_dict(self):
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
