"""User interface to access the app"""

from re import match
from socket import gethostname

from mariadb import Error
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .archive import Archive
from .registry import get_archive_password, get_key, set_connection


class MainWindow(QMainWindow):
    """Represents the main window"""

    _database: QLineEdit
    _drop_button: QPushButton
    _password: QLineEdit
    _username: QLineEdit
    archive: Archive

    def __init__(self) -> None:
        super().__init__()

        self.archive = Archive()
        self.setWindowTitle('Archivist Administer User Interface')
        self.setFixedSize(400, 300)

        self._username = QLineEdit()
        self._username.setPlaceholderText('Username...')

        self._password = QLineEdit()
        self._password.setPlaceholderText('Password...')

        self._database = QLineEdit()
        self._database.setPlaceholderText('Database...')

        layout = QVBoxLayout()

        layout.addWidget(QLabel('Connection Details:'))
        layout.addWidget(self._username)
        layout.addWidget(self._password)
        layout.addWidget(self._database)
        update_connection = QPushButton('Update Connection Details')
        update_connection.clicked.connect(self._update_connection)
        layout.addWidget(update_connection)

        connect = QPushButton('Connect to database')
        connect.clicked.connect(self._connect)
        layout.addWidget(connect)

        self._drop_button = QPushButton('Destroy Database')
        self._drop_button.setEnabled(False)
        self._drop_button.clicked.connect(self._drop)
        layout.addWidget(self._drop_button)

        view_password = QPushButton('View Archive Password')
        view_password.clicked.connect(self._show_password)
        layout.addWidget(view_password)

        view_key = QPushButton('View Key')
        view_key.clicked.connect(self._show_key)
        layout.addWidget(view_key)

        view_host = QPushButton('View Host Name')
        view_host.clicked.connect(self._show_host)
        layout.addWidget(view_host)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _connect(self) -> None:
        """Creates the archive if does not exist and connects to it"""

        try:
            self.archive.connect()
            self._drop_button.setEnabled(True)

            success = QMessageBox()
            success.setIcon(QMessageBox.Icon.Information)
            success.setWindowTitle('Success')
            success.setText('Connected to database.')
            success.exec()

        except Error:
            error = QMessageBox()
            error.setIcon(QMessageBox.Icon.Critical)
            error.setWindowTitle('Error')
            error.setText('Could not connect to the database')
            error.exec()

    def _drop(self) -> None:
        """Destroys the database"""

        query = QMessageBox()
        query.setIcon(QMessageBox.Icon.Warning)
        query.setWindowTitle('Are You Sure?')
        query.setText(
            'Are you sure you want to destroy the database?\nThis action is IRREVERSIBLE!'
        )
        query.addButton(QMessageBox.StandardButton.Cancel)
        query.addButton(QMessageBox.StandardButton.Yes)

        if query.exec() == QMessageBox.StandardButton.Yes:
            self.archive.drop()
            self._drop_button.setEnabled(False)

    def _show_host(self) -> None:
        """Shows the host name"""

        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle('Host Name')
        message_box.setText(gethostname())
        message_box.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message_box.setFont(QFont('Consolas'))
        message_box.exec()

    def _show_key(self) -> None:
        """Shows the key"""

        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle('Key')
        message_box.setText(get_key())
        message_box.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message_box.setFont(QFont('Consolas'))
        message_box.exec()

    def _show_password(self) -> None:
        """Shows the archive password"""

        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle('Archive Password')
        message_box.setText(get_archive_password())
        message_box.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message_box.setFont(QFont('Consolas'))
        message_box.exec()

    def _update_connection(self) -> None:
        """Updates the connection details according to the input"""

        try:
            username = self._username.text()
            password = self._password.text()
            database = self._database.text()

            for text in username, password, database:
                assert match(r'^[a-z_]*$', text)

            set_connection(
                username=self._username.text(),
                password=self._password.text(),
                database=self._database.text(),
            )

            success = QMessageBox()
            success.setIcon(QMessageBox.Icon.Information)
            success.setWindowTitle('Success')
            success.setText('Updated connection details.')
            success.exec()
        except AssertionError:
            error = QMessageBox()
            error.setIcon(QMessageBox.Icon.Critical)
            error.setWindowTitle('Error')
            error.setText('Invalid connection details.')
            error.exec()

        self._username.setText('')
        self._password.setText('')
        self._database.setText('')


def display() -> None:
    """Displays the main window and blocks the program"""

    window.show()
    app.exec()


app = QApplication([])
window = MainWindow()
