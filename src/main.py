import sys
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from database import initialize_database
from login_window import LoginWindow
from main_window import MainWindow
from offline import verify_offline_only
from theme import APPLICATION_STYLESHEET


if __name__ == "__main__":
    verify_offline_only()
    app = QApplication(sys.argv)
    app.setStyleSheet(APPLICATION_STYLESHEET)
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / "Resimler" / "ozsahinLogo.png")))
    database = None
    window = None

    def open_application() -> None:
        global database, window
        database = initialize_database()
        window = MainWindow(database)
        window.showMaximized()
        login_window.close()

    login_window = LoginWindow()
    login_window.authenticated.connect(open_application)
    login_window.showMaximized()
    exit_code = app.exec()
    if database is not None:
        database.close()
    sys.exit(exit_code)
