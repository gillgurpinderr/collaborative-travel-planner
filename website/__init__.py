from os import path
import os
from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # one to many relationship, one user with many itineraries

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(65))
    name = db.Column(db.String(100))
    key_phrase = db.Column(db.String(200), nullable = True)
    token = db.Column(db.String(200), nullable = True)
    
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'h'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

        
    # from .models import User

    with app.app_context():
        db.create_all()
        
    return app