import os
import unittest

from datetime import datetime
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash

from flask import Flask, render_template, g
from flask.ext.testing import TestCase

from flask.ext.login import login_user, logout_user, login_required, LoginManager, current_user

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES

class RoutesAdventuresTestCase(TestCase, unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'test.db')
		self.app = app.test_client()

		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def create_app(self):
		app = Flask(__name__)
		app.config['TESTING'] = True

		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 8943
		return app

	def login(self, username, password):
	    return self.app.post('/users/login/', data=dict(
	        username=username,
	        password=password
	    ), follow_redirects=True)

	def logout(self):
	    return self.app.get('/users/logout/', follow_redirects=True)

	def test_adventures_show_route_big_number(self):
		"""Ensure that adventures_id is not to big"""

		response = self.app.get('/adventures/320392480213849032841024803284103248712', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route_no_adventure(self):
		"""Ensure that show adventure require existing adventure"""

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route_no_creator(self):
		"""Ensure that show adventure require existing creator"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route(self):
		"""Ensure that show adventure redirect us to the right place"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('adventures/show.html')

	def test_adventures_join_route_requires_login(self):
		"""Ensure that join adventure requires login"""

		response = self.app.get('/adventures/join/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_adventures_join_route_big_number(self):
		"""Ensure that join adventure requires small adventure_id"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/3458304958390433485734895734085734', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_join_route_no_adventure(self):
		"""Ensure that join adventure require existing adventure"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_join_route_user_already_joined(self):
		"""Ensure that join adventure does not allow to join again"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		# check if user has been added to adventure
		participant = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).first()
		self.assertTrue(participant is not None)

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		participants = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).all()
		self.assertTrue(participants is not None)
		self.assertTrue(len(participants) == 1)

	def test_adventures_join_route_join(self):
		"""Ensure that join adventure create adventure participant"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		# check if user has been added to adventure
		participant = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).first()
		self.assertTrue(participant is not None)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_leave_route_requires_login(self):
		"""Ensure that leave adventures requires login"""

		response = self.app.get('/adventures/leave/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_adventures_leave_route_big_number(self):
		"""Ensure that leave adventure requires small adventure_id"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/leave/1324981234124381734891234', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_leave_route_no_adventure(self):
		"""Ensure that leave adventure require existing adventure"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/leave/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_leave_route_creator(self):
		"""Ensure that leave adventure do not allow leaving for creator of the adventure"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/leave/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_leave_route_no_joined(self):
		"""Ensure that leave adventure do not allow leaving for someone who does not joined to adventure"""

		# add adventure to database
		a = Adventure(creator_id=2, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/leave/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_leave_route_leave(self):
		"""Ensure that leave adventure actually allows to leave the adventure"""

		# add adventure to database
		a = Adventure(creator_id=2, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		ap = AdventureParticipant(user_id=1, adventure_id=1)
		db.session.add(ap)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/leave/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

		ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
		self.assertTrue(ap is None)

	def test_adventures_delete_route_requires_login(self):
		"""Ensure that delete adventure requires login"""

		response = self.app.get('/adventures/delete/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_adventures_delete_route_big_number(self):
		"""Ensure that delete adventure requires small adventure_id"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/delete/128345792384572394857234598982347582', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_delete_route_no_adventure(self):
		"""Ensure that delete adventure requires adventure to exists"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/delete/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_delete_route_no_creator(self):
		"""Ensure that delete adventure requires creator to be logged"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		# add adventure to database
		a = Adventure(creator_id=2, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		response = self.app.get('/adventures/delete/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_delete_route_delete(self):
		"""Ensure that delete adventure delete all the stuff"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add adventure participants to database
		ap = AdventureParticipant(adventure_id=1, user_id=2)
		db.session.add(ap)
		db.session.commit()

		ap = AdventureParticipant(adventure_id=1, user_id=3)
		db.session.add(ap)
		db.session.commit()

		# add some coordinates to database
		c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
		db.session.add(c)
		db.session.commit()

		c = Coordinate(adventure_id=1, path_point=2, latitude=50.24324242, longitude=50.24324242)
		db.session.add(c)
		db.session.commit()

		response = self.app.get('/adventures/delete/1', follow_redirects=True)

		a = Adventure.query.filter_by(id=1).first()
		ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
		c = Coordinate.query.filter_by(adventure_id=1).first()
		self.assertTrue(a is None)
		self.assertTrue(ap is None)
		self.assertTrue(c is None)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_new_route_requires_login(self):
		"""Ensure adventures new route requires a logged in user"""

		response = self.app.get('/adventures/new', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
