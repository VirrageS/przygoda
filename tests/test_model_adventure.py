import os
import unittest

from datetime import datetime
from app import app
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES


class AdventureTestCase(unittest.TestCase):
	def setUp(self):
		app.config.from_object('config.TestingConfig')
		self.app = app.test_client()

	def test_adventure_creator_id(self):
		a = Adventure(creator_id=1, date=datetime.now(), mode=ADVENTURES.AMATEURISH, info='Some info today')
		assert a.creator_id == 1

	def test_adventure_date(self):
		date = datetime.now()
		a = Adventure(creator_id=1, date=date, mode=ADVENTURES.AMATEURISH, info='Some info today')
		assert a.date == date

	def test_adventure_mode(self):
		a = Adventure(creator_id=3, date=datetime.now(), mode=ADVENTURES.AMATEURISH, info='Some info today')
		assert a.mode == ADVENTURES.AMATEURISH

	def test_adventure_info(self):
		a = Adventure(creator_id=2, date=datetime.now(), mode=ADVENTURES.AMATEURISH, info='Some info today')
		assert a.info == 'Some info today'


class CoordinateTestCase(unittest.TestCase):
	def setUp(self):
		app.config.from_object('config.TestingConfig')
		self.app = app.test_client()

	def test_coordinate_adventure_id(self):
		c = Coordinate(adventure_id=1, path_point=1, latitude=52.229937, longitude=21.011380)
		assert c.adventure_id == 1

	def test_coordinate_path_point(self):
		c = Coordinate(adventure_id=1, path_point=1, latitude=52.229937, longitude=21.011380)
		assert c.path_point == 1

	def test_coordinate_latitude(self):
		c = Coordinate(adventure_id=1, path_point=1, latitude=52.229937, longitude=21.011380)
		assert c.latitude == 52.229937

	def test_coordinate_longitude(self):
		c = Coordinate(adventure_id=1, path_point=1, latitude=52.229937, longitude=21.011380)
		assert c.longitude == 21.011380


class AdventureParticipantTestCase(unittest.TestCase):
	def setUp(self):
		app.config.from_object('config.TestingConfig')
		self.app = app.test_client()

	def test_coordinate_adventure_id(self):
		a = AdventureParticipant(adventure_id=1, user_id=1)
		assert a.adventure_id == 1

	def test_coordinate_path_point(self):
		a = AdventureParticipant(adventure_id=1, user_id=1)
		assert a.user_id == 1


if __name__ == '__main__':
	unittest.main()
