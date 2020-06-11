from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)
mongo.init_app(app)

from app import routes