import os
from collections import deque, namedtuple

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

import config
from utils import cachebuster, get_timestamp, dbg


app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
reserved_user = 'System'
users = set([reserved_user])
reserved_room = "Lobby"
rooms = set([reserved_room])


Message = namedtuple('Message', ['timestamp', 'user', 'message'])
# Using deque of size 100, entries "older than" 100 will be purged
# index 0 is always the latest message
messages = dict()
messages['lobby'] = deque([], 100)
initial_message = Message(get_timestamp(), 'System', 'Welcome to the lobby')
messages['lobby'].appendleft(initial_message)

@app.route("/")
def index():
    # "When you want to emit from a regular route you have to use 
    # socketio.emit(), only socket handlers have the socketio context necessary to call the plain emit()
    socketio.emit("update rooms", list(rooms), broadcast=True)
    return render_template('index.html', cachebuster=cachebuster())

@socketio.on("pull messages")
def pull_messages(data):
    messages_response = dict()
    for room_ in messages:
        messages_response[room_] = list(messages[room_])

    emit("update messages", messages_response, broadcast=True)

@socketio.on("new message")
def new_message(data):
    dbg(str(data))
    displayName = data["displayName"]
    room = data["room"]
    message = data["message"]
    messages[room].appendleft(Message(  get_timestamp(),
                                        displayName,
                                        message))

    # need to convert to jsoncompatible data structure
    # ToDo: make dict comprehensioon because python
    messages_response = dict()
    for room_ in messages:
        messages_response[room_] = list(messages[room_])
    # why are they still deque?
    dbg(messages_response)

    emit("update messages", messages_response, broadcast=True)


@app.route("/create_room", methods=['POST'])
def create_room():
    new_room = request.form.get('new_room')
    # using a set should take care of duplicate rooms
    rooms.add(new_room)
    loc_rooms = list(rooms)
    # sort everything after second item in place
    loc_rooms[1:].sort()
    socketio.emit("update rooms", loc_rooms, broadcast=True)
    return ""

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
    if displayName != reserved_user:
        try:
            users.remove(request.form.get('displayName'))
        except Exception as e:
            dbg(e)
    
    # if user doesn't exist in user list - so what.
    return jsonify( {"success": True} )



if __name__ == '__main__':
    app.run()
