"""Recieves POST requests to add a document"""

from flask import Blueprint, request

from server.client import send

add_document = Blueprint('add_document', __name__)


@add_document.post('/')
def post() -> dict[str, bool]:
    """
    Adds a document
    :return: {'success': bool}
    """

    return {
        'success': send(
            {
                'message': 'add_document',
                'password': request.cookies['password'],
                'name': request.json['name'],
            }
        )['success']
    }
