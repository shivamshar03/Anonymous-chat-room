from flask import redirect, render_template, request
from flask_socketio import emit, close_room, join_room, leave_room, rooms

import uuid
import time

from app import app, db, socketio
from app.models import Room

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create/')
def create():
    # generate a key
    key = str(uuid.uuid4())
    while Room.query.filter_by(key=key).all():
        key = str(uuid.uuid4())
    # create the room
    room = Room(key=key, size=0)
    db.session.add(room)
    db.session.commit()
    # redirect to room page
    return redirect(f'/room/{key}')

@app.route('/join/', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        # redirect to room page
        code = request.form['code'].strip()
        return redirect(f'/room/{code}/')
    else:
        return render_template('join.html')

@app.route('/room/<key>/')
def room(key):
    # check room exists
    if Room.query.filter_by(key=key):
        return render_template('room.html', room=key)
    else:
        return redirect('/')

@socketio.on('joined')
def joined(data):
    key = data['room']
    # query the room
    res = Room.query.filter_by(key=key).all()
    if len(res) == 0:
        # the room doesn't exist, so purge all instances of it
        emit('purge', {'room': key})
        return
    # join the room
    room = res[0]
    room.size += 1
    db.session.commit()
    join_room(key)
    # welcome event
    emit('welcome', {'timestamp': int(time.time() * 1000)}, to=key)

@socketio.on('disconnect')
def left():
    # find the room the user is it
    for key in rooms():
        res = Room.query.filter_by(key=key).all()
        if res:
            # if this room exists
            room = res[0]
            room.size -= 1
            if room.size == 0:
                # room is empty
                db.session.delete(room)
                close_room(key)
            else:
                leave_room(key)
                # goodbye event
                emit('goodbye', {'timestamp': int(time.time() * 1000)}, to=key)
            db.session.commit()

@socketio.on('send')
def send(data):
    room = data['room']
    msg = data['msg']
    timestamp = data['timestamp']
    emit('message', {'content': msg, 'timestamp': timestamp}, room=room)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html')
