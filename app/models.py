
from app import db

class Song(db.Model):
	__tablename__ = 'songs'
	id = db.Column('id', db.Integer, primary_key=True)
	filename_prefix = db.Column('filename', db.String(256), unique=True, nullable=False)
	artist = db.Column('artist', db.String(256), nullable=True)
	title = db.Column('title', db.String(256), nullable=True)
	sounds = db.relationship('Sound', backref='song', lazy='dynamic')
	image_filename = db.Column('image_filename', db.String(256), nullable=True)
	
	def __init__(self, filename_prefix, artist, title, image_filename=None):
		self.filename_prefix = filename_prefix
		self.artist = artist
		self.title = title
		self.image_filename = image_filename

class Sound(db.Model):
	@staticmethod
	def search(sound_type, q):
		sounds = { t.sound for t in Tag.query.filter(Tag.tag_name == q.lower()) }
		q = '%{}%'.format(q)
		for song in Song.query.filter(Song.artist.ilike(q) | Song.title.ilike(q)):
			sounds.update(song.sounds)
		return [ s for s in sounds if s.sound_type == sound_type ]
	
	__tablename__ = 'sounds'
	id = db.Column('id', db.Integer, primary_key=True)
	sound_type = db.Column('sound_type', db.String(16), nullable=False)
	filename = db.Column('filename', db.String(256), unique=True, nullable=False)
	song_id = db.Column('song_id', db.Integer,  db.ForeignKey('songs.id'), nullable=True)
	tags = db.relationship('Tag', backref='sound', lazy='dynamic')
	
	def __init__(self, sound_type, filename, song=None):
		self.sound_type = sound_type
		self.filename = filename
		self.song = song
	
	def get_data(self):
		data = { 'id': self.id, 'filename': self.filename }
		if self.song:
			data['artist'] = self.song.artist
			data['song_name'] = self.song.title
			if self.song.image_filename:
				data['image'] = self.song.image_filename
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
