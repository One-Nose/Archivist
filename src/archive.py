"""Access the database and make queries"""
from __future__ import annotations

from typing import Sequence, TypedDict

from mariadb import Connection, ProgrammingError, connect
from mariadb.cursors import Cursor


class ConnectionConfig(TypedDict):
    """
    Configuration of the connection to the database
    - user: The username to connect to the database
    - password: The password to connect to the database
    - database: The database to connect to
    """

    user: str
    password: str
    database: str


class ArchiveConfig(TypedDict):
    """
    Configuration of the database
    - connect: Configuration of the connection to the database
    """

    connect: ConnectionConfig


class Archive:
    """Allows access to the database"""

    _connect_options: ConnectionConfig
    _connection: Connection
    _cursor: Cursor

    def __init__(self, config: ArchiveConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """
        self._connect_options = config['connect']
        self.connect()

    def _create_table(self, name: str, columns: Sequence[tuple[str, str]]) -> None:
        """
        Creates a table
        :param name: The name of the table
        :param columns: A sequence of columns, each in the form of (name, type)
        """
        self._cursor.execute(
            f'CREATE TABLE {name} ({", ".join(" ".join(column) for column in columns)})'
        )

    def _use(self) -> None:
        """Sets the database as the connected database"""
        self._cursor.execute(f'USE {self._connect_options["database"]}')

    def commit(self) -> None:
        """Commits the changes to the database"""
        self._connection.commit()

    def connect(self) -> None:
        """Connects to the database, creates a cursor, and saves the connection and the cursor"""
        self._connection = connect(
            user=self._connect_options['user'],
            password=self._connect_options['password'],
        )
        self._cursor = self._connection.cursor()
        try:
            self._use()
        except ProgrammingError:
            self.init()

    def drop(self) -> None:
        """Deletes the database"""
        self._cursor.execute(f'DROP DATABASE {self._connect_options["database"]}')

    def init(self) -> None:
        """Creates the database and initializes it"""
        self._cursor.execute(f'CREATE DATABASE {self._connect_options["database"]}')
        self._use()

        self._create_table(
            'documents',
            (
                ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                ('name', 'VARCHAR(255) NOT NULL'),
                ('description', 'TEXT'),
            ),
        )

        self._create_table(
            'statements',
            (
                ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                ('document', 'INT NOT NULL'),
                ('type', 'ENUM("events") NOT NULL'),
                ('description', 'TEXT'),
            ),
        )

    def new_document(self, name: str, description: str | None = None) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :param description: An optional description
        :return: A document object to access the newly created document
        """
        self._cursor.execute(
            'INSERT INTO documents (name, description) VALUES (?, ?)',
            (name, description),
        )
        self._cursor.execute('SELECT LAST_INSERT_ID()')
        return Document(self._cursor.fetchone(), self._cursor)


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

    def add_statement(self, description: str | None = None) -> None:
        """
        Adds a statement to a document
        :param description: An optional description
        """
        self._cursor.execute(
            'INSERT INTO statements (document, description) VALUES (?, ?)',
            (self.id, description),
        )
