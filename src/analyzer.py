"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .archive import Archive


class Analyzer:
    """Analyzes an archive"""

    _archive: Archive

    def __init__(self, archive: Archive) -> None:
        """
        Creates an analyzer for an archive
        :param archive: The archive to analyze
        """
        self._archive = archive

    def init(self) -> None:
        """Creates the tables for analyzing"""

        self._archive.create_table(
            'elements',
            id='INT AUTO_INCREMENT PRIMARY KEY',
            type='INT NOT NULL',
        )
