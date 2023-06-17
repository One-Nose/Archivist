"""The website's documents page"""

from flask import Blueprint, render_template

from server.client import send

documents = Blueprint('documents', __name__, template_folder='templates')


@documents.route('/')
def show() -> str:
    """:return: The documents page HTML"""

    return render_template(
        'documents.html', documents=send({'message': 'get_documents'})['documents']
    )
