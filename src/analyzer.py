"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .archive import Archive, Declaration


class Analyzer:
    """Analyzes an archive"""

    _archive: Archive

    def __init__(self, archive: Archive) -> None:
        """
        Creates an analyzer for an archive
        :param archive: The archive to analyze
        """
        self._archive = archive

    def analyze_declaration(self, declaration: Declaration) -> None:
        """
        Analyzes a declaration and saves the result in the database
        :param declaration: The declaration to analyze
        """
