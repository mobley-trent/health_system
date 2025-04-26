from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import logging
import os

load_dotenv()  # Load environment variables from .env file
db = SQLAlchemy()
login_manager = LoginManager()
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)

    # Configuration
    app.config["SECRET_KEY"] = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes

    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
