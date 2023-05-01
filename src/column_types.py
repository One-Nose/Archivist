"""Types of columns in tables"""

from __future__ import annotations

from typing import ClassVar


class ColumnType:
    """Parent class for column types"""

    _SQL: ClassVar[str]

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


class LongText(ColumnType):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class Property(IntColumnType):
    """Represents a category property"""


class PropertyDeclaration(IntColumnType):
    """Represents a property declaration"""


class Rule(IntColumnType):
    """Represents a category rule"""


class ShortText(ColumnType):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'
