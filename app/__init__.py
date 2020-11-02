from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# init app
app = Flask(__name__)

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    tasks = db.relationship('Task', backref="user", lazy=True)
    groups = db.relationship('Group', backref="user", lazy=True)
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f"User('{self.username}', '{self.password}')"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, default=False)
    idUser = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    idGroup = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    due = db.Column(db.DateTime, nullable=True)
    def __repr__(self):
        return f"Task('{self.title}', '{self.desc}', '{self.done}')"

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref="group", lazy=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #color = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return f"Group('{self.name}')"
from app import views