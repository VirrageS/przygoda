# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries

import ast # for convering string to double
from datetime import datetime, date, timedelta # for current date

from app import app, db
from app.miscellaneous import confirmed_email_required
from app.adventures import constants as ADVENTURES
from app.adventures.miscellaneous import is_float
from app.adventures.models import Adventure, AdventureParticipant, Coordinate
from app.adventures.forms import NewForm, EditForm, SearchForm
from app.users.models import User

mod = Blueprint('adventures', __name__, url_prefix='/adventures')

@mod.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= app.config['DATABASE_QUERY_TIMEOUT']:
			app.logger.warning(
				"SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
				(query.statement, query.parameters, query.duration, query.context)
			)
	return response

# Show adventure with id
@mod.route('/<int:adventure_id>')
def show(adventure_id):
	"""Show adventure"""

	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	final_adventure = {}
	final_participants = []
	final_coordinates = []

	# get adventure and check if exists
	adventure = Adventure.query.filter_by(id=adventure_id).first()
	if adventure is None:
		flash('Adventure does not exists', 'danger')
		return redirect(url_for('simple_page.index'))

	# check if adventure is active
	if not adventure.is_active():
		flash('Adventure does not exists', 'danger')
		return redirect(url_for('simple_page.index'))

	# get adventures creator and check if exists
	user = User.query.filter_by(id=adventure.creator_id).first()
	if user is None:
		flash('Adventure creator does not exists', 'danger')
		return redirect(url_for('simple_page.index'))

	# get joined participants
	participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
	for participant in participants:
		user = User.query.filter_by(id=participant.user_id).first()

		if user is not None:
			final_participants.append(user)

	# check if creator exists
	if user is not None:
		final_adventure = {
			'id': adventure.id,
			'username': user.username,
			'date': adventure.date,
			'info': adventure.info,
			'joined': len(participants)
		}

	# update adventure views
	adventure.views += 1
	adventure.tomek += 1
	db.session.commit()

	# get coordinates of existing points
	coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
	final_coordinates = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

	return render_template(
		'adventures/show.html',
		adventure=final_adventure,
		participants=final_participants,
		markers=final_coordinates
	)

# Join to adventure with id
@mod.route('/join/<int:adventure_id>')
@login_required
def join(adventure_id):
	"""Allow to join to existing adventure"""

	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure and check if exists
	adventure = Adventure.query.filter_by(id=adventure_id).first()
	if adventure is None:
		flash('Adventure does not exists', 'danger')
		return redirect(url_for('simple_page.index'))

	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=current_user.id).first()

	# check if user joined adventure
	if participant is not None:
		flash('You arleady have joined to this adventure', 'warning')
	else:
		# add user to adventure participants to database
		participant = AdventureParticipant(adventure_id=adventure_id, user_id=current_user.id)
		db.session.add(participant)
		db.session.commit()
		flash('You have joined to this adventure', 'success')

	return redirect(url_for('simple_page.index'))

@mod.route('/leave/<int:adventure_id>')
@login_required
def leave(adventure_id):
	"""Allow to leave the adventure"""

	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure and check if exists
	adventure = Adventure.query.filter_by(id=adventure_id).first()
	if adventure is None:
		flash('Adventure does not exists', 'danger')
		return redirect(url_for('simple_page.index'))

	# check if user is the creator of the adventure
	if adventure.creator_id == current_user.id:
		flash('You cannot leave this adventure', 'warning')
		return redirect(url_for('simple_page.index'))

	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=current_user.id).first()

	# check if user joined adventure
	if participant is None:
		flash('You have not joined to this adventure', 'warning')
	else:
		# delete user from adventure participants from database
		db.session.delete(participant)
		db.session.commit()
		flash('You have left the adventure', 'success')

	return redirect(url_for('simple_page.index'))

# Check all created and joined adventures
@mod.route('/my/')
@login_required
def my_adventures():
	"""Show logged user's adventures"""

	final_adventures = []
	final_joined_adventures = []

	# get all adventures which created user
	adventures = Adventure.query.filter_by(creator_id=current_user.id).order_by(Adventure.date.asc()).all()

	# get all active adventures
	adventures = filter(lambda x: x.is_active(), adventures)

	for adventure in adventures:
		# get joined participants
		joined = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()

		if joined is not None:
			final_adventures.append({
				'id': adventure.id,
				'date': adventure.date,
				'info': adventure.info,
				'joined': len(joined)
			})

	# get all adventures to which user joined
	joined_adventures = AdventureParticipant.query.filter_by(user_id=current_user.id).all()
	for joined_adventure in joined_adventures:
		# get adventure
		adventure = Adventure.query.filter_by(id=joined_adventure.adventure_id).first()

		# check if adventure is active
		if not adventure.is_active():
			continue

		# check if user is not creator (we do not want duplicates)
		if (adventure is not None) and (adventure.creator_id != current_user.id):
			final_joined_adventures.append(adventure)

	return render_template('adventures/my.html', adventures=final_adventures, joined_adventures=final_joined_adventures)

# Edit adventure
@mod.route('/edit/<int:adventure_id>', methods=['GET', 'POST'])
@login_required
# @confirmed_email_required
def edit(adventure_id=0):
	"""Allows to edit adventure"""

	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure
	adventure = Adventure.query.filter_by(id=adventure_id).first()

	# check if adventure exists
	if adventure is None:
		flash('Adventure not found', 'danger')
		return redirect(url_for('simple_page.index'))

	# check if user is creator of adventure
	if adventure.creator_id != current_user.id:
		flash('You cannot edit this adventure!', 'danger')
		return redirect(url_for('simple_page.index'))

	# get form
	form = EditForm(request.form, obj=adventure)

	# get joined participants
	final_participants = []
	participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
	for participant in participants:
		user = User.query.filter_by(id=participant.user_id).first()

		if (user is not None) and (user.id != current_user.id):
			final_participants.append(user)

	# verify the edit form
	if form.validate_on_submit():
		# delete existing coordinates for the adventure_id
		db.session.query(Coordinate).filter_by(adventure_id=adventure_id).delete()
		db.session.commit()

		# add coordinates of adventure to database
		i = 0
		while True:
			# get value from html element
			marker = request.form.get('marker_' + str(i))
			if (marker is None) or (marker is ''):
				break

			# convert value to point (double, double) and add it to database
			raw_coordinate = ast.literal_eval(str(marker))
			if (raw_coordinate is not None) and is_float(raw_coordinate[0]) and is_float(raw_coordinate[1]):
				c = Coordinate(
					adventure_id=adventure.id,
					path_point=i,
					latitude=raw_coordinate[0],
					longitude=raw_coordinate[1]
				)
				db.session.add(c)
				db.session.commit()

			i = i + 1

		# get edited adventure from the form
		form.populate_obj(adventure)

		# update adventure in database
		db.session.commit()

		# everything is okay
		flash('Adventure has been successfully edited', 'success')
		return redirect(url_for('simple_page.index'))

	# get coordinates of existing points
	coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
	final_coordinates = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

	return render_template(
		'adventures/edit.html',
		form=form,
		adventure_id=adventure_id,
		markers=final_coordinates,
		participants=final_participants,
		min_date=datetime.now().strftime("%m/%d/%Y %H:%M")
	)

# New adventure
@mod.route('/new/', methods=['GET', 'POST'])
@login_required
# @confirmed_email_required
def new():
	"""Allows to create a new adventure"""

	# if new form has been submitted
	form = NewForm(request.form)

	# verify the new form
	if form.validate_on_submit():
		# add adventure to database
		adventure = Adventure(creator_id=current_user.id, date=form.date.data, mode=form.mode.data, info=form.info.data)
		db.session.add(adventure)
		db.session.commit()

		# add participant of adventure to database
		participant = AdventureParticipant(adventure_id=adventure.id, user_id=current_user.id)
		db.session.add(participant)
		db.session.commit()

		# add coordinates of adventure to database
		i = 0
		while True:
			# get value from html element
			marker = request.form.get('marker_' + str(i))
			if (marker is None) or (marker is ''):
				break

			# convert value to point (double, double) and add it to database
			raw_coordinate = ast.literal_eval(str(marker))
			if (raw_coordinate is not None) and is_float(raw_coordinate[0]) and is_float(raw_coordinate[1]):
				coordinate = Coordinate(adventure_id=adventure.id, path_point=i, latitude=raw_coordinate[0], longitude=raw_coordinate[1])
				db.session.add(coordinate)
				db.session.commit()

			i = i + 1 # check for next marker

		# everything is okay
		flash('Adventure item was successfully created', 'success')
		return redirect(url_for('simple_page.index'))

	return render_template(
		'adventures/new.html',
		form=form,
		min_date=datetime.now().strftime("%m/%d/%Y %H:%M"),
		date=(datetime.now() + timedelta(hours=1)).strftime("%m/%d/%Y %H:%M")
	)

# Delete adventure
@mod.route('/delete/<int:adventure_id>')
@login_required
# @confirmed_email_required
def delete(adventure_id):
	"""Allows to delete existing adventure"""

	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure
	adventure = Adventure.query.filter_by(id=adventure_id).first()

	# check if adventure exists
	if adventure is None:
		flash('Adventure not found', 'danger')
		return redirect(url_for('simple_page.index'))

	# check if user is creator of adventure
	if adventure.creator_id != current_user.id:
		flash('You cannot delete this adventure!', 'danger')
		return redirect(url_for('simple_page.index'))

	# delete all adventure participants
	participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
	for participant in participants:
		db.session.delete(participant)
		db.session.commit()

	# delete all adventure coordinates
	coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
	for coordinate in coordinates:
		db.session.delete(coordinate)
		db.session.commit()

	# delete adventure
	db.session.delete(adventure)
	db.session.commit()

	flash('Your adventure has been deleted', 'success')
	return redirect(url_for('simple_page.index'))

@mod.route('/search/', methods=['GET', 'POST'])
def search():
	"""Allows to search adventures"""

	final_adventures = []
	final_coordinates = ()

	form = SearchForm(request.form)

	if form.validate_on_submit():
		# get start position from html element
		start_pos = request.form.get('bl_corner')
		if (start_pos is None) or (start_pos is ''):
			flash('Something gone wrong start_pos', 'danger')
			return redirect(url_for('adventures.search'))

		# convert value to point (double, double)
		start_pos = ast.literal_eval(str(start_pos))
		if (start_pos is None) or (not is_float(start_pos[0])) or (not is_float(start_pos[1])):
			flash('Something gone wrong start_pos convert', 'danger')
			return redirect(url_for('adventures.search'))

		# get end position from html element
		end_pos = request.form.get('tr_corner')
		if (end_pos is None) or (end_pos is ''):
			flash('Something gone wrong end_pos', 'danger')
			return redirect(url_for('adventures.search'))

		# convert value to point (double, double)
		end_pos = ast.literal_eval(str(end_pos))
		if (end_pos is None) or (not is_float(end_pos[0])) or (not is_float(end_pos[1])):
			flash('Something gone wrong end_pos convert', 'danger')
			return redirect(url_for('adventures.search'))

		# get adventures from area
		coordinates = Coordinate.query.filter(
			Coordinate.latitude >= start_pos[0], Coordinate.latitude <= end_pos[0],
			Coordinate.longitude >= start_pos[1], Coordinate.longitude <= end_pos[1]
		).group_by(Coordinate.adventure_id).all()

		for coordinate in coordinates:
			# get adventure with coordinates id
			adventure = Adventure.query.filter_by(id=coordinate.adventure_id).first()

			# check if adventure is active
			if not adventure.is_active():
				continue

			check = False
			for mode in form.modes.data:
				if int(adventure.mode) == int(mode):
					check = True
					break

			if check:
				# get creator of the event
				user = User.query.filter_by(id=adventure.creator_id).first()

				# get joined participants
				participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()

				# add to all adventures
				final_adventures.append({
					'id': adventure.id,
					'username': user.username,
					'date': adventure.date,
					'info': adventure.info,
					'joined': len(participants),
					'mode': ADVENTURES.MODES[int(adventure.mode)],
				})

				# update adventure search times
				adventure.searched += 1
				db.session.commit()

		# updated search coordinates
		final_coordinates = (start_pos, end_pos)

		# sort adventures by date
		final_adventures = sorted(final_adventures, key=(lambda a: a['date']))

		# flash(u'Wyszukiwanie powiodlo sie', 'success')

	return render_template(
		'adventures/search.html',
		form=form,
		adventures=final_adventures,
		coordinates=final_coordinates
	)
