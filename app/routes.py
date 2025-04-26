from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from . import db, limiter
from .models import User, Program, Client, Enrollment

bp = Blueprint("main", __name__)


logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@bp.route("/")
def index():
    """
    GET /
    Redirects users to the dashboard if authenticated, otherwise redirects to the login page.
    Authentication: Not required.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET, POST /login
    Handles user login. Validates credentials and logs in the user.
    Authentication: Not required.
    Methods:
        - GET: Renders the login page.
        - POST: Processes login credentials.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        logging.info(f"Login attempt for user: {username}")
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        logging.warning(f"Failed login attempt for user: {username}")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    """
    GET /logout
    Logs out the current user and redirects to the login page.
    Authentication: Required.
    """
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET, POST /register
    Handles user registration. Creates a new user account.
    Authentication: Not required.
    Methods:
        - GET: Renders the registration page.
        - POST: Processes registration data.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logging.info(f"Failed register attempt for {username}")
            return redirect(url_for("main.register"))

        # Create user with hashed password
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        logging.info(f"User {username} successfully created!")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@bp.route("/user/delete", methods=["POST"])
@login_required
def delete_user():
    """
    POST /user/delete
    Deletes the current user account and logs them out.
    Authentication: Required.
    """
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    logging.info(f"User {user.username} successfully deleted!")
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def dashboard():
    """
    GET /dashboard
    Displays the dashboard with a list of programs.
    Authentication: Required.
    """
    programs = Program.query.all()
    return render_template("dashboard.html", programs=programs)


@bp.route("/profile")
@login_required
def profile():
    """
    GET /profile
    Displays the profile of the current user.
    Authentication: Required.
    """
    return render_template("profile.html", user=current_user)


@bp.route("/program/create", methods=["GET", "POST"])
@login_required
def create_program():
    """
    GET, POST /program/create
    Handles program creation. Allows users to create new programs.
    Authentication: Required.
    Methods:
        - GET: Renders the program creation page.
        - POST: Processes program creation data.
    """
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        if Program.query.filter_by(name=name).first():
            logging.info(f"Program {name} already exists!")
            return redirect(url_for("main.create_program"))

        program = Program(name=name, description=description)
        db.session.add(program)
        db.session.commit()
        logging.info(f"Program {name} successfully created!")
        return redirect(url_for("main.dashboard"))

    return render_template("create_program.html")


@bp.route("/program/<int:program_id>/delete", methods=["POST"])
@login_required
def delete_program(program_id):
    """
    POST /program/<int:program_id>/delete
    Deletes a program by its ID.
    Authentication: Required.
    """
    program = Program.query.get_or_404(program_id)
    program_name = program.name
    db.session.delete(program)
    db.session.commit()
    logging.info(f"Program {program_name} successfully deleted!")
    return redirect(url_for("main.dashboard"))


@bp.route("/program/<int:program_id>")
@login_required
def view_program(program_id):
    """
    GET /program/<int:program_id>
    Displays the details of a specific program.
    Authentication: Required.
    """
    program = Program.query.get_or_404(program_id)
    return render_template("program.html", program=program)


@bp.route("/client/register", methods=["GET", "POST"])
@login_required
def register_client():
    """
    GET, POST /client/register
    Handles client registration. Allows users to register new clients.
    Authentication: Required.
    Methods:
        - GET: Renders the client registration page.
        - POST: Processes client registration data.
    """
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]

        if Client.query.filter_by(name=name).first():
            logging.warning(f"Client {name} already exists!")
            return redirect(url_for("main.register_client"))

        client = Client(name=name, age=age, gender=gender)
        db.session.add(client)
        db.session.commit()
        logging.info(f"Client {name} registered successfully!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("register_client.html")


@bp.route("/client/<int:client_id>")
@login_required
def view_client(client_id):
    """
    GET /client/<int:client_id>
    Displays the profile of a specific client, including their enrolled programs.
    Authentication: Required.
    """
    client = Client.query.get_or_404(client_id)
    # Fetch enrolled programs by joining the Enrollment model with the Program model
    enrolled_programs = (
        Program.query.join(Enrollment).filter(Enrollment.client_id == client.id).all()
    )
    return render_template(
        "client_profile.html", client=client, programs=enrolled_programs
    )


@bp.route("/client/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    """
    GET, POST /client/<int:client_id>/edit
    Handles editing a client's profile. Allows users to update client information.
    Authentication: Required.
    Methods:
        - GET: Renders the client edit page.
        - POST: Processes client update data.
    """
    client = Client.query.get_or_404(client_id)

    if request.method == "POST":
        client.name = request.form["name"]
        client.age = request.form["age"]
        db.session.commit()
        logging.info(f"Client {client.name} updated successfully!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("edit_client.html", client=client)


@bp.route("/client/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    """
    POST /client/<int:client_id>/delete
    Deletes a client by their ID. Unenrolls the client from all programs.
    Authentication: Required.
    """
    client = Client.query.get_or_404(client_id)
    client_name = client.name

    # Unenroll the client from all programs
    enrollments = Enrollment.query.filter_by(client_id=client.id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)

    db.session.delete(client)
    db.session.commit()
    logging.info(f"Client {client_name} deleted successfully!")
    return redirect(url_for("main.clients"))


@bp.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    """
    GET, POST /clients
    Displays a list of all clients. Allows searching for clients by name.
    Authentication: Required.
    Methods:
        - GET: Renders the client list page.
        - POST: Processes search queries.
    """
    search_query = request.form.get("search", "")
    if search_query:
        clients = Client.query.filter(Client.name.ilike(f"%{search_query}%")).all()
    else:
        clients = Client.query.all()
    return render_template("clients.html", clients=clients)


@bp.route("/client/<int:client_id>/enroll", methods=["GET", "POST"])
@login_required
def enroll_client(client_id):
    """
    GET, POST /client/<int:client_id>/enroll
    Handles enrolling a client in a program. Displays a list of available programs.
    Authentication: Required.
    Methods:
        - GET: Renders the enrollment page with available programs.
        - POST: Processes enrollment data.
    """
    client = Client.query.get_or_404(client_id)
    programs = Program.query.all()  # List all programs to choose from

    if request.method == "POST":
        selected_program_ids = request.form.getlist(
            "programs"
        )  # Get selected program IDs
        selected_programs = Program.query.filter(
            Program.id.in_(selected_program_ids)
        ).all()

        # Add selected programs to the client
        for program in selected_programs:
            if not Enrollment.query.filter_by(
                client_id=client.id, program_id=program.id
            ).first():
                new_enrollment = Enrollment(client_id=client.id, program_id=program.id)
                db.session.add(new_enrollment)

        db.session.commit()
        logging.info(f"Client {client.name} enrollment successful!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("enroll_client.html", client=client, programs=programs)


@bp.route("/client/<int:client_id>/unenroll/<int:program_id>", methods=["POST"])
@login_required
def unenroll_client(client_id, program_id):
    """
    POST /client/<int:client_id>/unenroll/<int:program_id>
    Handles unenrolling a client from a program.
    Authentication: Required.
    """
    client = Client.query.get_or_404(client_id)
    program = Program.query.get_or_404(program_id)

    # Find the enrollment record for this client and program
    enrollment = Enrollment.query.filter_by(
        client_id=client.id, program_id=program.id
    ).first()

    if enrollment:
        # If enrollment exists, delete it
        db.session.delete(enrollment)
        db.session.commit()
        logging.info(f"{client.name} has been de-enrolled from {program.name}.")
    else:
        logging.warning(f"{client.name} is not enrolled in {program.name}.")

    # Redirect back to the client's profile
    return redirect(url_for("main.view_client", client_id=client.id))


@bp.route("/api/client/<int:client_id>", methods=["GET"])
@limiter.limit("100 per minute")
def api_get_client_profile(client_id):
    """
    GET /api/client/<int:client_id>
    Returns the profile of a specific client in JSON format.
    Authentication: Not required.
    """
    client = Client.query.get_or_404(client_id)
    enrollments = Enrollment.query.filter_by(client_id=client.id).all()
    programs = []
    for enrollment in enrollments:
        program = Program.query.get(enrollment.program_id)
        if program:
            programs.append(program.name)

    data = {
        "id": client.id,
        "name": client.name,
        "age": client.age,
        "gender": client.gender,
        "programs": programs,
    }

    return jsonify(data)


@bp.route("/api/clients", methods=["GET"])
@limiter.limit("100 per minute")
def api_get_all_clients():
    """
    GET /api/clients
    Returns a list of all clients in JSON format.
    Authentication: Not required.
    """
    clients = Client.query.all()
    client_list = []

    for client in clients:
        programs = [enrollment.program.name for enrollment in client.enrollments]
        client_list.append(
            {
                "id": client.id,
                "name": client.name,
                "age": client.age,
                "gender": client.gender,
                "programs": programs,
            }
        )

    return jsonify({"clients": client_list})
