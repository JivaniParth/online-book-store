from app import create_app
from database import db
from models.user import User

app = create_app()

with app.app_context():
    try:
        # Test insert
        user = User()
        user.name = "Test User"
        user.email = "test@test.com"
        user.set_password("password123")
        user.user_type = "customer"

        db.session.add(user)
        db.session.commit()
        print(f"✅ User created: {user.user_id}")

        # Test update
        user.city = "Test City"
        db.session.commit()
        print(f"✅ User updated")

        # Test delete
        db.session.delete(user)
        db.session.commit()
        print(f"✅ User deleted")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
