from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from ..models import db, User
from ..forms import LoginForm, RegisterForm
from .. import mail  # 🔁 Make sure mail is initialized in __init__.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('sign_in.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
        else:
            hashed_pw = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email

            # ✅ Send confirmation email
            msg = Message(
                subject='Welcome to TravelGo!',
                sender='your-sender-email@example.com',  # 🛠️ Update this
                recipients=[user.email]
            )
            msg.body = f"Hi {user.username},\n\nThank you for registering with TravelGo!\nHappy journey booking!\n\n- TravelGo Team"
            try:
                mail.send(msg)
                flash('Account created and confirmation email sent!', 'success')
            except Exception as e:
                flash('Account created, but failed to send confirmation email.', 'warning')
                print(f"Email send error: {e}")

            return redirect(url_for('main.index'))
    return render_template('sign_up.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
