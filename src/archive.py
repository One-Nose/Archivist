"""Provides archive user operations"""
from __future__ import annotations

from typing import Generic, TypedDict, TypeVar

from .analyzer import Analyzer
from .column_types import Category as _Category
from .column_types import Declaration as _Declaration
from .column_types import Document as _Document
from .column_types import IntColumnType
from .column_types import Property as _Property
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

    _analyzer: Analyzer
    database: Database
    greater: Category
    less: Category

    def __init__(self, config: ArchiveConfig) -> None:
        """
        Creates a Database object according to the optional config object
        :param config: An object containing the config options
        """

        self.database = Database(**config['connect'])
        self._analyzer = Analyzer(self)

        self.greater = Category(self, _Category(-1))
        self.less = Category(self, _Category(-2))

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.database.name)})'

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
        elif property1[1]:
            assert property1[1].parent == property1[0].category

        if isinstance(property2, Property):
            property2 = (property2, None)
        elif property2[1]:
            assert property2[1].parent == property2[0].category

        assert property1[0].parent == property2[0].parent

        self.database['rules'].insert(
            category=category.id.value,
            property1=property1[0].id.value,
            subproperty1=property1[1].id.value if property1[1] else 0,
            property2=property2[0].id.value,
            subproperty2=property2[1].id.value if property2[1] else 0,
        ).execute()

    def category(self, category_id: int) -> UserDefinedCategory:
        """
        Creates a category object to access an existing category
        :param category_id: The category's numeral ID
        :return: A category object that allows access to the category
        """

        return UserDefinedCategory(self, _Category(category_id))

    def close(self) -> None:
        """Closes the connection"""

        self.database.close()

    def commit(self) -> None:
        """Commits the changes to the database"""

        self.database.commit()

    def document(self, document_id: int) -> Document:
        """
        Creates a document object to access an existing document
        :param document_id: The document's numeral ID
        :return: A document object that allows access to the document
        """

        return Document(self, _Document(document_id))

    def drop(self) -> None:
        """Deletes the database"""

        self.database.drop()

    def new_category(self, name: str) -> UserDefinedCategory:
        """
        Creates a new category
        :param name: The name of the category
        :return: A category object to access the newly created category
        """

        self.database['categories'].insert(name=name).execute()
        return UserDefinedCategory(self, _Category(self.database.lastrowid))

    def new_document(self, name: str) -> Document:
        """
        Creates a new document
        :param name: The name of the document
        :return: A document object to access the newly created document
        """

        self.database['documents'].insert(name=name).execute()
        return Document(self, _Document(self.database.lastrowid))

    def reset(self) -> None:
        """Completely resets the database"""

        self.drop()
        self.database.init()


PrimaryKey = TypeVar('PrimaryKey', bound=IntColumnType)


class Row(Generic[PrimaryKey]):
    """Interface to allow access to part of an archive"""

    _archive: Archive
    id: PrimaryKey

    def __init__(self, archive: Archive, identifier: PrimaryKey) -> None:
        """
        Creates a proxy object to access a part of an archive
        :param archive: The proxy's archive
        :param identifier: The row's ID
        """

        self._archive = archive
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

    def new_property(
            self, name: str, category: UserDefinedCategory | None = None
    ) -> Property:
        """
        Adds a property to the category
        :param name: The property's name
        :param category: The property's optional category
        :return: A property object to access the newly created property
        """

        self._archive.database['properties'].insert(
            parent=self.id.value,
            name=name,
            category=category.id.value if category else 0,
        ).execute()
        return Property(
            self._archive, _Property(self._archive.database.lastrowid), self, category
        )


class Declaration(Row[_Declaration]):
    """Allows access to a declaration of an element"""

    def add_description(self, description: str) -> None:
        """
        Adds a description to the declaration
        :param description: The description to add
        """

        self._archive.database['descriptions'].insert(
            declaration=self.id.value, description=description
        ).execute()

    def declare_property(self, declared_property: Property, value: Declaration) -> None:
        """
        Declares a property of the declared element
        :param declared_property: The property to declare
        :param value: The value to declare the property as
        """

        self._archive.database['property_declarations'].insert(
            declaration=self.id.value,
            property=declared_property.id.value,
            value=value.id.value,
        ).execute()


class Document(Row[_Document]):
    """Allows access to a document"""

    def declare(self, category: UserDefinedCategory) -> Declaration:
        """
        Adds a declaration of an element to the document
        :param category: The category of the declared element
        :return: A declaration object to access the declaration
        """

        self._archive.database['declarations'].insert(
            document=self.id.value, category=category.id.value
        ).execute()
        return Declaration(
            self._archive, _Declaration(self._archive.database.lastrowid)
        )


class Property(Row[_Property]):
    """Allows access to a category property"""

    category: UserDefinedCategory | None
    parent: UserDefinedCategory

    def __init__(
            self,
            archive: Archive,
            identifier: _Property,
            parent: UserDefinedCategory,
            category: UserDefinedCategory | None,
    ) -> None:
        super().__init__(archive, identifier)

        self.parent = parent
        self.category = category
