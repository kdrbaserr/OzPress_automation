import sys
from PySide6.QtWidgets import QApplication

from database import initialize_database
from main_window import MainWindow


if __name__ == "__main__":
    database = initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec()
    database.close()
    sys.exit(exit_code)
