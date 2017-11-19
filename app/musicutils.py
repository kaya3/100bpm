import random
import uuid
import process

def unique_wav_filename():
	return str(uuid.uuid4()) + '.wav'

def convert_to_ogg(full_path_filename):
	process = subprocess.Popen(['ffmpeg', '-i', full_path_filename, full_path_filename + '.ogg'])
	process.wait()
	if process.returncode:
		print(process.communicate(timeout=1))
		raise RuntimeError('Failed to convert to ogg.')

def random_kick_sequence():
	kicks = random.choice([
		{0,                   1200,                   2400,                  3600},
		{0,              900,                         2400,            3300},
		{0,                         1500,             2400,                        3900},
		{0,              900,       1500,             2400,            3300,       3900}
	])
	
	add16th = random.random()
	if add16th > 0.8:
		kicks.add(2250)
		if add16th > 0.95:
			kicks.add(1050)
	elif add16th < 0.2:
		kicks.add(3750)
		if add16th < 0.05:
			kicks.add(1350)
	
	return kicks

def random_snare_sequence():
	return [600, 1800, 3000, 4200]
