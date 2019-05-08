import os
import time
from datetime import datetime
from collections import defaultdict
from collections import deque
from collections import namedtuple

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify 

from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
rooms = set('lobby')

users = set('System')

Message = namedtuple('Message', ['timestamp', 'user', 'message'])
messages = defaultdict(deque)
# Using deque of size 100, entries "older than" 100 will be purged
# index 0 is always the latest message
messages['lobby'] = deque([], 100)
initial_message = Message(get_timestamp(), 'System', 'Welcome to the lobby')
messages['lobby'].appendleft(initial_message)

debug = os.getenv("FLASK_DEBUG") == "1"

def cachebuster():
    return time.time() if debug else "static"

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route("/")
def index():
    return render_template('index.html', cachebuster=cachebuster())

@app.route('/socket')
def socket():
    pass

@app.route("/login")
def login():
    return render_template("login.html", cachebuster=cachebuster())

@app.route("/username_exists", methods=['POST'])
def check_username():
    if request.form.get('displayName') in users:
        return jsonify( {"username_exists": "true"} )
    return jsonify( {"username_exists": "false"} )

if __name__ == '__main__':
    app.run()