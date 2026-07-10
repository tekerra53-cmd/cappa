from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from ..models.user import User
from ..models.student import Student
from .forms import LoginForm, PasswordChangeForm
from ..extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.strip()
        user = User.query.filter(
            or_(
                User.username.ilike(identifier),
                User.email.ilike(identifier)
            )
        ).first()

        if not user:
            normalized = identifier.lower().replace('/', '').replace('-', '').replace(' ', '')
            if normalized != identifier:
                user = User.query.filter(User.username.ilike(normalized)).first()

        if not user:
            student = Student.query.filter(Student.matric_no.ilike(identifier)).first()
            if student and student.user:
                user = student.user
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.force_password_change:
                flash('Please change your password before continuing.', 'info')
                return redirect(url_for('auth.change_password'))
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        current_user.set_password(form.new_password.data)
        current_user.force_password_change = False
        if current_user.role == 'student' and current_user.student_profile:
            current_user.student_profile.temp_password = None
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('index'))
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/init')
def init_admin():
    if User.query.filter_by(role='admin').first():
        flash('Admin already exists', 'warning')
        return redirect(url_for('auth.login'))

    admin = User(username='admin', email='admin@srms.local', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    flash('Default admin created: username admin password admin123', 'success')
    return redirect(url_for('auth.login'))
