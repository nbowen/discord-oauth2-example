import os

from flask import Blueprint, redirect, request, session
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

discord_oauth_api = Blueprint('discord_oauth_api', __name__)

OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'
if 'OAUTH2_REDIRECT_URI' in os.environ:
    OAUTH2_REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@discord_oauth_api.route('/connect')
def discord_oauth_connect():
    scope = request.args.get(
        'scope',
        'identify')  # email connections guilds guilds.join')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@discord_oauth_api.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    discord_connection = {
        'oauth2_token': token,
        'user': discord.get(API_BASE_URL + '/users/@me').json(),
        'guilds': discord.get(API_BASE_URL + '/users/@me/guilds').json(),
        'connections': discord.get(API_BASE_URL + '/users/@me/connections').json()
    }
    session['discord_connection'] = discord_connection
    return redirect("/")


@discord_oauth_api.route("/disconnect")
def discord_oauth_disconnect():
    session.pop('discord_connection', None)

    return redirect("/")
