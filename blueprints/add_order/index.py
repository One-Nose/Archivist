"""Recieves POST requests to add an order"""

from flask import Blueprint, request

from server.client import send

add_order = Blueprint('add_order', __name__)


@add_order.post('/')
def post() -> dict[str, bool]:
    """
    Adds an order
    :return: {'success': bool}
    """

    return {
        'success': send(
            {
                'message': 'add_order',
                'password': request.cookies['password'],
                'document': request.json['document'],
                'large': request.json['large'],
                'small': request.json['small'],
            }
        )['success']
    }
