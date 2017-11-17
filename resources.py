from flask_restful import Resource, fields, reqparse, marshal_with, abort
from flask import request, session
from models import db, User, Room, Message
from datetime import datetime

message_fields = {
    'id': fields.Integer,
    'room_id': fields.Integer,
    'username': fields.String(attribute='user.username'),
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'message': fields.String,
}

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('room_id', type=int, required=True, location='json') # Required just sees if the key exists, could be null!
#parser.add_argument('user_id', type=int, required=True, location='json')
#parser.add_argument('timestamp', type=str, required=True, location='json')
parser.add_argument('message', type=str, location='json')

class MessageListResource(Resource):
    @marshal_with(message_fields)
    def get(self):
        print("------ GET REQUEST ------")
        query_parser = reqparse.RequestParser()
        query_parser.add_argument('room_id', type=int)

        query_args = query_parser.parse_args()

        messages = Message.query

        room_id = query_args['room_id']

        if Room.query.get(room_id) != None:
            messages = messages.filter_by(room_id=room_id)
            print("Room ID: ", room_id)

            user = User.query.get(session['user_id'])
            if room_id == user.currentRoom:
                print("User:", session["user_id"])

                # Filter messages by lastPolled session variable
                # Note: needed to store session variable as a string, because ran into weird bug with the datetime object in a session variable truncating milliseconds (talked to Todd about)
                print("lastPolled:", datetime.strptime(session["lastPolled"],"%Y-%m-%dT%H:%M:%S.%f"))
                messages = messages.filter(Message.timestamp >  datetime.strptime(session["lastPolled"],"%Y-%m-%dT%H:%M:%S.%f"))
                session["lastPolled"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                print("New lastPolled:", session["lastPolled"])

                print("Returning:",messages.all())

                return messages.all()
            else:
                # They're in another room, return an Error
                abort(403, message="The user has entered another room.")
        else:
            abort(404, message="Room not found. It may have been deleted.")

    @marshal_with(message_fields)
    def post(self):
        parsed_args = parser.parse_args()

        message = Message(
            room_id=parsed_args['room_id'],
            user_id=session['user_id'],
            timestamp=datetime.now(),
            message=parsed_args['message']
        )

        db.session.add(message)
        db.session.commit()
        return message, 201
