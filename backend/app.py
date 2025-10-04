from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config import Config
from database import db


def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    migrate = Migrate(app, db)
    cors = CORS(
        app,
        origins=Config.CORS_ORIGINS,
        supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS,
        max_age=Config.CORS_MAX_AGE,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    jwt = JWTManager(app)

    # Import models (this registers them with SQLAlchemy)
    import models.user
    import models.book
    import models.category
    import models.cart
    import models.order
    import models.review

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.review import reviews_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return (
            jsonify({"status": "healthy", "message": "BookHaven API is running"}),
            200,
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Token has expired",
                    "message": "Please login again",
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid token",
                    "message": "Authentication failed",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Authorization token is required",
                    "message": "Please login to continue",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Token has been revoked",
                    "message": "Please login again",
                }
            ),
            401,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
