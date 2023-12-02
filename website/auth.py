from functools import wraps
import json
import os
import requests
import google.auth.transport.requests
import secrets
from flask import Blueprint, redirect, render_template, request, session, abort, url_for, flash
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from werkzeug.security import generate_password_hash, check_password_hash
from .__init__ import db
from .__init__ import User
from random_word import RandomWords

r = RandomWords() # this object generates as the name suggests, random words; used for key phrase generation
auth = Blueprint('auth',__name__) # basically, creating the auth module of webpage
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # this will allow OAuth over insecure HTTP connection

with open('website/client_secret.json', 'r') as secret_json: # 'r' = read mode
    client_secret = json.load(secret_json)
GOOGLE_CLIENT_ID = client_secret['web']['client_id']
client_secrets_file = os.path.join(os.path.dirname(__file__), "client_secret.json") # set path of the json
flow = Flow.from_client_secrets_file( # flow object encapsulates and handles google auth process; feeding info to it here
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
    
    user = User.query.filter_by(email=email).first() # filter by first email (just in case), even though emails must be unique
    if user:
        flash('Email already exists. Please login with Google if your account was created with Google.', category='error')
    elif len(email) < 6:
        flash('Email must be greater than 5 characters.', category='error')
    elif len(name) < 2:
        flash('That is not your name.', category='error')
    elif len(password) < 6:
        flash('Password must be at least 5 characters.', category='error')
    elif len(email) > 255:
        flash('Email cannot exceed 255 characters.', category='error')
    elif len(name) > 99:
        flash('That is not your name.', category='error')
    elif len(password) > 64:
        flash('Password cannot exceed 64 characters.', category='error')
    else:
        new_user = User(name=name, email=email, password=generate_password_hash(password, method='scrypt'))
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            key_phrase = f"{r.get_random_word()} {r.get_random_word()} {r.get_random_word()}" # generate random key phrase for password recovery
            new_user.key_phrase = key_phrase
            db.session.commit()
            flash(f'NOTE Key Phrase: {key_phrase}', category='success')
        except Exception as e:
            flash(f'Error creating account: {str(e)}', category='error')
        
def handle_sign_in(form):
    email = form.get('email')
    password = form.get('password')
        
    user = User.query.filter_by(email=email).first() # filter by email, use first result (if more than 1)
    try:
        if user:
            if user.password == None:
                flash('Please login with Google.', category='error') # if user does not have password, they must have used Google to signup
            elif check_password_hash(user.password, password): # method from werkzeug lib, that matches PW in form to encrypted PW in DB
                # flash('Signed in! Redirecting...', category='success')
                session['logged_in'] = True # keep track of user being logged in till log out 
                print(session['logged_in'])
                session['name'] = user.name
                session['email'] = user.email
                return redirect(url_for("auth.protected")) # since logged in now true, user may access protected pages
            else:
                flash('Incorrect password. Hint: passwords are greater than 5 characters and less than 64 characters.', category='error')
                return None
        else:
            flash('Email does not exist.', category='error')
            return None
    except:
        return None

# where user starts if they have never used our app before
@auth.route("/auth", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'name' in request.form:
            new_html = handle_sign_up(request.form)
        else:
            new_html = handle_sign_in(request.form)
            
        if new_html == None: # is sign in unsuccesful or user signs up
            index_html = render_template('index.html')
            return index_html
        else:
            return new_html
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

    # id_info returns json-type object with these attributes which we can grab and store in session
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    
    user = User.query.filter_by(email=session["email"]).first()
    # add Google user to DB without storing PW (as Google auth handles login); Google user identified by PW being Null
    if not user:
        new_user = User(name=session["name"], email=session["email"])
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            flash(f'Error logging in: {str(e)}', category='error')
            
    session['logged_in'] = True # once true, Google user can access protected page
    return redirect(url_for("auth.protected"))

@auth.route("/logout")
def logout():
    session.clear() # flask session uses cookies, user only truly "logs out" after pressing logout (which is good digitial hygiene anyways) or using incognito
    return redirect(url_for("auth.index")) # redirect to /auth page

# this main page and other paths "protected" by @login_is_required
@auth.route("/")
@login_is_required
def protected():
    try:
        name = f", "
        name += str(session['name'])
    except:
        
        pass
    return render_template('protected.html', name=name)

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

# user can recover password here, granted they give correct email & key phrase
@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        key_phrase = request.form.get('password') # "password" in this case is user-submitted key phrase
        user = User.query.filter_by(email=email).first()

        if user:
            if key_phrase == user.key_phrase: # if phrase in form matches the one in DB for given email
                token = secrets.token_urlsafe(16) # generate secure token
                user.token = token # store token in DB
                db.session.commit()
                return redirect(url_for('auth.reset', email=email, token=token))
            else: 
                flash('Incorrect key phrase.', category='error')
        else:
            flash('Email not found. Please try again.', category='error')

    return render_template('forgot.html')

# if user gives correct creds, they can reset PW here
@auth.route('/reset/<email>/<token>', methods=['GET', 'POST'])
def reset(email, token):
    user = User.query.filter_by(email=email, token=token).first()
    if not user:
        abort(404) # return 404 if user somehow not found

    if request.method == 'POST':
        new_password = request.form.get('password')
        if len(new_password) < 6:
            flash('Password must be at least 5 characters.', category='error')
        elif len(new_password) > 64:
            flash('Password must not exceed 64 characters.', category='error')
        elif check_password_hash(user.password, new_password):
            flash('Password cannot be the same as previous password.', category='error')            
        else:
            user.password = generate_password_hash(new_password, method='scrypt')
            user.token = None # clear token once user has reset password
            db.session.commit()
            flash('Your password has been reset!', category='success')
            return redirect(url_for('auth.index'))

    return render_template('reset.html')