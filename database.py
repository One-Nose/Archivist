"""Access the database and make queries"""
from MySQLdb import connect, Connection
from MySQLdb.cursors import Cursor


class Database:
    """Allows access to the database"""
    database: Connection
    cursor: Cursor

    def __init__(self, config: dict) -> None:
        self.database = connect(**config.get('connect', {}))
        self.cursor = self.database.cursor()

    def get_tables(self) -> list:
        """:return: A list of the tables in the database"""
        self.cursor.execute("""SHOW TABLES""")
        return self.cursor.fetchone()
