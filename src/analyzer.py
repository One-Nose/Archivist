"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database


class Analyzer:
    """Analyzes an archive"""

    _database: Database

    def __init__(self, database: Database) -> None:
        """
        Creates an analyzer for an archive
        :param database: The database to analyze
        """

        self._database = database

    def analyze(self) -> None:
        """Analyzes the database and saves the results in the database"""
