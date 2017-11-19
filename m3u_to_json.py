#!/usr/bin/python3

import fileinput
import os
import json
import re
from queue import Queue

from app import db
from app.models import *

paths = {
	'sound': 'app/sounds/post_sounds',
	'kick': 'app/sounds/post_kicks',
	'snare': 'app/sounds/post_snares'
}

dir_list = { s: [ t for t in os.listdir(p) if t[-4:] == '.wav' ] for s,p in paths.items() }

image_dir_list = os.listdir('app/sounds/post_sounds_covers')
print(image_dir_list)

m3u = Queue()
for line in fileinput.input():
	m3u.put(line)

first_line = m3u.get().strip()
if first_line != '#EXTM3U':
	print(first_line)
	raise ValueError()

songs = []
sound_files = []

song_id = 1
sound_id = 1

while not m3u.empty():
	metadata = m3u.get().strip().split(',', 1)[-1]
	if ' - ' not in metadata:
		print("Can't parse metadata:", metadata)
		continue
	
	fullpath = m3u.get().strip()
	filename_prefix = fullpath.split('/')[-1]
	filename_prefix = re.sub(r'[^a-zA-Z0-9\.]', '', filename_prefix)
	title, artist = metadata.split(' - ', 1)
	
	#for spl in [' (feat. ', ' (Feat. ', ' (ft. ', ' (Ft. ']:
	#	if spl in title and title[-1] == ')':
	#		before, after = title.split(spl, 1)
	#		title = before
	#		artist = artist + spl + after
	
	image_filename=None
	for filename in image_dir_list:
		if filename.startswith(filename_prefix[:-4]):
			image_filename = 'sounds/post_sounds_covers/' + filename
	
	songs.append({
		'id': song_id,
		'filename_prefix': filename_prefix,
		'title': title,
		'artist': artist,
		'image_filename': image_filename
	})
	
	song = Song(filename_prefix, title, artist, image_filename)
	db.session.add(song)
	db.session.flush()
	
	for sound_type, path in paths.items():
		relative_path = path.split('/')[-1]
		for filename in list(dir_list[sound_type]):
			if filename.startswith(filename_prefix):
				dir_list[sound_type].remove(filename)
				
				sound = Sound(sound_type, relative_path + '/' + filename, song)
				db.session.add(sound)
				db.session.flush()
				
				sound_files.append({
					'id': sound_id,
					'song_id': song_id,
					'filename': path + '/' + filename
				})
				
				sound_id += 1
	song_id += 1

db.session.commit()

with open('json/songs.json', 'w') as f:
	f.write(json.dumps(songs))

with open('json/sounds.json', 'w') as f:
	f.write(json.dumps(sound_files))

print(dir_list)
