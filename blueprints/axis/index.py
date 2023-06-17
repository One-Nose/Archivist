"""An axis's page"""

from flask import Blueprint, render_template

from server.client import send

axis = Blueprint('axis', __name__, template_folder='templates')


@axis.route('/<int:axis_id>')
def show(axis_id: int) -> str:
    """
    :param axis_id: The axis's ID
    :return: The axis page HTML
    """

    return render_template(
        'axis.html',
        id=axis_id,
        points=send({'message': 'get_axis', 'id': axis_id})['points'],
    )
