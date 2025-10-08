from database import db


class Author(db.Model):
    __tablename__ = "author"

    author_name = db.Column(db.String(255), primary_key=True)
    biography = db.Column(db.Text, nullable=True)
    nationality = db.Column(db.String(100), nullable=True)

    # Relationship to books
    books = db.relationship(
        "Book",
        backref="author_ref",
        lazy=True,
        foreign_keys="Book.author_name",
    )

    def __init__(self, author_name, biography=None, nationality=None):
        self.author_name = author_name
        self.biography = biography
        self.nationality = nationality

    def to_dict(self):
        """Convert author object to dictionary"""
        return {
            "author_name": self.author_name,
            "biography": self.biography,
            "nationality": self.nationality,
        }

    def __repr__(self):
        return f"<Author {self.author_name}>"
