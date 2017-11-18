
from app import db

class Sound(db.Model):
	__tablename__ = 'sounds'
	id = db.Column('id', db.Integer, primary_key=True)
	filename = db.Column('filename', db.String(256), unique=True, nullable=False)
	artist = db.Column('artist', db.String(256), nullable=True)
	song_name = db.Column('song_name', db.String(256), nullable=True)
	tags = db.relationship('Tag', backref='sound', lazy='dynamic')

class Tag(db.Model):
	__tablename__ = 'tags'
	id = db.Column('id', db.Integer, primary_key=True)
	sound_id = db.Column('sound_id', db.Integer,  db.ForeignKey('sounds.id'), nullable=False)
	tag_name = db.Column('tag_name', db.String(256), nullable=False)
