"""
Authentication Debug Script
Run this to test and fix password issues
Usage: python test_auth.py
"""

import sys
import bcrypt
from app import create_app
from database import db
from models.user import User


def test_user_login():
    """Test user authentication"""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("AUTHENTICATION DEBUG TOOL")
        print("=" * 60)

        # Get user
        email = input("\nEnter email to test (default: john.doe@example.com): ").strip()
        if not email:
            email = "john.doe@example.com"

        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            print(f"\n❌ User with email '{email}' not found in database")
            print("\nAvailable users:")
            all_users = User.query.all()
            for u in all_users:
                print(f"  - {u.email}")
            return

        print(f"\n✅ User found: {user.name} ({user.email})")
        print(f"   User ID: {user.user_id}")
        print(f"   User Type: {user.user_type}")

        # Check stored password
        print(f"\n📝 Stored password hash: {user.password[:50]}...")
        print(f"   Hash length: {len(user.password)}")

        # Check if it looks like bcrypt
        is_bcrypt = (
            user.password.startswith("$2b$")
            or user.password.startswith("$2a$")
            or user.password.startswith("$2y$")
        )
        print(f"   Looks like bcrypt: {'✅ Yes' if is_bcrypt else '❌ No'}")

        # Test password
        test_password = input(
            "\nEnter password to test (default: password123): "
        ).strip()
        if not test_password:
            test_password = "password123"

        print(f"\n🔐 Testing password: '{test_password}'")

        # Try to verify
        try:
            result = user.check_password(test_password)
            print(
                f"\n{'✅ Password match!' if result else '❌ Password does not match'}"
            )
        except Exception as e:
            print(f"\n❌ Error checking password: {e}")
            print("\nThis usually means the password is not properly hashed.")

        # Offer to fix
        if not is_bcrypt or not user.check_password(test_password):
            fix = (
                input("\n🔧 Do you want to fix this user's password? (y/n): ")
                .strip()
                .lower()
            )
            if fix == "y":
                new_password = input("Enter new password: ").strip()
                if new_password:
                    user.set_password(new_password)
                    db.session.commit()
                    print(f"\n✅ Password updated for {user.email}")
                    print(f"   New hash: {user.password[:50]}...")

                    # Verify it works
                    if user.check_password(new_password):
                        print("✅ Verification successful!")
                    else:
                        print("❌ Verification failed - something went wrong")


def fix_all_passwords():
    """Reset all user passwords to 'password123'"""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("FIX ALL USER PASSWORDS")
        print("=" * 60)

        confirm = (
            input(
                "\n⚠️  This will reset ALL user passwords to 'password123'\nAre you sure? (yes/no): "
            )
            .strip()
            .lower()
        )

        if confirm != "yes":
            print("Cancelled.")
            return

        users = User.query.all()
        print(f"\nFound {len(users)} users")

        for user in users:
            user.set_password("password123")
            print(f"  ✅ Reset password for: {user.email}")

        db.session.commit()
        print(f"\n✅ Successfully reset passwords for {len(users)} users")
        print("   Default password: password123")


def create_test_user():
    """Create a test user with proper password hashing"""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("CREATE TEST USER")
        print("=" * 60)

        email = input("\nEnter email (default: test@example.com): ").strip()
        if not email:
            email = "test@example.com"

        # Check if exists
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            print(f"\n❌ User with email '{email}' already exists")
            return

        name = input("Enter full name (default: Test User): ").strip()
        if not name:
            name = "Test User"

        password = input("Enter password (default: password123): ").strip()
        if not password:
            password = "password123"

        # Create user
        user = User()
        user.name = name
        user.email = email.lower()
        user.user_type = "customer"
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"\n✅ User created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: {password}")
        print(f"   User ID: {user.user_id}")

        # Test login
        if user.check_password(password):
            print("✅ Password verification works!")
        else:
            print("❌ Password verification failed!")


def show_menu():
    """Show main menu"""
    print("\n" + "=" * 60)
    print("AUTHENTICATION DEBUG MENU")
    print("=" * 60)
    print("\n1. Test user login")
    print("2. Fix all user passwords (reset to 'password123')")
    print("3. Create test user")
    print("4. Exit")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        test_user_login()
    elif choice == "2":
        fix_all_passwords()
    elif choice == "3":
        create_test_user()
    elif choice == "4":
        print("\nGoodbye!")
        sys.exit(0)
    else:
        print("\n❌ Invalid option")

    # Show menu again
    show_menu()


if __name__ == "__main__":
    show_menu()
