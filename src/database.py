"""Provides database operations"""


class Column:
    """Represents an SQL table column"""

    type: str

    def __init__(self, column_type: str) -> None:
        self.type = column_type

    def __repr__(self) -> str:
        return self.type


class Database:
    """Represents an SQL database"""

    _name: str
    _password: str
    _username: str

    def __init__(self, username: str, password: str, database: str) -> None:
        self._username = username
        self._password = password
        self._name = database

    def use(self) -> str:
        """Retuns a USE statement"""
        return f'USE {self._name}'


class Table:
    """Represents an SQL table"""

    _columns: dict[str, Column]
    _name: str

    def __init__(self, name: str, **columns: Column) -> None:
        self._name = name
        self._columns = columns

    def __getattr__(self, name: str) -> Column:
        return self._columns[name]

    def create(self) -> str:
        """Returns a CREATE TABLE statement"""

        return (
            f'CREATE TABLE {self._name}'
            f' ({", ".join(f"{name} {column}" for name, column in self._columns.items())})'
        )
