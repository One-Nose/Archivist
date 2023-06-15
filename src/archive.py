"""Provides archive user operations"""
from __future__ import annotations

from typing import Generic, TypeVar

from .cells import Category as _Category
from .cells import Document as _Document
from .cells import Element as _Element
from .cells import KeyCell, LongText
from .cells import Point as _Point
from .cells import Property as _Property
from .cells import ShortText
from .database import Database


class Archive:
    """Allows access to the database"""

    _database: Database

    def __init__(self) -> None:
        """Creates a Database object according to the optional config object"""

        self._database = Database()

    def __repr__(self) -> str:
        return f'{type(self).__name__}()'

    def add_order_rule(self, large: Property, small: Property) -> None:
        """
        Adds a rule regarding the order of properties of a category
        :param large: The property that must be larger
        :param small: The property that must be smaller
        """

        if large.parent and small.parent:
            assert large.parent == small.parent
        self._database['order_rules'].insert(large=large.id, small=small.id).execute()

    def analyze_rules(self) -> None:
        """Analyzes the archive"""

        self._database.analyzer.analyze_rules()

    def category(self, category_id: int) -> Category:
        """
        Creates a category object to access an existing category
        :param category_id: The category's numeral ID
        :return: A category object that allows access to the category
        """

        return Category(self._database, _Category(category_id))

    def connect(self) -> None:
        """Connects to the database"""

        self._database.connect()

    @property
    def connected(self) -> bool:
        """Whether the database is connected"""

        return self._database.connected

    def close(self) -> None:
        """Closes the connection"""

        self._database.close()

    def commit(self) -> None:
        """Commits the changes to the database"""

        self._database.commit()

    def document(self, identifier: int) -> Document:
        """
        Creates a document object to access an existing document
        :param identifier: The document's numeral ID
        :return: A document object that allows access to the document
        """

        return Document(self._database, _Document(identifier))

    def drop(self) -> None:
        """Deletes the database"""

        self._database.drop()

    def element(self, identifier: int) -> Element:
        """
        Creates an element object to access an existing element
        :param identifier: The element's numeral ID
        :return: An element object to access the element
        """

        return Element(self._database, _Element(identifier))

    def get_categories(self) -> list[dict[str, str | int]]:
        """
        Fetches all categories
        :return: An alphabetical list of categories, in the form of {'id': id, 'name': name}
        """

        return [
            {'id': category['id'], 'name': category['name']}
            for category in self._database['categories']
            .select('id', 'name')
            .order_by('name')
            .execute()
        ]

    def new_category(self, name: str) -> Category:
        """
        Creates a new category
        :param name: The name of the category
        :return: A category object to access the newly created category
        """

        self._database['categories'].insert(name=ShortText(name)).execute()
        return self.category(self._database.last_row_id)

    def new_document(self, name: str) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :return: A document object to access the newly created document
        """

        self._database['documents'].insert(name=ShortText(name)).execute()
        return self.document(self._database.last_row_id)

    def new_element(self, category: Category) -> Element:
        """
        Creates a new element
        :param category: The element's category
        :return: An element object to access the newly created element
        """

        self._database['elements'].insert(category=category.id).execute()
        element_id = self._database.last_row_id

        self._database['properties'].select(element_id, 'id').where(
            category=category.id
        ).into('points', ('element', 'property')).execute()

        return self.element(element_id)

    def point(self, identifier: int) -> Point:
        """
        Creates a point object to access an existing point
        :param identifier: The point's numeral ID
        :return: The newly created point object
        """

        return Point(self._database, _Point(identifier))

    def property(self, identifier: int) -> Property:
        """
        Creates a property object with an unknown parent to access a category's property
        :param identifier: The property's ID
        :return: The newly created property object
        """

        return Property(self._database, _Property(identifier))

    def reset(self) -> None:
        """Completely resets the database"""

        self.drop()
        self._database.init()


PrimaryKey = TypeVar('PrimaryKey', bound=KeyCell)


class Row(Generic[PrimaryKey]):
    """Interface to allow access to part of an archive"""

    _database: Database
    id: PrimaryKey

    def __init__(self, database: Database, identifier: PrimaryKey) -> None:
        """
        Creates a proxy object to access a part of an archive
        :param database: The proxy's database
        :param identifier: The row's ID
        """

        self._database = database
        self.id = identifier

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, type(self)):
            return self.id == __value.id
        return False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'


class Category(Row[_Category]):
    """Allows access to a category"""

    _NO_CATEGORY = _Category(0)

    def get_name(self) -> str:
        """
        Fetches the category's name
        :return: The category's name
        """

        return (
            self._database['categories']
            .select('name')
            .where(id=self.id)
            .execute()[0]['name']
        )

    def get_order_rules(self) -> list[dict[str, str]]:
        """
        Fetches the category's order rules
        :return: A list of order rules, as {'large': name, 'small': name}
        """

        return [
            {'large': rule['large.name'], 'small': rule['small.name']}
            for rule in (
                self._database.table_references(
                    'order_rules', 'properties as large', 'properties as small'
                )
                .select('large.name', 'small.name')
                .where(
                    **{
                        'order_rules.large': 'large.id',
                        'order_rules.small': 'small.id',
                        'large.category': self.id,
                        'small.category': self.id,
                    }
                )
            ).execute()
        ]

    def get_property_names(self) -> list[str]:
        """
        Fetches the category's properties' names
        :return: An alphabetical list of the properties' names
        """

        return [
            property['name']
            for property in self._database['properties']
            .select('name')
            .where(category=self.id)
            .order_by('name')
            .execute()
        ]

    def new_property(self, name: str) -> Property:
        """
        Adds a property to the category
        :param name: The property's name
        :return: A property object to access the newly created property
        """

        self._database['properties'].insert(
            category=self.id, name=ShortText(name)
        ).execute()

        return self.property(self._database.last_row_id)

    def property(self, identifier: int) -> Property:
        """
        Creates a property object to access a property of the category
        :param identifier: The property's ID
        :return: The created property object
        """

        return Property(self, _Property(identifier))


class Document(Row[_Document]):
    """Allows access to a document"""

    def declare_description(self, element: Element, description: str) -> None:
        """Adds a declaration of a description of an element to the document"""

        self._database['descriptions'].insert(
            document=self.id, element=element.id, description=LongText(description)
        ).execute()

    def declare_order(self, large: Point, small: Point) -> None:
        """
        Declares an order of two properties of elements
        :param large: The property that must be larger, in the form of (element, property)
        :param small: The property that must be smaller, in the form of (element, property)
        """

        self._database['orders'].insert(
            document=self.id, large=large.id, small=small.id
        ).execute()

        self._database.analyzer.analyze_order(large.id, small.id)


class Element(Row[_Element]):
    """Allows access to an element"""


class Point(Row[_Point]):
    """Allows access to a point"""


class Property(Row[_Property]):
    """Allows access to a category property"""

    parent: Category | None

    def __init__(self, parent: Category | Database, identifier: _Property) -> None:
        """
        Creates a property object to access a property
        :param parent: Either the category parent or the database parent of the property
        :param identifier: The property's ID
        """

        super().__init__(
            parent._database if isinstance(parent, Category) else parent, identifier
        )

        self.parent = parent if isinstance(parent, Category) else None
