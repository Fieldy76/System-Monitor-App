"""Authentication blueprint for user login, registration, and management."""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, UserPreference
from datetime import datetime

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Validate input
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        # Check credentials
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # First user is admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        # Create default preferences
        preferences = UserPreference(user_id=user.id)
        db.session.add(preferences)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    """User logout handler."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page and update handler."""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update email
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'error')
            else:
                current_user.email = email
                flash('Email updated successfully.', 'success')
        
        # Update password
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            elif len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
            else:
                current_user.set_password(new_password)
                flash('Password updated successfully.', 'success')
        
        db.session.commit()
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html')


# API endpoints for AJAX requests
@auth.route('/api/check-username', methods=['POST'])
def check_username():
    """Check if username is available."""
    username = request.json.get('username')
    exists = User.query.filter_by(username=username).first() is not None
    return jsonify({'available': not exists})


@auth.route('/api/check-email', methods=['POST'])
def check_email():
    """Check if email is available."""
    email = request.json.get('email')
    exists = User.query.filter_by(email=email).first() is not None
    return jsonify({'available': not exists})
