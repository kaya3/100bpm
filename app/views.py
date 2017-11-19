
from app import app,db
from flask import request
import json
import re
import os

from processing import generate_drumbeat, generate_song_from_drumbeat
from app.models import *
from app.decorators import crossdomain
from app.musicutils import *
from config import BASE_DIR

@app.route('/api/search')
@crossdomain(origin='*')
def search():
	if 't' not in request.args:
		return 'Request must have t=... parameter.', 400
	if 'q' not in request.args:
		return 'Request must have q=... parameter.', 400
	t = request.args['t'].strip()
	q = request.args['q'].strip()
	if t not in ['sound', 'kick', 'snare']:
		return 'Invalid sound type.', 400
	if not q:
		return 'Empty search string.', 400
	return json.dumps([ s.get_data() for s in Sound.search(t, q) ])

@app.route('/api/generate_beat', methods=['POST'])
@crossdomain(origin='*')
def generate_beat():
	p_hits = ['notes_kick', 'notes_snare']
	p_sounds = ['sound_kick', 'sound_snare']
	
	try:
		params = dict()
		
		#TODO: generate randomly, or get from user
		params['notes_kick'] = random_kick_sequence()
		params['notes_snare'] = random_snare_sequence()
		
		#TODO: get hits from user?
		for p in p_sounds:
			if p not in request.form or not request.form[p]:
				return 'Request must have {}=... field.'.format(p), 400
			params[p] = json.loads(request.form[p])
		
		#for p in p_hits:
		#	if not isinstance(params[p], list) or not all(
		#		isinstance(i, int)
		#		for i in params[p]
		#	):
		#		return 'Request field {} must be a list of hits.'.format(p), 400
		
		for p in p_sounds:
			if not isinstance(params[p], int):
				return 'Request field {} must be a sound id.'.format(p), 400
			sound = Sound.query.get(params[p])
			if not sound:
				return 'No such sound id: {}.'.format(params[p]), 400
			params[p] = os.path.join(BASE_DIR, 'app', 'sounds', sound.filename)
		
		generated_filename = unique_wav_filename()
		full_path_filename = os.path.join(BASE_DIR, 'tmp', generated_filename)
		params['output_filename'] = full_path_filename
		
		# generate track
		generate_drumbeat(**params)
		
		# convert to ogg
		convert_to_ogg(full_path_filename)
		
		return generated_filename
	except:
		import sys, traceback
		print('Exception when generating drumbeat:')
		print('-'*60)
		traceback.print_exc(file=sys.stdout)
		print('-'*60)
		return 'Error when generating drumbeat.', 400

@app.route('/api/generate_melody', methods=['POST'])
@crossdomain(origin='*')
def generate_melody():
	p_notes = ['notes_melody']
	p_sounds = ['sound_melody']
	
	try:
		params = dict()
		if 'beat_filename' not in request.form:
			return 'Request must have beat_filename=... field.', 400
		elif not re.match(r'^[a-zA-Z0-9\-]+\.wav$', request.form['beat_filename']):
			return 'Malformed beat filename.', 400
		
		beat_filename = request.form['beat_filename']
		full_path_beat_filename = os.path.join(BASE_DIR, 'tmp', beat_filename)
		if not os.path.isfile(full_path_beat_filename):
			return 'Beat file not found.', 400
		params['beat_filename'] = full_path_beat_filename
		
		#TODO: get hits from user?
		for p in p_notes + p_sounds:
			if p not in request.form or not request.form[p]:
				return 'Request must have {}=... field.'.format(p), 400
			params[p] = json.loads(request.form[p])
		
		for p in p_notes:
			if not isinstance(params[p], list) or not all(
				isinstance(n, list)
				and len(n) == 3
				and all(isinstance(i, (int,str)) for i in n)
				for n in params[p]
			):
				return 'Request field {} must be a list of notes.'.format(p), 400
			params[p] = [ [ int(i) for i in n ] for n in params[p] ]
		
		for p in p_sounds:
			if not isinstance(params[p], int):
				return 'Request field {} must be a sound id.'.format(p), 400
			sound = Sound.query.get(params[p])
			if not sound:
				return 'No such sound id: {}.'.format(params[p]), 400
			params[p] = os.path.join(BASE_DIR, 'app', 'sounds', sound.filename)
		
		generated_filename = unique_wav_filename()
		full_path_filename = os.path.join(BASE_DIR, 'tmp', generated_filename)
		params['output_filename'] = full_path_filename
		
		# generate track
		generate_song_from_drumbeat(**params)
		
		# convert to ogg
		convert_to_ogg(full_path_filename)
		
		return generated_filename
	except:
		import sys, traceback
		print('Exception when generating melody:')
		print('-'*60)
		traceback.print_exc(file=sys.stdout)
		print('-'*60)
		return 'Error when generating melody.', 400

@app.route('/api/add_tag', methods=['POST'])
def add_tag():
	if 'sound' not in request.form or not request.form['sound']:
		return 'Request must have a sound=... field.', 400
	if not re.match(r'^[1-9][0-9]*$', request.form['sound']):
		return 'Malformed sound id.', 400
	sound_id = int(request.form['sound'])
	if 'tag_name' not in request.form or not request.form['tag_name']:
		return 'Request must have a tag_name=... field.', 400
	tag_name = request.form['tag_name'].strip()
	if not re.match(r'^[a-zA-Z ]+$', tag_name):
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
