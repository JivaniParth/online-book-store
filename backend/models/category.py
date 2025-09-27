from database import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', backref='category', lazy=True)
    
    def __init__(self, name, description=None):
        self.name = name
        self.slug = self.generate_slug(name)
        self.description = description
    
    def generate_slug(self, name):
        """Generate URL-friendly slug from name"""
        return name.lower().replace(' ', '-').replace('&', 'and')
    
    def to_dict(self):
        """Convert category object to dictionary"""
        return {
            'id': self.slug,
            'name': self.name,
            'description': self.description
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'