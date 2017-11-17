from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(120))
	currentRoom = db.Column(db.Integer)
	rooms = db.relationship('Room', backref='creator')
	messages = db.relationship('Message', backref='user')

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User #{} called {}>'.format(self.id, self.username)

class Room(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	name = db.Column(db.String(120))
	messages = db.relationship('Message', backref='room')

	def __init__(self, creator_id, name):
		self.creator_id = creator_id
		self.name = name

	def __repr__(self):
		return '<Room #{} called {} created by {}>'.format(self.id, self.name, self.creator_id)

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime)
	message = db.Column(db.Text)

	def __init__(self, room_id, user_id, timestamp, message):
		self.room_id = room_id
		self.user_id = user_id
		self.timestamp = timestamp
		self.message = message

	def __repr__(self):
		return '<Message #{} sent in room #{} by user #{}: {} at {}>'.format(self.id, self.room_id, self.user_id, self.message, self.timestamp)
