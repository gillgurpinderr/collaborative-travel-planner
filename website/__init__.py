from os import path
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'h'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    migrate = Migrate(app, db)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User
    create_database(app)
    
    return app

def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created database!')