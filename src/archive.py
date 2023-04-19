"""Access the database and make queries"""
from __future__ import annotations

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

    def commit(self) -> None:
        """Commits the changes to the database"""
        self._database.commit()

    def new_document(self, name: str, description: str = None) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :param description: An optional description
        :return: A document object to access the newly created document
        """
        self._cursor.execute('INSERT INTO documents (name, description) VALUES (?, ?)', (name, description))
        self._cursor.execute('SELECT LAST_INSERT_ID()')
        return Document(self._cursor.fetchone(), self._cursor)

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


class Document:
    """Allows access to a document"""
    _cursor: Cursor
    id: int

    def __init__(self, document_id: int, cursor: Cursor) -> None:
        """
        Creates a document object to access a document
        :param document_id: The document's ID
        :param cursor: The archive's cursor
        """
        self.id = document_id
        self._cursor = cursor

        print(document_id)

    def add_statement(self, description: str = None) -> None:
        """
        Adds a statement to a document
        :param description: An optional description
        """
        self._cursor.execute('INSERT INTO statements (document, description) VALUES (?, ?)', (self.id, description))
