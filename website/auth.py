import json
import os
import requests
import google.auth.transport.requests
from flask import Blueprint, Flask, redirect, render_template, request, session, abort, url_for, flash
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token

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

# store google id in session
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # authorization required
        else:
            return function()
    return wrapper

def handle_sign_up(form):
    name = form.get('name')
    email = form.get('email')
    password = form.get('password')
    if len(email) < 6:
        flash('Email must be greater than 5 characters.', category='error')
    elif len(name) < 2:
        flash('That is not your name.', category='error')
    elif len(password) < 6:
        flash('Password must be at least 5 characters.', category='error')
    else:
        flash('Account created!', category='success')
        
def handle_sign_in(form):
    email = form.get('email')
    password = form.get('password')
    if len(email) < 6:
        flash('Incorrect email.', category='error')
    elif len(password) < 6:
        flash('Incorrect password. Hint: passwords are greater than 5 characters.', category='error')
    else:
        flash('Signed in! Redirecting...', category='success')
    
@auth.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'name' in request.form:
            handle_sign_up(request.form)
        else:
            handle_sign_in(request.form)

        
    index_html = render_template('index.html', message='Hello, World!', othera='aa')
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
    session["birthday"] = id_info.get("birthday")

    print(id_info)
    print("User Profile:")
    print(f"Name: {session['name']}")
    print(f"Email: {session['email']}")
    print(f"ID: {session['google_id']}")    
    print(f"Birthday: {session['birthday']}")
    return redirect("/protected")

# logout
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# protected area
@auth.route("/protected")
def protected_area():
    return render_template('protected.html')

@auth.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')

@auth.route('/about')
def about():
    return render_template('about.html')

@auth.route('/contact')
def contact():
    return render_template('contact.html')