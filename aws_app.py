from flask import Flask, render_template, request, redirect, flash, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate
import boto3
import os

# AWS SES Configuration
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
SENDER_EMAIL = "your-verified-email@example.com"

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelgo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Routes from original blueprint structure as flat routes
main = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
booking_bp = Blueprint('booking', __name__)
services_bp = Blueprint('services', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']

    if User.query.filter_by(email=email).first():
        flash("Email already registered", "warning")
        return redirect(url_for('index'))

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Send email via AWS SES
    try:
        ses_client = boto3.client(
            'ses',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {'Data': 'Welcome to TravelGo2!'},
                'Body': {
                    'Text': {
                        'Data': 'Thank you for signing up! Your account was created successfully.'
                    }
                }
            }
        )
        flash("Account created and confirmation email sent!", "success")
    except Exception as e:
        flash("Account created, but failed to send confirmation email.", "danger")

    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
