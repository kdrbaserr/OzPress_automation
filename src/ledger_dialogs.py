"""Tahsilat girişi ve cari ekstre pencereleri."""
import sqlite3

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFormLayout, QLabel, QMessageBox, QTableWidgetItem, QVBoxLayout, QWidget

from components import DataTable, PrimaryButton, SecondaryButton, page_actions
from customers import list_customers
from ledger import account_statement, record_collection


class CollectionDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, customer_id: int | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Tahsilat Gir")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.customer = QComboBox()
        for item in list_customers(connection):
            self.customer.addItem(f"{item['kod']} — {item['unvan']}", item["id"])
        if customer_id is not None:
            index = self.customer.findData(customer_id)
            if index >= 0:
                self.customer.setCurrentIndex(index)
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, 10_000_000)
        self.amount.setDecimals(2)
        self.amount.setPrefix("₺ ")
        self.payment_date = QDateEdit(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        self.method = QComboBox()
        self.method.addItems(["Nakit", "Havale"])
        form.addRow("Müşteri", self.customer)
        form.addRow("Tutar", self.amount)
        form.addRow("Tarih", self.payment_date)
        form.addRow("Ödeme şekli", self.method)
        layout.addLayout(form)
        cancel = SecondaryButton("Vazgeç")
        cancel.clicked.connect(self.reject)
        save = PrimaryButton("Tahsilatı Kaydet")
        save.clicked.connect(self.save)
        layout.addWidget(page_actions(cancel, save))

    def save(self) -> None:
        if self.customer.currentData() is None:
            QMessageBox.warning(self, "Müşteri seçin", "Tahsilat için bir müşteri seçin.")
            return
        try:
            record_collection(self.connection, customer_id=self.customer.currentData(), amount=self.amount.value(),
                              payment_date=self.payment_date.date().toPython(), payment_method=self.method.currentText())
        except ValueError as error:
            QMessageBox.warning(self, "Tahsilat kaydedilemedi", str(error))
            return
        self.accept()


class StatementDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, customer_id: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cari Hesap Ekstresi")
        self.resize(760, 500)
        layout = QVBoxLayout(self)
        table = DataTable(["Tarih", "Açıklama", "Borç", "Alacak", "Bakiye", "Ödeme"])
        for movement in account_statement(connection, customer_id):
            row = table.rowCount()
            table.insertRow(row)
            values = [movement["hareket_tarihi"], movement["aciklama"] or "-", f"{movement['borc']:.2f} ₺" if movement["borc"] else "-",
                      f"{movement['alacak']:.2f} ₺" if movement["alacak"] else "-", f"{movement['bakiye']:.2f} ₺",
                      movement["odeme_sekli"] or "-"]
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))
        layout.addWidget(table)
        close = SecondaryButton("Kapat")
        close.clicked.connect(self.accept)
        layout.addWidget(page_actions(close))
