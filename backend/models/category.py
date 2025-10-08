from database import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = "category"

    category_name = db.Column(db.String(255), primary_key=True)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, name, description=None):
        self.category_name = name
        self.description = description

    @property
    def id(self):
        return self.slug

    @property
    def name(self):
        return self.category_name

    @property
    def slug(self):
        """Generate URL-friendly slug from name"""
        return self.category_name.lower().replace(" ", "-").replace("&", "and")

    @property
    def is_active(self):
        return True

    @property
    def created_at(self):
        return datetime.now(datetime.timezone.utc)

    def to_dict(self):
        """Convert category object to dictionary"""
        return {
            "id": self.slug,
            "name": self.category_name,
            "description": self.description,
        }

    def __repr__(self):
        return f"<Category {self.category_name}>"
