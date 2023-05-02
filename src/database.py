"""Provides database operations"""

from __future__ import annotations

from typing import Any, Sequence

from mariadb import Cursor, ProgrammingError, connect
from mariadb.connections import Connection

from .column_types import (
    Category,
    ColumnType,
    Declaration,
    Description,
    Document,
    Element,
    LongText,
    Property,
    PropertyDeclaration,
    Rule,
    ShortText,
)


class Column:
    """Represents an SQL table column"""

    _name: str
    _type: type[ColumnType]

    def __init__(self, name: str, column_type: type[ColumnType]) -> None:
        """
        :param name: The column's name
        :param column_type: The column's type
        """

        self._name = name
        self._type = column_type

    def __repr__(self) -> str:
        return f'{self._name} {self._type.sql()}'


class Statement:
    """Represents an SQL statement"""

    _database: Database
    _params: tuple[Any, ...]
    _statement: str

    def __init__(
        self, database: Database, statement: str, params: Sequence[Any] = ()
    ) -> None:
        """
        :param database: The statement's database
        :param statement: The SQL statement
        :param params: The parameters to pass to the execute command
        """

        self._database = database
        self._statement = statement
        self._params = tuple(params)

    def execute(self) -> None:
        """Executes the statement"""

        self._database.cursor.execute(self._statement, self._params)


class Table(dict[str, Column]):
    """Represents an SQL table"""

    _database: Database
    name: str

    def __init__(
        self, database: Database, table_name: str, **columns: type[ColumnType]
    ) -> None:
        """
        :param database: The table's database
        :param table_name: The table's name
        :param columns: The table's columns, in the form of name=type
        """

        super().__init__()
        self._database = database
        self.name = table_name
        self.update(
            {name: Column(name, column_type) for name, column_type in columns.items()}
        )

    def create(self) -> Statement:
        """Returns a CREATE TABLE statement"""

        return self._database.statement(
            f'CREATE TABLE {self.name} ({", ".join(map(str, self.values()))})'
        )

    def insert(self, **values: ColumnType) -> Statement:
        """
        Inserts values into the table (insecure)
        :param values: The values to insert in the form of column=value
        :return: An INSERT statement
        """

        return self._database.statement(
            f'INSERT INTO {self.name} ({", ".join(values)}) VALUES'
            f' ({", ".join("?" * len(values))})',
            tuple(value.value for value in values.values()),
        )


class Database(dict[str, Table]):
    """Represents an SQL database"""

    _connection: Connection
    _password: str
    _username: str
    cursor: Cursor
    name: str

    def __init__(self, username: str, password: str, database: str) -> None:
        super().__init__()

        self._username = username
        self._password = password
        self.name = database

        self.update(
            {
                table.name: table
                for table in (
                    self.table(
                        'categories',
                        id=Category.primary_key(),
                        name=ShortText,
                    ),
                    self.table(
                        'declarations',
                        id=Declaration.primary_key(),
                        document=Document,
                        category=Category,
                    ),
                    self.table(
                        'descriptions',
                        id=Description.primary_key(),
                        declaration=Declaration,
                        description=LongText,
                    ),
                    self.table(
                        'documents',
                        id=Document.primary_key(),
                        name=ShortText,
                    ),
                    self.table(
                        'elements',
                        id=Element.primary_key(),
                        category=Category,
                    ),
                    self.table(
                        'properties',
                        id=Property.primary_key(),
                        parent=Category,
                        name=ShortText,
                        category=Category,
                    ),
                    self.table(
                        'property_declarations',
                        id=PropertyDeclaration.primary_key(),
                        declaration=Declaration,
                        property=Property,
                        value=Declaration,
                    ),
                    self.table(
                        'rules',
                        id=Rule.primary_key(),
                        category=Category,
                        property1=Property,
                        subproperty1=Property,
                        property2=Property,
                        subproperty2=Property,
                    ),
                )
            }
        )

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
            user=self._username,
            password=self._password,
        )
        self.cursor = self._connection.cursor()
        try:
            self.use()
        except ProgrammingError:
            self.init()

    def drop(self) -> None:
        """Drops the database"""

        self.cursor.execute(f'DROP DATABASE {self.name}')

    def init(self) -> None:
        """Creates the database and initializes it"""

        self.cursor.execute(f'CREATE DATABASE {self.name}')
        self.use().execute()

        for table in self.values():
            table.create().execute()

    def use(self) -> Statement:
        """
        Creates a USE statement
        :return: The use statement
        """

        return self.statement(f'USE {self.name}')

    def statement(self, statement: str, params: Sequence[Any] = ()) -> Statement:
        """
        Creates a statement object
        :param statement: The SQL statement
        :param params: The statement's parameters
        :return: A statement object
        """

        return Statement(self, statement, params)

    def table(self, table_name: str, **columns: type[ColumnType]) -> Table:
        """
        Creates table object
        :param table_name: The table's name
        :param columns: The table's columns, in the form of name=type
        :return: A table object
        """

        return Table(self, table_name, **columns)

    @property
    def last_row_id(self) -> int:
        """
        The ID generated for AUTO_INCREMENT if the last query was INSERT or UPDATE, otherwise 0
        """

        return self.cursor.lastrowid
