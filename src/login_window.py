from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


APPLICATION_PASSWORD = "1415"


class LoginWindow(QMainWindow):
    """Ana uygulamayı açmadan önce gösterilen tam pencere giriş ekranı."""

    authenticated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Özşahin Metal Otomasyon — Giriş")
        self.setMinimumSize(720, 520)

        root = QWidget()
        root.setObjectName("loginRoot")
        outer_layout = QVBoxLayout(root)
        outer_layout.setContentsMargins(36, 36, 36, 36)
        outer_layout.addStretch(1)

        panel = QFrame()
        panel.setObjectName("loginPanel")
        panel.setMaximumWidth(560)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(64, 54, 64, 54)
        panel_layout.setSpacing(18)

        logo = QLabel()
        logo.setObjectName("loginLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = Path(__file__).resolve().parent.parent / "Resimler" / "ozsahinLogo.png"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    330,
                    210,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        panel_layout.addWidget(logo)

        title = QLabel("ÖZPRESS OTOMASYON")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("passwordInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setMaxLength(32)
        self.password_input.returnPressed.connect(self.try_login)
        self.password_input.textChanged.connect(self.clear_error)
        panel_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setObjectName("loginError")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setMinimumHeight(22)
        panel_layout.addWidget(self.error_label)

        login_button = QPushButton("Giriş Yap")
        login_button.setObjectName("loginButton")
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.try_login)
        panel_layout.addWidget(login_button)

        outer_layout.addWidget(panel, 0, Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addStretch(1)
        self.setCentralWidget(root)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.password_input.setFocus()

    def try_login(self) -> None:
        if self.password_input.text() == APPLICATION_PASSWORD:
            self.password_input.clear()
            self.authenticated.emit()
            return

        self.error_label.setText("Şifre hatalı. Lütfen tekrar deneyin.")
        self.password_input.selectAll()
        self.password_input.setFocus()

    def clear_error(self) -> None:
        self.error_label.clear()
