var selected = {};

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
            var songName = song.filename.split(' ').join('%20');
            audioFiles.push('../sounds/' + songName);
        }
        reloadAudio(audioFiles);
    });
    
    e.preventDefault();
});

function reloadAudio(audioFiles) {
    for (var file of audioFiles) {
        var div = $('<div>', {class: 'element'});
        var audio = $('<audio>', {controls: 'controls', preload: 'auto'});
        audio.text("Your browser does not support the audio element.");
        var source = $('<source>', {src: file, type: 'audio/wav'});
        var selector = $('<input>', {type: 'checkbox', value: file, class:'form-check-input'});
        selector.on('change', function(e) {
            var name = $(this).attr("value");
            selected[name] = $(this).prop('checked');
        });
        audio.append(source);
        div.append(selector);
        div.append(audio);
        $('#audioFiles').append(div);
    }
}

$("body").keypress(function(e){
    console.log(e.which);
});

$(document).on('click', '#send', function(e) {
    if (Object.keys(selected).length === 0) {
        $('#sendError').show();
        return;
    }
});

function keyToNote(key) {
    
}
// /api/search?q=""