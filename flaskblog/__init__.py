from flask import Flask
from datetime import datetime
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'eaadf320c8cf7fd987c088c019644588'
app.config["MONGO_URI"] = "mongodb://localhost:27017/flaskblog"
db = PyMongo(app)
Post = db.db.post
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes