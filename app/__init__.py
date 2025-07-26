# app/__init__.py

from flask import Flask
from .extensions import db, migrate
from .config import Config

# Import models so Flask-Migrate can detect them
from . import models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🔧 Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 🔌 Register blueprints
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    # from .routes.auth import auth_bp  # if you add login/signup in future

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    # Optional: add a root route for testing
    @app.route('/')
    def index():
        return "✅ Smart Water Metering System is Running!"

    return app
