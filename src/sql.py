"""Utility functions for generating SQL statements"""


class Statement:
    """Interface for representing an SQL statement"""


class Use(Statement):
    """This statement sets the current database to a chosen one"""

    _database: str

    def __init__(self, database: str) -> None:
        super().__init__()

        self._database = database

    def __repr__(self) -> str:
        return f'USE {self._database}'
