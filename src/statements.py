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
        return f'{type(self).__name__}({repr(str(self))})'

    def __str__(self) -> str:
        return self._statement

    def _get_params(self) -> tuple[Any, ...]:
        """
        :return: the statement's parameters
        """

        return self._params

    def execute(self) -> None:
        """Executes the statement"""

        self._database.execute(str(self), self._get_params())


class DataStatement(Statement):
    """Represents a data manipulation/query statement"""

    _limit: str = ''
    _limit_count: int | None = None
    _order_by: str = ''
    _where: str = ''
    _where_params: tuple[Any, ...] = ()

    def __str__(self) -> str:
        return super().__str__() + self._where + self._order_by + self._limit

    def _get_params(self) -> tuple[Any, ...]:
        return (
            super()._get_params()
            + self._where_params
            + (self._limit_count is not None) * (self._limit_count,)
        )

    def limit(self, amount: int) -> Self:
        """
        Modifies the LIMIT clause of the statement
        :param amount: The amount of rows to limit to
        :return: This statement
        """

        self._limit = f' LIMIT ?'
        self._limit_count = amount
        return self

    def order_by(self, column: str) -> Self:
        """
        Modifies the statement's ORDER BY clause
        :param column: The column to order by
        :return: This statement
        """

        self._order_by = f' ORDER BY {column}'
        return self

    def where(self, **conditions: Cell[Any] | str | tuple[Cell[Any], ...]) -> Self:
        """
        Modifies the statement's WHERE clause
        :param conditions: The conditions that must be met, in the form of column=value
            value may be either a cell, a string or a tuple of cells to match at least one.
        :return: This statement
        """

        clauses: list[str] = []
        params: list[Any] = []

        for column, value in conditions.items():
            if isinstance(value, tuple):
                clauses.append(f'{column} IN ({", ".join("?" * len(value))})')
                params.extend(value.value for value in value)
            elif isinstance(value, Cell):
                clauses.append(f'{column} = ?')
                params.append(value.value)
            else:
                clauses.append(f'{column} = {value}')

        self._where = ' WHERE ' + ' AND '.join(clauses)
        self._where_params = tuple(params)

        return self


class Select(DataStatement):
    """Represents a SELECT statement"""

    _into: str = ''

    def __str__(self) -> str:
        return self._into + super().__str__()

    def into(self, table: str, columns: Iterable[str]) -> Statement:
        """
        Turns the statement into a INSERT INTO ... SELECT statement
        :param table: The table to insert the selected values to
        :param columns: A list of columns to insert the selection into
        :return: This statement
        """

        self._into = f'INSERT INTO {table} ({", ".join(columns)}) '
        return self

    def execute(self) -> list[tuple[Any, ...]]:
        super().execute()

        return [] if self._into else self._database.fetch()
