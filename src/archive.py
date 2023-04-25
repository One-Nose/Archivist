"""Access the database and make queries"""
from __future__ import annotations

from typing import TypedDict

from mariadb import Connection, ProgrammingError, connect
from mariadb.cursors import Cursor


class ConnectionConfig(TypedDict):
    """
    Configuration of the connection to the database
    - user: The username to connect to the database
    - password: The password to connect to the database
    - database: The database to connect to (insecure)
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

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self._connect_options["database"])})'

    def _create_table(self, table: str, **columns: str) -> None:
        """
        Creates a table (insecure)
        :param table: The name of the table
        :param columns: A sequence of columns, each in the form of name=type
        """
        self._cursor.execute(
            f'CREATE TABLE {table} ({", ".join(" ".join(column) for column in columns.items())})'
        )

    def _use(self) -> None:
        """Sets the database as the connected database"""
        self._cursor.execute(f'USE {self._connect_options["database"]}')

    def close(self) -> None:
        """Closes the connection"""
        self._cursor.close()
        self._connection.close()

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

    def document(self, document_id: int) -> Document:
        """
        Creates a document object to access an existing document
        :param document_id: The document's numeral ID
        :return: A document object that allows access to the document
        """

        return Document(self, document_id)

    def drop(self) -> None:
        """Deletes the database"""
        self._cursor.execute(f'DROP DATABASE {self._connect_options["database"]}')

    def init(self) -> None:
        """Creates the database and initializes it"""
        self._cursor.execute(f'CREATE DATABASE {self._connect_options["database"]}')
        self._use()

        self._create_table(
            'declarations',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            document='INT NOT NULL',
            element_type='INT NOT NULL',
        )

        self._create_table(
            'documents',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            name='VARCHAR(255) NOT NULL',
        )

        self._create_table(
            'element_types',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            name='VARCHAR(255) NOT NULL',
        )

        self._create_table(
            'element_type_properties',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            element_type='INT NOT NULL',
            name='VARCHAR(255)',
        )

    def insert(self, table: str, **values: ...) -> None:
        """
        Inserts values into a table (insecure)
        :param table: The table to insert to
        :param values: The values to insert in the form of column=value
        """
        self._cursor.execute(
            f'INSERT INTO {table} ({", ".join(values)}) VALUES ({", ".join("?" for _ in values)})',
            tuple(values.values()),
        )

    def new_document(self, name: str) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :return: A document object to access the newly created document
        """
        self.insert('documents', name=name)
        self._cursor.execute('SELECT LAST_INSERT_ID()')
        return Document(self, self._cursor.fetchone()[0])

    def reset(self) -> None:
        """Completely resets the database"""
        self.drop()
        self.init()


class Document:
    """Allows access to a document"""

    _archive: Archive
    id: int

    def __init__(self, archive: Archive, document_id: int) -> None:
        """
        Creates a document object to access a document
        :param archive: The document's archive
        :param document_id: The document's ID
        """
        self.id = document_id
        self._archive = archive

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.id)})'

    def declare(self, element_type: int) -> None:
        """Adds a declaration to the document"""
        self._archive.insert(
            'declarations', document=self.id, element_type=element_type
        )
