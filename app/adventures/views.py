from flask import Blueprint, request, render_template, g, flash, redirect, url_for
from flask.ext.login import login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import db
from app.adventures.models import Adventure, AdventureParticipant, Coordinate
from app.adventures.forms import NewForm, EditForm
from app.users.models import User

from config import DATABASE_QUERY_TIMEOUT

mod = Blueprint('adventures', __name__, url_prefix='/adventures')


@mod.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= DATABASE_QUERY_TIMEOUT:
			app.logger.warning(
				"SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
				(query.statement, query.parameters, query.duration,
				 query.context)
			)
	return response

# New trip
@mod.route('/new/', methods=['GET', 'POST'])
@login_required
def new():
	# if new form has been submitted
	form = NewForm(request.form)

	if request.method == 'GET':
		return render_template('adventures/new.html', form=form)

	# verify the new form
	if form.validate_on_submit():
		# add adventure to database
		adventure = Adventure(creator_id=g.user.id, date=form.date.data, info=form.info.data, joined=1)
		db.session.add(adventure)
		db.session.commit()

		# add participant of adventure to database
		participant = AdventureParticipant(adventure_id=adventure.id, user_id=g.user.id)
		db.session.add(participant)
		db.session.commit()

		# add coordinates of adventure to database

		# everything is okay
		flash('Adventure item was successfully created')
		return redirect(url_for('simple_page.index'))

	return render_template('adventures/new.html', form=form)

@mod.route('/<int:adventure_id>')
def adventure_show(adventure_id):
	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	final_adventure = {}
	final_participants = []

	# get adventure and creator of it
	adventure = Adventure.query.filter_by(id=adventure_id).first()
	user = User.query.filter_by(id=adventure.creator_id).first()

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

	return render_template('adventures/show.html', adventure=final_adventure, participants=final_participants)

@mod.route('/join/<int:adventure_id>')
@login_required
def join(adventure_id):
	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=g.user.id).first()

	# check if user joined adventure
	if participant is not None:
		flash('You arleady have joined to this adventure')
	else:
		# add user to adventure participants to database
		participant = AdventureParticipant(adventure_id=adventure_id, user_id=g.user.id)
		db.session.add(participant)
		db.session.commit()
		flash('You have joined to this adventure')

	return redirect(url_for('simple_page.index'))

@mod.route('/my/')
@login_required
def my_adventures():
	final_adventures = []
	final_joined_adventures = []

	# get all adventures which created user
	adventures = Adventure.query.filter_by(creator_id=g.user.id).order_by(Adventure.date.asc()).all()
	for adventure in adventures:
		# get joined participants
		joined = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()

		final_adventures.append({
			'id': adventure.id,
			'date': adventure.date,
			'info': adventure.info,
			'joined': len(joined)
		})

	# get all adventures to which user joined
	joined_adventures = AdventureParticipant.query.filter_by(user_id=g.user.id).all()
	for joined_adventure in joined_adventures:
		# get adventure
		adventure = Adventure.query.get(joined_adventure.adventure_id)

		# check if user is not creator (we do not want duplicates)
		if (adventure is not None) and (adventure.creator_id != g.user.id):
			final_joined_adventures.append(adventure)

	return render_template('adventures/my.html', adventures=final_adventures, joined_adventures=final_joined_adventures)

# Edit adventure
@mod.route('/edit/<int:adventure_id>', methods=['GET', 'POST'])
@login_required
def edit(adventure_id=0):
	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure
	adventure = Adventure.query.get(adventure_id)

	# check if adventure exists
	if adventure is None:
		flash('Adventure not found.')
		return redirect(url_for('simple_page.index'))

	# check if user is creator of adventure
	if adventure.creator_id != g.user.id:
		flash('You cannot edit this adventure!')
		return redirect(url_for('simple_page.index'))

	# get form
	form = EditForm(request.form, obj=adventure)

	# verify the edit form
	if form.validate_on_submit():
		# delete existing coordinates for the adventure_id
		db.session.query(Coordinate).filter_by(adventure_id=adventure_id).delete()

		# get coordinates
		i = 0
		while True:
			marker = request.form.get('marker_' + str(i))
			if (marker is None) or (marker is ''):
				break

			raw_coordinate = eval(str(marker))
			if raw_coordinate is not None:
				coordinate = Coordinate(adventure_id=adventure_id, path_point=i, latitude=raw_coordinate[0], longitude=raw_coordinate[1])
				db.session.add(coordinate)

			db.session.commit()
			i = i + 1

		# get edited adventure from the form
		form.populate_obj(adventure)

		# add adventure to database
		db.session.commit()

		# everything is okay
		flash('Adventure has been successfully edited')
		return redirect(url_for('simple_page.index'))

	# get coordinates of existing points
	all_coordinates = []
	coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
	for coordinate in coordinates:
		all_coordinates.append((coordinate.latitude, coordinate.longitude))

	return render_template('adventures/edit.html', form=form, adventure_id=adventure_id, markers=all_coordinates)

@mod.route('/delete/<int:adventure_id>')
@login_required
def delete(adventure_id):
	# check if adventure_id is not max_int
	if adventure_id >= 9223372036854775807:
		return redirect(url_for('simple_page.index'))

	# get adventure
	adventure = Adventure.query.get(adventure_id)

	# check if adventure has been found
	if adventure is None:
		flash('Adventure not found.')
		return redirect(url_for('simple_page.index'))

	# check if user is creator of adventure
	if adventure.creator_id != g.user.id:
		flash('You cannot delete this adventure!')
		return redirect(url_for('simple_page.index'))

	# delete adventure
	db.session.delete(adventure)

	# delete all adventure participants
	participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
	for participant in participants:
		db.session.delete(participant)

	# delete all adventure coordinates
	coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
	for coordinate in coordinates:
		db.session.delete(coordinate)

	db.session.commit()
	flash('Your adventure has been deleted.')
	return redirect(url_for('simple_page.index'))
