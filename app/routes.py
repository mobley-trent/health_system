from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User, Program

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
