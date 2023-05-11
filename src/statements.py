"""Classes representing executable SQL statements"""


from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Self

from .cells import Cell

if TYPE_CHECKING:
    from .database import Database


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

        self._database.execute(self._statement, self._params)


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

        return self._database.fetch()
