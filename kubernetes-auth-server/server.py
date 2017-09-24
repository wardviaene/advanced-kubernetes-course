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

from flask import Response

import urllib3
urllib3.disable_warnings()

import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_AUDIENCE = env.get(constants.API_ID)
AUTH0_CONNECTION = env.get(constants.AUTH0_CONNECTION)
APP_HOST = env.get(constants.APP_HOST)
KUBERNETES_UI_HOST = env.get(constants.KUBERNETES_UI_HOST)

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

    session[constants.ID_TOKEN] = id_token

    session[constants.PROFILE_KEY] = {
        'user_id': payload['sub'],
        'name': payload['name'],
        'picture': payload['picture']
    }

    return redirect('/dashboard')


@APP.route('/login')
def login():
    return auth0.authorize(callback=AUTH0_CALLBACK_URL)

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
                           id_token=session[constants.ID_TOKEN],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@APP.route('/ui', defaults={'path': ''})
@APP.route('/api', defaults={'path': ''})
@APP.route('/api/<path:path>')
@requires_auth
def proxy_ui(path):
    # add bearer token
    new_headers = {key: value for (key, value) in request.headers if key != 'Host'}
    new_headers['Authorization'] = 'Bearer ' +session[constants.ID_TOKEN]

    url = request.url.replace(APP_HOST, KUBERNETES_UI_HOST).replace('http://', 'https://')
    try: 
      resp = requests.request(
          method=request.method,
          url=url,
          headers=new_headers,
          data=request.get_data(),
          cookies=request.cookies,
          allow_redirects=False,
          verify=False # remove this line when using real SSL certs
      )

      print("proxied: " + url + " - with status: " + str(resp.status_code))
      excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
      headers = [(name, value) for (name, value) in resp.raw.headers.items()
                 if name.lower() not in excluded_headers]

      response = Response(resp.content, resp.status_code, headers)
      return response

    except Exception as inst:
      print(inst)
      raise inst
      #return 'error: ' + str(inst)

@APP.route('/kubectl')
def kubectl():
  payload = {"grant_type":"http://auth0.com/oauth/grant-type/password-realm","username": request.args.get('username'),"password": request.args.get('password'),"client_id": AUTH0_CLIENT_ID, "client_secret": AUTH0_CLIENT_SECRET,"realm": AUTH0_CONNECTION, "scope": "openid", "audience": AUTH0_AUDIENCE}
  r = requests.post("https://"+AUTH0_DOMAIN+"/oauth/token", json=payload)
  return r.text




if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=env.get('PORT', 3000))
