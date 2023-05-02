from json import load

from pytest import fixture

from src.analyzer import Analyzer
from src.archive import Archive, Category


class TestArchive:
    class Test__init__:
        @fixture(scope='module')
        def archive(self):
            with open('config.json') as file:
                archive = Archive(load(file))
            yield archive
            archive.close()

        def test_database(self, archive: Archive):
            assert getattr(getattr(archive, '_database'), '_connection').ping() is None

        def test_analyzer(self, archive: Archive):
            analyzer = getattr(archive, '_analyzer')
            assert (type(analyzer), getattr(analyzer, '_archive')) == (
                Analyzer,
                archive,
            )

        def test_greater(self, archive: Archive):
            assert (type(archive.greater), archive.greater.id.value) == (Category, -1)

        def test_less(self, archive: Archive):
            assert (type(archive.less), archive.less.id.value) == (Category, -2)
