"""Page to add an order to a document"""

from flask import Blueprint, render_template

from server.client import send

add_order_page = Blueprint('add_order_page', __name__, template_folder='templates')


@add_order_page.route('/<int:document_id>')
def show(document_id: int) -> str:
    """
    :param document_id: The document's ID
    :return: The add order page's HTML
    """

    document_details = send({'message': 'get_document_and_points', 'id': document_id})

    return render_template(
        'add_order.html',
        document_id=document_id,
        document_name=document_details['name'],
        points=document_details['points'],
    )
