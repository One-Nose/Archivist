"""Provides database operations"""


class Column:
    """Represents an SQL table column"""

    _name: str
    _type: str

    def __init__(self, name: str, column_type: str) -> None:
        self._name = name
        self._type = column_type

    def __repr__(self) -> str:
        return f'{self._name} {self._type}'


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


class Table(dict[str, Column]):
    """Represents an SQL table"""

    _name: str

    def __init__(self, table_name: str, **columns: str) -> None:

        self._name = table_name
        self.update({name: Column(name, type) for name, type in columns.items()})

    def create(self) -> str:
        """Returns a CREATE TABLE statement"""

        return f'CREATE TABLE {self._name} ({", ".join(map(str, self.values()))})'
