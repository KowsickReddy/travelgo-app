from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from .forms import LoginForm, RegisterForm, SearchForm, PaymentForm
from .models import db, User, Booking, Service
from datetime import datetime
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/services')
def services():
    # Show main categories as cards
    categories = [
        {"key": "bus", "icon": "fa-bus", "label": "Bus", "img": "bus1.jpg"},
        {"key": "train", "icon": "fa-train", "label": "Train", "img": "train1.jpg"},
        {"key": "cab", "icon": "fa-car", "label": "Cab", "img": "cab1.jpg"},
        {"key": "hotel", "icon": "fa-hotel", "label": "Hotel", "img": "hotel1.jpg"},
        {"key": "air", "icon": "fa-plane", "label": "Air", "img": "air1.jpg"},
    ]
    from_location = request.args.get('from_location', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')
    return render_template('services.html', categories=categories, from_location=from_location, destination=destination, date=date)

@main.route('/services/<category>')
def service_category(category):
    # Map category to template and mock data
    from_location = request.args.get('from_location', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')
    mock_data = {
        'bus': [
            {'id': 1, 'name': 'Red Express', 'type': 'AC Sleeper', 'timing': '10:00 AM - 6:00 PM', 'price': 799, 'rating': 4.5},
            {'id': 2, 'name': 'CityLine', 'type': 'Non-AC Seater', 'timing': '8:00 AM - 2:00 PM', 'price': 499, 'rating': 4.0},
            {'id': 3, 'name': 'Luxury Travels', 'type': 'AC Luxury', 'timing': '9:00 PM - 5:00 AM', 'price': 1299, 'rating': 4.8},
        ],
        'train': [
            {'id': 4, 'name': 'Shatabdi Express', 'type': 'AC Chair Car', 'timing': '7:00 AM - 1:00 PM', 'price': 999, 'rating': 4.7},
            {'id': 5, 'name': 'Rajdhani', 'type': 'Sleeper', 'timing': '6:00 PM - 8:00 AM', 'price': 1499, 'rating': 4.6},
        ],
        'cab': [
            {'id': 6, 'name': 'Sedan Cab', 'type': 'Sedan', 'timing': 'Anytime', 'price': 299, 'rating': 4.2},
            {'id': 7, 'name': 'SUV Cab', 'type': 'SUV', 'timing': 'Anytime', 'price': 499, 'rating': 4.4},
        ],
        'hotel': [
            {'id': 8, 'name': 'Grand Palace', 'type': '5-Star', 'location': destination or 'City Center', 'price': 3999, 'rating': 4.9},
            {'id': 9, 'name': 'Budget Inn', 'type': 'Budget', 'location': destination or 'Near Station', 'price': 999, 'rating': 4.1},
        ],
        'air': [
            {'id': 10, 'name': 'IndiGo 6E', 'type': 'Domestic', 'timing': '11:00 AM - 1:00 PM', 'price': 2999, 'rating': 4.3},
            {'id': 11, 'name': 'Air India', 'type': 'International', 'timing': '2:00 PM - 8:00 PM', 'price': 8999, 'rating': 4.5},
        ],
    }
    template_map = {
        'bus': 'bus.html',
        'train': 'train.html',
        'cab': 'cab.html',
        'hotel': 'hotel.html',
        'air': 'air.html',
    }
    if category not in template_map:
        flash("Invalid service category.", "danger")
        return redirect(url_for('main.services'))
    options = mock_data.get(category, [])
    return render_template(template_map[category], options=options, category=category, from_location=from_location, destination=destination, date=date)

@main.route('/confirmation')
def confirmation():
    booking_id = session.get('last_booking_id')
    if not booking_id:
        flash("No booking found.", "danger")
        return redirect(url_for('main.services'))
    booking = Booking.query.get(booking_id)
    service = Service.query.filter_by(name=booking.destination, category=booking.category).first()
    return render_template('confirmation.html', booking=booking, service=service)

@main.route('/bookings')
def bookings():
    if 'user_id' not in session:
        flash("Please log in to view your bookings.", "danger")
        return redirect(url_for('main.sign_in'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.created_at.desc()).all()
    services = Service.query.all()
    return render_template('bookings.html', bookings=bookings, services=services)

@main.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "danger")
        return redirect(url_for('main.sign_in'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.sign_in'))

@main.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("No user found with this email.", "warning")
        elif not check_password_hash(user.password, form.password.data):
            flash("Password check failed for this user.", "warning")
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
        flash("Invalid email or password.", "danger")
    return render_template('sign_in.html', form=form)

@main.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
        if existing_user:
            flash("Email or username already exists.", "danger")
        else:
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please sign in.", "success")
            return redirect(url_for('main.sign_in'))
    return render_template('sign_up.html', form=form)

@main.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        category = form.category.data
        destination = form.destination.data
        date = form.date.data
        guests = form.guests.data
        # Mock data for demo
        all_results = {
            'hotel': [
                {'name': 'Grand Palace', 'type': 'Hotel', 'img': 'hotel1.jpg', 'price': 3500, 'rating': 4.5},
                {'name': 'City Inn', 'type': 'Hotel', 'img': 'hotel2.jpg', 'price': 2200, 'rating': 4.0}
            ],
            'bus': [
                {'name': 'Express Travels', 'type': 'Bus', 'img': 'bus1.jpg', 'price': 800, 'rating': 4.2}
            ],
            'train': [
                {'name': 'Shatabdi Express', 'type': 'Train', 'img': 'train1.jpg', 'price': 1200, 'rating': 4.3}
            ],
            'airplane': [
                {'name': 'IndiGo 6E', 'type': 'Airplane', 'img': 'airplane1.jpg', 'price': 4500, 'rating': 4.6}
            ]
        }
        return render_template('search_results.html', form=form, all_results=all_results, category=category, destination=destination, date=date, guests=guests, ajax=False)
    return redirect(url_for('main.index'))

@main.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        flash("You must be logged in to book.", "danger")
        return redirect(url_for('main.sign_in'))
    user_id = session['user_id']
    destination = request.form['destination']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    guests = int(request.form['guests'])
    category = request.form['category']
    new_booking = Booking(
        user_id=user_id,
        destination=destination,
        date=date,
        guests=guests,
        category=category
    )
    db.session.add(new_booking)
    db.session.commit()
    # Send confirmation email
    user = User.query.get(user_id)
    msg = Message(subject="TravelGo Booking Confirmation",
                  sender="noreply@travelgo.com",
                  recipients=[user.email])
    msg.body = f"You have successfully booked a {category} to {destination} on {date.date()} for {guests} guest(s)."
    mail.send(msg)
    flash("Booking successful and confirmation sent to your email.", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to view your dashboard.", "danger")
        return redirect(url_for('main.sign_in'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.date.desc()).all()
    return render_template('dashboard.html', bookings=bookings)

@main.route('/book-now')
def book_now():
    # Central booking selection page
    services = [
        {'icon': 'fa-hotel', 'title': 'Hotel', 'category': 'hotels'},
        {'icon': 'fa-train', 'title': 'Train', 'category': 'trains'},
        {'icon': 'fa-bus', 'title': 'Bus', 'category': 'buses'},
        {'icon': 'fa-car', 'title': 'Cab', 'category': 'cabs'},
        {'icon': 'fa-plane', 'title': 'Flight', 'category': 'flights'}
    ]
    return render_template('book_now.html', services=services)

@main.route('/book/<category>', methods=['GET', 'POST'])
def book_category(category):
    # Normalize category to singular for DB query
    singular_map = {
        'hotels': 'hotel',
        'buses': 'bus',
        'trains': 'train',
        'cabs': 'cab',
        'flights': 'air',
    }
    db_category = singular_map.get(category, category)
    options = Service.query.filter_by(category=db_category).all()
    if request.method == 'POST':
        session['selected_category'] = db_category
        session['selected_option'] = request.form.get('option_id')
        return redirect(url_for('main.payment'))
    return render_template('book_category.html', category=category, options=options)

@main.route('/payment-success')
def payment_success():
    if 'user_id' not in session or 'selected_category' not in session or 'selected_option' not in session:
        flash("Invalid booking session. Please book again.", "danger")
        return redirect(url_for('main.services'))
    user = User.query.get(session['user_id'])
    option_id = session['selected_option']
    category = session['selected_category']
    # Find the latest booking for this user and category
    booking = Booking.query.filter_by(user_id=user.id, category=category[:-1] if category.endswith('s') else category).order_by(Booking.created_at.desc()).first()
    if not booking:
        flash("No booking found. Please try again.", "danger")
        return redirect(url_for('main.services'))
    # Clean up session
    session.pop('selected_category', None)
    session.pop('selected_option', None)
    return render_template('ticket.html', user=user, booking=booking)

@main.route('/cancel-booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    if booking.status == 'Canceled':
        return jsonify({'success': False, 'message': 'Already canceled'})
    booking.status = 'Canceled'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking canceled successfully.'})

@main.route('/ticket/<int:booking_id>')
def ticket(booking_id):
    if 'user_id' not in session:
        flash("Please log in to view your ticket.", "danger")
        return redirect(url_for('main.sign_in'))
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash("You are not authorized to view this ticket.", "danger")
        return redirect(url_for('main.bookings'))
    service = Service.query.filter_by(name=booking.destination, category=booking.category).first()
    return render_template('ticket.html', booking=booking, service=service)

@main.route('/book/<service>/<int:id>', methods=['GET', 'POST'])
def book_service(service, id):
    if 'user_id' not in session:
        flash('Please log in to book.', 'danger')
        return redirect(url_for('main.sign_in'))
    service_map = {'air': 'flight', 'flight': 'flight', 'flights': 'flight', 'bus': 'bus', 'train': 'train', 'cab': 'cab', 'hotel': 'hotel'}
    db_category = service_map.get(service, service)
    valid_services = ['bus', 'train', 'cab', 'hotel', 'flight']
    if db_category not in valid_services:
        flash('Invalid service type.', 'danger')
        return redirect(url_for('main.services'))
    svc = Service.query.filter_by(id=id, category=db_category).first()
    if not svc:
        flash('Service not found.', 'danger')
        return redirect(url_for('main.services'))
    if request.method == 'POST':
        # Store booking details in session for payment
        booking_data = {
            'service_id': svc.id,
            'service_name': svc.name,
            'category': svc.category,
            'price': svc.price,
            'date': str(datetime.utcnow().date()),
            'user_id': session['user_id']
        }
        session['pending_booking'] = booking_data
        return redirect(url_for('main.payment'))
    return render_template('book_service.html', service=svc)

@main.route('/payment', methods=['GET'])
def payment():
    booking = session.get('pending_booking')
    if not booking:
        flash('No booking in progress.', 'danger')
        return redirect(url_for('main.services'))
    return render_template('payment.html', booking=booking)

@main.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    booking = session.get('pending_booking')
    if not booking:
        return jsonify({'success': False, 'message': 'No booking in session'})
    payment_method = request.form.get('payment_method')
    if not payment_method:
        return jsonify({'success': False, 'message': 'Missing payment method'}), 400
    # Save booking to DB
    new_booking = Booking(
        user_id=booking['user_id'],
        category=booking['category'],
        destination=booking['service_name'],
        date=booking['date'],
        guests=1,
        created_at=datetime.utcnow(),
        status='Success',
        paid=True,
        amount=booking['price'],
        payment_method=payment_method
    )
    db.session.add(new_booking)
    db.session.commit()
    session.pop('pending_booking', None)
    return jsonify({'success': True, 'booking_id': new_booking.id})
