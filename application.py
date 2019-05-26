'''**************************************************************
* IMPORTS
**************************************************************'''
import os
from collections import deque, namedtuple
from contextlib import suppress

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
    # if it's posted, it's a fresh user with default room
    if request.method == 'POST':
        session['user'] = request.form.get("user")
        session['room'] = reserved_room
        if session['user'] not in rooms_users[reserved_room]:
            rooms_users[reserved_room].append(session['user'])

    if not session.get('user'):
        return render_template("login.html", cachebuster=cachebuster())

    return render_template('index.html', cachebuster=cachebuster())

'''**************************************************************
* WEB SERVICE ROUTES
**************************************************************'''
@app.route("/user_exists", methods=['POST'])
def user_exists():
    return jsonify( {"user_exists": request.form.get('user') in users } )

# Allow user to logout / delete his display name (but not his messages)
@app.route("/logout", methods=['GET'])
def delete_user():
    with suppress(ValueError):
        users.remove(session["user"])
        rooms_users[session["room"]].remove(session["user"])

    session.clear()

    return jsonify( {"success": True} )

@app.route("/create_room", methods=['POST'])
def create_room():
    room = request.form.get('room')
    user = session['user']
    rooms_users[session['room']].remove(user)
    # if room exists just skip creation and put user in room
    session['room'] = room

    if room not in rooms_users.keys():
        rooms_users[room] = [reserved_user, user]
        messages[room] = deque([], 100)
        message = Message(get_timestamp(), 'System', f'Welcome to "{room}"')
        messages[room].append(message)
    elif user not in rooms_users[room]:
        rooms_users[room].append(user)

    socketio.emit("update messages", broadcast=True)
    socketio.emit("update rooms", broadcast=True)
    socketio.emit("update users", broadcast=True)

    return jsonify( {"success": True} )

@app.route("/pull_rooms", methods=['GET'])
def pull_rooms():
    loc_rooms = list(rooms_users.keys())
    # sort everything after second item in place
    if len(loc_rooms) > 1:
         loc_rooms[1:] = sorted(loc_rooms[1:])
    return jsonify( loc_rooms )

@app.route("/pull_messages", methods=['GET'])
def pull_messages():
    current_room = session["room"]
    return jsonify(list(messages[current_room]))

@app.route("/pull_users", methods=['GET'])
def pull_users():
    current_room = session["room"]
    return jsonify( sorted(rooms_users[current_room]) )

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('message')
    blob = TextBlob(text)
    text_en = blob.translate(to='en')

    return jsonify( {"translation": str(text_en) } )

@app.route("/send_message", methods=['POST'])
def new_message():
    message = request.form.get('message')
    user = session["user"]
    current_room = session["room"]
    
    messages[current_room].append(Message(  get_timestamp(),
                                            user,
                                            message))

    socketio.emit("update messages", broadcast=True)
    return jsonify( {"success": True} )

if __name__ == '__main__':
    app.run()
