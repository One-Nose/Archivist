"""Access the database and make queries"""
from typing import TypedDict

from MySQLdb import connect  # type: ignore[ads]
from MySQLdb import Connection
from MySQLdb.cursors import Cursor


class ConnectionConfig(TypedDict, total=False):
    """
    Configuration of the connection to the database
    - user: The username to connect to the database
    - password: The password to connect to the database
    - database: The database to connect to
    """
    user: str
    password: str
    database: str


class DatabaseConfig(TypedDict, total=False):
    """
    Configuration of the database
    - connect: Configuration of the connection to the database
    """
    connect: ConnectionConfig


class Database:
    """Allows access to the database"""
    database: Connection
    cursor: Cursor

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """
        config_connect = config.get('connect', {})
        self.database = connect(
            user=config_connect.get('user'),
            password=config_connect.get('password'),
            database=config_connect.get('database'),
        )
        self.cursor = self.database.cursor()  # type: ignore

    def create_tables(self) -> None:
        """Creates the required tables for the database"""
        # TODO: Implement function
