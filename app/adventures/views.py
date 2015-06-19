from flask import Blueprint, request, render_template, g, flash, redirect, url_for
from flask.ext.login import login_required

from app import db
from app.adventures.models import Adventure, AdventureParticipant
from app.adventures.forms import NewForm, EditForm
from app.users.models import User

mod = Blueprint('adventures', __name__, url_prefix='/adventures')

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

		# everything is okay
		flash('Adventure item was successfully created')
		return redirect(url_for('simple_page.index'))

	return render_template('adventures/new.html', form=form)

@mod.route('/<int:adventure_id>')
def adventure_show(adventure_id):
	# todo: make better checkout - check if adventure_id is small enough to query database
	if adventure_id >= 10000:
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
	# todo: make better checkout - check if adventure_id is small enough to query database
	if adventure_id >= 10000:
		return redirect(url_for('simple_page.index'))

	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=g.user.id).first()
	if participant is not None:
		flash('You arleady have joined to this adventure')
	else:
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
		adventure = Adventure.query.filter_by(id=joined_adventure.adventure_id).first()

		# check if user is not creator (we do not want duplicates)
		if (adventure is not None) and (adventure.creator_id != g.user.id):
			final_joined_adventures.append(adventure)

	return render_template('adventures/my.html', adventures=final_adventures, joined_adventures=final_joined_adventures)

# Edit adventure
@mod.route('/edit/<int:adventure_id>', methods=['GET', 'POST'])
@login_required
def edit(adventure_id=0):
	# check if adventure_id is not max_int
	if (adventure_id >= 9223372036854775807):
		return redirect(url_for('simple_page.index'))

	# get adventure
	adventure = Adventure.query.filter_by(id=adventure_id).first()

	# check if adventure exists
	if adventure is None:
		flash('Invalid adventure :C')
		return redirect(url_for('simple_page.index'))

	# check if user is creator of adventure
	if adventure.creator_id != g.user.id:
		flash('You are not creator of this adventure!')
		return redirect(url_for('simple_page.index'))

	# get form
	form = EditForm(request.form, obj=adventure)

	# verify the edit form
	if form.validate_on_submit():
		# get edited adventure from the form
		form.populate_obj(adventure)

		# add adventure to database
		db.session.commit()

		# everything is okay
		flash('Adventure has been successfully edited')
		return redirect(url_for('simple_page.index'))

	return render_template('adventures/edit.html', form=form, adventure_id=adventure_id)
