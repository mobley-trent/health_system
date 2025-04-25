from . import db
from flask_login import UserMixin
from . import login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))  # We'll hash this later


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    enrollments = db.relationship("Enrollment", back_populates="client")


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)

    enrollments = db.relationship("Enrollment", back_populates="program")


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"))

    client = db.relationship("Client", back_populates="enrollments")
    program = db.relationship("Program", back_populates="enrollments")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
