from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/book/<book_id>", methods=["GET"])
def get_book_reviews(book_id):
    """Get all reviews for a specific book"""
    try:
        from models.review import Review

        reviews = Review.get_book_reviews(book_id)

        return (
            jsonify(
                {
                    "success": True,
                    "reviews": [review.to_dict() for review in reviews],
                    "count": len(reviews),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        return jsonify({"error": "Failed to fetch reviews", "details": str(e)}), 500


@reviews_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_reviews():
    """Get all reviews by current user"""
    try:
        from models.review import Review

        user_id = int(get_jwt_identity())
        reviews = Review.get_user_reviews(user_id)

        return (
            jsonify(
                {
                    "success": True,
                    "reviews": [review.to_dict() for review in reviews],
                    "count": len(reviews),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching user reviews: {str(e)}")
        return jsonify({"error": "Failed to fetch reviews", "details": str(e)}), 500


@reviews_bp.route("", methods=["POST"])
@jwt_required()
def create_review():
    """Create a new review"""
    try:
        from database import db
        from models.review import Review
        from models.book import Book

        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Validate required fields
        if not data.get("book_id") or not data.get("rating"):
            return jsonify({"error": "book_id and rating are required"}), 400

        # Validate rating (1-5)
        rating = int(data["rating"])
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        # Check if book exists
        book = Book.query.filter_by(isbn=str(data["book_id"])).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404

        # Check if user already reviewed this book
        existing_review = Review.query.filter_by(
            user_id=user_id, book_id=str(data["book_id"])
        ).first()

        if existing_review:
            return jsonify({"error": "You have already reviewed this book"}), 400

        # Create review
        review = Review(
            user_id=user_id,
            book_id=str(data["book_id"]),
            rating=rating,
            review_text=data.get("review_text", ""),
        )

        db.session.add(review)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Review created successfully",
                    "review": review.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error creating review: {str(e)}")
        return jsonify({"error": "Failed to create review", "details": str(e)}), 500


@reviews_bp.route("/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):
    """Update user's own review"""
    try:
        from database import db
        from models.review import Review

        user_id = int(get_jwt_identity())

        review = Review.query.get(review_id)
        if not review:
            return jsonify({"error": "Review not found"}), 404

        # Check if review belongs to user
        if review.user_id != user_id:
            return jsonify({"error": "Unauthorized to update this review"}), 403

        data = request.get_json()

        # Update rating if provided
        if "rating" in data:
            rating = int(data["rating"])
            if rating < 1 or rating > 5:
                return jsonify({"error": "Rating must be between 1 and 5"}), 400
            review.rating = rating

        # Update review text if provided
        if "review_text" in data:
            review.review_text = data["review_text"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Review updated successfully",
                    "review": review.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error updating review: {str(e)}")
        return jsonify({"error": "Failed to update review", "details": str(e)}), 500


@reviews_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    """Delete user's own review"""
    try:
        from database import db
        from models.review import Review

        user_id = int(get_jwt_identity())

        review = Review.query.get(review_id)
        if not review:
            return jsonify({"error": "Review not found"}), 404

        # Check if review belongs to user
        if review.user_id != user_id:
            return jsonify({"error": "Unauthorized to delete this review"}), 403

        db.session.delete(review)
        db.session.commit()

        return jsonify({"success": True, "message": "Review deleted successfully"}), 200

    except Exception as e:
        from database import db

        db.session.rollback()
        logger.error(f"Error deleting review: {str(e)}")
        return jsonify({"error": "Failed to delete review", "details": str(e)}), 500
