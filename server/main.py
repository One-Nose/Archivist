"""The main executed file of the server program"""

from logging import INFO, basicConfig, info, error

from socket import gethostbyname, gaierror

from .client import connect, disconnect
from .server import start_server

basicConfig(format='[%(asctime)s] %(message)s', level=INFO, datefmt='%H:%M:%S')

try:
    host = gethostbyname(input('Enter host: '))
except gaierror:
    error('Could not find the host.')
else:
    key = input('Enter Key: ')

    try:
        connect(host, key)
    except ConnectionRefusedError:
        error('Could not connect')
    else:
        start_server()
        disconnect()
