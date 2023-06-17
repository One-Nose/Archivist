"""Recieves POST requests to add a category"""

from flask import Blueprint, request

from server.client import send

add_category = Blueprint('add_category', __name__)


@add_category.post('/')
def post() -> dict[str, bool]:
    """
    Adds an element
    :return: {'success': bool}
    """

    print()
    return {
        'success': send(
            {
                'message': 'add_category',
                'password': request.cookies['password'],
                'name': request.json['name'],
                'properties': request.json['properties'],
            }
        )['success']
    }
