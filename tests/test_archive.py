from json import load

from pytest import fixture

from src.analyzer import Analyzer
from src.archive import Archive, ArchiveConfig, Category


class TestArchive:
    @fixture(scope='module')
    def config(self):
        with open('config.json') as file:
            return load(file)

    @fixture(scope='module')
    def archive(self, config: ArchiveConfig):
        archive = Archive(config)
        yield archive
        archive.close()

    class Test__init__:
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

    def test___repr__(self, archive: Archive, config: ArchiveConfig):
        assert repr(archive) == f'Archive({repr(config["connect"]["database"])})'

