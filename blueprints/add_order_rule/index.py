"""Recieves POST requests to add an order rule"""

from flask import Blueprint, request

from server.client import send

add_order_rule = Blueprint('add_order_rule', __name__)


@add_order_rule.post('/')
def post() -> dict[str, bool]:
    """
    Adds an order rule
    :return: {'success': bool}
    """

    return {
        'success': send(
            {
                'message': 'add_order_rule',
                'password': request.cookies.get('password'),
                'large': request.form['large'],
                'small': request.form['small'],
            }
        )['success']
    }
