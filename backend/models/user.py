from database import db
from datetime import datetime
import bcrypt


class User(db.Model):
    __tablename__ = "User"  # Matches your DDL

    user_id = db.Column("user_id", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column("password", db.String(255), nullable=False)
    user_type = db.Column(
        db.Enum("customer", "admin", name="user_type_enum"),
        nullable=False,
        default="customer",
    )
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship(
        "CartItem", backref="user", lazy=True, foreign_keys="CartItem.user_id"
    )
    orders = db.relationship(
        "Order", backref="user", lazy=True, foreign_keys="Order.user_id"
    )
    reviews = db.relationship(
        "Review", backref="user", lazy=True, foreign_keys="Review.user_id"
    )

    # Property for backward compatibility with old code
    @property
    def id(self):
        return self.user_id

    @property
    def first_name(self):
        """Extract first name from full name"""
        return self.name.split()[0] if self.name else ""

    @property
    def last_name(self):
        """Extract last name from full name"""
        parts = self.name.split()
        return " ".join(parts[1:]) if len(parts) > 1 else ""

    @property
    def is_active(self):
        return True  # Default to active

    @property
    def created_at(self):
        return self.registration_date

    def set_password(self, password):
        """Hash and set the password"""
        password_bytes = password.encode("utf-8")
        self.password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        """Check if provided password matches the hash"""
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def get_avatar_url(self):
        """Generate avatar URL"""
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&background=6366f1&color=fff&size=40"

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": self.user_id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "postalCode": "",  # Not in your DDL
            "joinedDate": self.registration_date.strftime("%Y-%m-%d"),
            "avatar": self.get_avatar_url(),
            "user_type": self.user_type,
        }

    def __repr__(self):
        return f"<User {self.email}>"
