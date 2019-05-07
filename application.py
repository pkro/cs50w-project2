import os
import time
from collections import defaultdict

from flask import Flask
from flask import render_template

from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
rooms = set('lobby') 
messages = []

messages = defaultdict(list)
messages['lobby'] = [('System', 'Welcome to the lobby')]

debug = os.getenv("FLASK_DEBUG") == "1"

def cachebuster():
    return time.time() if debug else "static"


@app.route("/")
def index():
    

    return render_template('index.html', cachebuster=cachebuster())

@app.route('/socket')
def socket():
    pass

@app.route("/login")
def login():
    return render_template("login.html", cachebuster=cachebuster())

if __name__ == '__main__':
    app.run()