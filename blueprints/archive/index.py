"""The archive screen"""

from flask import Blueprint, render_template, request

from server.client import send

archive = Blueprint('archive', __name__, template_folder='templates')


@archive.route('/')
def show() -> str:
    """:return: The archive screen's HTML"""

    return render_template(
        'archive.html',
        archive_name=send({'message': 'get_database_name'})['name'],
        connected=request.cookies.get('password') is not None,
    )
