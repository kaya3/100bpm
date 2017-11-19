var selected = {};
var drumbeat;
var idToNames = {};
var valueInTypeInput = {};
$(document).ready(function() {
    $('input').changeOrDelayedKey(function(e) {
        e.preventDefault();    
        var type = $(this).attr("sound");
        if (type && (!valueInTypeInput[type] || valueInTypeInput[type] !== $(this).val())) {
            valueInTypeInput[type] = $(this).val();
            getAudioFiles(type, $(this));
        }
    });
    $('#generateDrumbeat').on('click', function() {
        var hasSnare = !!selected['snare'];
        var hasKick = !!selected['kick'];
        if (!hasKick || !hasSnare) {
            $('#drumbeatError').text('To generate the drumbeat you also need: ' 
                + hasKick ? '' : 'kick '
                + hasSnare ? '' : 'snare ');
            $('#drumbeatError').show();
            return;
        }
        $.post('/api/generate_beat', 
            {sound_kick: selected['kick'], sound_snare: selected['snare']},
            function(data) {
                drumbeat = data;
				load_beat_loop('/tmp/' + drumbeat);
            });
    }); 
    $('#send').on('click', function(){
        var noteArray = getCurrentNotesArray();
        if (noteArray.length === 0 || !drumbeat || !selected['sound']) {
            console.log('ERRROR!1111');
            return;
        }
        $.post('/api/generate_melody', {
			beat_filename: drumbeat,
			sound_melody: selected['sound'],
			notes_melody: JSON.stringify(noteArray)
		}, function(data) {
            var $div = $('<div>', {class: 'element row'}),
                $divAudio = $('<div>', {class: 'col-4'}),
                $divLink = $('<div>', {class: 'col-8'}),
                $link = $('<a>', {href: 'https://100bpm.org/tmp/' + data}),
                $audio = load_audio('/tmp/' + data);
            $link.text('Download the song');
            $divLink.append($link);
            $divAudio.append($audio);
            $div.append($divAudio);
            $div.append($divLink);
            $('#records').append($div);
			drumbeat = data;
			load_beat_loop('/tmp/' + drumbeat);
			clear_melody();
        });
    });
    $('#clear_notes').on('click', function() {
        //var hasKick = !!selected['sound'];
        //if (!drumbeat || !hasKick) {
        //    console.log('No drumbeat');
        //    return;
        //}
        //load_note_sounds('/sounds/' + idToNames[selected['sound']]);
       // load_beat_loop('/tmp/' + drumbeat);
			clear_melody();
    });
});

function getAudioFiles(type, e) {
    $('#sendError').hide();
    $('#' + type + 'Files').empty();
    $.get('/api/search', {t: type, q: e.val()}, function(data) {
        var audioFiles = [];
        var parsedData = JSON.parse(data);
        for (var song of parsedData) {
            var songName = song.filename;
            audioFiles.push({
                name: '/sounds/' + songName + '.ogg', 
                id: song.id, 
                song_name: song.song_name,
                artist: song.artist,
                image: song.image
            });
            idToNames[song.id] = songName;
            console.log(JSON.stringify(song));
        }
        reloadAudioElements(audioFiles, type);
    });
}

function reloadAudioElements(audioFiles, type) {
    for (var file of audioFiles) {
        var $div = $('<div>', {class: 'element row'}),
            $divPick = $('<div>', {class: 'col-1'}),
            $divThumb = $('<div>', {class: 'col-1'}),
            $divName = $('<div>', {class: 'col-3'}),
            $divAuthor = $('<div>', {class: 'col-4'}),
            $divMusic = $('<div>', {class: 'col-3'}),
            $image = $('<img>', {src: '/default-record-thumbnail.jpg', width: '32', height: '32'}),
            $audio = $('<audio>', {controls: 'controls'}),
            $source = $('<source>', {src: file.name, type: 'audio/wav'}),
            $selector = $('<input>', {type: 'radio', name: 'nameRadio',
                     value: file.id, class:'form-check-input'});
        if (file.image) {
            $image.attr('src', file.image);
        }
        $divPick.append($selector);
        $divThumb.append($image);
        $audio.text("Your browser does not support the audio element.");
        $audio.append($source);
        $divMusic.append($audio);
        $divName.text(file.song_name);
        $divAuthor.text(file.artist);
        $div.append($divPick);
        $div.append($divThumb);
        $div.append($divName);
        $div.append($divAuthor);
        $div.append($divMusic);
        $selector.on('change', function(e) {
            var name = $(this).attr("value");
            var checked = $(this).prop('checked');
            if(checked) {
                selected[type] = name;
				if(type == 'sound') {
					load_note_sounds('/sounds/' + idToNames[name]);
				}
			}
        });
        $('#' + type + 'Files').append($div);
    }
}
                          
$( document ).ready(function() {
    $( "#accordion" ).accordion({heightStyle: 'content'});
} );

