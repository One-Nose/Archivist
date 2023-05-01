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

    @classmethod
    def _sql(cls) -> str:
        """Returns the type's SQL representation without additional info"""

        return cls._SQL

    @classmethod
    def sql(cls) -> str:
        """Returns the type's SQL representation"""

        return f'{cls._sql()} NOT NULL'


class IntColumnType(ColumnType):
    """Represents an INT column type"""

    _SQL = 'INT'
    _SIGNED: ClassVar[bool] = False
    value: int

    def __init__(self, value: int) -> None:
        super().__init__(value)

    @classmethod
    def _sql(cls) -> str:
        return super()._sql() + ('' if cls._SIGNED else ' UNSIGNED')

    @classmethod
    def primary_key(cls: type[IntColumnType]) -> type[IntColumnType]:
        """
        Returns a primary key version of a column type
        :return: The result column type
        """

        class PrimaryKey(cls):
            """A primary key column type"""

            @classmethod
            def sql(cls) -> str:
                """Returns the type's SQL representation"""

                return f'{cls._sql()} AUTO_INCREMENT PRIMARY KEY'

        return PrimaryKey


class StrColumnType(ColumnType):
    """Represents a string column type"""

    value: str

    def __init__(self, value: str) -> None:
        super().__init__(value)


class Category(IntColumnType):
    """Represents a category"""

    _SIGNED = True


class Declaration(IntColumnType):
    """Represents an element declaration"""


class Description(IntColumnType):
    """Represents an element description"""


class Document(IntColumnType):
    """Represents a document"""


class Element(IntColumnType):
    """Represents an element"""


class Property(IntColumnType):
    """Represents a category property"""


class PropertyDeclaration(IntColumnType):
    """Represents a property declaration"""


class Rule(IntColumnType):
    """Represents a category rule"""


class LongText(StrColumnType):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class ShortText(StrColumnType):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'
