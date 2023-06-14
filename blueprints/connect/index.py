"""Recieves POST requests to connect to the archive"""

from flask import Blueprint, request

from server.client import send

connect = Blueprint('connect', __name__)


@connect.post('/')
def post() -> dict[str, bool]:
    """
    Connects the user to the archive
    :return: {'success': bool}
    """

    return {
        'success': send(
            {'message': 'connect_user', 'password': request.form['password']}
        )['success']
    }
