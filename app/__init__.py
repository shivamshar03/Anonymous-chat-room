from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('AC_SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('AC_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)