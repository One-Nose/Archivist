"""A socket client to connect to the main app"""

from json import loads
from logging import info
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from typing import Any

PORT = 8626


def connect() -> None:
    """Connects to the archive"""

    with socket(AF_INET, SOCK_STREAM) as client:
        client.connect((gethostname(), PORT))
        message = recieve(client)
        assert message['message'] == 'connection'
        info('Connected to archive')
        if message['connected']:
            info('Connected to database')
        else:
            info('Connecting to database...')
            message = recieve(client)
            if message['message'] == 'connection' and message['connected']:
                info('Connected to database')


def recieve(client: socket) -> dict[str, Any]:
    """
    Recieves JSON data
    :param client: The socket to listen to data
    :return: The data
    """

    return loads(client.recv(1024))
