"""Authentication blueprint for user login, registration, and management."""  # """Authentication blueprint for user login, registration, and management."""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify  # from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user  # from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, UserPreference  # from app.models import db, User, UserPreference
from datetime import datetime  # from datetime import datetime
  # blank line
auth = Blueprint('auth', __name__)  # auth = Blueprint('auth', __name__)
  # blank line
  # blank line
@auth.route('/login', methods=['GET', 'POST'])  # @auth.route('/login', methods=['GET', 'POST'])
def login():  # def login():
    """User login page and handler."""  # """User login page and handler."""
    # Redirect if already logged in  # # Redirect if already logged in
    if current_user.is_authenticated:  # if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # return redirect(url_for('main.index'))
      # blank line
    if request.method == 'POST':  # if request.method == 'POST':
        username = request.form.get('username')  # username = request.form.get('username')
        password = request.form.get('password')  # password = request.form.get('password')
        remember = request.form.get('remember', False)  # remember = request.form.get('remember', False)
          # blank line
        # Validate input  # # Validate input
        if not username or not password:  # if not username or not password:
            flash('Please provide both username and password.', 'error')  # flash('Please provide both username and password.', 'error')
            return render_template('login.html')  # return render_template('login.html')
          # blank line
        # Find user  # # Find user
        user = User.query.filter_by(username=username).first()  # user = User.query.filter_by(username=username).first()
          # blank line
        # Check credentials  # # Check credentials
        if user and user.check_password(password):  # if user and user.check_password(password):
            login_user(user, remember=remember)  # login_user(user, remember=remember)
            user.last_login = datetime.utcnow()  # user.last_login = datetime.utcnow()
            db.session.commit()  # db.session.commit()
              # blank line
            # Redirect to next page or dashboard  # # Redirect to next page or dashboard
            next_page = request.args.get('next')  # next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))  # return redirect(next_page if next_page else url_for('main.index'))
        else:  # else:
            flash('Invalid username or password.', 'error')  # flash('Invalid username or password.', 'error')
      # blank line
    return render_template('login.html')  # return render_template('login.html')
  # blank line
  # blank line
@auth.route('/register', methods=['GET', 'POST'])  # @auth.route('/register', methods=['GET', 'POST'])
def register():  # def register():
    """User registration page and handler."""  # """User registration page and handler."""
    # Redirect if already logged in  # # Redirect if already logged in
    if current_user.is_authenticated:  # if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # return redirect(url_for('main.index'))
      # blank line
    if request.method == 'POST':  # if request.method == 'POST':
        username = request.form.get('username')  # username = request.form.get('username')
        email = request.form.get('email')  # email = request.form.get('email')
        password = request.form.get('password')  # password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')  # confirm_password = request.form.get('confirm_password')
          # blank line
        # Validate input  # # Validate input
        if not all([username, email, password, confirm_password]):  # if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')  # flash('All fields are required.', 'error')
            return render_template('register.html')  # return render_template('register.html')
          # blank line
        if password != confirm_password:  # if password != confirm_password:
            flash('Passwords do not match.', 'error')  # flash('Passwords do not match.', 'error')
            return render_template('register.html')  # return render_template('register.html')
          # blank line
        if len(password) < 8:  # if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')  # flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')  # return render_template('register.html')
          # blank line
        # Check if user already exists  # # Check if user already exists
        if User.query.filter_by(username=username).first():  # if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')  # flash('Username already exists.', 'error')
            return render_template('register.html')  # return render_template('register.html')
          # blank line
        if User.query.filter_by(email=email).first():  # if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')  # flash('Email already registered.', 'error')
            return render_template('register.html')  # return render_template('register.html')
          # blank line
        # Create new user  # # Create new user
        user = User(username=username, email=email)  # user = User(username=username, email=email)
        user.set_password(password)  # user.set_password(password)
          # blank line
        # First user is admin  # # First user is admin
        if User.query.count() == 0:  # if User.query.count() == 0:
            user.is_admin = True  # user.is_admin = True
          # blank line
        db.session.add(user)  # db.session.add(user)
        db.session.commit()  # db.session.commit()
          # blank line
        # Create default preferences  # # Create default preferences
        preferences = UserPreference(user_id=user.id)  # preferences = UserPreference(user_id=user.id)
        db.session.add(preferences)  # db.session.add(preferences)
        db.session.commit()  # db.session.commit()
          # blank line
        flash('Registration successful! Please log in.', 'success')  # flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))  # return redirect(url_for('auth.login'))
      # blank line
    return render_template('register.html')  # return render_template('register.html')
  # blank line
  # blank line
@auth.route('/logout')  # @auth.route('/logout')
@login_required  # @login_required
def logout():  # def logout():
    """User logout handler."""  # """User logout handler."""
    logout_user()  # logout_user()
    flash('You have been logged out.', 'info')  # flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  # return redirect(url_for('auth.login'))
  # blank line
  # blank line
@auth.route('/profile', methods=['GET', 'POST'])  # @auth.route('/profile', methods=['GET', 'POST'])
@login_required  # @login_required
def profile():  # def profile():
    """User profile page and update handler."""  # """User profile page and update handler."""
    if request.method == 'POST':  # if request.method == 'POST':
        email = request.form.get('email')  # email = request.form.get('email')
        current_password = request.form.get('current_password')  # current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')  # new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')  # confirm_password = request.form.get('confirm_password')
          # blank line
        # Update email  # # Update email
        if email and email != current_user.email:  # if email and email != current_user.email:
            if User.query.filter_by(email=email).first():  # if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'error')  # flash('Email already in use.', 'error')
            else:  # else:
                current_user.email = email  # current_user.email = email
                flash('Email updated successfully.', 'success')  # flash('Email updated successfully.', 'success')
          # blank line
        # Update password  # # Update password
        if current_password and new_password:  # if current_password and new_password:
            if not current_user.check_password(current_password):  # if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')  # flash('Current password is incorrect.', 'error')
            elif new_password != confirm_password:  # elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')  # flash('New passwords do not match.', 'error')
            elif len(new_password) < 8:  # elif len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')  # flash('Password must be at least 8 characters long.', 'error')
            else:  # else:
                current_user.set_password(new_password)  # current_user.set_password(new_password)
                flash('Password updated successfully.', 'success')  # flash('Password updated successfully.', 'success')
          # blank line
        db.session.commit()  # db.session.commit()
        return redirect(url_for('auth.profile'))  # return redirect(url_for('auth.profile'))
      # blank line
    return render_template('profile.html')  # return render_template('profile.html')
  # blank line
  # blank line
# API endpoints for AJAX requests  # # API endpoints for AJAX requests
@auth.route('/api/check-username', methods=['POST'])  # @auth.route('/api/check-username', methods=['POST'])
def check_username():  # def check_username():
    """Check if username is available."""  # """Check if username is available."""
    username = request.json.get('username')  # username = request.json.get('username')
    exists = User.query.filter_by(username=username).first() is not None  # exists = User.query.filter_by(username=username).first() is not None
    return jsonify({'available': not exists})  # return jsonify({'available': not exists})
  # blank line
  # blank line
@auth.route('/api/check-email', methods=['POST'])  # @auth.route('/api/check-email', methods=['POST'])
def check_email():  # def check_email():
    """Check if email is available."""  # """Check if email is available."""
    email = request.json.get('email')  # email = request.json.get('email')
    exists = User.query.filter_by(email=email).first() is not None  # exists = User.query.filter_by(email=email).first() is not None
    return jsonify({'available': not exists})  # return jsonify({'available': not exists})
