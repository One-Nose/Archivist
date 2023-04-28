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


class Table(dict[str, Column]):
    """Represents an SQL table"""

    name: str

    def __init__(self, table_name: str, **columns: str) -> None:
        """
        :param table_name: The name of the table
        :param columns: The table's columns, in the form of name=type
        """

        self.name = table_name
        self.update({name: Column(name, type) for name, type in columns.items()})

    def create(self) -> str:
        """Returns a CREATE TABLE statement"""

        return f'CREATE TABLE {self.name} ({", ".join(map(str, self.values()))})'


class Database(dict[str, Table]):
    """Represents an SQL database"""

    _name: str
    _password: str
    _username: str

    def __init__(self, username: str, password: str, database: str) -> None:
        self._username = username
        self._password = password
        self._name = database

        self.update(
            {
                table.name: table
                for table in (
                    Table(
                        'categories',
                        id='INT AUTO_INCREMENT PRIMARY KEY',
                        name='VARCHAR(255) NOT NULL',
                    ),
                    Table(
                        'declarations',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        document='INT UNSIGNED NOT NULL',
                        category='INT NOT NULL',
                    ),
                    Table(
                        'descriptions',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        declaration='INT UNSIGNED NOT NULL',
                        description='TEXT NOT NULL',
                    ),
                    Table(
                        'documents',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        name='VARCHAR(255) NOT NULL',
                    ),
                    Table(
                        'elements',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        category='INT NOT NULL',
                    ),
                    Table(
                        'properties',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        parent='INT NOT NULL',
                        name='VARCHAR(255) NOT NULL',
                        category='INT NOT NULL',
                    ),
                    Table(
                        'property_declarations',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        declaration='INT UNSIGNED NOT NULL',
                        property='INT UNSIGNED NOT NULL',
                        value='INT UNSIGNED NOT NULL',
                    ),
                    Table(
                        'rules',
                        id='INT UNSIGNED AUTO_INCREMENT PRIMARY KEY',
                        category='INT NOT NULL',
                        property1='INT UNSIGNED NOT NULL',
                        subproperty1='INT UNSIGNED NOT NULL',
                        property2='INT UNSIGNED NOT NULL',
                        subproperty2='INT UNSIGNED NOT NULL',
                    ),
                )
            }
        )

    def use(self) -> str:
        """Retuns a USE statement"""
        return f'USE {self._name}'
