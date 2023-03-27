"""Access the database and make queries"""
from collections.abc import Sequence

from MySQLdb import connect, Connection
from MySQLdb.cursors import Cursor


class Database:
    """Allows access to the database"""
    database: Connection
    cursor: Cursor

    def __init__(self, config: dict) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """
        config_connect = config.get('connect', {})
        self.database = connect(
            user=config_connect.get('user'),
            password=config_connect.get('password'),
            database=config_connect.get('database'),
        )
        self.cursor = self.database.cursor()

    def create_table(self, table: str, columns: Sequence[tuple[str, str]]) -> None:
        """
        Creates a table
        :param columns: The columns of the table. Each column is in the form of (name, type)
        :param table: The name of the table
        """
        self.cursor.execute(f"""CREATE TABLE %s ({'%s %s, ' * len(columns)});""", (table, *[*columns]))

    def create_tables(self) -> None:
        """Creates the required tables for the database"""
        # TODO: Implement function
