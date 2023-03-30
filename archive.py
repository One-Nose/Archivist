"""Access the database and make queries"""
from typing import TypedDict

from mariadb import Connection, connect
from mariadb.cursors import Cursor


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


class ArchiveConfig(TypedDict, total=False):
    """
    Configuration of the database
    - connect: Configuration of the connection to the database
    """
    connect: ConnectionConfig


class Archive:
    """Allows access to the database"""
    _database: Connection
    _cursor: Cursor

    def __init__(self, config: ArchiveConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """
        config_connect = config.get('connect', {})
        self._database = connect(
            user=config_connect.get('user'),
            password=config_connect.get('password'),
            database=config_connect.get('database'),
        )
        assert self._database is not None

        self._cursor = self._database.cursor()

    def create_tables(self) -> None:
        """Creates the required tables for the database"""
        # TODO: Implement function

    def exec(self, statement: str) -> None:
        """Executes an SQL statement"""
        self.cursor.execute(statement)
