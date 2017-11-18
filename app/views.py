
from app import app,db
from flask import request
import json
import re

from app.models import *
from app.decorators import crossdomain

@app.route('/')
def index():
	return 'Hello, world!'

@app.route('/api/search')
@crossdomain(origin='*')
def search():
	if 'q' not in request.args:
		return 'Request must have q=... parameter.', 400
	q = request.args['q'].strip()
	if not q:
		return 'Empty search string.', 400
	return json.dumps([ s.get_data() for s in Sound.search(q) ])

@app.route('/api/add_tag', methods=['POST'])
def add_tag():
	if 'sound' not in request.form or not request.form['sound']:
		return 'Request must have a sound=... field.', 400
	if not re.match('/^[1-9][0-9]*$/', request.form['sound']):
		return 'Malformed sound id.', 400
	sound_id = int(request.form['sound'])
	if 'tag_name' not in request.form or not request.form['tag_name']:
		return 'Request must have a tag_name=... field.', 400
	tag_name = request.form['tag_name'].strip()
	if not re.match('/^[a-zA-Z ]+$/', tag_name):
		return 'No special characters allowed in tag name.', 400
	
	sound = Sound.query.get(sound_id)
	if not sound:
		return 'No such sound.', 400
	if tag_name in sound.tags:
		return 'Sound already has that tag.', 400
	
	tag = Tag(sound, tag_name)
	db.session.add(tag)
	db.session.commit()
	return 'Tag added successfully.'
