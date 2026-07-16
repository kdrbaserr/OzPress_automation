"""Müşteri ekleme ve müşteri detay pencereleri."""
import sqlite3

from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPlainTextEdit, QTableWidgetItem, QVBoxLayout, QWidget

from components import Card, DataTable, PrimaryButton, SecondaryButton, page_actions
from customers import create_customer, customer_detail


class CustomerDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Yeni Müşteri")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("Ad soyad veya firma ünvanı")
        self.phone = QLineEdit()
        self.address, self.note = QPlainTextEdit(), QPlainTextEdit()
        form.addRow("Ad soyad / Firma", self.name)
        form.addRow("Telefon", self.phone)
        form.addRow("Adres", self.address)
        form.addRow("Not", self.note)
        layout.addLayout(form)
        cancel = SecondaryButton("Vazgeç")
        cancel.clicked.connect(self.reject)
        save = PrimaryButton("Müşteriyi Kaydet")
        save.clicked.connect(self.save)
        layout.addWidget(page_actions(cancel, save))

    def save(self) -> None:
        if not self.name.text().strip():
            self.name.setFocus()
            return
        customer_id = create_customer(self.connection, unvan=self.name.text(), telefon=self.phone.text(),
                                      adres=self.address.toPlainText(), notlar=self.note.toPlainText())
        self.done(customer_id)


class CustomerDetailDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, customer_id: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Müşteri Detayı")
        self.resize(760, 610)
        customer, orders, movements = customer_detail(connection, customer_id)
        layout = QVBoxLayout(self)
        if not customer:
            return
        summary = Card(customer["unvan"])
        summary.layout.addWidget(QLabel(f"Telefon: {customer['telefon'] or '-'}\nAdres: {customer['adres'] or '-'}"))
        balance = QLabel(f"Güncel bakiye: {float(customer['bakiye']):.2f} ₺")
        balance.setStyleSheet("font-size: 20px; font-weight: 700; color: #17A2A4;")
        summary.layout.addWidget(balance)
        if customer["notlar"]:
            summary.layout.addWidget(QLabel(f"Not: {customer['notlar']}"))
        layout.addWidget(summary)
        layout.addWidget(QLabel("Geçmiş siparişler"))
        order_table = DataTable(["Sipariş No", "Tarih", "Proje", "Durum", "Toplam"])
        for row_data in orders:
            row = order_table.rowCount()
            order_table.insertRow(row)
            for column, value in enumerate(row_data):
                order_table.setItem(row, column, QTableWidgetItem(str(value)))
        layout.addWidget(order_table)
        layout.addWidget(QLabel("Cari hareketler"))
        movement_table = DataTable(["Tarih", "Tip", "Tutar", "Açıklama"])
        for row_data in movements:
            row = movement_table.rowCount()
            movement_table.insertRow(row)
            for column, value in enumerate(row_data):
                movement_table.setItem(row, column, QTableWidgetItem(str(value or "-")))
        layout.addWidget(movement_table)
        close = SecondaryButton("Kapat")
        close.clicked.connect(self.accept)
        layout.addWidget(page_actions(close))
