"""Types of columns in tables"""

from __future__ import annotations

from typing import ClassVar


class ColumnType:
    """Parent class for column types"""

    _SQL: ClassVar[str]

    @classmethod
    def sql(cls) -> str:
        """Returns the type's SQL representation"""

        return f'{cls._SQL} NOT NULL'

    @classmethod
    def primary_key(cls: type[ColumnType]) -> type[ColumnType]:
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


class Category(ColumnType):
    """Represents a category"""

    _SQL = 'INT'


class Declaration(ColumnType):
    """Represents an element declaration"""

    _SQL = 'INT UNSIGNED'


class Description(ColumnType):
    """Represents an element description"""

    _SQL = 'INT UNSIGNED'


class Document(ColumnType):
    """Represents a document"""

    _SQL = 'INT UNSIGNED'


class Element(ColumnType):
    """Represents an element"""

    _SQL = 'INT UNSIGNED'


class LongText(ColumnType):
    """Represents a TEXT long text"""

    _SQL = 'TEXT'


class Property(ColumnType):
    """Represents a category property"""

    _SQL = 'INT UNSIGNED'


class PropertyDeclaration(ColumnType):
    """Represents a property declaration"""

    _SQL = 'INT UNSIGNED'


class Rule(ColumnType):
    """Represents a category rule"""

    _SQL = 'INT UNSIGNED'


class ShortText(ColumnType):
    """Represents a VARCHAR(255) short text"""

    _SQL = 'VARCHAR(255)'
