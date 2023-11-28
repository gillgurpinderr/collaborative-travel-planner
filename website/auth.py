from functools import wraps
import json
import os
import requests
import google.auth.transport.requests
from flask import Blueprint, redirect, render_template, request, session, abort, url_for, flash
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from werkzeug.security import generate_password_hash, check_password_hash
from .__init__ import db
from .__init__ import User

auth = Blueprint('auth',__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # this will allow OAuth over insecure HTTP connection

with open('website/client_secret.json', 'r') as secret_json: # open json, r is read mode
    client_secret = json.load(secret_json)
    
GOOGLE_CLIENT_ID = client_secret['web']['client_id']
client_secrets_file = os.path.join(os.path.dirname(__file__), "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    )

def login_is_required(func):
    @wraps(func)
    def function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.index'))
        else:
            return func()
    return function

def handle_sign_up(form):
    name = form.get('name')
    email = form.get('email')
    password = form.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already exists. Please login with Google if your account was created with Google.', category='error')
    elif len(email) < 6:
        flash('Email must be greater than 5 characters.', category='error')
    elif len(name) < 2:
        flash('That is not your name.', category='error')
    elif len(password) < 6:
        flash('Password must be at least 5 characters.', category='error')
    else:
        new_user = User(name=name, email=email, password=generate_password_hash(password, method='scrypt'))
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
        except Exception as e:
            flash(f'Error creating account: {str(e)}', category='error')
        
def handle_sign_in(form):
    email = form.get('email')
    password = form.get('password')
        
    user = User.query.filter_by(email=email).first() # filter by email, use first result (if more than 1)
    try:
        if user:
            if user.password == None:
                flash('Please login with Google.', category='error')
            elif check_password_hash(user.password, password):
                # flash('Signed in! Redirecting...', category='success')
                session['logged_in'] = True
                return redirect(url_for("auth.protected"))
            else:
                flash('Incorrect password. Hint: passwords are greater than 5 characters.', category='error')
                return None
        else:
            flash('Email does not exist.', category='error')
            return None
    except:
        return None

@auth.route("/auth", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'name' in request.form:
            html = handle_sign_up(request.form)
        else:
            html = handle_sign_in(request.form)
            
        if html == None:
            index_html = render_template('index.html')
            return index_html
        else:
            return html
    else:
        index_html = render_template('index.html')
        return index_html

# redirect to google
@auth.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# recieve data from google
@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    
    user = User.query.filter_by(email=session["email"]).first()
    if not user:
        new_user = User(name=session["name"], email=session["email"])
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            flash(f'Error logging in: {str(e)}', category='error')
            
    session['logged_in'] = True
    return redirect(url_for("auth.protected"))

# logout
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))

# protected area
@auth.route("/")
@login_is_required
def protected():
    return render_template('protected.html')

@auth.route('/recommendation')
@login_is_required
def recommendation():
    return render_template('recommendation.html')

@auth.route('/about')
@login_is_required
def about():
    return render_template('about.html')

@auth.route('/contact')
@login_is_required
def contact():
    return render_template('contact.html')