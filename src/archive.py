"""Access the database and make queries"""
from __future__ import annotations

from enum import IntEnum, auto
from typing import TypedDict

from mariadb import Connection, ProgrammingError, connect
from mariadb.cursors import Cursor

from .sql import Column, Database
from .analyzer import Analyzer


class ArchiveConfig(TypedDict):
    """
    Configuration of the database
    - connect: Configuration of the connection to the database
    """

    connect: ConnectionConfig


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


class BuiltInCategory(IntEnum):
    """A negative integer enum for built-in rule categories"""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[int]
    ) -> int:
        del name, start, last_values
        return -count - 1

    GREATER = auto()
    LESS = auto()


class Archive:
    """Allows access to the database"""

    _analyzer: Analyzer
    _connect_options: ConnectionConfig
    _connection: Connection
    _database: Database
    cursor: Cursor

    def __init__(self, config: ArchiveConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """

        self._connect_options = config['connect']
        self._database = Database(self._connect_options['database'])
        self.connect()
        self._analyzer = Analyzer(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self._connect_options["database"])})'

    def _use(self) -> None:
        """Sets the database as the connected database"""

        self.cursor.execute(self._database.use())

    def add_rule(
        self,
        category: Category | BuiltInCategory,
        property1: tuple[Property, Property | None] | Property,
        property2: tuple[Property, Property | None] | Property,
    ) -> None:
        """
        Adds a rule to the archive
        :param category: The category of the rule, may be built-in
        :param property1: The rule's first argument, either as (property, subproperty) or property
        :param property2: The rule's second argument, either as (property, subproperty) or property
        """

        if isinstance(property1, Property):
            property1 = (property1, None)
        elif property1[1]:
            assert property1[1].parent == property1[0].category

        if isinstance(property2, Property):
            property2 = (property2, None)
        elif property2[1]:
            assert property2[1].parent == property2[0].category

        assert property1[0].parent == property2[0].parent

        self.insert(
            'rules',
            category=category,
            property1=property1[0].id,
            subproperty1=property1[1].id if property1[1] else 0,
            property2=property2[0].id,
            subproperty2=property2[1].id if property2[1] else 0,
        )

    def category(self, category_id: int) -> Category:
        """
        Creates a category object to access an existing category
        :param type_id: The category's numeral ID
        :return: A category object that allows access to the category
        """

        return Category(self, category_id)

    def close(self) -> None:
        """Closes the connection"""

        self.cursor.close()
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
        self.cursor = self._connection.cursor()
        try:
            self._use()
        except ProgrammingError:
            self.init()

    def create_table(self, table: str, **columns: Column) -> None:
        """
        Creates a table (insecure)
        :param table: The name of the table
        :param columns: A sequence of columns, each in the form of name=column
        """

        self.cursor.execute(
            f'CREATE TABLE {table}'
            f'({", ".join(f"{name} {column.type}" for name, column in columns.items())})'
        )

    def document(self, document_id: int) -> Document:
        """
        Creates a document object to access an existing document
        :param document_id: The document's numeral ID
        :return: A document object that allows access to the document
        """

        return Document(self, document_id)

    def drop(self) -> None:
        """Deletes the database"""

        self.cursor.execute(f'DROP DATABASE {self._connect_options["database"]}')

    def init(self) -> None:
        """Creates the database and initializes it"""

        self.cursor.execute(f'CREATE DATABASE {self._connect_options["database"]}')
        self._use()

        self._analyzer.init()

        self.create_table(
            'categories',
            id=Column('INT AUTO_INCREMENT PRIMARY KEY'),
            name=Column('VARCHAR(255) NOT NULL'),
        )

        self.create_table(
            'declarations',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            document=Column('INT UNSIGNED NOT NULL'),
            category=Column('INT NOT NULL'),
        )

        self.create_table(
            'descriptions',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            declaration=Column('INT UNSIGNED NOT NULL'),
            description=Column('TEXT NOT NULL'),
        )

        self.create_table(
            'documents',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            name=Column('VARCHAR(255) NOT NULL'),
        )

        self.create_table(
            'properties',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            parent=Column('INT NOT NULL'),
            name=Column('VARCHAR(255) NOT NULL'),
            category=Column('INT NOT NULL'),
        )

        self.create_table(
            'property_declarations',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            declaration=Column('INT UNSIGNED NOT NULL'),
            property=Column('INT UNSIGNED NOT NULL'),
            value=Column('INT UNSIGNED NOT NULL'),
        )

        self.create_table(
            'rules',
            id=Column('INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'),
            category=Column('INT NOT NULL'),
            property1=Column('INT UNSIGNED NOT NULL'),
            subproperty1=Column('INT UNSIGNED NOT NULL'),
            property2=Column('INT UNSIGNED NOT NULL'),
            subproperty2=Column('INT UNSIGNED NOT NULL'),
        )

    def insert(self, table: str, **values: ...) -> None:
        """
        Inserts values into a table (insecure)
        :param table: The table to insert to
        :param values: The values to insert in the form of column=value
        """

        self.cursor.execute(
            f'INSERT INTO {table} ({", ".join(values)}) VALUES ({", ".join("?" for _ in values)})',
            tuple(values.values()),
        )

    def new_category(self, name: str) -> Category:
        """
        Creates a new category
        :param name: The name of the category
        :return: A category object to access the newly created category
        """

        self.insert('categories', name=name)
        return Category(self, self.cursor.lastrowid)

    def new_document(self, name: str) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :return: A document object to access the newly created document
        """

        self.insert('documents', name=name)
        return Document(self, self.cursor.lastrowid)

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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, ArchiveProxy):
            return self.id == __value.id
        return False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.id)})'


class Category(ArchiveProxy):
    """Allows access to a category"""

    def new_property(self, name: str, category: Category | None = None) -> Property:
        """
        Adds a property to the category
        :param name: The property's name
        :param category: The property's optional category
        :return: A property object to access the newly created property
        """

        self._archive.insert(
            'properties',
            parent=self.id,
            name=name,
            category=category.id if category else 0,
        )
        return Property(self._archive, self._archive.cursor.lastrowid, self, category)


class Declaration(ArchiveProxy):
    """Allows access to a declaration of an element"""

    def add_description(self, description: str) -> None:
        """
        Adds a description to the declaration
        :param description: The description to add
        """

        self._archive.insert(
            'descriptions', declaration=self.id, description=description
        )

    def declare_property(self, declared_property: Property, value: Declaration) -> None:
        """
        Declares a property of the declared element
        :param declared_property: The property to declare
        :param value: The value to declare the property as
        """

        self._archive.insert(
            'property_declarations',
            declaration=self.id,
            property=declared_property.id,
            value=value.id,
        )


class Document(ArchiveProxy):
    """Allows access to a document"""

    def declare(self, category: Category) -> Declaration:
        """
        Adds a declaration of an element to the document
        :param category: The category of the declared element
        :return: A declaration object to access the declaration
        """

        self._archive.insert('declarations', document=self.id, category=category.id)
        return Declaration(self._archive, self._archive.cursor.lastrowid)


class Property(ArchiveProxy):
    """Allows access to an element type property"""

    category: Category | None
    parent: Category

    def __init__(
        self,
        archive: Archive,
        identifier: int,
        parent: Category,
        category: Category | None,
    ) -> None:
        super().__init__(archive, identifier)

        self.parent = parent
        self.category = category
