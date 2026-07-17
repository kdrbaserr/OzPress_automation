"""Müşteri ekleme ve müşteri detay pencereleri."""
import sqlite3

from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPlainTextEdit, QTableWidgetItem, QVBoxLayout, QWidget

from components import Card, DataTable, PrimaryButton, SecondaryButton, page_actions
from customers import create_customer, customer_detail, format_customer_balance, update_customer


class CustomerDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, customer_id: int | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.customer_id = customer_id
        self.setWindowTitle("Müşteri Düzenle" if customer_id else "Yeni Müşteri")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("Ad soyad veya firma ünvanı")
        self.phone = QLineEdit()
        self.email, self.tax_office, self.tax_no = QLineEdit(), QLineEdit(), QLineEdit()
        self.address, self.note = QPlainTextEdit(), QPlainTextEdit()
        form.addRow("Ad soyad / Firma", self.name)
        form.addRow("Telefon", self.phone)
        form.addRow("E-posta", self.email)
        form.addRow("Vergi dairesi", self.tax_office)
        form.addRow("VKN / TCKN", self.tax_no)
        form.addRow("Adres", self.address)
        form.addRow("Not", self.note)
        layout.addLayout(form)
        cancel = SecondaryButton("Vazgeç")
        cancel.clicked.connect(self.reject)
        save = PrimaryButton("Müşteriyi Kaydet")
        save.clicked.connect(self.save)
        layout.addWidget(page_actions(cancel, save))
        if customer_id:
            self.load_customer()

    def load_customer(self) -> None:
        customer, _, _ = customer_detail(self.connection, self.customer_id)
        if not customer: self.reject(); return
        self.name.setText(customer["unvan"]); self.phone.setText(customer["telefon"] or ""); self.email.setText(customer["eposta"] or "")
        self.tax_office.setText(customer["vergi_dairesi"] or ""); self.tax_no.setText(customer["vergi_no"] or "")
        self.address.setPlainText(customer["adres"] or ""); self.note.setPlainText(customer["notlar"] or "")

    def save(self) -> None:
        if not self.name.text().strip():
            self.name.setFocus()
            return
        values=dict(unvan=self.name.text(), telefon=self.phone.text(), adres=self.address.toPlainText(), notlar=self.note.toPlainText(), eposta=self.email.text(), vergi_dairesi=self.tax_office.text(), vergi_no=self.tax_no.text())
        if self.customer_id: update_customer(self.connection, self.customer_id, **values); customer_id=self.customer_id
        else: customer_id = create_customer(self.connection, **values)
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
        balance = QLabel(f"Güncel bakiye: {format_customer_balance(float(customer['bakiye']))}")
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
