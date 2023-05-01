"""Provides archive user operations"""
from __future__ import annotations

from typing import ClassVar, Generic, TypedDict, TypeVar

from .analyzer import Analyzer
from .column_types import Category as _Category
from .column_types import Declaration as _Declaration
from .column_types import Document as _Document
from .column_types import IntColumnType, LongText
from .column_types import Property as _Property
from .column_types import ShortText as ShortText
from .database import Database


class ArchiveConfig(TypedDict):
    """
    Configuration of the database
    - connect: Configuration of the connection to the database
    """

    connect: ConnectionConfig


class ConnectionConfig(TypedDict):
    """
    Configuration of the connection to the database
    - username: The username to connect to the database
    - password: The password to connect to the database
    - database: The database to connect to (insecure)
    """

    username: str
    password: str
    database: str


class Archive:
    """Allows access to the database"""

    _NO_PROPERTY: ClassVar[_Property] = _Property(0)

    _analyzer: Analyzer
    _database: Database
    greater: Category
    less: Category

    def __init__(self, config: ArchiveConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """

        self._database = Database(**config['connect'])
        self._analyzer = Analyzer(self)

        self.greater = Category(self._database, _Category(-1))
        self.less = Category(self._database, _Category(-2))

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self._database.name)})'

    def add_rule(
        self,
        category: Category,
        property1: tuple[Property, Property | None] | Property,
        property2: tuple[Property, Property | None] | Property,
    ) -> None:
        """
        Adds a rule to the archive
        :param category: The category of the rule, may be built-in
        :param property1: The rule's first argument, either as (property, sub-property) or property
        :param property2: The rule's second argument, either as (property, sub-property) or property
        """

        if isinstance(property1, Property):
            property1 = (property1, None)
        if isinstance(property2, Property):
            property2 = (property2, None)

        assert property1[0].parent == property2[0].parent
        for prop in property1, property2:
            assert prop[1] is None or prop[1].parent == prop[0].category

        self._database['rules'].insert(
            category=category.id,
            property1=property1[0].id,
            subproperty1=property1[1].id if property1[1] else self._NO_PROPERTY,
            property2=property2[0].id,
            subproperty2=property2[1].id if property2[1] else self._NO_PROPERTY,
        ).execute()

    def category(self, category_id: int) -> UserDefinedCategory:
        """
        Creates a category object to access an existing category
        :param category_id: The category's numeral ID
        :return: A category object that allows access to the category
        """

        return UserDefinedCategory(self._database, _Category(category_id))

    def close(self) -> None:
        """Closes the connection"""

        self._database.close()

    def commit(self) -> None:
        """Commits the changes to the database"""

        self._database.commit()

    def document(self, document_id: int) -> Document:
        """
        Creates a document object to access an existing document
        :param document_id: The document's numeral ID
        :return: A document object that allows access to the document
        """

        return Document(self._database, _Document(document_id))

    def drop(self) -> None:
        """Deletes the database"""

        self._database.drop()

    def new_category(self, name: str) -> UserDefinedCategory:
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

    def reset(self) -> None:
        """Completely resets the database"""

        self.drop()
        self._database.init()


PrimaryKey = TypeVar('PrimaryKey', bound=IntColumnType)


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
        return f'{self.__class__.__name__}({self.id.value})'


class Category(Row[_Category]):
    """Allows access to a category"""


class UserDefinedCategory(Category):
    """Allows access to a non-built-in category"""

    _NO_CATEGORY: ClassVar[_Category] = _Category(0)

    def new_property(
        self, name: str, category: UserDefinedCategory | None = None
    ) -> Property:
        """
        Adds a property to the category
        :param name: The property's name
        :param category: The property's optional category
        :return: A property object to access the newly created property
        """

        self._database['properties'].insert(
            parent=self.id,
            name=ShortText(name),
            category=category.id if category else self._NO_CATEGORY,
        ).execute()

        return self.property(self._database.last_row_id, category)

    def property(
        self, identifier: int, category: UserDefinedCategory | None
    ) -> Property:
        """
        Creates a property object to access a property of the category
        :param identifier: The property's ID
        :param category: The property's category
        :return: The created property object
        """

        return Property(self, _Property(identifier), category)


class Declaration(Row[_Declaration]):
    """Allows access to a declaration of an element"""

    def add_description(self, description: str) -> None:
        """
        Adds a description to the declaration
        :param description: The description to add
        """

        self._database['descriptions'].insert(
            declaration=self.id, description=LongText(description)
        ).execute()

    def declare_property(self, declared_property: Property, value: Declaration) -> None:
        """
        Declares a property of the declared element
        :param declared_property: The property to declare
        :param value: The value to declare the property as
        """

        self._database['property_declarations'].insert(
            declaration=self.id, property=declared_property.id, value=value.id
        ).execute()


class Document(Row[_Document]):
    """Allows access to a document"""

    def declare(self, category: UserDefinedCategory) -> Declaration:
        """
        Adds a declaration of an element to the document
        :param category: The category of the declared element
        :return: A declaration object to access the declaration
        """

        self._database['declarations'].insert(
            document=self.id, category=category.id
        ).execute()

        return Declaration(self._database, _Declaration(self._database.last_row_id))


class Property(Row[_Property]):
    """Allows access to a category property"""

    category: UserDefinedCategory | None
    parent: UserDefinedCategory

    def __init__(
        self,
        parent: UserDefinedCategory,
        identifier: _Property,
        category: UserDefinedCategory | None,
    ) -> None:
        super().__init__(parent._database, identifier)

        self.parent = parent
        self.category = category
