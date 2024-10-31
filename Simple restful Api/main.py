from flask import Flask, request
from flask_restful import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# Fake Database (for demonstration)
fakeDatabase = {
    1: {'name': 'Clean car'},
    2: {'name': 'Write blog'},
    3: {'name': 'Start stream'},
}

taskField = {
    'id': fields.Integer,
    'name': fields.String(attribute='name')
}

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.name

# Create the database tables
with app.app_context():
    db.create_all()

# Resource to handle multiple tasks
class Items(Resource):
    @marshal_with(taskField)
    def get(self):
        tasks = Task.query.all()
        return tasks
    
    @marshal_with(taskField)
    def post(self):
        data = request.json
        task = Task(name=data['name'])
        db.session.add(task)
        db.session.commit()
        # ItemId = len(fakeDatabase.keys()) + 1
        # fakeDatabase[ItemId] = {'name': data['name']}

        return task, 201  # Return 201 for resource created

# Resource to handle individual tasks
class Item(Resource):
    @marshal_with(taskField)
    def get(self, pk):
        task = Task.query.filter_by(id=pk).first()
        return task
    

    @marshal_with(taskField)
    def put(self, pk):
        data = request.json
        task = Task.query.filter_by(id=pk).first()
        task.name = data['name']
        db.session.commit()
        return task
    
    @marshal_with(taskField)
    def delete(self, pk):
        task = Task.query.filter_by(id=pk).first()
        db.session.delete(task)
        tasks = Task.query.all()
        return tasks

# Add resources to API
api.add_resource(Items, '/')
api.add_resource(Item, '/<int:pk>')

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
