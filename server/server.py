"""Server running and utilities"""

from logging import info

from flask import Flask

from blueprints import (
    add_order_rule,
    add_order_rule_page,
    archive,
    categories,
    category,
    connect,
    index,
)

PORT = 8627


def _create_app() -> Flask:
    """Returns a new app."""

    app = Flask(__name__)
    app.register_blueprint(index)
    app.register_blueprint(add_order_rule_page, url_prefix='/add-order-rule-page')
    app.register_blueprint(archive, url_prefix='/archive')
    app.register_blueprint(categories, url_prefix='/categories')
    app.register_blueprint(category, url_prefix='/category')

    app.register_blueprint(add_order_rule, url_prefix='/add-order-rule')
    app.register_blueprint(connect, url_prefix='/connect')

    return app


def start_server() -> None:
    """Starts a server"""

    info('Starting server...')
    _create_app().run('0.0.0.0', PORT)
