function load_audio(f) {
	var a = document.createElement('audio');
	var source1 = document.createElement('source');
	source1.type = 'audio/wav';
	source1.src = f;
	var source2 = document.createElement('source');
	source2.type = 'audio/ogg';
	source2.src = f + '.ogg';
	a.appendChild(source1);
	a.appendChild(source2);
	a.load();
	return a;
}

var note_sounds = {};
function load_note_sounds(base_filename) {
	base_filename = base_filename.replace('/post_sounds/', '/post_sounds_pitched/');
	for(var i = 48; i <= 65; ++i) {
		note_sounds[i] = load_audio(base_filename + '_' + i + '.wav');
	}
}

var beat_loop_1 = null, beat_loop_2 = null, current_beat_loop = null;
var current_offset = 0;
function load_beat_loop(base_filename) {
	beat_loop_1 = load_audio(base_filename);
	beat_loop_2 = load_audio(base_filename);
	
	current_beat_loop = beat_loop_1;
	setTimeout(play_beat_loop, 1000);
}

function play_beat_loop() {
	if(beat_loop_1 === null || beat_loop_2 === null) { return; }
	
	for(pitch in currentNotes) {
		newNoteArray.push([pitch, currentNotes[pitch], 4800]);
	}
	for(var i = 0; i < newNoteArray.length; ++i) {
		var nn = newNoteArray[i];
		currentNoteArray = currentNoteArray.filter(function(cn) {
			return cn[2] <= nn[1] || cn[1] >= nn[2];
		});
		currentNoteArray.push(nn);
	}
	currentNotes = {};
	newNoteArray = [];
	
	if(current_beat_loop === beat_loop_1) {
		current_beat_loop = beat_loop_2;
	} else {
		current_beat_loop = beat_loop_1;
	}
	current_beat_loop.play();
	current_offset = (new Date).getTime();
	setTimeout(play_beat_loop, 4800);
	
	for(var i = 0; i < currentNoteArray.length; ++i) {
		(function(index) {
			var cn = currentNoteArray[index];
			setTimeout(function() {
				var a = note_sounds[cn[0]];
				a.currentTime = 0;
				a.play();
			}, cn[1]);
		})(i);
	}
}
function stop_beat_loop() {
	if(current_beat_loop !== null) {
		current_beat_loop.pause();
		current_beat_loop = null;
	}
	beat_loop_1 = null;
	beat_loop_2 = null;
}

function get_time() {
	// quantized to multiples of 300
	return 300 * Math.round(1000*current_beat_loop.currentTime / 300);
}

var keyToPitch = {
	65: 48,
	87: 49,
	83: 50,
	69: 51,
	68: 52,
	70: 53,
	84: 54,
	71: 55,
	89: 56,
	72: 57,
	85: 58,
	74: 59,
	75: 60,
	79: 61,
	76: 62,
	80: 63,
	186: 64,
	222: 65,
};

var currentNotes = {}, currentNoteArray = [], newNoteArray = [];
document.addEventListener('keydown', function(e) {
	var pitch = keyToPitch[e.keyCode];
	if (pitch && current_beat_loop) {
		currentNotes[pitch] = get_time();
		if(pitch in note_sounds) {
			note_sounds[pitch].play();
		}
	}
});

document.addEventListener('keyup', function(e) {
	var pitch = keyToPitch[e.keyCode];
	if (pitch in currentNotes && currentNotes[pitch]) {
		if(current_beat_loop) {
			var time = get_time();
			if(time >= 0 && time < 4800) {
				newNoteArray.push([pitch, currentNotes[pitch], time]);
			}
		}
		
		delete currentNotes[pitch];
		if(pitch in note_sounds) {
			note_sounds[pitch].pause();
			note_sounds[pitch].currentTime = 0;
		}
	}
});

$(document).ready(function() {
	//test
	//load_note_sounds('https://100bpm.org/sounds/post_sounds/01ShowNoLovefeat.WrdUp.wav');
	//load_beat_loop('https://100bpm.org/tmp/11c37a7b-7e58-4bb9-81ef-9e3ac425341b.wav');
});


