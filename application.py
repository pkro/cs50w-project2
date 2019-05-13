'''**************************************************************
* IMPORTS
**************************************************************'''
import os
from collections import deque, namedtuple

from flask import Flask, jsonify, render_template, request, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room

import config
from utils import cachebuster, get_timestamp, dbg

# ToDo: Complete rewrite to use socket rooms and users I guess


'''**************************************************************
* INIT
**************************************************************'''
app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
reserved_user = 'System'
users = [reserved_user]
reserved_room = "Lobby"
rooms_users = {reserved_room:[reserved_user]}

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
    
    users.append(displayName)
    return jsonify( {"displayName_exists": False } )

# Allow user to logout / delete his display name (but not his messages)
@app.route("/delete_displayName", methods=['POST'])
def delete_displayName():
    displayName = request.form.get('displayName')
    room = request.form.get('room')
    if displayName != reserved_user:
        try:
            users.remove(displayName)
            rooms_users[room].remove(displayName)
        except Exception as e:
            dbg(e)

    return jsonify( {"success": True} )

@app.route("/create_room", methods=['POST'])
def create_room():
    new_room = request.form.get('new_room')
    displayName = request.form.get('displayName')
    if new_room not in rooms_users.keys():
        rooms_users[new_room] = [reserved_user, displayName]
        messages[new_room] = deque([], 100)
        message = Message(get_timestamp(), 'System', f'Welcome to "{new_room}"')
        messages[new_room].append(message)

    # using list explicitly creates a copy from the "set like" .keys() object
    loc_rooms = list(rooms_users.keys())
    # Keep Lobby first, sort everything else
    loc_rooms[1:] = sorted(loc_rooms[1:])
    # "only socket handlers have the socketio context necessary to call the plain emit()"
    socketio.emit("update rooms", loc_rooms, broadcast=True)
    socketio.emit("update messages", list(messages[new_room]), broadcast=True)
    return jsonify( {"success": True} )

@app.route("/change_room", methods=['POST'])
def change_room():
    new_room = request.form.get('new_room')
    displayName = request.form.get('displayName')
    if new_room not in rooms_users.keys():
        # Something went wrong, browser data out of sync with app data?
        return jsonify( {"success": False} )

    socketio.emit("update messages", list(messages[new_room]), broadcast=True)
    return jsonify( {"success": True} )

'''**************************************************************
* SOCKETS
**************************************************************'''
@socketio.on("pull rooms")
def pull_rooms(data):
    displayName = data["displayName"]
    current_room = data["room"]
    loc_rooms = list(rooms_users.keys())
    # sort everything after second item in place
    loc_rooms[1:] = sorted(loc_rooms[1:])
    emit("update rooms", loc_rooms, broadcast=True)
    if displayName not in rooms_users[current_room]:
        rooms_users[current_room].append(displayName)
    if displayName not in users:
        users.append(displayName)
    emit("update users", list(rooms_users[current_room]), broadcast=True)


@socketio.on("pull messages")
def pull_messages(data):
    messages_response = dict()
    emit("update messages", list(messages[data['room']]), broadcast=True)

@socketio.on("new message")
def new_message(data):
    displayName = data["displayName"]
    current_room = data["room"]
    message = data["message"]
    if current_room in rooms_users.keys():
        if displayName not in rooms_users[current_room]:
            rooms_users[current_room].append(displayName)
        if displayName not in users:
            users.append(displayName)
        messages[current_room].append(Message(  get_timestamp(),
                                            displayName,
                                            message))
        # need to convert deque to jsoncompatible data structure (list)
        emit("update messages", list(messages[current_room]), broadcast=True)

if __name__ == '__main__':
    app.run()
