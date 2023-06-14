"""Server running and utilities"""

from logging import info

from flask import Flask

from blueprints import connect, index

PORT = 8627


def _create_app() -> Flask:
    """Returns a new app."""

    app = Flask(__name__)
    app.register_blueprint(index)
    app.register_blueprint(connect, url_prefix='/connect')

    return app


def start_server() -> None:
    """Starts a server"""

    info('Starting server...')
    _create_app().run('0.0.0.0', PORT)
