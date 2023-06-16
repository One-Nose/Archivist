"""A category's elements page"""

from flask import Blueprint, render_template

from server.client import send

elements = Blueprint('elements', __name__, template_folder='templates')


@elements.route('/<int:category_id>')
def show(category_id: int) -> str:
    """
    :param category_id: The category's ID
    :return: The category elements page HTML
    """

    category_details = send({'message': 'get_category_and_elements', 'id': category_id})

    return render_template(
        'elements.html',
        category_id=category_id,
        name=category_details['name'],
        elements=category_details['elements'],
    )
