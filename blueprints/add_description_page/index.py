"""Page to add a description to an element"""

from flask import Blueprint, render_template

from server.client import send

add_description_page = Blueprint(
    'add_description_page', __name__, template_folder='templates'
)


@add_description_page.route('/<int:document_id>')
def show(document_id: int) -> str:
    """
    :param document_id: The document's ID
    :return: The add description page's HTML
    """

    document_details = send({'message': 'get_document_and_elements', 'id': document_id})

    return render_template(
        'add_description.html',
        document_id=document_id,
        document_name=document_details['name'],
        elements=document_details['elements'],
    )
