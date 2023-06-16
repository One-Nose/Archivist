"""Recieves POST requests to add an order rule"""

from typing import Any
from flask import Blueprint, request

from server.client import send

add_element = Blueprint('add_element', __name__)


@add_element.post('/')
def post() -> dict[str, bool]:
    """
    Adds an order rule
    :return: {'success': bool}
    """

    category: Any = request.form['category']

    return {
        'success': send(
            {
                'message': 'add_element',
                'password': request.cookies['password'],
                'category': int(category),
            }
        )['success']
    }
