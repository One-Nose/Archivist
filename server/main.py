"""The main executed file of the server program"""

from logging import INFO, basicConfig

from .client import connect, disconnect

basicConfig(format='[%(asctime)s] %(message)s', level=INFO, datefmt='%H:%M:%S')

connect()
disconnect()
