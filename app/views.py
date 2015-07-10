from flask import Blueprint, render_template

from flask.ext.login import current_user
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES
from app.users.models import User

mod = Blueprint('simple_page', __name__, template_folder='templates')

def show_all_adventures():
	all_adventures = []
	all_markers = []

	# get all adventures
	adventures = Adventure.query.order_by(Adventure.date.asc()).all()

	# get all active adventures
	adventures = list(filter(lambda a: a.is_active(), adventures))

	for adventure in adventures:
		# get creator of the event
		user = User.query.filter_by(id=adventure.creator_id).first()

		# get joined participants
		participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
		participants = list(filter(lambda ap: ap.is_active(), participants))

		action = -1
		if current_user.is_authenticated():
			participant = AdventureParticipant.query.filter_by(adventure_id=adventure.id, user_id=current_user.id).first()
			if (participant is None) or (not participant.is_active()):
				action = 0
			else:
				action = 1

			if adventure.creator_id == current_user.id:
				action = -1

		coordinates = Coordinate.query.filter_by(adventure_id=adventure.id).all()
		markers = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

		if markers:
			all_markers.append(markers)

		# check if creator still exists
		if user is not None:
			all_adventures.append({
				'id': adventure.id,
				'username': user.username,
				'date': adventure.date,
				'info': adventure.info,
				'joined': len(participants),
				'mode': ADVENTURES.MODES[int(adventure.mode)],
				'action': action,
				'markers': markers
			})



	return render_template('all.html', adventures=all_adventures, adventures_markers=all_markers)

# Index - main path
@mod.route("/")
def index():
	if not current_user.is_authenticated():
		return render_template('landing.html')

	return show_all_adventures()

# Show all adventures (if not logged in)
@mod.route("/all/")
def all():
	return show_all_adventures()

# About us
@mod.route("/about")
def about():
	return render_template('about.html')

# Contact
@mod.route("/contact")
def contact():
	return render_template('contact.html')

# How it works
@mod.route("/how-it-works")
def how_it_works():
	return render_template('how-it-works.html')

# Features in our app
@mod.route("/features")
def features():
	return render_template('features.html')

# Carrers - avaiable
@mod.route("/carrers")
def carrers():
	return render_template('carrers.html')

# Support
@mod.route("/support")
def support():
	return render_template('support.html')
