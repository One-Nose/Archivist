"""Page to add a document"""

from flask import Blueprint, render_template

add_document_page = Blueprint(
    'add_document_page', __name__, template_folder='templates'
)


@add_document_page.route('/')
def show() -> str:
    """:return: The add document page's HTML"""

    return render_template('add_document.html')
