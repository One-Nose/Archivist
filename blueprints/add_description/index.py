"""Recieves POST requests to add a description"""

from flask import Blueprint, request

from server.client import send

add_description = Blueprint('add_description', __name__)


@add_description.post('/')
def post() -> dict[str, bool]:
    """
    Adds a description
    :return: {'success': bool}
    """

    return {
        'success': send(
            {
                'message': 'add_description',
                'password': request.cookies['password'],
                'document': request.json['document'],
                'element': request.json['element'],
                'description': request.json['description'],
            }
        )['success']
    }
