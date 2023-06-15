"""Page to add an order rule to a category"""

from flask import Blueprint, render_template

from server.client import send

add_order_rule_page = Blueprint(
    'add_order_rule_page', __name__, template_folder='templates'
)


@add_order_rule_page.route('/<int:category_id>')
def show(category_id: int) -> str:
    """
    :param category_id: The category's ID
    :return: The add order rule page's HTML
    """

    category_details = send(
        {'message': 'get_category_and_properties', 'id': category_id}
    )

    return render_template(
        'add_order_rule.html',
        category_id=category_id,
        category_name=category_details['name'],
        properties=category_details['properties'],
    )
