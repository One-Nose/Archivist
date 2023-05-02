from pytest import fixture

from src.column_types import ColumnType, IntColumnType, StrColumnType


class TestColumnType:
    class Empty(ColumnType):
        _SQL = 'EMPTY'

    @fixture(scope='module')
    def column_type(self):
        return ColumnType(123)

    @fixture(scope='module')
    def empty(self):
        return self.Empty(123)

    def test___init__(self, column_type: ColumnType):
        assert column_type.value == 123

    class Test__str__:
        def test_int(self, column_type: ColumnType):
            assert str(column_type) == '123'

        def test_str(self):
            assert str(ColumnType('value')) == 'value'

    def test__sql(self, empty: Empty):
        assert getattr(empty, '_sql')() == 'EMPTY'

    def test_sql(self, empty: Empty):
        assert empty.sql() == 'EMPTY NOT NULL'


class TestIntColumnType:
    @fixture(scope='module')
    def column_type(self):
        return IntColumnType(123)

    def test___init__(self, column_type: IntColumnType):
        assert column_type.value == 123

    class Test__eq__:
        def test_true(self, column_type: IntColumnType):
            assert column_type == IntColumnType(123)

        def test_wrong_value(self, column_type: IntColumnType):
            assert column_type != IntColumnType(456)

        def test_wrong_type(self, column_type: IntColumnType):
            assert column_type != ColumnType(123)

    class Test_sql:
        class Signed(IntColumnType):
            _SIGNED = True

        def test_signed(self):
            assert getattr(self.Signed(123), '_sql')() == 'INT'

        def test_unsigned(self, column_type: IntColumnType):
            assert getattr(column_type, '_sql')() == 'INT UNSIGNED'

    def test_primary_key(self, column_type: IntColumnType):
        assert (
            column_type.primary_key().sql() == 'INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'
        )


class TestStrColumnType:
    def test___init__(self):
        assert StrColumnType('type').value == 'type'
