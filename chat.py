"""
	Chatty Kathy
	CS 1520 Fall 2017 Assignment 4
	Jordan Grogan
	Tu/Th 6:00 Lecture / Th 7:30 Recitation
"""

from flask import Flask, request, session, url_for, redirect, render_template, flash
from models import db, User, Room, Message
from datetime import datetime
from flask_restful import Api
from resources import MessageListResource

app = Flask(__name__)

app.secret_key = "this is a terrible secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db.init_app(app)

api = Api(app, prefix="/api")
api.add_resource(MessageListResource, '/messages/', endpoint='messages')

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

# by default, direct to login
@app.route("/", methods=['GET', 'POST'])
def default():
	"""Default page."""

	if "username" in session:
		user = User.query.get(session['user_id'])

		if request.method == 'POST':
			# Add a Chat Room
			if not request.form['name']:
				flash("Please enter a chat room name.")
			elif Room.query.filter_by(name=request.form['name']).count() > 0:
				flash("Sorry, that name is not available.")
			else:
				db.session.add(Room(name=request.form['name'], creator_id=user.id))
				db.session.commit()
				flash("The chat room has been added!")

		rooms = Room.query.all()
		return render_template('rooms.html', rooms=rooms)

	return redirect(url_for('login'))

@app.route('/chat')
def chat():
	"""Show a chat room."""

	if "username" in session:
		if request.args.get('room'):
			room = Room.query.get(request.args.get('room'))
			messages = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp).all()
			return render_template('chat.html', room=room, messages=messages)
		else:
			flash("Error displaying chat room.")
	else:
		flash("You do not have permission to access this page.")

	return redirect(url_for('default'))

@app.route("/login", methods=['GET', 'POST'])
def login():
	"""Logs the user in."""

	# first check if the user is already logged in
	if "username" in session:
		flash("Already logged in!")
		return redirect(url_for('default'))

	# if not, and the incoming request is via POST try to log them in
	elif request.method == 'POST':
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			flash("Invalid username, please try again.")
		elif user.password != request.form['password']:
			flash("Invalid password, please try again.")
		else:
			session['user_id'] = user.id
			session['username'] = user.username
			return redirect(url_for('default'))

	return render_template('login.html')

@app.route("/logout")
def logout():
	"""Logs the user out."""

	# if logged in, log out, otherwise offer to log in
	if "username" in session:
		session.clear()
		flash("Successfully logged out!")
	else:
		flash("Not currently logged in!")

	return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the user."""

	if "username" in session:
		return redirect(url_for('default'))

	if request.method == 'POST':
		if not request.form['username']:
			flash("Please enter a username.")
		elif not request.form['password']:
			flash("Plase enter a password.")
		elif User.query.filter_by(username = request.form['username']).count() > 0:
			flash("Sorry, that username is already taken.")
		else:
			db.session.add(User(username=request.form['username'], password=request.form['password']))
			db.session.commit()
			flash("You were successfully registered and can login now.")
			return redirect(url_for('login'))
	return render_template('register.html')
