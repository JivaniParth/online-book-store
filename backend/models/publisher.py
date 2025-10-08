from database import db
from datetime import datetime


class Publisher(db.Model):
    __tablename__ = "publisher"

    publisher_name = db.Column(db.String(255), primary_key=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    established_date = db.Column(db.Date, nullable=False)

    # Relationship to books
    books = db.relationship(
        "Book",
        backref="publisher_ref",
        lazy=True,
        foreign_keys="Book.publisher_name",
    )

    def __init__(
        self,
        publisher_name,
        established_date,
        address=None,
        city=None,
        phone=None,
        email=None,
    ):
        self.publisher_name = publisher_name
        self.address = address
        self.city = city
        self.phone = phone
        self.email = email
        self.established_date = established_date

    def to_dict(self):
        """Convert publisher object to dictionary"""
        return {
            "publisher_name": self.publisher_name,
            "address": self.address,
            "city": self.city,
            "phone": self.phone,
            "email": self.email,
            "established_date": (
                self.established_date.strftime("%Y-%m-%d")
                if self.established_date
                else None
            ),
        }

    def __repr__(self):
        return f"<Publisher {self.publisher_name}>"
