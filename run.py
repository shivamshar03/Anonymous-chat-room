from app import app, socketio
from app.views import *

if __name__ == '__main__':
    socketio.run(app)
