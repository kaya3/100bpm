var selected = {};
var beats = {};

$(document).on('click', '.dropdown-menu', function(e) {
    // console.log(e.target.text);
    $('#send').show();
    $('#sendError').hide();
    selected = {};
    $('#audioFiles').empty();
    $.get('../api/search', {t: 'sound', q: e.target.text}, function(data) {
        console.log(data);
        var audioFiles = [];
        var parsedData = JSON.parse(data);
        for (var song of parsedData) {
            var songName = song.filename/*.split(' ').join('%20')*/;
            audioFiles.push({
				name: '../sounds/' + songName + '.ogg', 
                id: song.id, 
                song_name: song.song_name,
                artist: song.artist
			});
            console.log(JSON.stringify(song));
            beats[songName] = song;
        }
        reloadAudio(audioFiles);
    });
    
    e.preventDefault();
});

function reloadAudio(audioFiles) {
    for (var file of audioFiles) {
        var $div = $('<div>', {class: 'element row'}),
            $divPick = $('<div>', {class: 'col-1'}),
            $divName = $('<div>', {class: 'col-4'}),
            $divAuthor = $('<div>', {class: 'col-4'}),
            $divMusic = $('<div>', {class: 'col-3'}),
            $audio = $('<audio>', {controls: 'controls'}),
            $source = $('<source>', {src: file.name, type: 'audio/wav'}),
            $selector = $('<input>', {type: 'radio', name: 'nameRadio',
                     value: file.id, class:'form-check-input'});
        
        $divPick.append($selector);
        $audio.text("Your browser does not support the audio element.");
        $audio.append($source);
        $divMusic.append($audio);
        $divName.text(file.song_name);
        $divAuthor.text(file.artist);
        $div.append($divPick);
        $div.append($divName);
        $div.append($divAuthor);
        $div.append($divMusic);
        $selector.on('change', function(e) {
            var name = $(this).attr("value");
            var checked = $(this).prop('checked');
            if (checked)
                selected[name] = checked;
            else
                delete selected[name];
            console.log(JSON.stringify(selected));
        });
        $('#audioFiles').append($div);
    }
}

$(document).on('click', '#send', function(e) {
    if (Object.keys(selected).length === 0 || lastNotes.length === 0) {
        $('#sendError').show();
        return;
    }
    console.log(JSON.stringify(lastNotes));
    let selectedId = Object.keys(selected)[0];
    $.post('../api/generate_track', {sound_melody: selectedId,
        sound_kick: 144,
        sound_snare: 135,
        notes_melody: JSON.stringify(lastNotes)}, function(data) {
            console.log(JSON.stringify(data));
        });
});

var record;
var currentNotes = {};
var currentNoteArray = [];
var lastNotes = [];
$(document).on('click', '#record', function(e) {
    var time = new Date;
    time = time.getTime();
    if (record && time - record < 4800) {
        return;
    }
    console.log('recording');
    record = time;
    currentNotes = {};
    currentNoteArray = [];
    setTimeout(function() {
        console.log(record);
        var time = (new Date).getTime();
        for (var pitch in currentNotes) {
            currentNoteArray.push([pitch, currentNotes[pitch], 4800]);
        }
        lastNotes = currentNoteArray;
        for (var note of lastNotes) {
            note[1] -= record;
            note[2] -= record;
        }
        currentNoteArray = [];
        currentNotes = {};
        console.log(JSON.stringify(lastNotes));
    }, 4800);    
});

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

document.addEventListener('keydown', function(event) {
    var pitch = 0;
    pitch = keyToPitch[event.keyCode];
    if (pitch && !currentNotes[pitch]) {
        currentNotes[pitch] = (new Date).getTime();
    }
});

document.addEventListener('keyup', function(event) {
    var pitch = 0;
    pitch = keyToPitch[event.keyCode];
    if (currentNotes[pitch]) {
        var time = (new Date).getTime();
        currentNoteArray.push([pitch, currentNotes[pitch], time]);
        delete currentNotes[pitch];
    }
});

