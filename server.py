"""Server running and utilities"""
from flask import Flask

from blueprints import index


def create_app() -> Flask:
    """Returns a new app."""

    app = Flask(__name__)
    app.register_blueprint(index)

    return app


def start_server() -> None:
    """Starts a server"""

    create_app().run('127.0.0.1', 8080, debug=True)
