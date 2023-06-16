"""A socket server that connects to the web server"""

from json import dumps, loads
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from time import sleep
from typing import Any

from mariadb import Error

from .interface import window
from .registry import get_archive_password, get_database

PORT = 8626


def handle(connection: socket, data: bytes) -> None:
    """
    Handles a recieved message
    :param connection: The socket to use to handle the message
    :param data: The recieved data
    """

    message: dict[str, Any] = loads(data)

    response: dict[str, Any] = {'message': 'response', 'response': message['message']}

    match message['message']:
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
                except (Error, AssertionError):
                    success = False
            else:
                success = False
            response.update({'success': success})
        case 'connect_user':
            response.update({'success': message['password'] == get_archive_password()})
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
                {'name': category.get_name(), 'properties': category.get_properties()}
            )
        case 'get_database_name':
            response.update({'name': get_database()})
        case _:
            pass

    connection.sendall(dumps(response).encode())


def listen() -> None:
    """Starts a server and listens"""

    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((gethostname(), PORT))
        server.listen()
        while True:
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
