"""Server running and utilities"""

from logging import info

from flask import Flask

PORT = 8627


def _create_app() -> Flask:
    """Returns a new app."""

    app = Flask(__name__)
    app.register_blueprint(index)

    return app


def start_server() -> None:
    """Starts a server"""

    info('Starting server...')
    _create_app().run('0.0.0.0', PORT)
