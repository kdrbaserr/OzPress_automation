"""Katalogdan ürün seçerek proje/sipariş sepeti oluşturan pencere."""
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
    QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from components import PrimaryButton, SecondaryButton, page_actions
from orders import create_order, list_customers
from products import list_products


class OrderDialog(QDialog):
    PROJECT_TYPES = ["Konteyner Ev", "Panel Çatı", "Trapez Çatı", "Diğer"]

    def __init__(self, connection: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.cart: list[dict[str, float | int | str]] = []
        self.setWindowTitle("Yeni Sipariş / Proje")
        self.resize(780, 600)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.project_type = QComboBox()
        self.project_type.addItems(self.PROJECT_TYPES)
        self.customer = QComboBox()
        self._load_customers()
        form.addRow("Proje tipi", self.project_type)
        form.addRow("Müşteri", self.customer)
        layout.addLayout(form)

        product_row = QHBoxLayout()
        self.product = QComboBox()
        self._load_products()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.01, 1_000_000)
        self.quantity.setValue(1)
        self.quantity.setDecimals(2)
        add_button = PrimaryButton("Sepete Ekle")
        add_button.clicked.connect(self.add_to_cart)
        product_row.addWidget(QLabel("Katalog ürünü"))
        product_row.addWidget(self.product, 1)
        product_row.addWidget(QLabel("Miktar"))
        product_row.addWidget(self.quantity)
        product_row.addWidget(add_button)
        layout.addLayout(product_row)

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["Ürün", "Miktar", "Birim fiyat", "Ara toplam", "İşlem"])
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setMinimumHeight(270)
        layout.addWidget(self.cart_table)
        self.total_label = QLabel("Ara toplam: 0,00 ₺")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #132638;")
        self.total_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_label)
        cancel = SecondaryButton("Vazgeç")
        cancel.clicked.connect(self.reject)
        save = PrimaryButton("Siparişi Kaydet")
        save.clicked.connect(self.save_order)
        layout.addWidget(page_actions(cancel, save))

    def _load_customers(self) -> None:
        self.customer.clear()
        self.customer.addItem("Müşteri seçin", None)
        for customer in list_customers(self.connection):
            self.customer.addItem(f"{customer['kod']} — {customer['unvan']}", customer["id"])

    def _load_products(self) -> None:
        self.product.clear()
        self.product.addItem("Ürün seçin", None)
        for product in list_products(self.connection):
            self.product.addItem(
                f"{product['kod']} — {product['ad']} ({product['birim_fiyat']:.2f} ₺)",
                {"id": product["id"], "ad": product["ad"], "fiyat": product["birim_fiyat"]},
            )

    def add_to_cart(self) -> None:
        product = self.product.currentData()
        if not product:
            QMessageBox.warning(self, "Ürün seçin", "Sepete eklemek için katalogdan bir ürün seçin.")
            return
        self.cart.append({"urun_id": product["id"], "ad": product["ad"], "miktar": self.quantity.value(),
                          "birim_fiyat": product["fiyat"]})
        self.render_cart()

    def render_cart(self) -> None:
        self.cart_table.setRowCount(0)
        for row, item in enumerate(self.cart):
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item["ad"])))
            amount = QDoubleSpinBox()
            amount.setRange(0.01, 1_000_000)
            amount.setDecimals(2)
            amount.setValue(float(item["miktar"]))
            amount.valueChanged.connect(lambda value, i=row: self.update_quantity(i, value))
            self.cart_table.setCellWidget(row, 1, amount)
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{float(item['birim_fiyat']):.2f} ₺"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{self.line_total(item):.2f} ₺"))
            delete = SecondaryButton("Sil")
            delete.clicked.connect(lambda checked=False, i=row: self.remove_cart_line(i))
            self.cart_table.setCellWidget(row, 4, delete)
        self.total_label.setText(f"Ara toplam: {self.cart_total():.2f} ₺")

    @staticmethod
    def line_total(item: dict[str, float | int | str]) -> float:
        return float(item["miktar"]) * float(item["birim_fiyat"])

    def cart_total(self) -> float:
        return sum(self.line_total(item) for item in self.cart)

    def update_quantity(self, row: int, amount: float) -> None:
        self.cart[row]["miktar"] = amount
        self.render_cart()

    def remove_cart_line(self, row: int) -> None:
        self.cart.pop(row)
        self.render_cart()

    def save_order(self) -> None:
        customer_id = self.customer.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Müşteri seçin", "Siparişi kaydetmeden önce bir müşteri seçin.")
            return
        try:
            order_id = create_order(self.connection, musteri_id=customer_id, proje_tipi=self.project_type.currentText(),
                                    items=self.cart)
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Sipariş kaydedilemedi", str(error))
            return
        self.done(order_id)
