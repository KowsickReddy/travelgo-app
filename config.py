import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Use only SQLite, no environment variable needed
    SQLALCHEMY_DATABASE_URI = "sqlite:///travelgo.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "supersecretkey"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = "your-email@gmail.com"
    MAIL_PASSWORD = "your-app-password"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # Add more robust defaults and comments for local development