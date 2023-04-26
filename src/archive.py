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

    def element_type(self, type_id: int) -> ElementType:
        """
        Creates an element type object to access an existing element type
        :param type_id: The element type's numeral ID
        :return: An element type object that allows access to the element type
        """

        return ElementType(self, type_id)

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
            'element_type_properties',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            element_type='INT NOT NULL',
            name='VARCHAR(255) NOT NULL',
        )

        self._create_table(
            'element_types',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            name='VARCHAR(255) NOT NULL',
        )

        self._create_table(
            'relation_types',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            element_type='INT NOT NULL',
            description='VARCHAR(255) NOT NULL',
            target_element_type='INT NOT NULL',
        )

        self._create_table(
            'relations',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            type='INT NOT NULL',
            declaration='INT NOT NULL',
            target_declaration='INT NOT NULL',
        )

        self._create_table(
            'titles',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            declaration='INT NOT NULL',
            title='VARCHAR(255) NOT NULL',
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

    def last_id(self) -> int:
        """
        Gets the ID of the last inserted row
        :return: The row's ID
        """

        self._cursor.execute('SELECT LAST_INSERT_ID()')
        return self._cursor.fetchone()[0]

    def new_document(self, name: str) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :return: A document object to access the newly created document
        """

        self.insert('documents', name=name)
        return Document(self, self.last_id())

    def new_element_type(self, name: str) -> ElementType:
        """
        Creates a new element type
        :param name: The name of the element type
        :return: An element type object to access the newly created element type
        """

        self.insert('element_types', name=name)
        return ElementType(self, self.last_id())

    def reset(self) -> None:
        """Completely resets the database"""

        self.drop()
        self.init()


class ArchiveProxy:
    """Interface to allow access to part of an archive"""

    _archive: Archive
    id: int

    def __init__(self, archive: Archive, identifier: int) -> None:
        """
        Creates a proxy object to access a part of an archive
        :param archive: The proxy's archive
        :param identifier: Numeral ID of the part the proxy points towards
        """

        self._archive = archive
        self.id = identifier

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.id)})'


class Declaration(ArchiveProxy):
    """Allows access to a declaration"""

    def add_title(self, title: str) -> None:
        """
        Adds a title to the declaration
        :param title: The title to add
        """

        self._archive.insert('titles', declaration=self.id, title=title)


class Document(ArchiveProxy):
    """Allows access to a document"""

    def declare(self, element_type: ElementType) -> Declaration:
        """
        Adds a declaration to the document
        :return: A declaration object to access the declaration
        """

        self._archive.insert(
            'declarations', document=self.id, element_type=element_type.id
        )
        return Declaration(self._archive, self._archive.last_id())


class ElementType(ArchiveProxy):
    """Allows access to an element type"""

    def add_property(self, name: str) -> None:
        """
        Adds a property to the element type
        :param name: The property's name
        """

        self._archive.insert('element_type_properties', element_type=self.id, name=name)

    def new_relation_type(
        self, description: str, target_element_type: ElementType
    ) -> RelationType:
        """
        Creates a new type of relation between an element of this type and a target element
        :param description: The relation type's description, with %% for the target element
        :param target_element_type: The type of the target element
        :return: A relation type object to access the newly created relation type
        """

        self._archive.insert(
            'relation_types',
            element_type=self.id,
            description=description,
            target_element_type=target_element_type.id,
        )
        return RelationType(self._archive, self._archive.last_id())


class RelationType(ArchiveProxy):
    """Allows access to a relation type"""
