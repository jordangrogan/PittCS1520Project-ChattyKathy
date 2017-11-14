from flask_restful import Resource, fields, reqparse, marshal_with
from flask import request
from models import db, Message
from datetime import datetime

message_fields = {
    'id': fields.Integer,
    'room_id': fields.Integer,
    'user_id': fields.Integer,
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'message': fields.String
}

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('room_id', type=int, required=True, location='json') # Required just sees if the key exists, could be null!
parser.add_argument('user_id', type=int, required=True, location='json')
parser.add_argument('timestamp', type=str, required=True, location='json')
parser.add_argument('message', type=str, location='json')

class MessageListResource(Resource):
    @marshal_with(message_fields)
    def get(self):
        query_parser = reqparse.RequestParser()
        query_parser.add_argument('room_id', type=int)
        query_parser.add_argument('since', type=str)

        query_args = query_parser.parse_args()

        messages = Message.query

        room_id = None
        since = None

        if query_args['room_id']:
            room_id = query_args['room_id']
            messages = messages.filter_by(room_id=room_id)
            print("Room ID: ", room_id)
        if query_args['since']:
            since = query_args['since']
            print("Since: ", since)
            since = datetime.strptime(since, "%Y-%m-%dT%H:%M:%S.%f")
            messages = messages.filter(Message.timestamp>since)

        return messages.all()

    @marshal_with(message_fields)
    def post(self):
        parsed_args = parser.parse_args()

        message = Message(
            room_id=parsed_args['room_id'],
            user_id=parsed_args['user_id'],
            timestamp=datetime.strptime(parsed_args['timestamp'], "%Y-%m-%dT%H:%M:%S.%f"),
            message=parsed_args['message']
        )

        db.session.add(message)
        db.session.commit()
        return message, 201
