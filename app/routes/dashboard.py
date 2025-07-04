from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import Booking, Payment, User, db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please sign in to view your dashboard.', 'warning')
        return redirect(url_for('auth.sign_in'))
    user_id = session['user_id']
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.date.desc()).all()
    return render_template('dashboard.html', bookings=bookings)

@dashboard_bp.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        flash('Please sign in to view your profile.', 'warning')
        return redirect(url_for('auth.sign_in'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@dashboard_bp.route('/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    user = User.query.get(session['user_id'])
    username = request.form.get('username')
    contact = request.form.get('contact')
    if username:
        user.username = username
    if contact:
        user.contact = contact
    db.session.commit()
    return jsonify({'success': True, 'username': user.username, 'contact': user.contact})

@dashboard_bp.route('/profile/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    user = User.query.get(session['user_id'])
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    if not check_password_hash(user.password, old_password):
        return jsonify({'success': False, 'message': 'Old password incorrect'}), 400
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
def ajax_cancel_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    if booking.status == 'Confirmed':
        return jsonify({'success': False, 'message': 'Cannot cancel a confirmed booking. Contact support.'}), 400
    booking.status = 'Canceled'
    db.session.commit()
    return jsonify({'success': True})
