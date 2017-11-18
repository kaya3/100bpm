
from app import db

class Song(db.Model):
	__tablename__ = 'songs'
	id = db.Column('id', db.Integer, primary_key=True)
	filename_prefix = db.Column('filename', db.String(256), unique=True, nullable=False)
	artist = db.Column('artist', db.String(256), nullable=True)
	title = db.Column('title', db.String(256), nullable=True)
	sounds = db.relationship('Sound', backref='song', lazy='dynamic')
	
	def __init__(self, filename_prefix, artist, title):
		self.filename_prefix = filename_prefix
		self.artist = artist
		self.title = title

class Sound(db.Model):
	@staticmethod
	def search(q):
		sounds = { t.sound for t in Tag.query.filter(Tag.tag_name == q.lower()) }
		q = '%{}%'.format(q)
		for song in Song.query.filter(Song.artist.ilike(q) | Song.title.ilike(q)):
			sounds.update(song.sounds)
		return list(sounds)
	
	__tablename__ = 'sounds'
	id = db.Column('id', db.Integer, primary_key=True)
	filename = db.Column('filename', db.String(256), unique=True, nullable=False)
	song_id = db.Column('song_id', db.Integer,  db.ForeignKey('songs.id'), nullable=True)
	tags = db.relationship('Tag', backref='sound', lazy='dynamic')
	
	def __init__(self, filename, song=None):
		self.filename = filename
		self.song = song
	
	def get_data(self):
		data = { 'id': self.id, 'filename': self.filename }
		if self.song:
			data['artist'] = self.song.artist
			data['song_name'] = self.song.title
		tags = list(self.tags)
		if tags:
			data['tags'] = [ t.tag_name for t in tags ]
		return data

class Tag(db.Model):
	__tablename__ = 'tags'
	id = db.Column('id', db.Integer, primary_key=True)
	sound_id = db.Column('sound_id', db.Integer,  db.ForeignKey('sounds.id'), nullable=False)
	tag_name = db.Column('tag_name', db.String(256), nullable=False)
	
	def __init__(self, sound, tag_name):
		self.sound = sound
		self.tag_name = tag_name
