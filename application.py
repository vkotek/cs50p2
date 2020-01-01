import os

from flask import Flask, session, redirect, url_for, request, flash, render_template
from flask_session import Session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

from functools import wraps
from datetime import datetime

app = Flask(__name__)
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# app.config["SECRET_KEY"] = "THISISNOTAGOODSECRETKEY"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DEBUG"] = True

socketio = SocketIO(app)
Session(app)

# Server data structure
# TODO: Change this to use the create_room function instead.
rooms = {
    'general': {
        'name': 'general',
        'messages': [], # Last 100 messages only
        'participants': []
    }
}

# FLASK ROUTES

@app.route("/")
def home():
    return render_template("room.html")

@app.route("/rooms")
def get_rooms():
    # if not rooms:
    #     rooms = create_room('general')
    return rooms

# SOCKET HANDLERS

@socketio.on('message')
def socket_message(message):

    print('received message: ' + str(message))

    msg = {
        'user': message['user'],
        'message': message['message'],
        'room': message['room'],
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

    msgs = rooms[ message['room'] ]['messages']
    msgs.append(msg)

    # Crop to only 100 latest messages
    if len(msgs) > 100:
        msgs = msgs[-100:]

    rooms[message['room']]['messages'] = msgs

    print(f"Sending {msg}")

    emit('new_message', msg, broadcast=True)

@socketio.on('socket_create_room')
def socket_create_room(socket_create_room):
    print('New room creation request:', socket_create_room)
    create_room(socket_create_room)
    emit('created_room', socket_create_room, broadcast=True)

@socketio.on('join_room')
def socket_join_room(join_room):
    print('Request to join room: ', join_room)

    user = join_room['user']
    new_room = join_room['new_room']

    # create room if it doesn't exist
    if new_room not in rooms:
        print(f'Room \'{new_room}\' not found, setting up new room.')
        create_room(new_room)
        emit('created_room', socket_create_room, broadcast=True)

    # Try to remove user from his old room
    try:
        old_room = rooms[ join_room['old_room'] ]
        old_room['participants'].remove(user)
    except:
        print(f'Could not find {user} in old room, strange.')

    # And add him to the new room
    participants = rooms[ new_room ]['participants']
    if user not in participants:
        participants.append(user)

    result = rooms[ new_room ]
    result['user'] = user

    # Add old room data if it exists
    if old_room:
        result['old_room'] = dict(old_room) # create dict copy to avoid circular reference

    emit('joined_room', result, broadcast=True)

# HELPER FUNCTIONS

def create_room(name):
    rooms[name] = {
        'name': name,
        'messages': [],
        'participants': [],
    }

if __name__ == "__main__":
    socketio.run(app, port=8888, host="0.0.0.0")
