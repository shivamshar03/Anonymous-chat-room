from app import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    size = db.Column(db.Integer, nullable=False)
