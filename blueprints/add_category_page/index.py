"""Page to add a category"""

from flask import Blueprint, render_template

add_category_page = Blueprint(
    'add_category_page', __name__, template_folder='templates'
)


@add_category_page.route('/')
def show() -> str:
    """:return: The add category page's HTML"""

    return render_template('add_category.html')
