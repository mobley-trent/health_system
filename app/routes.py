from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from . import db
from .models import User, Program, Client, Enrollment

bp = Blueprint("main", __name__)


logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
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
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("main.register"))

        # Create user with hashed password
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@bp.route("/user/delete", methods=["POST"])
@login_required
def delete_user():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.", "info")
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def dashboard():
    programs = Program.query.all()
    return render_template("dashboard.html", programs=programs)


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@bp.route("/program/create", methods=["GET", "POST"])
@login_required
def create_program():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        if Program.query.filter_by(name=name).first():
            flash("Program with that name already exists.")
            return redirect(url_for("main.create_program"))

        program = Program(name=name, description=description)
        db.session.add(program)
        db.session.commit()
        return redirect(url_for("main.dashboard"))

    return render_template("create_program.html")


@bp.route("/program/<int:program_id>/delete", methods=["POST"])
@login_required
def delete_program(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    flash(f"Program '{program.name}' deleted.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/program/<int:program_id>")
@login_required
def view_program(program_id):
    program = Program.query.get_or_404(program_id)
    return render_template("program.html", program=program)


@bp.route("/client/register", methods=["GET", "POST"])
@login_required
def register_client():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]

        if Client.query.filter_by(name=name).first():
            flash("Client with that name already exists.")
            return redirect(url_for("main.register_client"))

        client = Client(name=name, age=age, gender=gender)
        db.session.add(client)
        db.session.commit()
        flash("Client registered successfully!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("register_client.html")


@bp.route("/client/<int:client_id>")
@login_required
def view_client(client_id):
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
    client = Client.query.get_or_404(client_id)

    if request.method == "POST":
        client.name = request.form["name"]
        client.age = request.form["age"]
        db.session.commit()
        flash("Client updated successfully!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("edit_client.html", client=client)


@bp.route("/client/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash("Client deleted successfully!")
    return redirect(url_for("main.clients"))


@bp.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    search_query = request.form.get("search", "")
    if search_query:
        clients = Client.query.filter(Client.name.ilike(f"%{search_query}%")).all()
    else:
        clients = Client.query.all()
    return render_template("clients.html", clients=clients)


@bp.route("/client/<int:client_id>/enroll", methods=["GET", "POST"])
@login_required
def enroll_client(client_id):
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
        flash("Client enrolled in selected programs!")
        return redirect(url_for("main.view_client", client_id=client.id))

    return render_template("enroll_client.html", client=client, programs=programs)


@bp.route("/client/<int:client_id>/unenroll/<int:program_id>", methods=["POST"])
@login_required
def unenroll_client(client_id, program_id):
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
        flash(f"{client.name} has been de-enrolled from {program.name}.", "success")
    else:
        flash(f"{client.name} is not enrolled in {program.name}.", "danger")

    # Redirect back to the client's profile
    return redirect(url_for("main.view_client", client_id=client.id))


@bp.route("/api/client/<int:client_id>", methods=["GET"])
def api_get_client_profile(client_id):
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
def api_get_all_clients():
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
