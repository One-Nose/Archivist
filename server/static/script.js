$('#connect-button').click(() => {
    $.post('/connect', { password: $('#connect-password').val() }, (data) => {
        alert(data.success)
    })
})
