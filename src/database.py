"""Provides database operations"""

from __future__ import annotations

from collections.abc import Collection, Iterable
from typing import Any, Self

from mariadb import Cursor, ProgrammingError, connect
from mariadb.connections import Connection

from .analyzer import Analyzer
from .cells import (
    Axis,
    Boolean,
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
    UnsignedInt,
)


class Column:
    """Represents an SQL table column"""

    _name: str
    _type: type[Cell[Any]]

    def __init__(self, name: str, column_type: type[Cell[Any]]) -> None:
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

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self._statement)})'

    def execute(self) -> None:
        """Executes the statement"""

        self._database.cursor.execute(self._statement, self._params)


class DataStatement(Statement):
    """Represents a data manipulation/query statement"""

    def where(self, **conditions: Cell[Any] | str | tuple[Cell[Any], ...]) -> Self:
        """
        Creates a version of the statement with a WHERE clause
        :param conditions: The conditions that must be met, in the form of column=value
            value may be either a cell, a string or a tuple of cells to match at least one.
        :return: The new statement
        """

        clauses: list[str] = []
        params = list(self._params)

        for column, value in conditions.items():
            if isinstance(value, tuple):
                clauses.append(f'{column} IN ({", ".join("?" * len(value))})')
                params.extend(value.value for value in value)
            elif isinstance(value, Cell):
                clauses.append(f'{column} = ?')
                params.append(value.value)
            else:
                clauses.append(f'{column} = {value}')

        return self.__class__(
            self._database, f'{self._statement} WHERE {" AND ".join(clauses)}', params
        )


class Select(DataStatement):
    """Represents a SELECT statement"""

    def into(self, table: str, columns: Iterable[str]) -> Statement:
        """
        Creates an INSERT INTO ... SELECT version of the SELECT statement
        :param table: The table to insert the selected values to
        :param columns: A list of columns to insert the selection into
        :return: An INSERT...SELECT statement
        """

        return Statement(
            self._database,
            f'INSERT INTO {table} ({", ".join(columns)}) {self._statement}',
            self._params,
        )

    def execute(self) -> list[tuple[Any, ...]]:
        super().execute()

        return self._database.cursor.fetchall()


class TableReferences:
    """Table refrences that can be used with FROM clauses"""

    _database: Database
    _references: str

    def __init__(self, database: Database, references: Iterable[str]) -> None:
        """
        :param database: The table's database
        :param references: A list of table references
        """

        self._database = database
        self._references = ', '.join(references)

    def select(self, *columns: str | int) -> Select:
        """
        Creates a SELECT statement that selects data from the table
        :param columns: The names of the columns/values to select from the table
        :return: A SELECT statement
        """

        return Select(
            self._database,
            f'SELECT {", ".join(column if isinstance(column, str) else "?" for column in columns)}'
            f' FROM {self._references}',
            (column for column in columns if isinstance(column, int)),
        )

    def set(self, **columns: str) -> DataStatement:
        """
        Creates an UPDATE statement to update tables
        :param columns: The columns to set, in the form of column=value
        :return: An UPDATE statement
        """

        return DataStatement(
            self._database,
            f'UPDATE {self._references}'
            f' SET {", ".join(f"{column} = {value}" for column, value in columns.items())}',
        )


class Table(TableReferences, dict[str, Column]):
    """Represents an SQL table"""

    name: str

    def __init__(
        self, database: Database, table_name: str, **columns: type[Cell[Any]]
    ) -> None:
        """
        :param database: The table's database
        :param table_name: The table's name
        :param columns: The table's columns, in the form of name=type
        """
        super().__init__(database, [table_name])

        self.name = table_name
        self.update(
            {name: Column(name, column_type) for name, column_type in columns.items()}
        )

    def create(self) -> Statement:
        """Returns a CREATE TABLE statement"""

        return self._database.statement(
            f'CREATE TABLE {self.name} ({", ".join(map(str, self.values()))})'
        )

    def insert(self, **values: Cell[Any]) -> Statement:
        """
        Creates an INSERT statement that inserts values into the table (insecure)
        :param values: The values to insert in the form of column=value
        :return: An INSERT statement
        """

        return self.insert_many(values.keys(), values.values())

    def insert_many(
        self, columns: Collection[str], *rows: Collection[Cell[Any]]
    ) -> Statement:
        """
        Creates an INSERT statement to insert multiple rows into the table
        :param columns: The columns to insert into
        :param rows: The rows to insert, each as a sequence of values
        :return: An INSERT statement
        """

        return self._database.statement(
            f'INSERT INTO {self.name} ({", ".join(columns)}) VALUES'
            f' ({"), (".join(", ".join("?" * len(values)) for values in rows)})',
            tuple(value.value for row in rows for value in row),
        )


class Database(dict[str, Table]):
    """Represents an SQL database"""

    _connection: Connection
    _password: str
    _username: str
    analyzer: Analyzer
    cursor: Cursor
    name: str

    def __init__(self, username: str, password: str, database: str) -> None:
        super().__init__()

        self._username = username
        self._password = password
        self.name = database

        self.analyzer = Analyzer(self)

        self.update(
            {
                table.name: table
                for table in (
                    self.table(
                        'axes',
                        id=Axis.primary_key(),
                    ),
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
                        'points',
                        id=Point.primary_key(),
                        element=Element,
                        property=Property,
                        analyzed=Boolean,
                    ),
                    self.table(
                        'analysis',
                        point=Point,
                        axis=Axis,
                        value=UnsignedInt,
                    ),
                    self.table(
                        'order_rules',
                        id=OrderRule.primary_key(),
                        large=Property,
                        small=Property,
                    ),
                    self.table(
                        'orders',
                        id=Order.primary_key(),
                        document=Document,
                        large=Point,
                        small=Point,
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

    def statement(self, statement: str, params: Iterable[Any] = ()) -> Statement:
        """
        Creates a statement object
        :param statement: The SQL statement
        :param params: The statement's parameters
        :return: A statement object
        """

        return Statement(self, statement, params)

    def table(self, table_name: str, **columns: type[Cell[Any]]) -> Table:
        """
        Creates table object
        :param table_name: The table's name
        :param columns: The table's columns, in the form of name=type
        :return: A table object
        """

        return Table(self, table_name, **columns)

    def table_refrences(self, *references: str) -> TableReferences:
        """
        Creates a table refrences object to use with FROM clauses
        :param references: A list of table references
        :return: A table references object
        """

        return TableReferences(self, references)

    def use(self) -> Statement:
        """
        Creates a USE statement
        :return: The use statement
        """

        return self.statement(f'USE {self.name}')

    @property
    def last_row_id(self) -> int:
        """
        The ID generated for AUTO_INCREMENT if the last query was INSERT or UPDATE, otherwise 0
        """

        return self.cursor.lastrowid
