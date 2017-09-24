#!/usr/bin/python3

from os import environ as env
from dotenv import load_dotenv, find_dotenv
from jose import jwt
from six.moves.urllib.request import urlopen
from os.path import expanduser

import getpass
import requests
import json
import sys

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CLIENT_ID = env.get('AUTH0_CLIENT_ID')
AUTH0_DOMAIN = env.get('AUTH0_DOMAIN')
APP_HOST = env.get('APP_HOST')
HOME = expanduser("~")

def auth():
  sys.stderr.write("Login: ") 
  login = input() 
  password = getpass.getpass()

  r = requests.get("http://"+APP_HOST+"/kubectl?username="+login+"&password="+password)

  resp = json.loads(r.text)

  if 'error' in resp:

    print("There was an auth0 error: "+resp['error']+": "+resp['error_description'])

  else:

    id_token = resp['id_token']

    jwks = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")

    with open(HOME+'/.kube/jwks.json', 'w') as f: f.write (jwks.read().decode('utf-8'))
    with open(HOME+'/.kube/id_token', 'w') as f: f.write (id_token)

    print(id_token) 

def main():
  try:
    with open(HOME+'/.kube/jwks.json', 'r') as content_file: jwks = content_file.read()
    with open(HOME+'/.kube/id_token', 'r') as content_file: id_token = content_file.read()

    payload = jwt.decode(id_token, jwks, algorithms=['RS256'],
                       audience=AUTH0_CLIENT_ID, issuer="https://"+AUTH0_DOMAIN+"/")
    
    print(id_token) 
  except OSError as e:
    auth()
  except jwt.ExpiredSignatureError as e:
    auth()
  except jwt.JWTClaimsError as e:
    auth()


if __name__ == '__main__':
  main()
