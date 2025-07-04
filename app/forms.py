from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign Up")

class SearchForm(FlaskForm):
    destination = StringField("Destination", validators=[DataRequired()])
    date = DateField("Travel Date", validators=[DataRequired()])
    guests = IntegerField("Guests", validators=[DataRequired()])
    category = SelectField("Travel Type", choices=[('hotel', 'Hotel'), ('bus', 'Bus'), ('train', 'Train'), ('airplane', 'Airplane')])
    submit = SubmitField("Search")

class PaymentForm(FlaskForm):
    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("razorpay", "Razorpay (Card/UPI/NetBanking)"),
            ("upi", "UPI"),
            ("netbanking", "Net Banking"),
            ("card", "Credit/Debit Card"),
            ("paypal", "PayPal"),
            ("wallet", "Wallet")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Pay Now")
