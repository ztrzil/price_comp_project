$(function() {
    $('#uploadButton').click(function() {
        var form_data = new FormData($('#imgUpload')[0]);
        var file = $("input[type='file']")[0].files[0];
        form_data.append("file", file);
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Success!');
            },
        });
    });
});

