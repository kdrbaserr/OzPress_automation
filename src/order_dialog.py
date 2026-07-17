"""Katalogdan ürün seçerek proje/sipariş sepeti oluşturan pencere."""
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QHeaderView, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from components import PrimaryButton, SecondaryButton, page_actions
from orders import create_order, get_order_for_edit, list_customers, update_order
from products import list_products, update_catalog_price
from projects import list_projects
from weight_calculator import WeightCalculatorDialog


class OrderDialog(QDialog):
    PROJECT_TYPES = ["Konteyner Ev", "Panel Çatı", "Trapez Çatı", "Diğer"]

    def __init__(self, connection: sqlite3.Connection, parent: QWidget | None = None,
                 order_id: int | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.order_id = order_id
        self.cart: list[dict[str, float | int | str]] = []
        self.setWindowTitle("Siparişi Düzenle" if order_id else "Yeni Sipariş / Proje")
        self.resize(950, 650)
        self.setMinimumWidth(900)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.project_type = QComboBox()
        self.project_type.addItems(self.PROJECT_TYPES)
        self.project_type.currentTextChanged.connect(self.toggle_custom_project_type)
        self.custom_project_type = QLineEdit()
        self.custom_project_type.setPlaceholderText("Proje türünü yazın")
        self.custom_project_type.setVisible(False)
        self.project = QComboBox()
        self.project.addItem("Kayıtlı proje seçmeden devam et", None)
        for project in list_projects(connection):
            self.project.addItem(f"{project['ad']} — {project['proje_tipi']}", project["id"])
        self.project.currentIndexChanged.connect(self.apply_selected_project)
        self.customer = QComboBox()
        self._load_customers()
        form.addRow("Proje tipi", self.project_type)
        form.addRow("Özel proje türü", self.custom_project_type)
        form.addRow("Kayıtlı proje", self.project)
        form.addRow("Müşteri", self.customer)
        layout.addLayout(form)

        product_row = QHBoxLayout()
        self.product = QComboBox()
        self._load_products()
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0.01, 1_000_000)
        self.quantity.setValue(1)
        self.quantity.setDecimals(2)
        self.quantity.setSingleStep(1.0)
        add_button = PrimaryButton("Sepete Ekle")
        add_button.clicked.connect(self.add_to_cart)
        calculator_button = SecondaryButton("Ağırlık Hesapla")
        calculator_button.clicked.connect(self.open_weight_calculator)
        product_row.addWidget(QLabel("Katalog ürünü"))
        product_row.addWidget(self.product, 1)
        product_row.addWidget(QLabel("Miktar"))
        product_row.addWidget(self.quantity)
        product_row.addWidget(add_button)
        product_row.addWidget(calculator_button)
        layout.addLayout(product_row)

        extra_row = QHBoxLayout()
        self.extra_description = QLineEdit()
        self.extra_description.setPlaceholderText("İşçilik, nakliye vb. açıklama")
        self.extra_amount = QDoubleSpinBox()
        self.extra_amount.setRange(0.01, 10_000_000)
        self.extra_amount.setDecimals(2)
        self.extra_amount.setSingleStep(1.0)
        add_extra = SecondaryButton("Serbest Kalem Ekle")
        add_extra.clicked.connect(self.add_extra_item)
        extra_row.addWidget(QLabel("Serbest kalem"))
        extra_row.addWidget(self.extra_description, 1)
        extra_row.addWidget(QLabel("Tutar"))
        extra_row.addWidget(self.extra_amount)
        extra_row.addWidget(add_extra)
        layout.addLayout(extra_row)

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["Kalem", "Miktar", "KDV'siz birim fiyat", "KDV'li toplam", "İşlem"])
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setMinimumHeight(270)
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(1, 135)
        self.cart_table.setColumnWidth(2, 175)
        self.cart_table.setColumnWidth(3, 125)
        self.cart_table.setColumnWidth(4, 90)
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
        if order_id:
            self.load_order()

    def load_order(self) -> None:
        try:
            order, items = get_order_for_edit(self.connection, self.order_id)
        except ValueError as error:
            QMessageBox.warning(self, "Sipariş açılamadı", str(error))
            self.reject()
            return
        project_index = self.project.findData(order["proje_id"])
        if project_index >= 0:
            self.project.setCurrentIndex(project_index)
        customer_index = self.customer.findData(order["musteri_id"])
        if customer_index >= 0:
            self.customer.setCurrentIndex(customer_index)
        project_type = order["proje_tipi"]
        if project_type in self.PROJECT_TYPES:
            self.project_type.setCurrentText(project_type)
        else:
            self.project_type.setCurrentText(self.PROJECT_TYPES[-1])
            self.custom_project_type.setText(project_type)
        self.cart = items
        for item in self.cart:
            if item["tip"] == "urun":
                item["katalog_fiyat"] = item["birim_fiyat"]
        self.render_cart()

    def toggle_custom_project_type(self, project_type: str) -> None:
        self.custom_project_type.setVisible(project_type == self.PROJECT_TYPES[-1])

    def apply_selected_project(self) -> None:
        project_id = self.project.currentData()
        if not project_id:
            return
        selected = next((item for item in list_projects(self.connection) if item["id"] == project_id), None)
        if not selected:
            return
        self.project_type.setCurrentText(selected["proje_tipi"] if selected["proje_tipi"] in self.PROJECT_TYPES else self.PROJECT_TYPES[-1])
        if self.project_type.currentText() == self.PROJECT_TYPES[-1]:
            self.custom_project_type.setText(selected["proje_tipi"])
        customer_index = self.customer.findData(selected["musteri_id"])
        if customer_index >= 0:
            self.customer.setCurrentIndex(customer_index)

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
                f"{product['kod']} — {product['ad']} ({product['birim_fiyat']:.2f} ₺ + %{product['kdv_orani']:g} KDV)",
                {"id": product["id"], "ad": product["ad"], "fiyat": product["birim_fiyat"],
                 "kdv_orani": product["kdv_orani"]},
            )

    def add_to_cart(self) -> None:
        product = self.product.currentData()
        if not product:
            QMessageBox.warning(self, "Ürün seçin", "Sepete eklemek için katalogdan bir ürün seçin.")
            return
        self.cart.append({"tip": "urun", "urun_id": product["id"], "ad": product["ad"], "miktar": self.quantity.value(),
                          "birim_fiyat": product["fiyat"], "katalog_fiyat": product["fiyat"],
                          "kdv_orani": product["kdv_orani"]})
        self.render_cart()

    def open_weight_calculator(self) -> None:
        calculator = WeightCalculatorDialog(self.connection, self)
        if calculator.exec() and calculator.cart_item:
            self.cart.append(calculator.cart_item)
            self.render_cart()

    def add_extra_item(self) -> None:
        description = self.extra_description.text().strip()
        if not description:
            QMessageBox.warning(self, "Açıklama gerekli", "Serbest kalem için açıklama girin.")
            return
        self.cart.append({"tip": "ekstra", "aciklama": description, "tutar": self.extra_amount.value()})
        self.extra_description.clear()
        self.extra_amount.setValue(0.01)
        self.render_cart()

    def render_cart(self) -> None:
        self.cart_table.setRowCount(0)
        for row, item in enumerate(self.cart):
            self.cart_table.insertRow(row)
            if item["tip"] == "urun":
                self.render_product_row(row, item)
            else:
                self.render_extra_row(row, item)
            delete = SecondaryButton("Sil")
            delete.setMinimumWidth(64)
            delete.clicked.connect(lambda checked=False, i=row: self.remove_cart_line(i))
            self.cart_table.setCellWidget(row, 4, delete)
        self.total_label.setText(f"Ara toplam: {self.cart_total():.2f} ₺")

    def render_product_row(self, row: int, item: dict[str, float | int | str]) -> None:
        self.cart_table.setItem(row, 0, QTableWidgetItem(str(item["ad"])))
        amount = QDoubleSpinBox()
        amount.setRange(0.01, 1_000_000)
        amount.setDecimals(2)
        amount.setSingleStep(1.0)
        amount.setValue(float(item["miktar"]))
        amount.setMinimumWidth(125)
        amount.valueChanged.connect(lambda value, i=row: self.update_quantity(i, value))
        self.cart_table.setCellWidget(row, 1, amount)
        price = QDoubleSpinBox()
        price.setRange(0, 10_000_000)
        price.setDecimals(2)
        price.setSingleStep(1.0)
        price.setPrefix("₺ ")
        price.setValue(float(item["birim_fiyat"]))
        price.setMinimumWidth(165)
        price.editingFinished.connect(lambda i=row, widget=price: self.update_unit_price(i, widget.value()))
        self.cart_table.setCellWidget(row, 2, price)
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"{self.line_total(item):.2f} ₺"))

    def render_extra_row(self, row: int, item: dict[str, float | int | str]) -> None:
        self.cart_table.setItem(row, 0, QTableWidgetItem(f"Serbest: {item['aciklama']}"))
        self.cart_table.setItem(row, 1, QTableWidgetItem("-"))
        self.cart_table.setItem(row, 2, QTableWidgetItem(f"{float(item['tutar']):.2f} ₺"))
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"{float(item['tutar']):.2f} ₺"))

    @staticmethod
    def line_total(item: dict[str, float | int | str]) -> float:
        if item["tip"] == "ekstra":
            return float(item["tutar"])
        net = float(item["miktar"]) * float(item["birim_fiyat"])
        return net * (1 + float(item.get("kdv_orani", 0)) / 100)

    def cart_total(self) -> float:
        return sum(self.line_total(item) for item in self.cart)

    def update_quantity(self, row: int, amount: float) -> None:
        self.cart[row]["miktar"] = amount
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"{self.line_total(self.cart[row]):.2f} ₺"))
        self.update_total_label()

    def update_unit_price(self, row: int, price: float) -> None:
        item = self.cart[row]
        if price == float(item["birim_fiyat"]):
            return
        answer = QMessageBox.question(
            self, "Katalog fiyatı", "Katalogdaki sabit fiyat da güncellensin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,
        )
        item["birim_fiyat"] = price
        if answer == QMessageBox.StandardButton.Yes:
            update_catalog_price(self.connection, int(item["urun_id"]), price)
            item["katalog_fiyat"] = price
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"{self.line_total(item):.2f} ₺"))
        self.update_total_label()

    def update_total_label(self) -> None:
        self.total_label.setText(f"Ara toplam: {self.cart_total():.2f} ₺")

    def remove_cart_line(self, row: int) -> None:
        self.cart.pop(row)
        self.render_cart()

    def save_order(self) -> None:
        customer_id = self.customer.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Müşteri seçin", "Siparişi kaydetmeden önce bir müşteri seçin.")
            return
        project_type = self.project_type.currentText()
        if project_type == self.PROJECT_TYPES[-1]:
            project_type = self.custom_project_type.text().strip()
            if not project_type:
                QMessageBox.warning(self, "Proje türü gerekli", "Diğer seçildiğinde proje türünü yazın.")
                return
        try:
            if self.order_id:
                update_order(self.connection, order_id=self.order_id, musteri_id=customer_id,
                             proje_tipi=project_type, items=self.cart, proje_id=self.project.currentData())
                order_id = self.order_id
            else:
                order_id = create_order(self.connection, musteri_id=customer_id, proje_tipi=project_type,
                                        items=self.cart, proje_id=self.project.currentData())
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Sipariş kaydedilemedi", str(error))
            return
        self.done(order_id)
