"""Types of columns in tables"""


from typing import Self


class ColumnType:
    """Parent class for column types"""

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
