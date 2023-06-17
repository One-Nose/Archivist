function lastPathPart() {
    return location.pathname.match(/\/([^/]+)$/)[1]
}

function post(url, data, success) {
    $.post({
        url: url,
        data: JSON.stringify(data),
        success: success,
        contentType: 'Application/JSON',
        error: () => {
            alert('An error has occurred.')
        },
    })
}

$('#add-category').click(() => {
    const name = $('#category-name').val()
    if (name === '') alert('Please enter a category name.')
    else
        post(
            '/add-category',
            {
                name: name,
                properties: $('#properties text')
                    .map((_, text) => text.textContent)
                    .get(),
            },
            (data) => {
                if (data.success) $('#view-categories').click()
                else alert('Could not add category.')
            }
        )
})

$('.add-description').click((event) => {
    const description = $('textarea').val()
    if (description === '') alert('Please enter a description.')
    else
        post(
            '/add-description',
            {
                document: parseInt(lastPathPart()),
                element: parseInt(event.currentTarget.value),
                description: description,
            },
            (data) => {
                if (data.success) {
                    alert('Added description.')
                    $('.view-document').click()
                } else alert('Could not add the description.')
            }
        )
})

$('#add-document').click(() => {
    const name = $('#document-name').val()
    if (name === '') alert('Please enter a document name.')
    else
        post('/add-document', { name: name }, (data) => {
            if (data.success) $('#view-documents').click()
            else alert('Could not add document.')
        })
})

$('#add-element').click(() => {
    post('/add-element', { category: parseInt(lastPathPart()) }, (data) => {
        if (data.success) location.reload()
        else alert('Could not add the element.')
    })
})

$('#add-order').click(() => {
    const large = parseInt($('input[name="large"]:checked').val())
    const small = parseInt($('input[name="small"]:checked').val())

    if (isNaN(large) || isNaN(small))
        alert('Please choose a large point and a small point.')
    else if (large === small) alert('Please choose different points.')
    else
        post(
            '/add-order',
            {
                document: parseInt(lastPathPart()),
                large: large,
                small: small,
            },
            (data) => {
                if (data.success) $('.view-document').click()
                else alert('Could not add the order.')
            }
        )
})

$('#add-order-rule').click(() => {
    const large = $('#select-large').val()
    const small = $('#select-small').val()

    if (large === '' || small === '') alert('Please choose two properties.')
    else if (large === small) alert('Please choose different properties.')
    else
        post(
            '/add-order-rule',
            { large: parseInt(large), small: parseInt(small) },
            (data) => {
                if (data.success) {
                    alert('Order rule added successfully.')
                    $('.view-category').click()
                } else alert('Could not add order rule.')
            }
        )
})

$('#add-property').click(() => {
    const propertyNameInput = $('#property-name')
    const propertyName = propertyNameInput.val()

    if (propertyName !== '') {
        $('#properties').append('<div><text></text><button>-</button></div>')
        const div = $('#properties div').last()

        $('text', div).text(propertyName)

        $('button', div).click(() => {
            div.remove()
        })

        propertyNameInput.val('')
    }
})

$('#analyze').click(() => {
    post('/analyze', {}, (data) => {
        if (data.success) {
            alert('Analyzed archive.')
            location.reload()
        } else alert('Could not analyze the archive.')
    })
})

$('#connect-button').click(() => {
    const connectPassword = $('#connect-password')
    const password = connectPassword.val()
    post('/connect', { password: password }, (data) => {
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

$('#view-add-category').click(() => {
    location.replace('/add-category-page')
})

$('#view-add-description').click(() => {
    location.replace(`/add-description-page/${lastPathPart()}`)
})

$('#view-add-document').click(() => {
    location.replace('/add-document-page')
})

$('#view-add-order').click(() => {
    location.replace(`/add-order-page/${lastPathPart()}`)
})

$('#view-add-order-rule').click(() => {
    location.replace(`/add-order-rule-page/${lastPathPart()}`)
})

$('#view-archive').click(() => {
    location.replace('/archive')
})

$('#view-axes').click(() => {
    location.replace('/axes')
})

$('.view-axis').click((event) => {
    location.replace(`/axis/${event.currentTarget.value}`)
})

$('#view-categories').click(() => {
    location.replace('/categories')
})

$('.view-category').click((event) => {
    location.replace(`/category/${event.currentTarget.value}`)
})

$('.view-document').click((event) => {
    location.replace(`/document/${event.currentTarget.value}`)
})

$('#view-documents').click(() => {
    location.replace('/documents')
})

$('#view-elements').click(() => {
    location.replace(`/elements/${lastPathPart()}`)
})

$('#view-index').click(() => {
    location.replace('/')
})

$(() => {
    if (location.pathname === '/' && Cookies.get('password') !== undefined)
        location.replace('/archive')
})
