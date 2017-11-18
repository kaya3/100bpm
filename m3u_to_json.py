#!/usr/bin/python3

import fileinput
import os
import json
import re
from queue import Queue

paths = {
	'sound': 'app/sounds/post_sounds',
	'kick': 'app/sounds/post_kicks',
	'snare': 'app/sounds/post_snares'
}

dir_list = { s: os.listdir(p) for s,p in paths.items() }

m3u = Queue()
for line in fileinput.input():
	m3u.put(line)

first_line = m3u.get().strip()
if first_line != '#EXTM3U':
	print(first_line)
	raise ValueError()

songs = []
sound_files = []
tags = []

song_id = 1
sound_id = 1

while not m3u.empty():
	metadata = m3u.get().strip()
	fullpath = m3u.get().strip()
	filename_prefix = fullpath.split('/')[-1]
	filename_prefix = re.sub(r'[^a-zA-Z0-9\.]', '', filename_prefix)
	title, artist = metadata.split(',', 1)[-1].split(' - ', 1)
	
	for spl in [' (feat. ', ' (Feat. ', ' (ft. ', ' (Ft. ']:
		if spl in title and title[-1] == ')':
			before, after = title.split(spl, 1)
			title = before
			artist = artist + spl + after
	
	songs.append({
		'id': song_id,
		'filename_prefix': filename_prefix,
		'title': title,
		'artist': artist
	})
	
	for tag, path in paths.items():
		for filename in list(dir_list[tag]):
			if filename.startswith(filename_prefix):
				dir_list[tag].remove(filename)
				sound_files.append({
					'id': sound_id,
					'song_id': song_id,
					'filename': path + '/' + filename
				})
				tags.append({
					'sound_id': sound_id,
					'tag_name': tag
				})
				sound_id += 1
	song_id += 1

with open('json/songs.json', 'w') as f:
	f.write(json.dumps(songs))

with open('json/sounds.json', 'w') as f:
	f.write(json.dumps(sound_files))

with open('json/tags.json', 'w') as f:
	f.write(json.dumps(tags))

print(dir_list)
