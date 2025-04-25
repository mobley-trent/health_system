from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging
import os

db = SQLAlchemy()
login_manager = LoginManager()
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)

    # Configuration
    app.config["SECRET_KEY"] = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/health.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes

    app.register_blueprint(routes.bp)

    with app.app_context():
        from .models import User, Client, Program, Enrollment

        db.create_all()

        # Create default doctor user if not exists
        from .models import User
        from werkzeug.security import generate_password_hash

        if not User.query.filter_by(username="doctor").first():
            doctor = User(
                username="doctor", password=generate_password_hash("password")
            )
            db.session.add(doctor)
            db.session.commit()

    return app
