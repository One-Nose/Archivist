"""Provides database operations"""

from __future__ import annotations

from collections.abc import Collection, Iterable, Sequence
from typing import Any

from mariadb import Cursor, ProgrammingError, connect
from mariadb.connections import Connection

from .analyzer import Analyzer
from .cells import (
    Analysis,
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
from .statements import DataStatement, Select, Statement


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


class TableReferences:
    """Table references that can be used with FROM clauses"""

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

        return Select(self._database, self._references, columns)

    def set(self, **columns: Cell[Any] | str) -> DataStatement:
        """
        Creates an UPDATE statement to update tables
        :param columns: The columns to set, in the form of column=value
        :return: An UPDATE statement
        """

        clauses = ', '.join(
            f'{column} = {"?" if isinstance(value, Cell) else value}'
            for column, value in columns.items()
        )

        return DataStatement(
            self._database,
            f'UPDATE {self._references}' f' SET {clauses}',
            (value.value for value in columns.values() if isinstance(value, Cell)),
        )


class Table(TableReferences, dict[str, Column]):
    """Represents an SQL table"""

    _unique: tuple[str, ...]
    name: str

    def __init__(
            self,
            database: Database,
            table_name: str,
            unique: tuple[str, ...] | None,
            **columns: type[Cell[Any]],
    ) -> None:
        """
        :param database: The table's database
        :param table_name: The table's name
        :param unique: An optional list of columns to form a unique index
        :param columns: The table's columns, in the form of name=type
        """
        super().__init__(database, [table_name])

        self.name = table_name
        self._unique = unique if unique else ()
        self.update(
            {name: Column(name, column_type) for name, column_type in columns.items()}
        )

    def create(self) -> Statement:
        """Returns a CREATE TABLE statement"""

        return self._database.statement(
            f'CREATE TABLE {self.name} ({", ".join(map(str, self.values()))}'
            + (f', UNIQUE ({", ".join(self._unique)})' if self._unique else '')
            + ')'
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
    _cursor: Cursor
    _password: str
    _username: str
    analyzer: Analyzer
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
                    id=Analysis.primary_key(),
                    point=Point,
                    axis=Axis,
                    value=UnsignedInt,
                    unique=('axis', 'value'),
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

        self._cursor.close()
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
        self._cursor = self._connection.cursor()
        try:
            self.use().execute()
        except ProgrammingError:
            self.init()

    def drop(self) -> None:
        """Drops the database"""

        self.execute(f'DROP DATABASE {self.name}')

    def execute(self, statement: str, params: Sequence[Any] = ()) -> None:
        """
        Executes an SQL statement
        :param statement: The statement to execute
        :param params: Params to pass to the database
        """

        self._cursor.execute(statement, params)

    def init(self) -> None:
        """Creates the database and initializes it"""

        self.execute(f'CREATE DATABASE {self.name}')
        self.use().execute()

        for table in self.values():
            table.create().execute()

    def fetch(self) -> list[tuple[Any, ...]]:
        """
        Fetches all pending rows from the database
        :return: A list of rows
        """

        return self._cursor.fetchall()

    def statement(self, statement: str, params: Iterable[Any] = ()) -> Statement:
        """
        Creates a statement object
        :param statement: The SQL statement
        :param params: The statement's parameters
        :return: A statement object
        """

        return Statement(self, statement, params)

    def table(
            self,
            table_name: str,
            unique: tuple[str, ...] | None = None,
            **columns: type[Cell[Any]],
    ) -> Table:
        """
        Creates table object
        :param table_name: The table's name
        :param unique: An optional list of columns to form a unique index
        :param columns: The table's columns, in the form of name=type
        :return: A table object
        """

        return Table(self, table_name, unique, **columns)

    def table_references(self, *references: str) -> TableReferences:
        """
        Creates a table references object to use with FROM clauses
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

        return self._cursor.lastrowid
