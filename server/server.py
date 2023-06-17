"""Server running and utilities"""

from logging import info

from flask import Flask

from blueprints import (
    add_category,
    add_category_page,
    add_description,
    add_description_page,
    add_document,
    add_document_page,
    add_element,
    add_order,
    add_order_page,
    add_order_rule,
    add_order_rule_page,
    analyze,
    archive,
    axes,
    axis,
    categories,
    category,
    connect,
    document,
    documents,
    elements,
    index,
)

PORT = 8627


def _create_app() -> Flask:
    """Returns a new app."""

    app = Flask(__name__)
    app.register_blueprint(index)
    app.register_blueprint(add_category_page, url_prefix='/add-category-page')
    app.register_blueprint(add_description_page, url_prefix='/add-description-page')
    app.register_blueprint(add_document_page, url_prefix='/add-document-page')
    app.register_blueprint(add_order_page, url_prefix='/add-order-page')
    app.register_blueprint(add_order_rule_page, url_prefix='/add-order-rule-page')
    app.register_blueprint(archive, url_prefix='/archive')
    app.register_blueprint(axes, url_prefix='/axes')
    app.register_blueprint(axis, url_prefix='/axis')
    app.register_blueprint(categories, url_prefix='/categories')
    app.register_blueprint(category, url_prefix='/category')
    app.register_blueprint(document, url_prefix='/document')
    app.register_blueprint(documents, url_prefix='/documents')
    app.register_blueprint(elements, url_prefix='/elements')

    app.register_blueprint(add_category, url_prefix='/add-category')
    app.register_blueprint(add_description, url_prefix='/add-description')
    app.register_blueprint(add_document, url_prefix='/add-document')
    app.register_blueprint(add_element, url_prefix='/add-element')
    app.register_blueprint(add_order, url_prefix='/add-order')
    app.register_blueprint(add_order_rule, url_prefix='/add-order-rule')
    app.register_blueprint(analyze, url_prefix='/analyze')
    app.register_blueprint(connect, url_prefix='/connect')

    return app


def start_server() -> None:
    """Starts a server"""

    info('Starting server...')
    _create_app().run('0.0.0.0', PORT)
