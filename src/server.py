"""A socket server that connects to the web server"""

from json import dumps, loads
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from time import sleep
from typing import Any

from cryptography.fernet import Fernet
from mariadb import Error as MariaDBError

from .interface import window
from .registry import generate_key, get_archive_password, get_database, get_key

PORT = 8626


def handle(connection: socket, data: bytes) -> None:
    """
    Handles a recieved message
    :param connection: The socket to use to handle the message
    :param data: The recieved data
    """

    message: dict[str, Any] = loads(data)

    response: dict[str, Any] = {'message': 'response', 'response': message['message']}

    if 'password' in message:
        message['password'] = fernet.decrypt(message['password']).decode()

    try:
        match message['message']:
            case 'add_category':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        category = window.archive.new_category(message['name'])
                        for property_name in message['properties']:
                            category.new_property(property_name)
                        window.archive.commit()
                    except MariaDBError:
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'add_description':
                success = True
                if message['password'] == get_archive_password():
                    assert isinstance(message['document'], int)
                    assert isinstance(message['element'], int)
                    try:
                        window.archive.document(
                            message['document']
                        ).declare_description(
                            window.archive.element(message['element']),
                            message['description'],
                        )
                        window.archive.commit()
                    except (MariaDBError, AssertionError):
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'add_document':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        window.archive.new_document(message['name'])
                        window.archive.commit()
                    except MariaDBError:
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'add_element':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        assert isinstance(message['category'], int)
                        window.archive.new_element(
                            window.archive.category(message['category'])
                        )
                        window.archive.commit()
                    except (MariaDBError, AssertionError):
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'add_order':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        assert isinstance(message['document'], int)
                        assert isinstance(message['large'], int)
                        assert isinstance(message['small'], int)
                        window.archive.document(message['document']).declare_order(
                            window.archive.point(message['large']),
                            window.archive.point(message['small']),
                        )
                        window.archive.commit()
                    except (MariaDBError, AssertionError):
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'add_order_rule':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        assert isinstance(message['large'], int)
                        assert isinstance(message['small'], int)
                        window.archive.add_order_rule(
                            window.archive.property(message['large']),
                            window.archive.property(message['small']),
                        )
                        window.archive.commit()
                    except (MariaDBError, AssertionError):
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'analyze':
                success = True
                if message['password'] == get_archive_password():
                    try:
                        window.archive.analyze_rules()
                        window.archive.commit()
                    except MariaDBError:
                        success = False
                else:
                    success = False
                response.update({'success': success})
            case 'connect_user':
                response.update(
                    {'success': message['password'] == get_archive_password()}
                )
            case 'get_axes':
                response.update({'axes': window.archive.get_axes()})
            case 'get_axis':
                assert isinstance(message['id'], int)
                response.update({'points': window.archive.get_axis(message['id'])})
            case 'get_categories':
                response.update({'categories': window.archive.get_categories()})
            case 'get_category':
                assert isinstance(message['id'], int)
                category = window.archive.category(message['id'])
                response.update(
                    {
                        'name': category.get_name(),
                        'properties': category.get_property_names(),
                        'order_rules': category.get_order_rules(),
                    }
                )
            case 'get_category_and_elements':
                assert isinstance(message['id'], int)
                category = window.archive.category(message['id'])
                response.update(
                    {'name': category.get_name(), 'elements': category.get_elements()}
                )
            case 'get_category_and_properties':
                assert isinstance(message['id'], int)
                category = window.archive.category(message['id'])
                response.update(
                    {
                        'name': category.get_name(),
                        'properties': category.get_properties(),
                    }
                )
            case 'get_database_name':
                response.update({'name': get_database()})
            case 'get_document':
                document = window.archive.document(message['id'])
                response.update(
                    {
                        'name': document.get_name(),
                        'orders': document.get_orders(),
                    }
                )
            case 'get_document_and_elements':
                assert isinstance(message['id'], int)
                response.update(
                    {
                        'name': window.archive.document(message['id']).get_name(),
                        'elements': window.archive.get_elements(),
                    }
                )
            case 'get_document_and_points':
                assert isinstance(message['id'], int)
                response.update(
                    {
                        'name': window.archive.document(message['id']).get_name(),
                        'points': window.archive.get_points(),
                    }
                )
            case 'get_documents':
                response.update({'documents': window.archive.get_documents()})
            case _:
                pass
    except MariaDBError:
        pass

    connection.sendall(dumps(response).encode())


def listen() -> None:
    """Starts a server and listens"""
    global fernet

    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((gethostname(), PORT))
        server.listen()
        while True:
            generate_key()
            fernet = Fernet(get_key())
            connection = server.accept()[0]
            with connection:
                send(
                    connection,
                    {'message': 'connection', 'connected': window.archive.connected},
                )
                if not window.archive.connected:
                    while not window.archive.connected:
                        sleep(1)
                    send(connection, {'message': 'connection', 'connected': True})

                try:
                    while data := connection.recv(1024):
                        handle(connection, data)

                except ConnectionResetError:
                    pass


def send(connection: socket, data: dict[str, Any]) -> None:
    """
    Sends data via sockets
    :param connection: The socket to send the data through
    :param data: The data to send
    """

    connection.sendall(dumps(data).encode())
