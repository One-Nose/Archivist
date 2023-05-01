from src.column_types import ColumnType, IntColumnType, StrColumnType


class TestColumnType:
    def test_init(self):
        assert ColumnType(123).value == 123

    def test_str_int(self):
        assert str(ColumnType(123)) == '123'

    def test_str_str(self):
        assert str(ColumnType('hello')) == 'hello'

    def test__sql(self):
        class GenericColumnType(ColumnType):
            _SQL = 'GENERIC'

            def test_sql(self):
                return self._sql()

        assert GenericColumnType(123).test_sql() == 'GENERIC'

    def test_sql(self):
        class GenericColumnType(ColumnType):
            _SQL = 'GENERIC'

        assert GenericColumnType(123).sql() == 'GENERIC NOT NULL'


class TestIntColumnType:
    def test_init(self):
        assert IntColumnType(123).value == 123

    def test_eq_true(self):
        assert IntColumnType(123) == IntColumnType(123)

    def test_eq_wrong_id(self):
        assert IntColumnType(123) != IntColumnType(456)

    def test_eq_wrong_type(self):
        assert IntColumnType(123) != ColumnType(123)

    def test_sql_signed(self):
        class SignedIntColumnType(IntColumnType):
            _SIGNED = True

            def test_sql(self):
                return self._sql()

        assert SignedIntColumnType(123).test_sql() == 'INT'

    def test_sql_unsigned(self):
        class UnsignedIntColumnType(IntColumnType):
            def test_sql(self):
                return self._sql()

        assert UnsignedIntColumnType(123).test_sql() == 'INT UNSIGNED'

    def test_primary_key(self):
        assert (
            IntColumnType(123).primary_key().sql()
            == 'INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'
        )


class TestStrColumnType:
    def test_init(self):
        assert StrColumnType('hello').value == 'hello'
