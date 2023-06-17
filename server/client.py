"""A socket client to connect to the main app"""

from json import dumps, loads
from logging import info
from socket import AF_INET, SOCK_STREAM, gethostname, socket
from typing import Any

PORT = 8626


def connect(host: str) -> None:
    """
    Connects to the archive
    :param host: The host to connect to
    """

    info('Connecting to archive...')
    client.connect((host, PORT))
    message = recieve()
    assert message['message'] == 'connection'
    info('Connected to archive')
    if not message['connected']:
        info('Connecting to database...')
        message = recieve()
        assert message['message'] == 'connection' and message['connected']
    info('Connected to database')


def disconnect() -> None:
    """Closes the connection"""

    info('Disconnecting...')
    client.close()
    info('Disconnected')


def recieve() -> dict[str, Any]:
    """
    Recieves JSON data
    :return: The data
    """

    data = client.recv(2**16)
    return loads(data)


def send(message: dict[str, Any]) -> dict[str, Any]:
    """
    Sends a message to the archive and awaits the response
    :param message: The message to send
    :return: The response
    """

    client.sendall(dumps(message).encode())
    data = recieve()
    assert data['message'] == 'response' and data['response'] == message['message']
    return data


client = socket(AF_INET, SOCK_STREAM)
