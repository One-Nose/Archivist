"""Allows access to the registry"""

from winreg import (
    HKEY_CURRENT_USER,
    KEY_WRITE,
    REG_SZ,
    CreateKeyEx,
    OpenKeyEx,
    QueryValueEx,
    SetValueEx,
)


def get_database() -> str:
    """
    Fetches the name of the database from the registry
    :return: The name of the database
    """

    with OpenKeyEx(HKEY_CURRENT_USER, r'SOFTWARE\\Archivist\\') as archivist:
        return QueryValueEx(archivist, 'Database')[0]


def get_connection() -> dict[str, str]:
    """
    Fetches the username and password from the registry
    :return: The connection details, in the form of {'user': username, 'password': password}
    """

    with OpenKeyEx(HKEY_CURRENT_USER, r'SOFTWARE\\Archivist\\') as archivist:
        return {
            'user': QueryValueEx(archivist, 'Username')[0],
            'password': QueryValueEx(archivist, 'Password')[0],
        }


def set_connection(username: str, password: str, database: str) -> None:
    """
    Sets the connection registry keys
    :param username: The username to set to
    :param password: The password to set to
    :param database: The database to set to
    """

    with OpenKeyEx(
        HKEY_CURRENT_USER, r'SOFTWARE\\Archivist\\', access=KEY_WRITE
    ) as archivist:
        if username:
            SetValueEx(archivist, 'Username', 0, REG_SZ, username)
        if password:
            SetValueEx(archivist, 'Password', 0, REG_SZ, password)
        if database:
            SetValueEx(archivist, 'Database', 0, REG_SZ, database)


def setup() -> None:
    """Creates the registry keys if they don't exist"""

    with OpenKeyEx(HKEY_CURRENT_USER, r'SOFTWARE\\') as software:
        try:
            with OpenKeyEx(software, r'Archivist\\'):
                pass
        except FileNotFoundError:
            with CreateKeyEx(software, 'Archivist') as archivist:
                SetValueEx(archivist, 'Username', 0, REG_SZ, 'root')
                SetValueEx(archivist, 'Password', 0, REG_SZ, 'root')
                SetValueEx(archivist, 'Database', 0, REG_SZ, 'archivist')
