from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os


SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/default.db"
SQLALCHEMY_BINDS = {
	"dev": "postgresql://bismith:msconfig@localhost/dev"
#	,"prod": "postgresql://bismith:msconfig@localhost/prod"
}

app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)


# Users table model

class User (db.Model):
	__bind_key__ = 'dev'
	__tablename__ = 'users'
	__searchable__ = ['name']

	# table attributes
	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(80), unique=True)

	def __init__ (self, id=0, name=''):
		self.id = id
		self.name = name

	def __repr__ (self):
		return '<User %r>' % self.name


# Projects table model

class Project (db.Model):
	__bind_key__ = 'dev'
	__tablename__ = 'projects'
	__searchable__ = ['name']

	# table attributes
	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(80), unique=True)
	author = db.Column(db.Integer)
	description = db.Column(db.Text)

	def __init__ (self, id=0, name='', author=0, description=""):
		self.id = id
		self.name = name
		self.author = author
		self.description = description

	def __repr__ (self):
		return '<Project %r>' % self.name


