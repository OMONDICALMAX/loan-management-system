from flask import Flask
from app.models import Customer
from app.config import Config
from app.extensions import bcrypt, db, jwt, migrate
from app.routes.health import health_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(health_bp)

    return app
