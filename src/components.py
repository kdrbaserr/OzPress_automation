"""Sayfalarda tekrar kullanılan buton, kart, tablo ve form bileşenleri."""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from images import resolve_image_path


class PrimaryButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("primaryButton")


class SecondaryButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("secondaryButton")


class Card(QFrame):
    def __init__(self, title: str | None = None) -> None:
        super().__init__()
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)
        self.layout.setSpacing(12)
        if title:
            heading = QLabel(title)
            heading.setObjectName("cardTitle")
            self.layout.addWidget(heading)


class DataTable(QTableWidget):
    def __init__(self, headers: list[str]) -> None:
        super().__init__(0, len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setMinimumHeight(220)

    def add_demo_row(self, values: list[str]) -> None:
        row = self.rowCount()
        self.insertRow(row)
        for column, value in enumerate(values):
            self.setItem(row, column, QTableWidgetItem(value))


class ThumbnailLabel(QLabel):
    """Ürün listelerinde kullanılan küçük görsel önizlemesi."""
    def __init__(self, image_path: str | None, size: int = 52) -> None:
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: #EEF3F6; border: 1px solid #DDE4EA; border-radius: 5px; color: #72808B;")
        resolved_path = resolve_image_path(image_path)
        pixmap = QPixmap(str(resolved_path)) if resolved_path else QPixmap()
        if pixmap.isNull():
            self.setText("Görsel\nyok")
            return
        self.setPixmap(pixmap.scaled(size - 4, size - 4, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class FormCard(Card):
    def __init__(self, title: str, fields: list[str]) -> None:
        super().__init__(title)
        form = QFormLayout()
        self.inputs: dict[str, QLineEdit] = {}
        for field in fields:
            input_widget = QLineEdit()
            self.inputs[field] = input_widget
            form.addRow(field, input_widget)
        self.layout.addLayout(form)


def page_actions(*buttons: QPushButton) -> QWidget:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch()
    for button in buttons:
        layout.addWidget(button)
    return container
