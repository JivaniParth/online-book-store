from functools import wraps
from flask import request, jsonify
import re


def validate_json(*required_fields):
    """Validate JSON request has required fields"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400

            data = request.get_json()
            missing = [field for field in required_fields if not data.get(field)]

            if missing:
                return (
                    jsonify({"error": "Missing required fields", "missing": missing}),
                    400,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_price(price):
    """Validate price is positive and reasonable"""
    try:
        price_float = float(price)
        return 0 <= price_float <= 10000
    except:
        return False


def validate_isbn(isbn):
    """Validate ISBN format"""
    # Remove hyphens and spaces
    isbn = isbn.replace("-", "").replace(" ", "")
    # Check if it's 10 or 13 digits
    return len(isbn) in [10, 13] and isbn.isdigit()


def validate_stock(stock):
    """Validate stock quantity"""
    try:
        stock_int = int(stock)
        return 0 <= stock_int <= 100000
    except:
        return False
