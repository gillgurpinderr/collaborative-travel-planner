from os import path
import os
from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from .models import *
    
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