"""A socket server that connects to the web server"""

from json import dumps, loads
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from time import sleep
from typing import Any

from .interface import window
from .registry import get_archive_password

PORT = 8626


def handle(connection: socket, data: bytes) -> None:
    """
    Handles a recieved message
    :param connection: The socket to use to handle the message
    :param data: The recieved data
    """

    message: dict[str, Any] = loads(data)

    response: dict[str, Any] = {'message': 'response', 'response': message['message']}

    if message['message'] == 'connect_user':
        response.update({'success': message['password'] == get_archive_password()})
    else:
        raise ValueError

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
