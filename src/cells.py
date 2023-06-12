"""Types of columns in tables"""

from __future__ import annotations

from typing import Generic, TypeVar

CellValue = TypeVar('CellValue')


class Cell(Generic[CellValue]):
    """Parent class for cells"""

    _SQL: str
    negated: bool
    value: CellValue

    def __init__(self, value: CellValue, negate: bool = False) -> None:
        """
        :param value: The object's value
        :param negate: Whether the cell uses != instead of =
        """

        self.value = value
        self.negated = negate

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _sql(cls) -> str:
        """
        Returns the cell's non-final SQL representation
        :return: The cell's SQL representation
        """

        return f'{cls._SQL} NOT NULL'

    @classmethod
    def nullable(cls: type[Cell[CellValue]]) -> type[Cell[CellValue]]:
        """
        Returns a nullable version of the cell
        :return: The result cell
        """

        class Nullable(cls):
            """A nullable cell"""

            @classmethod
            def _sql(cls) -> str:
                return cls._SQL

        return Nullable

    @classmethod
    def sql(cls) -> str:
        """
        Returns the cell's SQL representation
        :return: The cell's SQL representation
        """

        return cls._sql()


class Boolean(Cell[bool]):
    """Represents a BOOLEAN cell, default to FALSE"""

    _SQL = 'BOOLEAN'

    @classmethod
    def sql(cls) -> str:
        return f'{cls._sql()} DEFAULT FALSE'


class LongText(Cell[str]):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class ShortText(Cell[str]):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'


class UnsignedInt(Cell[int]):
    """Represents an INT UNSIGNED cell"""

    _SQL = 'INT UNSIGNED'


class KeyCell(UnsignedInt):
    """Represents an ID cell"""

    _TABLE: str

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, type(self)):
            return self.value == __value.value
        return False

    @classmethod
    def primary_key(cls: type[KeyCell]) -> type[KeyCell]:
        """
        Returns a primary key version of the cell
        :return: The result cell
        """

        class PrimaryKey(cls):
            """A primary key cell"""

            @classmethod
            def sql(cls) -> str:
                """Returns the type's SQL representation"""

                return f'{cls._sql()} AUTO_INCREMENT PRIMARY KEY'

        return PrimaryKey

    @classmethod
    def sql(cls) -> str:
        return f'{cls._sql()} REFERENCES {cls._TABLE}(id)'


class Analysis(KeyCell):
    """Represents a placing of a point on an axis"""

    _TABLE = 'analysis'


class Axis(KeyCell):
    """Represents an axis"""

    _TABLE = 'axes'


class Category(KeyCell):
    """Represents a category"""

    _TABLE = 'categories'


class Description(KeyCell):
    """Represents an element description"""

    _TABLE = 'descriptions'


class Document(KeyCell):
    """Represents a document"""

    _TABLE = 'documents'


class Element(KeyCell):
    """Represents an element"""

    _TABLE = 'elements'


class Point(KeyCell):
    """Represents a point in an axis"""

    _TABLE = 'points'


class Order(KeyCell):
    """Represents an order declaration"""

    _TABLE = 'orders'


class OrderRule(KeyCell):
    """Represents an order rule"""

    _TABLE = 'order_rules'


class Property(KeyCell):
    """Represents a category property"""

    _TABLE = 'properties'
