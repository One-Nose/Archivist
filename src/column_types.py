"""Types of columns in tables"""

from __future__ import annotations

from typing import Any, ClassVar


class ColumnType:
    """Parent class for column types"""

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
    def sql(cls) -> str:
        """Returns the type's SQL representation"""

        return f'{cls._SQL} NOT NULL'


class PrimaryColumnType(ColumnType):
    """Represents an INT column type"""

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
    def primary_key(cls: type[PrimaryColumnType]) -> type[PrimaryColumnType]:
        """
        Returns a primary key version of a column type
        :return: The result column type
        """

        class PrimaryKey(cls):
            """A primary key column type"""

            @classmethod
            def sql(cls) -> str:
                """Returns the type's SQL representation"""

                return f'{cls._SQL} AUTO_INCREMENT PRIMARY KEY'

        return PrimaryKey

    @classmethod
    def sql(cls) -> str:
        return super().sql() + f' REFERENCES {cls._TABLE}(id)'


class StrColumnType(ColumnType):
    """Represents a string column type"""

    value: str

    def __init__(self, value: str) -> None:
        super().__init__(value)


class Category(PrimaryColumnType):
    """Represents a category"""

    _TABLE = 'categories'


class Description(PrimaryColumnType):
    """Represents an element description"""

    _TABLE = 'descriptions'


class Document(PrimaryColumnType):
    """Represents a document"""

    _TABLE = 'documents'


class Element(PrimaryColumnType):
    """Represents an element"""

    _TABLE = 'elements'


class Order(PrimaryColumnType):
    """Represents an order declaration"""

    _TABLE = 'orders'


class OrderRule(PrimaryColumnType):
    """Represents an order rule"""

    _TABLE = 'order_rules'


class Property(PrimaryColumnType):
    """Represents a category property"""

    _TABLE = 'properties'


class LongText(StrColumnType):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class ShortText(StrColumnType):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'
