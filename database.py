"""Access the database and make queries"""
from collections.abc import Sequence
from typing import TypedDict

from MySQLdb import connect, Connection
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
        self.cursor = self.database.cursor()

    def create_table(self, table: str, columns: Sequence[tuple[str, str]]) -> None:
        """
        Creates a table
        :param columns: The columns of the table. Each column is in the form of (name, type)
        :param table: The name of the table
        """
        self.cursor.execute(f"""CREATE TABLE %s ({'%s %s, ' * len(columns)});""", (table, *[*columns]))

    def create_tables(self) -> None:
        """Creates the required tables for the database"""
        # TODO: Implement function
