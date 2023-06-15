"""A category's page"""

from flask import Blueprint, render_template

from server.client import send

category = Blueprint('category', __name__, template_folder='templates')


@category.route('/<int:category_id>')
def show(category_id: int) -> str:
    """
    :param category_id: he category's ID
    :return: The category page HTML
    """

    category_details = send({'message': 'get_category', 'id': category_id})

    return render_template(
        'category.html',
        name=category_details['name'],
        properties=', '.join(category_details['properties']),
        order_rules=category_details['order_rules'],
    )
