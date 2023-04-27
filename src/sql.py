"""Utility functions for generating SQL statements"""


class Column:
    """Represents an SQL table column"""

    type: str

    def __init__(self, column_type: str) -> None:
        self.type = column_type


class Database:
    """Represents an SQL database"""

    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    def use(self) -> str:
        """Retuns a USE statement"""
        return f'USE {self._name}'


class Table:
    """Represents an SQL table"""

    _name: str

    def __init__(self, name: str) -> None:
        self._name = name
