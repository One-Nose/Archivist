"""Recieves POST requests to add an order rule"""

from typing import Any

from flask import Blueprint, request

from server.client import send

add_order_rule = Blueprint('add_order_rule', __name__)


@add_order_rule.post('/')
def post() -> dict[str, bool]:
    """
    Adds an order rule
    :return: {'success': bool}
    """

    large: Any = request.form['large']
    small: Any = request.form['small']

    return {
        'success': send(
            {
                'message': 'add_order_rule',
                'password': request.cookies['password'],
                'large': int(large),
                'small': int(small),
            }
        )['success']
    }
