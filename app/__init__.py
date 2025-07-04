from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set in config!")

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register blueprints
    from .routes.main import main
    from .routes.auth import auth_bp
    from .routes.booking import booking_bp
    from .routes.services import services_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(dashboard_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        try:
            return render_template('404.html'), 404
        except Exception:
            return '<h1>404 Not Found</h1>', 404

    @app.errorhandler(500)
    def internal_error(e):
        try:
            return render_template('500.html'), 500
        except Exception:
            return '<h1>500 Internal Server Error</h1>', 500

    return app
