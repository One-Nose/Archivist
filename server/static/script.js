function lastPathPart() {
    return location.pathname.match(/\/([^/]+)$/)[1]
}

$('#add-order-rule').click(() => {
    const large = $('#select-large').val()
    const small = $('#select-small').val()

    if (large === '' || small === '') alert('Please choose two properties.')
    else if (large === small) alert('Please choose different properties.')
    else
        $.post('/add-order-rule', { large: large, small: small }, (data) => {
            if (data.success) {
                alert('Order rule added successfully.')
                $('#view-category').click()
            } else alert('Could not add order rule.')
        }).fail(() => {
            alert('An error has occurred.')
        })
})

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
    }).fail(() => {
        alert('An error has occurred.')
    })
})

$('#disconnect').click(() => {
    Cookies.remove('password')
    location.replace('/')
})

$('#guest-button').click(() => {
    location.replace('/archive')
})

$('#view-add-order-rule').click(() => {
    location.replace(`/add-order-rule-page/${lastPathPart()}`)
})

$('#view-archive').click(() => {
    location.replace('/archive')
})

$('#view-categories').click(() => {
    location.replace('/categories')
})

$('#view-category').click((event) => {
    location.replace(`/category/${event.currentTarget.name}`)
})

$('#view-index').click(() => {
    location.replace('/')
})

$(() => {
    if (location.pathname === '/' && Cookies.get('password') !== undefined)
        location.replace('/archive')
})
