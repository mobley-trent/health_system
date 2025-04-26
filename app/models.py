from . import db
from flask_login import UserMixin
from . import login_manager


class User(UserMixin, db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for the user.
        password (str): Hashed password for the user.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class Client(db.Model):
    """
    Represents a client in the system.

    Attributes:
        id (int): Primary key for the client.
        name (str): Name of the client.
        age (int): Age of the client.
        gender (str): Gender of the client.
        enrollments (list): List of enrollments associated with the client.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    enrollments = db.relationship("Enrollment", back_populates="client")


class Program(db.Model):
    """
    Represents a program in the system.

    Attributes:
        id (int): Primary key for the program.
        name (str): Unique name of the program.
        description (str): Description of the program.
        enrollments (list): List of enrollments associated with the program.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    enrollments = db.relationship(
        "Enrollment", back_populates="program", cascade="all, delete-orphan"
    )


class Enrollment(db.Model):
    """
    Represents an enrollment of a client in a program.

    Attributes:
        id (int): Primary key for the enrollment.
        client_id (int): Foreign key referencing the client.
        program_id (int): Foreign key referencing the program.
        client (Client): Relationship to the associated client.
        program (Program): Relationship to the associated program.
    """

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
