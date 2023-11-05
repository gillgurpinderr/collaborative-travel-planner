import json
import os
import requests
import google.auth.transport.requests
from flask import Flask, redirect, render_template, request, session, abort, url_for
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token

app = Flask(__name__)
app.secret_key = "login" # secret key, i dont what this is used for, but error if not included

with open('client_secret.json', 'r') as secret_json: # open json, r is read mode
    client_secret = json.load(secret_json)
GOOGLE_CLIENT_ID = client_secret['web']['client_id']

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # this will allow OAuth over insecure HTTP connection

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

# default
@app.route("/")
def index():
    index_html = render_template('index.html', message='Hello, World!', othera='aa')
    return index_html

# redirect to google
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# recieve data from google
@app.route("/callback")
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
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# protected area
@app.route("/protected")
@login_is_required
def protected_area():
    protected_html = render_template('protected.html')
    return protected_html

if __name__ == '__main__':
    app.run(debug=True)