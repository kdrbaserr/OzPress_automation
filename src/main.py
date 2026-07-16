import sys
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from database import initialize_database
from main_window import MainWindow
from offline import verify_offline_only
from theme import APPLICATION_STYLESHEET


if __name__ == "__main__":
    verify_offline_only()
    database = initialize_database()
    app = QApplication(sys.argv)
    app.setStyleSheet(APPLICATION_STYLESHEET)
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / "Resimler" / "ozsahinLogo.png")))
    window = MainWindow(database)
    window.show()
    exit_code = app.exec()
    database.close()
    sys.exit(exit_code)
