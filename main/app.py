import os

from flask import Flask, session, redirect, request, jsonify, render_template
from dotenv import load_dotenv

from main.discordoauth import discord_oauth_api

load_dotenv()

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.environ.get('FLASK_SESSION_SECRET_KEY')


@app.route('/')
def index():
    return render_template("homepage.html")


if __name__ == '__main__':

    port = None
    if 'FLASK_LISTEN_PORT' in os.environ:
        port = int(os.environ['FLASK_LISTEN_PORT'])

    host = None
    if 'FLASK_LISTEN_HOST' in os.environ:
        host = os.environ['FLASK_LISTEN_HOST']

    app.register_blueprint(discord_oauth_api)

    app.run(host=host, port=port)

