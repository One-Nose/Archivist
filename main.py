"""The root file of the program"""
from json import load

from database import Database
# from server import start_server

if __name__ == '__main__':
    with open('config.json') as file:
        config = load(file)

    database = Database(config)

    # start_server()
