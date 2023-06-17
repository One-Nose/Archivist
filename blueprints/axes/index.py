"""The website's axes page"""

from flask import Blueprint, render_template

from server.client import send

axes = Blueprint('axes', __name__, template_folder='templates')


@axes.route('/')
def show() -> str:
    """:return: The axes page HTML"""

    return render_template('axes.html', axes=send({'message': 'get_axes'})['axes'])
