$('#connect-button').click(() => {
    const connectPassword = $('#connect-password')
    const password = connectPassword.val()
    $.post('/connect', { password: password }, (data) => {
        if (data.success) {
            Cookies.set('password', password)
            location.reload()
        } else {
            connectPassword.val('')
            alert('Wrong password')
        }
    })
})

$('#disconnect').click(() => {
    Cookies.remove('password')
    location.replace('/')
})

$('#guest-button').click(() => {
    location.replace('/archive')
})

$('#view-archive').click(() => {
    location.replace('/archive')
})

$('#view-categories').click(() => {
    location.replace('/categories')
})

$('#view-category').click((event) => {
    location.replace(`/category/${event.target.name}`)
})

$('#view-index').click(() => {
    location.replace('/')
})

$(() => {
    if (location.pathname === '/' && Cookies.get('password') !== undefined)
        location.replace('/archive')
})
