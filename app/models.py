from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='user', cascade='all, delete-orphan')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(128), nullable=True)  # <-- Add this line
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=4.0)
    description = db.Column(db.String(255), nullable=False)
    bookings = db.relationship('Booking', back_populates='service', cascade='all, delete-orphan')
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    category = db.Column(db.String(20))
    destination = db.Column(db.String(100))
    date = db.Column(db.Date)
    guests = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')
    paid = db.Column(db.Boolean, default=False)
    amount = db.Column(db.Integer, default=0)
    payment_method = db.Column(db.String(32), nullable=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=True, unique=True)
    user = db.relationship('User', back_populates='bookings')
    service = db.relationship('Service', back_populates='bookings')
    payment = db.relationship('Payment', back_populates='booking', uselist=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'service_id', 'date', name='unique_booking'),)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_type = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    amount = db.Column(db.Integer, default=0)
    method = db.Column(db.String(32), nullable=True)
    transaction_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='payments')
    booking = db.relationship('Booking', back_populates='payment', uselist=False)