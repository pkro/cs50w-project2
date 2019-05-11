'''**************************************************************
* IMPORTS
**************************************************************'''
import os
from collections import deque, namedtuple

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

import config
from utils import cachebuster, get_timestamp, dbg

'''**************************************************************
* INTIT
**************************************************************'''
app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
reserved_user = 'System'
users = [reserved_user]
reserved_room = "Lobby"
rooms = [reserved_room]

Message = namedtuple('Message', ['timestamp', 'user', 'message'])
# Using deque of size 100, entries "older than" 100 will be purged
# index 0 is always the latest message
messages = dict()
messages[reserved_room] = deque([], 100)
initial_message = Message(get_timestamp(), 'System', 'Welcome to the lobby')
messages[reserved_room].append(initial_message)

'''**************************************************************
* REGULAR ROUTES
**************************************************************'''
@app.route("/")
def index():
    return render_template('index.html', cachebuster=cachebuster())

@app.route("/login")
def login():
    return render_template("login.html", cachebuster=cachebuster())


'''**************************************************************
* WEB SERVICE ROUTES
**************************************************************'''
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

@app.route("/create_room", methods=['POST'])
def create_room():
    new_room = request.form.get('new_room')
    if new_room not in rooms:
        rooms.append(new_room)
    loc_rooms = rooms
    # Keep Lobby first, sort everything else
    loc_rooms[1:] = sorted(loc_rooms[1:])
    # "only socket handlers have the socketio context necessary to call the plain emit()"
    socketio.emit("update rooms", loc_rooms, broadcast=True)
    return jsonify( {"success": True} )


'''**************************************************************
* SOCKETS
**************************************************************'''
@socketio.on("pull rooms")
def pull_rooms():
    loc_rooms = list(rooms)
    # sort everything after second item in place
    loc_rooms[1:] = sorted(loc_rooms[1:])
    socketio.emit("update rooms", loc_rooms, broadcast=True)

@socketio.on("pull messages")
def pull_messages(data):
    messages_response = dict()
    emit("update messages", list(messages[data['room']]), broadcast=True)

@socketio.on("new message")
def new_message(data):
    displayName = data["displayName"]
    current_room = data["room"]
    message = data["message"]
    messages[current_room].append(Message(  get_timestamp(),
                                        displayName,
                                        message))

    # need to convert deque to jsoncompatible data structure (list)
    emit("update messages", list(messages[current_room]), broadcast=True)




if __name__ == '__main__':
    app.run()
