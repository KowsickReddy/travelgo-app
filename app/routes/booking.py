from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from ..models import db, Booking, Payment, Service
from ..forms import PaymentForm
from flask import current_app
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

booking_bp = Blueprint('booking', __name__)

def send_booking_confirmation_email(to_email, booking, service):
    ses_client = boto3.client(
        'ses',
        region_name='us-east-1',  # Update if using a different region
        aws_access_key_id='YOUR_AWS_ACCESS_KEY',
        aws_secret_access_key='YOUR_AWS_SECRET_KEY'
    )

    subject = "Booking Confirmation"
    body_text = f"""
    Dear Customer,

    Your booking for {service.name} on {booking.date.strftime('%d-%m-%Y')} has been confirmed.

    Booking ID: {booking.id}
    Service: {service.name}
    Guests: {booking.guests}
    Amount Paid: ₹{booking.amount}

    Thank you for booking with TravelGo!

    Regards,
    TravelGo Team
    """

    try:
        response = ses_client.send_email(
            Source='your_verified_email@example.com',
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body_text}}
            }
        )
    except ClientError as e:
        print(f"Email sending failed: {e.response['Error']['Message']}")

@booking_bp.route('/book/<service_type>/<int:service_id>', methods=['GET', 'POST'])
def book_service(service_type, service_id):
    if 'user_id' not in session:
        flash('Please sign in to book.', 'warning')
        return redirect(url_for('auth.sign_in'))
    user_id = session['user_id']
    service = Service.query.get_or_404(service_id)
    today = datetime.utcnow().date()
    if request.method == 'POST':
        guests = int(request.form.get('guests', 1))
        date_str = request.form.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            flash('Invalid date format.', 'danger')
            return render_template('book_service.html', service=service)
        if date < today:
            flash('Cannot book for a past date.', 'danger')
            return render_template('book_service.html', service=service)
        existing = Booking.query.filter_by(user_id=user_id, service_id=service_id, date=date).first()
        if existing:
            flash('You have already booked this service for the selected date.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        total_price = service.price * guests
        booking = Booking(
            user_id=user_id,
            service_id=service_id,
            category=service_type,
            destination=service.name,
            date=date,
            guests=guests,
            status='Pending',
            paid=False,
            amount=total_price
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('booking.payment', booking_id=booking.id))
    return render_template('book_service.html', service=service)

@booking_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    service = Service.query.get(booking.service_id)
    if booking.paid:
        return redirect(url_for('booking.confirmation', booking_id=booking.id))
    if request.method == 'POST':
        method = request.form.get('payment_method')
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        vpa = request.form.get('vpa')
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        wallet_id = request.form.get('wallet_id')
        if method == 'Card':
            if not (card_number and expiry and cvv):
                flash('Please enter all card details.', 'danger')
                return render_template('payment.html', booking=booking, service=service)
        elif method == 'UPI':
            if not vpa:
                flash('Please enter your UPI VPA.', 'danger')
                return render_template('payment.html', booking=booking, service=service)
        elif method == 'NetBanking':
            if not (bank_name and account_number):
                flash('Please enter your bank details.', 'danger')
                return render_template('payment.html', booking=booking, service=service)
        elif method == 'Wallet':
            if not wallet_id:
                flash('Please enter your wallet ID.', 'danger')
                return render_template('payment.html', booking=booking, service=service)
        else:
            flash('Please select a payment method.', 'danger')
            return render_template('payment.html', booking=booking, service=service)
        payment = Payment(
            user_id=booking.user_id,
            service_type=booking.category,
            service_id=booking.service_id,
            status='success',
            amount=booking.amount,
            method=method,
            transaction_id='SIMULATED123'
        )
        db.session.add(payment)
        db.session.commit()
        booking.status = 'Confirmed'
        booking.paid = True
        booking.payment_method = method
        booking.payment_id = payment.id
        db.session.commit()
        db.session.refresh(booking)
        user_email = session.get('user_email')
        if user_email:
            send_booking_confirmation_email(user_email, booking, service)
        flash('Payment successful! Booking confirmed.', 'success')
        return redirect(url_for('booking.confirmation', booking_id=booking.id))
    return render_template('payment.html', booking=booking, service=service)

@booking_bp.route('/confirmation/<int:booking_id>')
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    service = Service.query.get(booking.service_id)
    return render_template('confirmation.html', booking=booking, service=service)

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'Confirmed':
        booking.status = 'Cancelled'
        if booking.payment:
            booking.payment.status = 'Refunded'
        db.session.commit()
        flash('Booking cancelled and payment refunded.', 'success')
    else:
        booking.status = 'Cancelled'
        db.session.commit()
        flash('Booking cancelled.', 'info')
    return redirect(url_for('dashboard.dashboard'))

@booking_bp.route('/bookings')
def user_bookings():
    if 'user_id' not in session:
        flash('Please sign in to view your bookings.', 'warning')
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.date.desc()).all()
    services = {s.id: s for s in Service.query.all()}
    return render_template('bookings.html', bookings=bookings, services=services)
