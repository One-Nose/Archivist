"""Data analyzing of the archive"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .cells import Axis as _Axis
from .cells import Boolean, Point, UnsignedInt

if TYPE_CHECKING:
    from .database import Database

LARGEST_VALUE = 2 ** 32 - 1


class Analyzer:
    """Analyzes an archive"""

    _database: Database

    def __init__(self, database: Database) -> None:
        """
        Creates an analyzer for an archive
        :param database: The database to analyze
        """

        self._database = database

    def _add_axis(self, large: Point, small: Point) -> None:
        """
        Adds a new axis and adds two points to it
        :param large: The larger point to add
        :param small: The smaller point to add
        """

        self._database['axes'].insert().execute()
        axis = _Axis(self._database.last_row_id)

        self._database['analysis'].insert_many(
            ('point', 'axis', 'value'),
            (large, axis, UnsignedInt(LARGEST_VALUE)),
            (small, axis, UnsignedInt(0)),
        ).execute()

    def _axis(self, identifier: int) -> Axis:
        """
        Creates an axis object to access an axis
        :param identifier: The axis's numeral ID
        :return: An axis object
        """

        return Axis(self._database, identifier)

    def _unanalyzed_orders(self) -> list[dict[str, Point]]:
        """
        Fetches the order_rules ordering of unanalyzed points
        :return: A list of unanalyzed orders, each in the form of {'large': point, 'small': Point}
        """

        results = (
            self._database.table_references(
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

        return [
            {'large': Point(points['large.id']), 'small': Point(points['small.id'])}
            for points in results
        ]

    def analyze_order(self, large: Point, small: Point) -> None:
        """
        Analyzes two points with a known order and saves the results in analysis
        :param large: The larger point
        :param small: The smaller point
        """

        matches = (
            self._database['analysis']
            .select('axis', 'point')
            .where_either(
                {'point': large, 'value': UnsignedInt(0)},
                {'point': small, 'value': UnsignedInt(LARGEST_VALUE)},
            )
            .execute()
        )

        large_matches = [match for match in matches if match['point'] == large.value]
        small_matches = [match for match in matches if match['point'] == small.value]

        if len(large_matches) == 1:
            self._axis(large_matches[0]['axis']).add_before(small)

        elif len(small_matches) == 1:
            self._axis(small_matches[0]['axis']).add_after(large)

        else:
            self._add_axis(large, small)

    def analyze_rules(self) -> None:
        """
        Analyzes the unanalyzed points according to order_rules and saves the results in analysis
        """

        for order in self._unanalyzed_orders():
            self.analyze_order(**order)

        self._database['points'].set(analyzed=Boolean(True)).where(
            analyzed=Boolean(False)
        ).execute()


class Axis:
    """Allows access to an axis"""

    _database: Database
    _id: _Axis

    def __init__(self, database: Database, identifier: int) -> None:
        self._database = database
        self._id = _Axis(identifier)

    def add_after(self, point: Point) -> None:
        """
        Adds a point after the last point in the axis
        :param point: The point to add
        """

        largest, second_largest = (
            self._database['analysis']
            .select('id', 'value')
            .where(axis=self._id)
            .order_by('value', descending=True)
            .limit(2)
            .execute()
        )

        new_value: int = (largest['value'] + second_largest['value']) // 2

        self._database['analysis'].set(value=UnsignedInt(new_value)).where(
            id=UnsignedInt(largest['id'])
        ).execute()

        self._add_point(point, LARGEST_VALUE)

    def add_before(self, point: Point) -> None:
        """
        Adds a point before the first point in the axis
        :param point: The point to add
        """

        smallest, second_smallest = (
            self._database['analysis']
            .select('id', 'value')
            .where(axis=self._id)
            .order_by('value')
            .limit(2)
            .execute()
        )

        new_value: int = second_smallest['value'] // 2

        self._database['analysis'].set(value=UnsignedInt(new_value)).where(
            id=UnsignedInt(smallest['id'])
        ).execute()

        self._add_point(point, 0)

    def _add_point(self, point: Point, value: int) -> None:
        """
        Adds a new point to the axis
        :param point: The point to add
        :param value: The point's value within the axis
        """

        self._database['analysis'].insert(
            point=point, axis=self._id, value=UnsignedInt(value)
        ).execute()
