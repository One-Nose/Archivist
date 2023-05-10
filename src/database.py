"""Provides database operations"""

from __future__ import annotations

from typing import Any, Iterable

from mariadb import Cursor, ProgrammingError, connect
from mariadb.connections import Connection

from .cells import (
    Category,
    Cell,
    Description,
    Document,
    Element,
    LongText,
    Order,
    OrderRule,
    Point,
    Property,
    ShortText,
)


class Column:
    """Represents an SQL table column"""

    _name: str
    _type: type[Cell]

    def __init__(self, name: str, column_type: type[Cell]) -> None:
        """
        :param name: The column's name
        :param column_type: The column's cell type
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
        self, database: Database, statement: str, params: Iterable[Any] = ()
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
        self, database: Database, table_name: str, **columns: type[Cell]
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

    def insert(self, **values: Cell) -> Statement:
        """
        Creates an INSERT statement that inserts values into the table (insecure)
        :param values: The values to insert in the form of column=value
        :return: An INSERT statement
        """

        return self._database.statement(
            f'INSERT INTO {self.name} ({", ".join(values)}) VALUES'
            f' ({", ".join("?" * len(values))})',
            tuple(value.value for value in values.values()),
        )

    def select(self, *columns: str, **where: Cell) -> Statement:
        """
        Creates a SELECT statement that selects data from the table
        :param columns: The names of the columns to select from the table
        :param where: Column conditions to filter selection in the form of column=value
        :return: A SELECT statement
        """

        return self._database.statement(
            f'SELECT {", ".join(columns)} FROM {self.name} WHERE'
            f' {" AND ".join(f"{column} = ?" for column in where)}',
            (value.value for value in where.values()),
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
                        'descriptions',
                        id=Description.primary_key(),
                        document=Document,
                        element=Element,
                        description=LongText,
                    ),
                    self.table(
                        'properties',
                        id=Property.primary_key(),
                        category=Category,
                        name=ShortText,
                    ),
                    self.table(
                        'orders',
                        id=Order.primary_key(),
                        document=Document,
                        large_element=Element,
                        large_property=Property,
                        small_element=Element,
                        small_property=Property,
                    ),
                    self.table(
                        'order_rules',
                        id=OrderRule.primary_key(),
                        large=Property,
                        small=Property,
                    ),
                    self.table(
                        'points',
                        id=Point.primary_key(),
                        element=Element,
                        property=Property,
                        previous=Point,
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
            self.use().execute()
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

    def statement(self, statement: str, params: Iterable[Any] = ()) -> Statement:
        """
        Creates a statement object
        :param statement: The SQL statement
        :param params: The statement's parameters
        :return: A statement object
        """

        return Statement(self, statement, params)

    def table(self, table_name: str, **columns: type[Cell]) -> Table:
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
