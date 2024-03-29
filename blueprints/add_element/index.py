"""Recieves POST requests to add an element"""

from flask import Blueprint, request

from server.client import send

add_element = Blueprint('add_element', __name__)


@add_element.post('/')
def post() -> dict[str, bool]:
    """
    Adds an element
    :return: {'success': bool}
    """

    return {
        'success': send(
            {
                'message': 'add_element',
                'password': request.cookies['password'],
                'category': request.json['category'],
            }
        )['success']
    }
