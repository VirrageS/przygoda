from datetime import datetime
from app import db
from app.users.models import User
from app.adventures import constants as MODES

class Adventure(db.Model):
	__tablename__ = 'adventures'
	id = db.Column(db.Integer, primary_key=True)
	creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	date = db.Column('date', db.DateTime)
	info = db.Column('info', db.String)
	joined = db.Column('joined', db.Integer)
	mode = db.Column('mode', db.SmallInteger, default=MODES.RECREATIONAL)

	def __init__(self, creator_id, date, info, joined=1):
		self.creator_id = creator_id
		self.date = date
		self.info = info
		self.joined = joined

	def get_mode(self):
		return MODES.MODES[self.mode]

class Coordinate(db.Model):
	__tablename__ = 'coordinates'
	id = db.Column(db.Integer, primary_key=True)
	adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
	path_point = db.Column('path_point', db.Integer)
	latitude = db.Column('latitude', db.Float)
	longitude = db.Column('longitude', db.Float)

	def __init__(self, adventure_id, path_point, latitude, longitude):
		self.adventure_id = adventure_id
		self.path_point = path_point
		self.latitude = latitude
		self.longitude = longitude

class AdventureParticipant(db.Model):
	__tablename__ = 'adventure_participants'
	id = db.Column(db.Integer, primary_key=True)
	adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __init__(self, adventure_id, user_id):
		self.adventure_id = adventure_id
		self.user_id = user_id

