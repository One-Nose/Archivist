from json import load

from mariadb import InterfaceError
from pytest import fixture, raises

from src.archive import ConnectionConfig
from src.column_types import Category, Declaration, Document, ShortText
from src.database import Column, Database, Statement, Table


@fixture
def connect_options():
    with open('config.json') as file:
        return load(file)['connect']


@fixture
def connected_database(database: Database):
    database.connect()
    yield database
    database.close()


@fixture
def database(connect_options: dict[str, str]):
    return Database(**connect_options)


class TestColumn:
    @fixture
    def column(self):
        return Column('column', Category)

    class Test__init__:
        def test_name(self, column: Column):
            assert getattr(column, '_name') == 'column'

        def test_type(self, column: Column):
            assert getattr(column, '_type') == Category

    def test___repr__(self, column: Column):
        assert repr(column) == 'column INT NOT NULL'


class TestStatement:
    class Test__init__:
        @fixture
        def statement(self, database: Database):
            return Statement(database, 'NOOP', ['param1', 'param2'])

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(self, statement: Statement):
            assert getattr(statement, '_statement') == 'NOOP'

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == ('param1', 'param2')

    def test_execute(self, connected_database: Database):
        Statement(connected_database, 'SELECT ?', (1,)).execute()
        assert connected_database.cursor.fetchall() == [(1,)]


class TestTable:
    @fixture
    def table(self, database: Database):
        return Table(database, 'table', column1=Category, column2=Declaration)

    class Test__init__:
        def test_database(self, table: Table, database: Database):
            assert getattr(table, '_database') is database

        def test_name(self, table: Table):
            assert table.name == 'table'

        def test_column1_name(self, table: Table):
            assert getattr(table['column1'], '_name') == 'column1'

        def test_column1_type(self, table: Table):
            assert getattr(table['column1'], '_type') is Category

        def test_column2_name(self, table: Table):
            assert getattr(table['column2'], '_name') == 'column2'

        def test_column2_type(self, table: Table):
            assert getattr(table['column2'], '_type') is Declaration

    class TestCreate:
        @fixture
        def statement(self, table: Table):
            return table.create()

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(self, statement: Statement):
            assert (
                getattr(statement, '_statement')
                == 'CREATE TABLE table (column1 INT NOT NULL, column2 INT UNSIGNED NOT NULL)'
            )

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == ()

    class TestInsert:
        @fixture
        def statement(self, table: Table):
            return table.insert(column1=Category(123), column2=Declaration(456))

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(self, statement: Statement):
            assert (
                getattr(statement, '_statement')
                == 'INSERT INTO table (column1, column2) VALUES (?, ?)'
            )

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == (123, 456)

    class TestSelect:
        @fixture
        def statement(self, table: Table):
            return table.select(
                'column1', 'column2', column1=Category(123), column2=Declaration(456)
            )

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(self, statement: Statement):
            assert (
                getattr(statement, '_statement')
                == 'SELECT column1, column2 FROM table WHERE column1 = ? AND column2 = ?'
            )

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == (123, 456)


class TestDatabase:
    class Test__init__:
        def test_username(self, database: Database, connect_options: ConnectionConfig):
            assert getattr(database, '_username') == connect_options['username']

        def test_password(self, database: Database, connect_options: ConnectionConfig):
            assert getattr(database, '_password') == connect_options['password']

        def test_name(self, database: Database, connect_options: ConnectionConfig):
            assert database.name == connect_options['database']

        def test_tables(self, database: Database):
            assert len(database) == 8

    class TestClose:
        @fixture
        def database(self, database: Database):
            database.connect()
            database.close()
            return database

        def test_cursor(self, database: Database):
            assert database.cursor.closed

        def test_connection(self, database: Database):
            with raises(InterfaceError):
                getattr(database, '_connection').ping()

    def test_commit(self, connected_database: Database):
        connected_database['documents'].insert(name=ShortText('Document')).execute()
        document_id = connected_database.last_row_id
        connected_database.commit()
        connected_database.close()

        connected_database.connect()
        connected_database['documents'].select(
            'name', id=Document(document_id)
        ).execute()
        assert connected_database.cursor.fetchall() == [('Document',)]

    class TestConnect:
        def test_exists(self, connected_database: Database):
            assert getattr(connected_database, '_connection').ping() is None

        def test_abscent(self, connected_database: Database):
            connected_database.drop()
            connected_database.close()

            connected_database.connect()
            connected_database.cursor.execute('SHOW TABLES')
            assert len(connected_database.cursor.fetchall()) == 8

    def test_drop(
        self, connected_database: Database, connect_options: ConnectionConfig
    ):
        connected_database.drop()
        connected_database.cursor.execute('SHOW DATABASES')
        assert (
            connect_options['database'],
        ) not in connected_database.cursor.fetchall()

    def test_init(self, connected_database: Database):
        connected_database.drop()
        connected_database.init()
        connected_database.cursor.execute('SHOW TABLES')
        assert len(connected_database.cursor.fetchall()) == 8

    class TestUse:
        @fixture
        def statement(self, database: Database):
            return database.use()

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(
            self, statement: Statement, connect_options: ConnectionConfig
        ):
            assert (
                getattr(statement, '_statement') == f'USE {connect_options["database"]}'
            )

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == ()

    class TestStatement:
        @fixture
        def statement(self, database: Database):
            return database.statement('NOOP', [123, 456])

        def test_database(self, statement: Statement, database: Database):
            assert getattr(statement, '_database') is database

        def test_statement(self, statement: Statement):
            assert getattr(statement, '_statement') == 'NOOP'

        def test_params(self, statement: Statement):
            assert getattr(statement, '_params') == (123, 456)

    class TestTable:
        @fixture
        def table(self, database: Database):
            return database.table('table', column1=Category, column2=Declaration)

        def test_database(self, table: Table, database: Database):
            assert getattr(table, '_database') is database

        def test_name(self, table: Table):
            assert table.name == 'table'

        def test_column1_name(self, table: Table):
            assert getattr(table['column1'], '_name') == 'column1'

        def test_column1_type(self, table: Table):
            assert getattr(table['column1'], '_type') is Category

        def test_column2_name(self, table: Table):
            assert getattr(table['column2'], '_name') == 'column2'

        def test_column2_type(self, table: Table):
            assert getattr(table['column2'], '_type') is Declaration

    def test_last_row_id(self, connected_database: Database):
        connected_database.drop()
        connected_database.init()
        connected_database['documents'].insert(name=ShortText('Document')).execute()
        assert connected_database.last_row_id == 1
