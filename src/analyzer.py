"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .archive import Archive


class Analyzer:
    """Analyzes an archive"""

    _archive: Archive

    def __init__(self, archive: Archive) -> None:
        self._archive = archive
