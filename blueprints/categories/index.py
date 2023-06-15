"""The website's main page"""

from flask import Blueprint, render_template

from server.client import send

categories = Blueprint('categories', __name__, template_folder='templates')


@categories.route('/')
def show() -> str:
    """:return: The categories page HTML"""

    return render_template(
        'categories.html', categories=send({'message': 'get_categories'})['categories']
    )
