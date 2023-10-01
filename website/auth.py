from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   #means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import send_from_directory, abort
import os
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 8:
            flash('Email must be at least 8 characters', category='error')
        elif len(first_name) < 3:
            flash('First name must be at least 3 characters', category='error')
        elif len(last_name) < 3:
            flash('Last name must be at least 3 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, bio=None, profile_picture=None, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


# change this to user clicked on (log in not login_required)
@auth.route('/profile', defaults={'user_id': None})
@auth.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if user_id:
        user = User.query.get(user_id)
        if not user:  # If user is not found
            abort(404)
    else:
        user = current_user
    return render_template("profile.html", user=user)

UPLOAD_FOLDER = 'profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio')
        file = request.files.get('profile_picture')

        updated = False  # Use a flag to check if any updates were made

        # Update bio if provided
        if bio:
            current_user.bio = bio
            db.session.commit()
            updated = True

        # Check and update profile picture if provided
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Now read the file and save it in the database
            with open(filepath, "rb") as f:
                image_data = f.read()

            current_user.profile_picture = image_data
            db.session.commit()
            updated = True
        elif file and file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)
        elif file and not allowed_file(file.filename):
            flash('Invalid file type.', category='error')
            return redirect(request.url)

        if updated:  # If either bio or profile picture was updated
            flash('Profile updated!', category='success')
            return redirect(url_for('auth.profile'))

    return render_template("editprofile.html", user=current_user)

@auth.route('/get-profile-picture/<int:user_id>')
def get_profile_picture(user_id):
    user = User.query.get(user_id)
    if user and user.profile_picture:
        return user.profile_picture
    return send_from_directory(UPLOAD_FOLDER, 'default.png')  # You should have a default.png in the UPLOAD_FOLDER for users without a profile picture

