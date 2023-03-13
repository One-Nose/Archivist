"""The website's main page"""
from flask import Blueprint, render_template

index = Blueprint('index', __name__, template_folder='templates')


@index.route('/')
def show() -> str:
    """:return: The website's main page HTML"""
    return render_template('index.html')
