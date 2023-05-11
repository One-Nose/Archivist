"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .cells import Axis, Boolean, Point, UnsignedInt

if TYPE_CHECKING:
    from .database import Database


class Analyzer:
    """Analyzes an archive"""

    LARGEST_VALUE = 2**32 - 1

    _database: Database

    def __init__(self, database: Database) -> None:
        """
        Creates an analyzer for an archive
        :param database: The database to analyze
        """

        self._database = database

    def analyze_order(self, large: Point, small: Point) -> None:
        """
        Analyzes two points with a known order and saves the results in analysis
        :param large: The larger point
        :param small: The smaller point
        """

        self._database['axes'].insert().execute()
        axis = Axis(self._database.last_row_id)
        self._database['analysis'].insert_many(
            ('point', 'axis', 'value'),
            (large, axis, UnsignedInt(self.LARGEST_VALUE)),
            (small, axis, UnsignedInt(0)),
        ).execute()

    def analyze_rules(self) -> None:
        """
        Analyzes the unanalyzed points according to order_rules and saves the results in analysis
        """

        for order in self._unanalyzed_orders():
            self.analyze_order(*order)

    def _unanalyzed_orders(self) -> list[tuple[Point, Point]]:
        """
        Fetches the order_rules ordering of unanalyzed points
        :return: A list of unanalyzed orders, each in the form of (large, small)
        """

        results = (
            self._database.table_refrences(
                'points AS large', 'points AS small', 'order_rules'
            )
            .select('large.id', 'small.id')
            .where(
                **{
                    'large.analyzed': Boolean(False),
                    'small.analyzed': Boolean(False),
                    'large.element': 'small.element',
                    'large.property': 'order_rules.large',
                    'small.property': 'order_rules.small',
                }
            )
            .execute()
        )

        return [tuple(Point(id) for id in points) for points in results]
