from database import db
from datetime import datetime
import string
import random
from sqlalchemy import Numeric
from decimal import Decimal

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', name='order_status'), default='pending')
    
    # Customer Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Shipping Address
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    
    # Payment Information
    payment_method = db.Column(db.Enum('cod', 'online', name='payment_method'), default='cod')
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded', name='payment_status'), default='pending')
    
    # Order Totals
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    tax_amount = db.Column(Numeric(10, 2), default=0.00)
    shipping_cost = db.Column(Numeric(10, 2), default=0.00)
    discount_amount = db.Column(Numeric(10, 2), default=0.00)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, first_name, last_name, email, phone, address, city, 
                 postal_code, payment_method='cod'):
        self.user_id = user_id
        self.order_number = self.generate_order_number()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.postal_code = postal_code
        self.payment_method = payment_method
        self.subtotal = 0.00
        self.total_amount = 0.00
    
    def generate_order_number(self):
        """Generate unique order number"""
        prefix = "BH"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_part}"
    
    def calculate_totals(self):
      """Calculate order totals"""
      # Calculate subtotal from order items
      self.subtotal = sum(item.total_price for item in self.order_items)
      
      # Convert float to Decimal for tax calculation
      tax_rate = Decimal('0.10')  # 10% tax as Decimal instead of float
      self.tax_amount = self.subtotal * tax_rate
      
      # Calculate total
      self.total_amount = self.subtotal + self.tax_amount
      
      return self.total_amount
    
    def add_item(self, book, quantity, price_per_item):
        """Add item to order"""
        order_item = OrderItem(
            book_id=book.id,
            quantity=quantity,
            price_per_item=price_per_item
        )
        self.order_items.append(order_item)
        self.calculate_totals()
    
    def update_status(self, new_status):
        """Update order status with timestamp tracking"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == 'shipped':
            self.shipped_at = datetime.utcnow()
        elif new_status == 'delivered':
            self.delivered_at = datetime.utcnow()
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def cancel(self):
        """Cancel order"""
        if self.can_cancel():
            self.status = 'cancelled'
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    @property
    def full_name(self):
        """Get customer full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        return f"{self.address}, {self.city} {self.postal_code}"
    
    @property
    def items_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.order_items)
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'orderNumber': self.order_number,
            'status': self.status,
            'customer': {
                'firstName': self.first_name,
                'lastName': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'fullName': self.full_name
            },
            'shipping': {
                'address': self.address,
                'city': self.city,
                'postalCode': self.postal_code,
                'fullAddress': self.full_address
            },
            'payment': {
                'method': self.payment_method,
                'status': self.payment_status
            },
            'totals': {
                'subtotal': float(self.subtotal),
                'taxAmount': float(self.tax_amount),
                'shippingCost': float(self.shipping_cost),
                'discountAmount': float(self.discount_amount),
                'totalAmount': float(self.total_amount)
            },
            'items': [item.to_dict() for item in self.order_items],
            'itemsCount': self.items_count,
            'timestamps': {
                'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'shippedAt': self.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if self.shipped_at else None,
                'deliveredAt': self.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if self.delivered_at else None
            }
        }
    
    def to_dict_simple(self):
        """Convert order to simple dictionary (for order lists)"""
        return {
            'id': self.id,
            'orderNumber': self.order_number,
            'status': self.status,
            'totalAmount': float(self.total_amount),
            'itemsCount': self.items_count,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def get_user_orders(cls, user_id):
        """Get all orders for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    def __repr__(self):
        return f'<Order {self.order_number} - {self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __init__(self, book_id, quantity, price_per_item):
        self.book_id = book_id
        self.quantity = quantity
        self.price_per_item = price_per_item
    
    @property
    def total_price(self):
        """Calculate total price for this order item"""
        return self.price_per_item * self.quantity
    
    def to_dict(self):
        """Convert order item to dictionary"""
        book_data = self.book.to_dict_simple() if self.book else {}
        
        return {
            'id': self.id,
            'bookId': self.book_id,
            'title': book_data.get('title', ''),
            'author': book_data.get('author', ''),
            'image': book_data.get('image', ''),
            'quantity': self.quantity,
            'pricePerItem': float(self.price_per_item),
            'totalPrice': float(self.total_price),
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Book:{self.book_id} Qty:{self.quantity}>'