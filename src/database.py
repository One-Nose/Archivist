"""Provides database operations"""

from __future__ import annotations

from typing import Self

from mariadb import Cursor, ProgrammingError, connect
from mariadb.connections import Connection


class Column:
    """Represents an SQL table column"""

    _name: str
    _type: ColumnType

    def __init__(self, name: str, column_type: ColumnType) -> None:
        """
        :param name: The column's name
        :param column_type: The colum's type
        """

        self._name = name
        self._type = column_type

    def __repr__(self) -> str:
        return f'{self._name} {self._type}'


class ColumnType:
    """Represents a column type"""

    _type: str
    _is_nullable: bool

    def __init__(self, column_type: str, nullable: bool = False) -> None:
        self._type = column_type
        self._is_nullable = nullable

    def __repr__(self) -> str:
        return self._type + ('' if self._is_nullable else ' NOT NULL')

    def nullable(self) -> Self:
        """Returns a nullable version of the column type"""

        return type(self)(self._type, nullable=True)

    def primary_key(self) -> Self:
        """Returns an auto-increment primary key version of the column type"""

        return type(self)(f'{self._type} AUTO_INCREMENT PRIMARY KEY', nullable=True)


class Table(dict[str, Column]):
    """Represents an SQL table"""

    name: str

    def __init__(self, table_name: str, **columns: ColumnType) -> None:
        """
        :param table_name: The name of the table
        :param columns: The table's columns, in the form of name=type
        """

        self.name = table_name
        self.update({name: Column(name, type) for name, type in columns.items()})

    def create(self) -> str:
        """Returns a CREATE TABLE statement"""

        return f'CREATE TABLE {self.name} ({", ".join(map(str, self.values()))})'


class Database(dict[str, Table]):
    """Represents an SQL database"""

    _connection: Connection
    _password: str
    _username: str
    cursor: Cursor
    name: str

    def __init__(self, username: str, password: str, database: str) -> None:
        self._username = username
        self._password = password
        self.name = database

        category = ColumnType('INT')
        declaration = ColumnType('INT UNSIGNED')
        description = ColumnType('INT UNSIGNED')
        document = ColumnType('INT UNSIGNED')
        element = ColumnType('INT UNSIGNED')
        property_declaration = ColumnType('INT UNSIGNED')
        property_definition = ColumnType('INT UNSIGNED')
        rule = ColumnType('INT UNSIGNED')
        text = ColumnType('TEXT')
        varchar = ColumnType('VARCHAR(255)')

        self.update(
            {
                table.name: table
                for table in (
                    Table(
                        'categories',
                        id=category.primary_key(),
                        name=varchar,
                    ),
                    Table(
                        'declarations',
                        id=declaration.primary_key(),
                        document=document,
                        category=category,
                    ),
                    Table(
                        'descriptions',
                        id=description.primary_key(),
                        declaration=declaration,
                        description=text,
                    ),
                    Table(
                        'documents',
                        id=document.primary_key(),
                        name=varchar,
                    ),
                    Table(
                        'elements',
                        id=element.primary_key(),
                        category=category,
                    ),
                    Table(
                        'properties',
                        id=property_definition.primary_key(),
                        parent=category,
                        name=varchar,
                        category=category,
                    ),
                    Table(
                        'property_declarations',
                        id=property_declaration.primary_key(),
                        declaration=declaration,
                        property=property_definition,
                        value=declaration,
                    ),
                    Table(
                        'rules',
                        id=rule.primary_key(),
                        category=category,
                        property1=property_definition,
                        subproperty1=property_definition,
                        property2=property_definition,
                        subproperty2=property_definition,
                    ),
                )
            }
        )

        self._connect()

    def _connect(self) -> None:
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

    def init(self) -> None:
        """Creates the database and initializes it"""

        self.cursor.execute(f'CREATE DATABASE {self.name}')
        self.cursor.execute(self.use())

        for table in self.values():
            self.cursor.execute(table.create())

    def close(self) -> None:
        """Closes the connection"""

        self.cursor.close()
        self._connection.close()

    def commit(self) -> None:
        """Commits the changes to the database"""

        self._connection.commit()

    def use(self) -> str:
        """Retuns a USE statement"""

        return f'USE {self.name}'
