from database import db
from datetime import datetime


class Review(db.Model):
    __tablename__ = "Review"  # Matches your DDL table name

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    book_id = db.Column(
        db.String(13), db.ForeignKey("Book_Details.isbn"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Properties for backward compatibility
    @property
    def id(self):
        return self.review_id

    @property
    def created_at(self):
        return self.review_date

    @property
    def comment(self):
        return self.review_text

    def __init__(self, user_id, book_id, rating, review_text=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.review_text = review_text
        self.review_date = datetime.utcnow()

    def to_dict(self):
        """Convert review to dictionary"""
        return {
            "id": self.review_id,
            "userId": self.user_id,
            "bookId": self.book_id,
            "rating": self.rating,
            "comment": self.review_text,
            "reviewDate": (
                self.review_date.strftime("%Y-%m-%d %H:%M:%S")
                if self.review_date
                else ""
            ),
            "user": self.user.to_dict() if self.user else None,
        }

    @classmethod
    def get_book_reviews(cls, book_id):
        """Get all reviews for a book"""
        return (
            cls.query.filter_by(book_id=book_id).order_by(cls.review_date.desc()).all()
        )

    @classmethod
    def get_user_reviews(cls, user_id):
        """Get all reviews by a user"""
        return (
            cls.query.filter_by(user_id=user_id).order_by(cls.review_date.desc()).all()
        )

    def __repr__(self):
        return f"<Review User:{self.user_id} Book:{self.book_id} Rating:{self.rating}>"
