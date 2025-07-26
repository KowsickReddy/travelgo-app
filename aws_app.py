import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import boto3
from boto3.dynamodb.conditions import Key
import hashlib

app = Flask(__name__)
app.secret_key = 'travelgo2_secret_key_2025'

# AWS Config
AWS_REGION = 'us-east-1'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:TravelGo2BookingTopic'  # replace with your actual ARN
SES_SENDER_EMAIL = 'verified-sender@example.com'  # must be verified in SES

# DynamoDB table names
USERS_TABLE = 'travelgo2_user'
SERVICE_TABLE = 'travelgo2_service'
BOOKING_TABLE = 'travelgo2_booking'
PAYMENT_TABLE = 'travelgo2_payment'

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)
ses_client = boto3.client('ses', region_name=AWS_REGION)

# DynamoDB tables
users_table = dynamodb.Table(USERS_TABLE)
service_table = dynamodb.Table(SERVICE_TABLE)
booking_table = dynamodb.Table(BOOKING_TABLE)
payment_table = dynamodb.Table(PAYMENT_TABLE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_sns_notification(message):
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="New TravelGo2 Booking Alert"
        )
    except Exception as e:
        print(f"SNS Error: {e}")

def send_email(recipient, subject, body_text):
    try:
        ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text}
                }
            }
        )
    except Exception as e:
        print(f"SES Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = hash_password(request.form['password'])

        try:
            if 'Item' in users_table.get_item(Key={'email': email}):
                flash('Email already exists!', 'error')
                return redirect(url_for('register'))

            users_table.put_item(
                Item={
                    'email': email,
                    'username': username,
                    'password': password,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            flash('Registered successfully!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])

        try:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')
            if user and user['password'] == password:
                session['user_email'] = email
                session['username'] = user['username']
                flash('Logged in!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials!', 'error')
        except Exception as e:
            flash(f'Login error: {e}', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/services')
def services():
    try:
        services = service_table.scan()['Items']
    except Exception as e:
        services = []
    return render_template('services.html', services=services)

@app.route('/book', methods=['POST'])
def book():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    service_id = request.form['service_id']
    booking_id = str(uuid.uuid4())

    try:
        booking_table.put_item(
            Item={
                'booking_id': booking_id,
                'user_email': session['user_email'],
                'service_id': service_id,
                'status': 'Pending',
                'created_at': datetime.utcnow().isoformat()
            }
        )

        # Send SNS notification
        message = f"User {session['user_email']} booked service {service_id} at {datetime.utcnow().isoformat()}"
        send_sns_notification(message)

        # Send SES email
        subject = "Your TravelGo2 Booking Confirmation"
        body = f"Hi {session['username']},\n\nYour booking for service ID {service_id} has been received.\n\nThank you,\nTravelGo2 Team"
        send_email(session['user_email'], subject, body)

        flash('Booking created and email sent!', 'success')
    except Exception as e:
        flash(f'Booking error: {e}', 'error')

    return redirect(url_for('dashboard'))

@app.route('/bookings')
def bookings():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    try:
        result = booking_table.scan(
            FilterExpression=Key('user_email').eq(session['user_email'])
        )
        user_bookings = result['Items']
    except Exception as e:
        user_bookings = []
    return render_template('bookings.html', bookings=user_bookings)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
