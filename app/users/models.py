from datetime import datetime
from app import db
from app.users import constants as USER

class User(db.Model):
	"""Provides class for User"""

	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column('username', db.String(120), unique=True, index=True)
	password = db.Column('password', db.String(255))
	email = db.Column('email', db.String(50), unique=True, index=True)
	registered_on = db.Column('registered_on', db.DateTime)
	role = db.Column('role', db.SmallInteger, default=USER.USER)

	def __init__(self, username, password, email):
		self.username = username
		self.password = password
		self.email = email
		self.registered_on = datetime.utcnow()

	def is_authenticated(self):
		return True

	def is_active(self):
		# todo: change to email confirmed or not
		return True

	def is_anonymous(self):
		return False

	def get_role(self):
		return USER.ROLE[self.role]

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

	def __repr__(self):
		return '<User %r>' % (self.username)
