from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from ..models import db, Booking, Payment, Service
from ..forms import PaymentForm
from flask import current_app
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

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
            status='Pending',   # Not confirmed yet
            paid=False,         # Not paid yet
            amount=total_price
        )
        db.session.add(booking)
        db.session.commit()
        # Always redirect to payment page
        return redirect(url_for('booking.payment', booking_id=booking.id))
    return render_template('book_service.html', service=service)

@booking_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    service = Service.query.get(booking.service_id)
    if booking.paid:
        # If already paid, redirect to confirmation
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
        # Server-side validation
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
        # If all required fields are present, consider payment successful
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
        # Update booking as paid and confirmed
        booking.status = 'Confirmed'
        booking.paid = True
        booking.payment_method = method
        booking.payment_id = payment.id
        db.session.commit()
        # Refresh booking to ensure latest state
        db.session.refresh(booking)
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
    # Optionally join with Service for details
    services = {s.id: s for s in Service.query.all()}
    return render_template('bookings.html', bookings=bookings, services=services)
