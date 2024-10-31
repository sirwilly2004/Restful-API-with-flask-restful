from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to suppress a warning  
db = SQLAlchemy(app)

names = {"willy": {"age":20, "gender":"male"},
        "wale": {"age":33, "gender":"male"},
        "omolola": {"age":28, "gender":"female"}}

# database initialization
class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	views = db.Column(db.Integer, nullable=False)
	likes = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Video(name = {name}, views = {views}, likes = {likes})"
     
class HelloWorld(Resource):
    def get(self,name):
        return names[name]
    def post(self):
        return {"data":'data posted'}

api.add_resource(HelloWorld, "/helloworld/<string:name>/")

video_put_args = reqparse.RequestParser()
video_put_args.add_argument('name', type=str, help='Name of video is required', required=True)
video_put_args.add_argument('likes', type=int, help='Likes of the videos is required', required=True)
video_put_args.add_argument('views', type=int, help='Views of the videos is required', required=True)

video_updates_args = reqparse.RequestParser()
video_updates_args.add_argument('name', type=str, help='Name of video is required')
video_updates_args.add_argument('likes', type=int, help='Likes of the videos is required')
video_updates_args.add_argument('views', type=int, help='Views of the videos is required')

# Videos = { }

# def abort_if_video_id_doesnt_exit(video_id):
#      if video_id not in Videos:
#         abort(404, message='Video id is not valid...')

# def abort_if_video_exit(video_id):
#      if video_id in Videos:
#         abort(409, message='Video exits for that id...')

resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}
     
class Video(Resource):
    @marshal_with(resource_fields)
    def get(self, video_id):
        # abort_if_video_id_doesnt_exit(video_id)
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message='Video does not exit')
        return result


    
    @marshal_with(resource_fields)
    def put(self, video_id):
        args = video_put_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409, message='Video id taken')
        video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        # abort_if_video_exit(video_id)
        # args = video_put_args.parse_args()
        # Videos[video_id] = args
        return video , 201
    
    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_updates_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort('404', message='Video does not exit')

        if args['name']:
            result.name = args['name']
        if args['likes']:
            result.likes = args['likes']
        if args['views']:
            result.views = args['views']
        db.session.commit()
        return result
    
    def delete(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        # abort_if_video_id_doesnt_exit(video_id)
        if not result:
             abort(404, message='Video does not exit')
        db.session.delete(result)
        db.session.commit()
        # del Videos[video_id]
        return {'message': 'Video deleted successfully', 'video_id': video_id}, 200  
         


api.add_resource(Video, '/video/<int:video_id>')


if __name__ == "__main__":
	app.run(debug=True)