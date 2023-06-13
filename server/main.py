"""The main executed file of the server program"""

from logging import INFO, basicConfig, info

from .client import connect

basicConfig(format='[%(asctime)s] %(message)s', level=INFO, datefmt='%H:%M:%S')

info('Connecting to archive...')
connect()
