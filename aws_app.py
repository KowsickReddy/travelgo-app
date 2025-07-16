import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import boto3
from boto3.dynamodb.conditions import Key
import hashlib
import threading
import time

app = Flask(__name__)
app.secret_key = 'travelgo2_secret_key_2025'

# AWS Config
AWS_REGION = 'us-east-1'

# DynamoDB table names
USERS_TABLE = 'travelgo2_user'
SERVICE_TABLE = 'travelgo2_service'
BOOKING_TABLE = 'travelgo2_booking'
PAYMENT_TABLE = 'travelgo2_payment'

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
users_table = dynamodb.Table(USERS_TABLE)
service_table = dynamodb.Table(SERVICE_TABLE)
booking_table = dynamodb.Table(BOOKING_TABLE)
payment_table = dynamodb.Table(PAYMENT_TABLE)


def create_dynamodb_tables():
    """Create tables if not exist"""
    try:
        # USER table
        try:
            users_table.load()
        except:
            dynamodb.create_table(
                TableName=USERS_TABLE,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created: {USERS_TABLE}")

        # SERVICE table
        try:
            service_table.load()
        except:
            dynamodb.create_table(
                TableName=SERVICE_TABLE,
                KeySchema=[
                    {'AttributeName': 'service_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'service_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created: {SERVICE_TABLE}")

        # BOOKING table
        try:
            booking_table.load()
        except:
            dynamodb.create_table(
                TableName=BOOKING_TABLE,
                KeySchema=[
                    {'AttributeName': 'booking_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'booking_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created: {BOOKING_TABLE}")

        # PAYMENT table
        try:
            payment_table.load()
        except:
            dynamodb.create_table(
                TableName=PAYMENT_TABLE,
                KeySchema=[
                    {'AttributeName': 'payment_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'payment_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created: {PAYMENT_TABLE}")

        print("✅ All tables checked and ready.")

    except Exception as e:
        print(f"Error creating tables: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
            # Check user exists
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
        flash('Booking created!', 'success')
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
    create_dynamodb_tables()
    app.run(debug=True, port=5000)