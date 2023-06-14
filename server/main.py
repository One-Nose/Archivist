"""The main executed file of the server program"""

from logging import INFO, basicConfig

from .client import connect, disconnect
from .server import start_server

basicConfig(format='[%(asctime)s] %(message)s', level=INFO, datefmt='%H:%M:%S')

connect()
start_server()
disconnect()
