"""A socket server that connects to the web server"""

from json import dumps
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from time import sleep
from typing import Any

from .interface import window

PORT = 8626


def listen() -> None:
    """Starts a server and listens"""

    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((gethostname(), PORT))
        server.listen()
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


def send(connection: socket, data: dict[str, Any]) -> None:
    """
    Sends data via sockets
    :param connection: The socket to send the data through
    :param data: The data to send
    """

    connection.sendall(dumps(data).encode())
