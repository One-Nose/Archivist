"""Access the database and make queries"""
from collections.abc import Sequence

from MySQLdb import connect, Connection
from MySQLdb.cursors import Cursor


class Database:
    """Allows access to the database"""
    database: Connection
    cursor: Cursor

    def __init__(self, config: dict) -> None:
        self.database = connect(**config.get('connect', {}))
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
