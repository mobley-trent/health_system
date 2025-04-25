from . import db
from flask_login import UserMixin
from . import login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # We'll hash this later


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    enrollments = db.relationship("Enrollment", back_populates="client")


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    enrollments = db.relationship(
        "Enrollment", back_populates="program", cascade="all, delete-orphan"
    )


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), nullable=False
    )
    program_id = db.Column(
        db.Integer, db.ForeignKey("program.id", ondelete="CASCADE"), nullable=False
    )

    client = db.relationship("Client", back_populates="enrollments")
    program = db.relationship("Program", back_populates="enrollments")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
