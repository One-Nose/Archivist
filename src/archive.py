"""Access the database and make queries"""
from typing import Sequence, TypedDict

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

    def _create_table(self, name: str, columns: Sequence[tuple[str, str]]) -> None:
        """
        Creates a table
        :param name: The name of the table
        :param columns: A sequence of columns, each in the form of (name, type)
        """
        self._cursor.execute(
            f'CREATE TABLE {name} ({", ".join(" ".join(column) for column in columns)})'
        )

    def create_document(self, name: str, description: str = None) -> None:
        """
        Creates a document
        :param name: The name of the document
        :param description: An optional description
        """
        self._cursor.execute('INSERT INTO documents (NAME, DESCRIPTION) VALUES (?, ?)', (name, description))

    def init(self) -> None:
        """Creates the required tables for the database"""

        self._create_table('documents', (
            ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
            ('name', 'VARCHAR(255) NOT NULL'),
            ('description', 'TEXT'),
        ))

        self._create_table('statements', (
            ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
            ('document', 'INT NOT NULL'),
            ('description', 'TEXT'),
        ))
