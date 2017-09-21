"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
import requests
from os import environ as env

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_oauthlib.client import OAuth
from jose import jwt
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen

import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_AUDIENCE = env.get(constants.API_ID)

APP = Flask(__name__, static_url_path='/public', static_folder='./public')
APP.secret_key = constants.SECRET_KEY
APP.debug = True


# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


#@APP.errorhandler(Exception)
#def handle_auth_error(ex):
#    response = jsonify(ex.error)
#    response.status_code = ex.status_code
#    return response

oauth = OAuth(APP)


auth0 = oauth.remote_app(
    'auth0',
    consumer_key=AUTH0_CLIENT_ID,
    consumer_secret=AUTH0_CLIENT_SECRET,
    request_token_params={
        'scope': 'openid profile',
        'audience': AUTH0_AUDIENCE
    },
    base_url='https://%s' % AUTH0_DOMAIN,
    access_token_method='POST',
    access_token_url='/oauth/token',
    authorize_url='/authorize',
)

auth0_offline = oauth.remote_app(
    'auth0offline',
    consumer_key=AUTH0_CLIENT_ID,
    consumer_secret=AUTH0_CLIENT_SECRET,
    request_token_params={
        'scope': 'offline access',
        'audience': AUTH0_AUDIENCE
    },
    base_url='https://%s' % AUTH0_DOMAIN,
    access_token_method='POST',
    access_token_url='/oauth/token',
    authorize_url='/authorize',
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


# Controllers API
@APP.route('/')
def home():
    return render_template('home.html')


@APP.route('/callback')
def callback_handling():
    if request.args['code']:
      print('code: '+request.args['code'])
      #conn = http.client.HTTPSConnection("")
      payload = "{\"grant_type\":\"authorization_code\",\"client_id\": \""+AUTH0_CLIENT_ID+"\",\"client_secret\": \""+AUTH0_CLIENT_SECRET+"\",\"code\": \""+request.args['code']+"\",\"redirect_uri\": \""+AUTH0_CALLBACK_URL+"\"}"
      headers = { 'content-type': "application/json" }
      print('going to post: '+payload)
      #conn.request("POST", "/newtechacademy.eu.auth0.com/oauth/token", payload, headers)
      res = requests.post('https://'+AUTH0_DOMAIN+'/oauth/token', json=json.loads(payload))
      print('posted: ' + res.text)
      #res = conn.getresponse()
      session[constants.OFFLINE] = res.text
      print(session[constants.OFFLINE])
    else:
      resp = auth0.authorized_response()
      if resp is None:
          raise AuthError({'code': request.args['error_reason'],
                           'description': request.args['error_description']}, 401)

      # Obtain JWT and the keys to validate the signature
      id_token = resp['id_token']
      jwks = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")

      payload = jwt.decode(id_token, jwks.read().decode('utf-8'), algorithms=['RS256'],
                           audience=AUTH0_CLIENT_ID, issuer="https://"+AUTH0_DOMAIN+"/")

      session[constants.JWT_PAYLOAD] = payload

      session[constants.PROFILE_KEY] = {
          'user_id': payload['sub'],
          'name': payload['name'],
          'picture': payload['picture']
      }

    return redirect('/dashboard')


@APP.route('/login')
def login():
    return auth0.authorize(callback=AUTH0_CALLBACK_URL)

@APP.route('/offline')
def offline():
    return auth0_offline.authorize(callback=AUTH0_CALLBACK_URL)


@APP.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.base_url + '/v2/logout?' + urlencode(params))


@APP.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_raw=session[constants.JWT_PAYLOAD],
                           token=session[constants.OFFLINE],
                           issuer_url=AUTH0_DOMAIN,
                           client_id=AUTH0_CLIENT_ID,
                           client_secret=AUTH0_CLIENT_SECRET,
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))



if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=env.get('PORT', 3000))
