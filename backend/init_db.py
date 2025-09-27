#!/usr/bin/env python3
"""
Database initialization script for BookHaven
This script sets up the database, creates tables, and populates sample data
"""

import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize database with tables and sample data"""
    
    # Import the app and db from your main application
    from app import create_app
    from database import db

    app = create_app()
    
    with app.app_context():
        try:
            # Import models to register them with SQLAlchemy
            import models.user
            import models.category
            import models.book
            import models.cart
            import models.order
            
            from models.user import User
            from models.category import Category
            from models.book import Book
            from models.cart import CartItem
            from models.order import Order, OrderItem
            
            print("Creating database tables...")
            db.create_all()
            
            # Check if data already exists
            if Category.query.first():
                print("Database already contains data. Skipping initialization.")
                return True
            
            # Create sample categories
            print("Creating sample categories...")
            categories_data = [
                {'name': 'Classics', 'description': 'Timeless literary works that have stood the test of time'},
                {'name': 'Science Fiction', 'description': 'Futuristic and sci-fi novels exploring technology and space'},
                {'name': 'Fantasy', 'description': 'Magic, dragons, and fantasy adventures in imaginary worlds'},
                {'name': 'Romance', 'description': 'Love stories and romantic novels for the heart'},
                {'name': 'Thriller', 'description': 'Suspenseful and thrilling stories that keep you on edge'},
                {'name': 'Dystopian', 'description': 'Dystopian and post-apocalyptic fiction'},
                {'name': 'Mystery', 'description': 'Crime, detective, and mystery novels'},
                {'name': 'Biography', 'description': 'Life stories of notable people'},
                {'name': 'Self Help', 'description': 'Books for personal development and improvement'},
                {'name': 'History', 'description': 'Historical events and periods'}
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                categories[cat_data['name']] = category
            
            db.session.commit()
            print(f"Created {len(categories_data)} categories")
            
            # Create sample books
            print("Creating sample books...")
            books_data = [
                {
                    'title': 'The Great Gatsby',
                    'author': 'F. Scott Fitzgerald',
                    'description': 'A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream.',
                    'price': 12.99,
                    'original_price': 15.99,
                    'stock': 15,
                    'rating': 4.5,
                    'reviews': 1234,
                    'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop',
                    'category': 'Classics',
                    'isbn': '9780743273565'
                },
                {
                    'title': 'To Kill a Mockingbird',
                    'author': 'Harper Lee',
                    'description': 'A gripping tale of racial injustice and childhood innocence in the American South.',
                    'price': 13.99,
                    'original_price': 16.99,
                    'stock': 12,
                    'rating': 4.8,
                    'reviews': 2156,
                    'image': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop',
                    'category': 'Classics',
                    'isbn': '9780061120084'
                },
                {
                    'title': '1984',
                    'author': 'George Orwell',
                    'description': 'A dystopian masterpiece about totalitarianism, surveillance, and the power of language.',
                    'price': 13.99,
                    'original_price': 15.99,
                    'stock': 25,
                    'rating': 4.7,
                    'reviews': 2890,
                    'image': 'https://images.unsplash.com/photo-1495640452828-3df6795cf69b?w=300&h=400&fit=crop',
                    'category': 'Dystopian',
                    'isbn': '9780451524935'
                },
                {
                    'title': 'Dune',
                    'author': 'Frank Herbert',
                    'description': 'Epic science fiction saga set on the desert planet Arrakis, featuring politics, religion, and ecology.',
                    'price': 16.99,
                    'original_price': 19.99,
                    'stock': 20,
                    'rating': 4.6,
                    'reviews': 3421,
                    'image': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop',
                    'category': 'Science Fiction',
                    'isbn': '9780441013593'
                },
                {
                    'title': 'The Hobbit',
                    'author': 'J.R.R. Tolkien',
                    'description': 'An unexpected journey to the Lonely Mountain with Bilbo Baggins and thirteen dwarves.',
                    'price': 14.99,
                    'original_price': 17.99,
                    'stock': 30,
                    'rating': 4.9,
                    'reviews': 4532,
                    'image': 'https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=300&h=400&fit=crop',
                    'category': 'Fantasy',
                    'isbn': '9780547928227'
                },
                {
                    'title': 'Pride and Prejudice',
                    'author': 'Jane Austen',
                    'description': 'A timeless romance and social commentary about Elizabeth Bennet and Mr. Darcy.',
                    'price': 10.99,
                    'original_price': 13.99,
                    'stock': 18,
                    'rating': 4.4,
                    'reviews': 1876,
                    'image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=300&h=400&fit=crop',
                    'category': 'Romance',
                    'isbn': '9780141439518'
                },
                {
                    'title': 'Gone Girl',
                    'author': 'Gillian Flynn',
                    'description': 'A psychological thriller about a marriage gone wrong, full of twists and unreliable narrators.',
                    'price': 15.99,
                    'original_price': 18.99,
                    'stock': 14,
                    'rating': 4.3,
                    'reviews': 2134,
                    'image': 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=300&h=400&fit=crop',
                    'category': 'Thriller',
                    'isbn': '9780307588364'
                },
                {
                    'title': 'The Girl with the Dragon Tattoo',
                    'author': 'Stieg Larsson',
                    'description': 'A gripping mystery thriller featuring journalist Mikael Blomkvist and hacker Lisbeth Salander.',
                    'price': 16.99,
                    'original_price': 19.99,
                    'stock': 10,
                    'rating': 4.5,
                    'reviews': 3421,
                    'image': 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=300&h=400&fit=crop',
                    'category': 'Mystery',
                    'isbn': '9780307949486'
                }
            ]
            
            for book_data in books_data:
                category = categories[book_data['category']]
                book = Book(
                    title=book_data['title'],
                    author=book_data['author'],
                    description=book_data['description'],
                    price=book_data['price'],
                    original_price=book_data['original_price'],
                    stock=book_data['stock'],
                    rating=book_data['rating'],
                    reviews=book_data['reviews'],
                    image=book_data['image'],
                    isbn=book_data['isbn'],
                    category_id=category.id
                )
                db.session.add(book)
            
            db.session.commit()
            print(f"Created {len(books_data)} books")
            
            # Create a sample admin user
            print("Creating admin user...")
            admin_user = User(
                first_name='Admin',
                last_name='User',
                email='admin@bookhaven.com',
                phone='+1234567890',
                address='123 Admin Street',
                city='New York',
                postal_code='10001'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # Create a sample customer user
            customer_user = User(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='+1234567891',
                address='456 Customer Ave',
                city='Los Angeles',
                postal_code='90210'
            )
            customer_user.set_password('customer123')
            db.session.add(customer_user)
            
            db.session.commit()
            print("Created sample users")
            
            print("\nDatabase initialization completed successfully!")
            print("\nSample login credentials:")
            print("Admin: admin@bookhaven.com / admin123")
            print("Customer: john.doe@example.com / customer123")
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            return False
        
    return True

if __name__ == '__main__':
    print("BookHaven Database Initialization")
    print("=" * 40)
    
    if init_database():
        print("\nDatabase setup complete!")
        print("You can now start the Flask application with: python app.py")
    else:
        print("\nDatabase setup failed!")
        sys.exit(1)