import os
import time
from flask import Flask
from flask import render_template

from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# using set to just put user in existing room if he tries to create an existing name
rooms = set('lobby') 
messages = []

# better as class?
message = {
    'room': 'lobby',
    'user': 'bot',
    'message': 'Welcome to the lobby'
}

messages.append(message)

@app.route("/")
def index():
    if os.getenv("FLASK_DEBUG") == "1":
        cachebuster = time.time()
    else:
        cachebuster = "static"

    return render_template('index.html', cachebuster=cachebuster)

@app.route('/socket')
def socket():
    pass

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run()