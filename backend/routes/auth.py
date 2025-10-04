from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.auth import validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        from database import db
        from models.user import User

        data = request.get_json()

        # Validate required fields
        required_fields = ["firstName", "lastName", "email", "password"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # Validate email format
        if not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password
        password_error = validate_password(data["password"])
        if password_error:
            return jsonify({"error": password_error}), 400

        # Check if user already exists
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already registered"}), 400

        # Create new user
        full_name = f"{data['firstName']} {data['lastName']}"
        user = User()
        user.name = full_name
        user.email = data["email"].lower()
        user.phone = data.get("phone", "")
        user.address = data.get("address", "")
        user.city = data.get("city", "")
        user.user_type = "customer"
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.user_id))

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "access_token": access_token,
                }
            ),
            201,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        from database import db
        from models.user import User

        data = request.get_json()

        # Validate required fields
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        # Find user
        user = User.query.filter_by(email=data["email"].lower()).first()

        # Check credentials
        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        # Create access token
        access_token = create_access_token(identity=str(user.user_id))

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "access_token": access_token,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        from models.user import User

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"success": True, "user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get profile", "details": str(e)}), 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        from database import db
        from models.user import User

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        # Update user fields
        if "firstName" in data or "lastName" in data:
            first_name = data.get("firstName", user.first_name)
            last_name = data.get("lastName", user.last_name)
            user.name = f"{first_name} {last_name}"

        if "email" in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data["email"].lower()).first()
            if existing_user and existing_user.user_id != user.user_id:
                return jsonify({"error": "Email already in use"}), 400
            user.email = data["email"].lower()

        if "phone" in data:
            user.phone = data["phone"]
        if "address" in data:
            user.address = data["address"]
        if "city" in data:
            user.city = data["city"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": user.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500


@auth_bp.route("/verify-token", methods=["POST"])
@jwt_required()
def verify_token():
    try:
        from models.user import User

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"success": True, "user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Token verification failed"}), 401
