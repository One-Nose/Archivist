"""The main executed file of the server program"""

from logging import INFO, basicConfig, info

from .client import connect, disconnect
from .server import start_server

basicConfig(format='[%(asctime)s] %(message)s', level=INFO, datefmt='%H:%M:%S')

try:
    connect()
except ConnectionRefusedError:
    info('Could not connect')
else:
    start_server()
    disconnect()
