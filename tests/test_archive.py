from json import load

from pytest import fixture

from src.archive import Archive, ArchiveConfig


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

    def test___repr__(self, archive: Archive, config: ArchiveConfig):
        assert repr(archive) == f'Archive({repr(config["connect"]["database"])})'
