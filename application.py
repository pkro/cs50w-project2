import os
from collections import defaultdict, deque, namedtuple

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

import config
from utils import cachebuster, get_timestamp, dbg


app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
rooms = set(['lobby'])

users = set(['System'])

Message = namedtuple('Message', ['timestamp', 'user', 'message'])
messages = defaultdict(deque)
# Using deque of size 100, entries "older than" 100 will be purged
# index 0 is always the latest message
messages['lobby'] = deque([], 100)
initial_message = Message(get_timestamp(), 'System', 'Welcome to the lobby')
messages['lobby'].appendleft(initial_message)


@app.route("/")
def index():
    return render_template('index.html', cachebuster=cachebuster())

@socketio.on("create_room")
def vote(data):
    selection = data["room_name"]
    votes[selection] += 1
    emit("vote totals", votes, broadcast=True)

@app.route("/login")
def login():
    return render_template("login.html", cachebuster=cachebuster())

@app.route("/displayName_exists", methods=['POST'])
def displayName_exists():
    displayName = request.form.get('displayName')
    if displayName in users:
        return jsonify( {"displayName_exists": True } )
    return jsonify( {"displayName_exists": False } )

# Allow user to logout / delete his display name (but not his messages)
@app.route("/delete_displayName", methods=['POST'])
def delete_displayName():
    displayName = request.form.get('displayName')
    dbg(f"Deleting {displayName}")
    try:
        users.remove(request.form.get('displayName'))
    except Exception as e:
        dbg(e)
    
    # if user doesn't exist in user list - so what.
    return jsonify( {"success": True} )



if __name__ == '__main__':
    app.run()
