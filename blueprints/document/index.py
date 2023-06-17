"""A document's page"""

from flask import Blueprint, render_template

from server.client import send

document = Blueprint('document', __name__, template_folder='templates')


@document.route('/<int:document_id>')
def show(document_id: int) -> str:
    """
    :param document_id: The document's ID
    :return: The document page HTML
    """

    document_details = send({'message': 'get_document', 'id': document_id})

    return render_template(
        'document.html',
        name=document_details['name'],
        orders=document_details['orders'],
    )
