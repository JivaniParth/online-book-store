"""
Test script to verify INSERT, UPDATE, DELETE operations
Run this from your backend directory: python test_db_operations.py
"""

import sys

sys.path.append(".")

from app import create_app
from database import db
from models.user import User
from models.book import Book
from models.category import Category
from models.cart import CartItem
import bcrypt


def test_database_operations():
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 50)
        print("🧪 TESTING DATABASE OPERATIONS")
        print("=" * 50 + "\n")

        # Test 1: INSERT operation
        print("📝 Test 1: INSERT Operation")
        try:
            # Create a test user
            test_user = User()
            test_user.name = "Test User"
            test_user.email = f"test_{datetime.now().timestamp()}@test.com"
            test_user.phone = "1234567890"
            test_user.user_type = "customer"
            test_user.set_password("TestPass@123")

            db.session.add(test_user)
            db.session.commit()

            print(f"✅ INSERT Success: Created user with ID {test_user.user_id}")

        except Exception as e:
            print(f"❌ INSERT Failed: {str(e)}")
            db.session.rollback()
            return

        # Test 2: UPDATE operation
        print("\n📝 Test 2: UPDATE Operation")
        try:
            test_user.name = "Updated Test User"
            test_user.phone = "9876543210"
            db.session.commit()

            print(f"✅ UPDATE Success: Updated user {test_user.user_id}")

        except Exception as e:
            print(f"❌ UPDATE Failed: {str(e)}")
            db.session.rollback()
            return

        # Test 3: INSERT with relationships (Cart)
        print("\n📝 Test 3: INSERT with Relationships (Cart)")
        try:
            # Get a book (assuming you have books in database)
            book = Book.query.first()

            if book:
                cart_item = CartItem(
                    user_id=test_user.user_id, book_id=book.isbn, quantity=1
                )
                db.session.add(cart_item)
                db.session.commit()
                print(f"✅ CART INSERT Success: Added book {book.isbn} to cart")
            else:
                print("⚠️  No books found in database. Skipping cart test.")

        except Exception as e:
            print(f"❌ CART INSERT Failed: {str(e)}")
            db.session.rollback()

        # Test 4: DELETE operation
        print("\n📝 Test 4: DELETE Operation")
        try:
            user_id = test_user.user_id
            db.session.delete(test_user)
            db.session.commit()

            print(f"✅ DELETE Success: Deleted user {user_id}")

        except Exception as e:
            print(f"❌ DELETE Failed: {str(e)}")
            db.session.rollback()

        # Test 5: Verify foreign key constraints
        print("\n📝 Test 5: Foreign Key Constraints")
        try:
            # Try to insert a cart item with non-existent user
            invalid_cart = CartItem(
                user_id=999999, book_id="1234567890123", quantity=1  # Non-existent user
            )
            db.session.add(invalid_cart)
            db.session.commit()

            print(
                "❌ Foreign Key Constraint FAILED: Should have rejected invalid user_id"
            )

        except Exception as e:
            db.session.rollback()
            if "foreign key constraint" in str(e).lower():
                print("✅ Foreign Key Constraint Working: Rejected invalid user_id")
            else:
                print(f"⚠️  Error (not FK): {str(e)}")

        print("\n" + "=" * 50)
        print("🏁 DATABASE TESTS COMPLETED")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    from datetime import datetime

    test_database_operations()
