"""
Quick Password Fix Script
This will reset passwords for all users to 'password123' with proper bcrypt hashing
Usage: python fix_passwords.py
"""

from app import create_app
from database import db
from models.user import User


def main():
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("QUICK PASSWORD FIX")
        print("=" * 60)

        # Get all users
        users = User.query.all()

        if not users:
            print("\n❌ No users found in database")
            return

        print(f"\n📋 Found {len(users)} user(s):")
        for user in users:
            print(f"   - {user.email} ({user.name})")

        print("\n⚠️  This will reset ALL passwords to: password123")
        confirm = input("Continue? (yes/no): ").strip().lower()

        if confirm != "yes":
            print("\n❌ Cancelled")
            return

        print("\n🔧 Fixing passwords...")

        success_count = 0
        for user in users:
            try:
                # Set password using bcrypt
                user.set_password("password123")
                print(f"   ✅ Fixed: {user.email}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Failed for {user.email}: {e}")

        # Commit changes
        db.session.commit()

        print(f"\n✅ Successfully fixed {success_count}/{len(users)} user passwords")
        print("\n📝 Login credentials:")
        for user in users:
            print(f"   Email: {user.email}")
            print(f"   Password: password123")
            print()

        # Verify one user
        if users:
            test_user = users[0]
            if test_user.check_password("password123"):
                print("✅ Verification test passed!")
            else:
                print("❌ Verification test failed - please check User model")


if __name__ == "__main__":
    main()
