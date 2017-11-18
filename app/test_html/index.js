var selected = {};
var beats = {};

$(document).on('click', '.dropdown-menu', function(e) {
    // console.log(e.target.text);
    $('#send').show();
    $('#sendError').hide();    
    selected = {};
    $('#audioFiles').empty();
    $.get('../api/search', {q: e.target.text}, function(data) {
        console.log(data);
        var audioFiles = [];
        var parsedData = JSON.parse(data);
        for (var song of parsedData) {
            var songName = song.filename/*.split(' ').join('%20')*/;
            audioFiles.push({name: '../sounds/' + songName, id: song.id});
            beats[songName] = song;
        }
        reloadAudio(audioFiles);
    });
    
    e.preventDefault();
});

function reloadAudio(audioFiles) {
    for (var file of audioFiles) {
        var div = $('<div>', {class: 'element'});
        var audio = $('<audio>', {controls: 'controls'});
        audio.text("Your browser does not support the audio element.");
        var source = $('<source>', {src: file.name, type: 'audio/wav'});
        var selector = $('<input>', {type: 'checkbox', value: file.id, class:'form-check-input'});
        selector.on('change', function(e) {
            var name = $(this).attr("value");
            var checked = $(this).prop('checked');
            if (checked)
                selected[name] = checked;
            else
                delete selected[name];
            console.log(JSON.stringify(selected));
        });
        audio.append(source);
        div.append(selector);
        div.append(audio);
        $('#audioFiles').append(div);
    }
}

$(document).on('click', '#send', function(e) {
    if (Object.keys(selected).length === 0) {
        $('#sendError').show();
        return;
    }
});

var record;
// var 
$(document).on('click', '#record', function(e) {
    record = new Date;
    record = record.getTime();
    console.log(record);
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
    console.log('keydown ' + pitch);
});

document.addEventListener('keyup', function(event) {
    var pitch = 0;
    pitch = keyToPitch[event.keyCode];
    console.log('keyup ' + pitch);
});