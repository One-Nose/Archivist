"""User interface to access the app"""

from re import match

from mariadb import OperationalError
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
from .registry import set_connection


class MainWindow(QMainWindow):
    """Represents the main window"""

    _archive: Archive
    _database: QLineEdit
    _drop_button: QPushButton
    _password: QLineEdit
    _username: QLineEdit

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle('Archivist Administer User Interface')
        self.setFixedSize(400, 200)

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

        connect = QPushButton('Create Database (unless exists) and Connect to it')
        connect.clicked.connect(self._connect)
        layout.addWidget(connect)

        self._drop_button = QPushButton('Destroy Database')
        self._drop_button.setEnabled(False)
        self._drop_button.clicked.connect(self._drop)
        layout.addWidget(self._drop_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _connect(self) -> None:
        """Creates the archive if does not exist and connects to it"""

        try:
            self._archive = Archive()
            self._drop_button.setEnabled(True)

            success = QMessageBox()
            success.setIcon(QMessageBox.Icon.Information)
            success.setWindowTitle('Success')
            success.setText('Connected to database.')
            success.exec()

        except OperationalError:
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
            self._archive.drop()
            self._drop_button.setEnabled(False)

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
