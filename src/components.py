"""Sayfalarda tekrar kullanılan buton, kart, tablo ve form bileşenleri."""
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


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
