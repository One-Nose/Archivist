"""The root file of the program"""
from database import Database
from server import start_server

if __name__ == '__main__':
    database = Database({'connect': {'user': 'root', 'password': 'root', 'database': 'archivist'}})
    print(database.get_tables())

    start_server()
