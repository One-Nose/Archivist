"""Recieves POST requests to analyze the archive"""

from flask import Blueprint, request

from server.client import send

analyze = Blueprint('analyze', __name__)


@analyze.post('/')
def post() -> dict[str, bool]:
    """
    Analyzes the archive
    :return: {'success': bool}
    """

    return {
        'success': send(
            {'message': 'analyze', 'password': request.cookies['password']}
        )['success']
    }
