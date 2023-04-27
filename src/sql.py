"""Utility functions for generating SQL statements"""


class Database:
    """Represents an SQL database"""

    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    def use(self) -> str:
        """Retuns a USE statement"""
        return f'USE {self._name}'
