from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"

class Itinerary(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    members = db.Column(db.String(100))
    user_email = db.Column(db.String(256), db.ForeignKey('user.email'))  # Reference the 'email' field in 'User' model
    user = db.relationship('User', backref=db.backref('itineraries', lazy=True))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer)
    email = db.Column(db.String(256), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(65))
    name = db.Column(db.String(100))
    key_phrase = db.Column(db.String(200), nullable=True)
    token = db.Column(db.String(200), nullable=True)