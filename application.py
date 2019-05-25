'''**************************************************************
* ToDo: rework session and user adressing
* ToDo: Mark users active rom
* Bug: creating a new room puts all others in the same room.
**************************************************************'''


'''**************************************************************
* IMPORTS
**************************************************************'''
import os
from collections import deque, namedtuple

from flask import Flask, jsonify, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session;

from textblob import TextBlob

import config
from utils import cachebuster, get_timestamp, dbg


'''**************************************************************
* INIT
**************************************************************'''
app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#  init socketio
socketio = SocketIO(app)

# init initial room
reserved_user = 'System'
users = [reserved_user]
reserved_room = "Lobby"
rooms_users = {reserved_room:[reserved_user]}

# message structure 
Message = namedtuple('Message', ['timestamp', 'user', 'message'])

# key = rooms, value = deque of messages
messages = dict()
messages[reserved_room] = deque([], 100)

initial_message = Message(get_timestamp(), 'System', 'Welcome to the lobby')
messages[reserved_room].append(initial_message)

'''**************************************************************
* REGULAR ROUTES
**************************************************************'''
@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        session['user'] = request.form.get("user")
        dbg('user' + session.get('user'))

    if not session.get('user'):
        dbg(session.get('user'))
        return render_template("login.html", cachebuster=cachebuster())
    dbg('user' + session.get('user'))

    return render_template('index.html', cachebuster=cachebuster())

'''**************************************************************
* WEB SERVICE ROUTES
**************************************************************'''
@app.route("/user_exists", methods=['POST'])
def user_exists():
    user = request.form.get('user')
    if user in users:
        return jsonify( {"user_exists": True } )

    return jsonify( {"user_exists": False } )

# Allow user to logout / delete his display name (but not his messages)
@app.route("/delete_user", methods=['POST'])
def delete_user():
    user = request.form.get('user')
    room = request.form.get('room')
    if user != reserved_user:
        try:
            session.clear()
            users.remove(user)
            rooms_users[room].remove(user)
            
        except Exception as e:
            dbg(e)

    return jsonify( {"success": True} )

@app.route("/create_room", methods=['POST'])
def create_room():
    new_room = request.form.get('new_room')
    user = request.form.get('user')
    if new_room not in rooms_users.keys():
        rooms_users[new_room] = [reserved_user, user]
        messages[new_room] = deque([], 100)
        message = Message(get_timestamp(), 'System', f'Welcome to "{new_room}"')
        messages[new_room].append(message)

    # using list explicitly creates a copy from the "set like" .keys() object
    loc_rooms = list(rooms_users.keys())
    # Keep Lobby first, sort everything else
    loc_rooms[1:] = sorted(loc_rooms[1:])
    # "only socket handlers have the socketio context necessary to call the plain emit()"
    socketio.emit("update rooms", loc_rooms, broadcast=True)

    current_room = str(new_room)
    data_out =  {
            'room': current_room,
            'messages': list(messages[current_room])
        }
    socketio.emit("update messages", data_out, broadcast=True)
    return jsonify( {"success": True} )

@app.route("/change_room", methods=['POST'])
def change_room():
    new_room = request.form.get('new_room')
    user = request.form.get('user')
    if new_room not in rooms_users.keys():
        # Something went wrong, browser data out of sync with app data?
        return jsonify( {"success": False} )

    socketio.emit("update messages", list(messages[new_room]), broadcast=True)
    return jsonify( {"success": True} )

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('message')
    blob = TextBlob(text)
    text_en = blob.translate(to='en')

    return jsonify( {"translation": str(text_en) } )


'''**************************************************************
* SOCKETS
**************************************************************'''
@socketio.on("pull rooms")
def pull_rooms(data):
    user = data["user"]
    current_room = data["room"]
    loc_rooms = list(rooms_users.keys())
    # sort everything after second item in place
    loc_rooms[1:] = sorted(loc_rooms[1:])
    emit("update rooms", loc_rooms, broadcast=True)
    if user not in rooms_users[current_room]:
        rooms_users[current_room].append(user)
    if user not in users:
        users.append(user)
    emit("update users", list(rooms_users[current_room]), broadcast=True)


@socketio.on("pull messages")
def pull_messages(data):
    current_room = data["room"]
    data_out =  {
            'room': current_room,
            'messages': list(messages[current_room])
        }
    emit("update messages", data_out)

@socketio.on("new message")
def new_message(data):
    user = data["user"]
    current_room = data["room"]
    message = data["message"]
    if current_room in rooms_users.keys():
        if user not in rooms_users[current_room]:
            rooms_users[current_room].append(user)
        if user not in users:
            users.append(user)
        messages[current_room].append(Message(  get_timestamp(),
                                            user,
                                            message))
        # need to convert deque to jsoncompatible data structure (list)
        data_out =  {
            'room': current_room,
            'messages': list(messages[current_room])
        }
        emit("update messages", data_out, broadcast=True)

if __name__ == '__main__':
    app.run()
