from datetime import datetime
from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from flaskblog import login_manager
from flask_login import UserMixin
# Establish a connection to the database.
connect('mongodb://localhost:27017/flaskblog', connect=False)



class User(MongoModel, UserMixin):
    email = fields.EmailField(primary_key=True, required=True)
    username = fields.CharField(required=True)
    password = fields.CharField(required=True)
    image_file = fields.CharField(required=True, default='default.jpg')

    def __repr__(self):
    	return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Comment(EmbeddedMongoModel):
    author = fields.EmailField(required=True)
    date = fields.DateTimeField(required=True)
    body = fields.CharField(required=True)

class Post(MongoModel):
    title = fields.CharField(required=True, blank=False)
    body = fields.CharField(required=True)
    date = fields.DateTimeField(required=True)
    author = fields.ReferenceField(User, required=True)
    comments = fields.EmbeddedDocumentListField(Comment, default=[])

    #objects printed
    def __repr__(self):
    	return f"Post('{self.title}', '{self.date}')"
