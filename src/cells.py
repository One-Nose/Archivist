"""Types of columns in tables"""

from __future__ import annotations

from typing import Any, ClassVar


class Cell:
    """Parent class for cells"""

    _SQL: ClassVar[str]
    value: Any

    def __init__(self, value: Any) -> None:
        """
        :param value: The object's value
        """

        self.value = value

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
    def sql(cls) -> str:
        """Returns the type's SQL representation"""

        return cls._sql()


class KeyCell(Cell):
    """Represents an ID cell"""

    _SQL = 'INT UNSIGNED'
    _TABLE: ClassVar[str]
    value: int

    def __init__(self, value: int) -> None:
        super().__init__(value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, type(self)):
            return self.value == __value.value
        return False

    @classmethod
    def primary_key(cls: type[KeyCell]) -> type[KeyCell]:
        """
        Returns a primary key version of a cell
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


class StrCell(Cell):
    """Represents a string cell"""

    value: str

    def __init__(self, value: str) -> None:
        super().__init__(value)


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


class LongText(StrCell):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class ShortText(StrCell):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'
