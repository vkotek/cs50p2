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

rooms = {}

def name_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            session["next_url"] = request.url
            return redirect( url_for("user_login") )
        return f(*args, **kwargs)
    return decorated_function

@app.route("/debug/")
@name_required
def index():
    user = {
        "name": session.get("user"),
        "rooms": rooms,
    }
    html = user
    return html

@app.route("/r/<string:room>/")
@name_required
def chatroom_single(room):

    if not room:
        room = create_room('general')
    if room not in rooms:
        flash(f"Room {room} does not exist.")
        return redirect(url_for('chatroom'))

    # if create room in url params, crate the room and redirect there.
    if request.args.get("room"):
        room = create_room(request.args.get("room"))
        return redirect(url_for('chatroom_single', room=room))

    user = { "name": session.get("user") }
    room = { "name": room }

    return render_template("room.html", title=room['name'], user=user, room=room, rooms=rooms)

@app.route("/")
@name_required
def chatroom():

    last_room = session.get("room")
    print("lastroom:", last_room)
    if last_room and last_room in rooms:
        room = last_room
    else:
        create_room('general')
        room = 'general'

    #redirect to default room
    return redirect( url_for( 'chatroom_single', room=room ) )

@app.route("/user/login/")
def user_login():
    user = request.args.get("user")
    password = request.args.get("pass")
    if user and password == "gizem":
        session["user"] = user
        x = session.get("user")
        return redirect( session.get("next_url") )
    html = """
        <form method="GET" action="">
        <input name="user" type="text" placeholder="Set username..">
        <input name="pass" type="password" placeholder="Security Code">
        <button type="submit"> > </submit>
        </form>"""
    return html

@app.route("/user/logout/")
def user_logout():
    user = session.pop("user")
    return f"Consider yourself forgotten, {user}!"

@socketio.on('json')
def handle_json(json):

    print('received json: ' + str(json))

    msg = {
        'user': json['user'],
        'message': json['message'],
        'room': json['room'],
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

    msgs = rooms[json['room']]['messages']
    msgs.append(msg)

    if len(msgs) > 100:
        msgs = msgs[-100:]

    rooms[json['room']]['messages'] = msgs

    print(f"Sending {msg}")

    x = emit('response', msg, room=json['room'])
    print(x)

@socketio.on('join')
def on_join(data):
    user = data['user']
    room = data['room']

    session['room'] = room
    print(session)

    join_room(room)
    msg = {
        'user': "",
        'message': f'{user} entered.',
        'room': room,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    emit('response', msg, room=room)

@socketio.on('leave')
def on_leave(data):
    user = data['user']
    room = data['room']
    leave_room(room)
    msg = {
        'user': "",
        'message': f'{user} left.',
        'room': room,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    emit('response', msg, room=room)

def create_room(name):
    if not name:
        if not str(name).isalpha():
            flash("Room name can only contain letters.")
        return False

    name = name.lower()

    if name in rooms:
        flash(f"Room {name} already exists!")
        return False

    rooms[name] = {
        'created': datetime.now(),
        'messages': []
    }
    flash(f"Room {name} created!")
    return name

if __name__ == "__main__":
    socketio.run(app, port=8888, host="0.0.0.0")
