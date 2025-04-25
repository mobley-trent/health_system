from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User, Program, Client

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    programs = Program.query.all()
    return render_template('dashboard.html', programs=programs)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@bp.route('/program/create', methods=['GET', 'POST'])
@login_required
def create_program():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if Program.query.filter_by(name=name).first():
            flash("Program with that name already exists.")
            return redirect(url_for('main.create_program'))

        program = Program(name=name, description=description)
        db.session.add(program)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_program.html')

@bp.route('/program/<int:program_id>')
@login_required
def view_program(program_id):
    program = Program.query.get_or_404(program_id)
    return render_template('program.html', program=program)

@bp.route('/client/register', methods=['GET', 'POST'])
@login_required
def register_client():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        
        if Client.query.filter_by(name=name).first():
            flash("Client with that name already exists.")
            return redirect(url_for('main.register_client'))

        client = Client(name=name, age=age)
        db.session.add(client)
        db.session.commit()
        flash("Client registered successfully!")
        return redirect(url_for('main.view_client', client_id=client.id))

    return render_template('register_client.html')

@bp.route('/client/<int:client_id>')
@login_required
def view_client(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('client_profile.html', client=client)

@bp.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)

    if request.method == 'POST':
        client.name = request.form['name']
        client.age = request.form['age']
        db.session.commit()
        flash("Client updated successfully!")
        return redirect(url_for('main.view_client', client_id=client.id))

    return render_template('edit_client.html', client=client)

@bp.route('/client/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash("Client deleted successfully!")
    return redirect(url_for('main.clients'))

@bp.route('/clients', methods=['GET', 'POST'])
@login_required
def clients():
    search_query = request.form.get('search', '')
    if search_query:
        clients = Client.query.filter(Client.name.ilike(f'%{search_query}%')).all()
    else:
        clients = Client.query.all()
    return render_template('clients.html', clients=clients)
