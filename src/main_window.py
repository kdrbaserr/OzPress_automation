from pathlib import Path
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from components import Card, DataTable, FormCard, PrimaryButton, SecondaryButton, ThumbnailLabel, page_actions
from customer_dialog import CustomerDetailDialog, CustomerDialog
from customers import customer_summary, list_customers
from images import resolve_image_path
from order_dialog import OrderDialog
from ledger_dialogs import CollectionDialog, StatementDialog
from orders import confirm_order, list_orders
from products import create_product, get_product, list_categories, list_products, soft_delete_product, update_product


PAGES = [
    ("Ana Menü", "Genel Bakış", "Yerel veriler ve hızlı işlemler"),
    ("Katalog", "Katalog", "Ürün ve hizmet kartları"),
    ("Sipariş", "Sipariş", "Sipariş oluşturma ve takip"),
    ("Cari", "Cari", "Müşteri hesapları ve hareketleri"),
    ("Ayarlar", "Ayarlar", "Uygulama tercihleri ve yerel dosya yönetimi"),
]


class ProductDialog(QDialog):
    CATEGORIES = ["", "Panel", "Profil", "Trapez Sac", "Aksesuar", "Diğer"]

    def __init__(self, connection: sqlite3.Connection, product_id: int | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.product_id = product_id
        self.image_source: str | None = None
        self.setWindowTitle("Ürün Düzenle" if product_id else "Yeni Ürün")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code_input, self.name_input = QLineEdit(), QLineEdit()
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(self.CATEGORIES)
        self.unit_input, self.price_input = QLineEdit("Adet"), QLineEdit("0")
        form.addRow("Ürün kodu", self.code_input)
        form.addRow("Ürün adı", self.name_input)
        form.addRow("Kategori", self.category_input)
        form.addRow("Birim", self.unit_input)
        form.addRow("Birim fiyat", self.price_input)
        layout.addLayout(form)

        image_row = QHBoxLayout()
        self.image_preview = ThumbnailLabel(None, 88)
        self.image_name = QLabel("Görsel seçilmedi")
        select_image = SecondaryButton("Görsel Seç")
        select_image.clicked.connect(self.choose_image)
        image_row.addWidget(self.image_preview)
        image_row.addWidget(self.image_name, 1)
        image_row.addWidget(select_image)
        layout.addWidget(QLabel("Ürün görseli"))
        layout.addLayout(image_row)

        cancel_button = SecondaryButton("Vazgeç")
        cancel_button.clicked.connect(self.reject)
        save_button = PrimaryButton("Kaydet")
        save_button.clicked.connect(self.save_product)
        layout.addWidget(page_actions(cancel_button, save_button))
        if self.product_id:
            self.load_product()

    def load_product(self) -> None:
        product = get_product(self.connection, self.product_id)
        if not product:
            self.reject()
            return
        self.code_input.setText(product["kod"])
        self.name_input.setText(product["ad"])
        self.category_input.setCurrentText(product["kategori"] or "")
        self.unit_input.setText(product["birim"])
        self.price_input.setText(str(product["birim_fiyat"]))
        self.image_name.setText(product["image_path"] or "Görsel seçilmedi")
        existing_image = resolve_image_path(product["image_path"])
        pixmap = QPixmap(str(existing_image)) if existing_image else QPixmap()
        if not pixmap.isNull():
            self.image_preview.setText("")
            self.image_preview.setPixmap(pixmap.scaled(84, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Ürün görseli seç", "", "Görseller (*.png *.jpg *.jpeg *.webp *.bmp *.svg)"
        )
        if not path:
            return
        self.image_source = path
        self.image_name.setText(Path(path).name)
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.image_preview.setText("")
            self.image_preview.setPixmap(pixmap.scaled(84, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def save_product(self) -> None:
        if not self.code_input.text().strip() or not self.name_input.text().strip():
            QMessageBox.warning(self, "Eksik bilgi", "Ürün kodu ve ürün adı zorunludur.")
            return
        try:
            values = dict(kod=self.code_input.text(), ad=self.name_input.text(), kategori=self.category_input.currentText(),
                          birim=self.unit_input.text(), birim_fiyat=float(self.price_input.text().replace(",", ".")),
                          source_image=self.image_source)
            if self.product_id:
                update_product(self.connection, product_id=self.product_id, **values)
                product_id = self.product_id
            else:
                product_id = create_product(self.connection, **values)
        except (ValueError, sqlite3.Error, OSError) as error:
            QMessageBox.warning(self, "Ürün kaydedilemedi", str(error))
            return
        self.done(product_id)


class MainWindow(QMainWindow):
    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__()
        self.connection = connection
        self.setWindowTitle("Özpress Otomasyon")
        self.resize(1160, 720)
        self._buttons: list[QPushButton] = []
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._create_sidebar())
        self.pages = QStackedWidget()
        for key, title, subtitle in PAGES:
            self.pages.addWidget(self._create_page(key, title, subtitle))
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.show_page(0)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        logo = QLabel()
        logo.setPixmap(QPixmap(str(Path(__file__).resolve().parent.parent / "Resimler" / "ozpress-logo.svg")).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo)
        brand, tagline = QLabel("ÖZPRESS"), QLabel("OTOMASYON")
        brand.setObjectName("brandName")
        tagline.setObjectName("brandTagline")
        layout.addWidget(brand)
        layout.addWidget(tagline)
        layout.addSpacing(30)
        for index, (label, _, _) in enumerate(PAGES):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, i=index: self.show_page(i))
            self._buttons.append(button)
            layout.addWidget(button)
        layout.addStretch()
        offline = QLabel("● ÇEVRİMDIŞI MOD")
        offline.setStyleSheet("color: #78D5C9; font-size: 11px; font-weight: 600;")
        layout.addWidget(offline)
        return sidebar

    def _create_page(self, page_key: str, title: str, subtitle: str) -> QWidget:
        page = QFrame()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 36, 42, 36)
        heading, description = QLabel(title), QLabel(subtitle)
        heading.setObjectName("pageTitle")
        description.setObjectName("subtitle")
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(18)
        if page_key == "Katalog":
            new_product = PrimaryButton("+ Yeni Ürün")
            new_product.clicked.connect(self.open_product_dialog)
            self.edit_product_button = SecondaryButton("Düzenle")
            self.edit_product_button.clicked.connect(self.edit_selected_product)
            self.delete_product_button = SecondaryButton("Sil")
            self.delete_product_button.clicked.connect(self.delete_selected_product)
            layout.addWidget(page_actions(self.delete_product_button, self.edit_product_button, new_product))
            filters = QHBoxLayout()
            self.catalog_search = QLineEdit()
            self.catalog_search.setPlaceholderText("Kod veya ürün adı ara...")
            self.catalog_category_filter = QComboBox()
            self.catalog_image_filter = QComboBox()
            self.catalog_image_filter.addItems(["Tümü", "Görselli", "Görselsiz"])
            filters.addWidget(self.catalog_search, 2)
            filters.addWidget(QLabel("Kategori"))
            filters.addWidget(self.catalog_category_filter)
            filters.addWidget(QLabel("Görünüm"))
            filters.addWidget(self.catalog_image_filter)
            layout.addLayout(filters)
            self.catalog_table = DataTable(["Görsel", "Kod", "Ürün adı", "Kategori", "Birim", "Fiyat"])
            self.catalog_table.setColumnWidth(0, 72)
            layout.addWidget(self.catalog_table)
            self.catalog_search.textChanged.connect(self.refresh_catalog)
            self.catalog_category_filter.currentTextChanged.connect(self.refresh_catalog)
            self.catalog_image_filter.currentTextChanged.connect(self.refresh_catalog)
            self.catalog_table.itemSelectionChanged.connect(self.update_catalog_actions)
            self.refresh_catalog()
        elif page_key == "Sipariş":
            new_order = PrimaryButton("+ Yeni Sipariş / Proje")
            new_order.clicked.connect(self.open_order_dialog)
            confirm = SecondaryButton("Siparişi Onayla")
            confirm.clicked.connect(self.confirm_selected_order)
            layout.addWidget(page_actions(confirm, new_order))
            self.order_table = DataTable(["Sipariş No", "Müşteri", "Tarih", "Durum", "Toplam"])
            layout.addWidget(self.order_table)
            self.refresh_orders()
        elif page_key == "Cari":
            new_customer = PrimaryButton("+ Yeni Müşteri")
            new_customer.clicked.connect(self.open_customer_dialog)
            detail = SecondaryButton("Detay")
            detail.clicked.connect(self.open_customer_detail)
            collection = SecondaryButton("Tahsilat Gir")
            collection.clicked.connect(self.open_collection_dialog)
            statement = SecondaryButton("Ekstre")
            statement.clicked.connect(self.open_statement)
            layout.addWidget(page_actions(statement, collection, detail, new_customer))
            cards = QHBoxLayout()
            self.customer_count_card = self._summary_card("Müşteri", "0")
            self.customer_debt_card = self._summary_card("Borçlu", "0")
            self.customer_balance_card = self._summary_card("Net Bakiye", "0,00 ₺")
            for card in (self.customer_count_card, self.customer_debt_card, self.customer_balance_card):
                cards.addWidget(card)
            layout.addLayout(cards)
            filters = QHBoxLayout()
            self.customer_search = QLineEdit()
            self.customer_search.setPlaceholderText("Müşteri, kod veya telefon ara...")
            self.customer_balance_filter = QComboBox()
            self.customer_balance_filter.addItems(["Tümü", "Borçlu", "Alacaklı", "Bakiyesi Sıfır"])
            filters.addWidget(self.customer_search, 1)
            filters.addWidget(self.customer_balance_filter)
            layout.addLayout(filters)
            self.customer_table = DataTable(["Kod", "Müşteri", "Telefon", "Güncel Bakiye"])
            self.customer_table.itemDoubleClicked.connect(lambda _: self.open_customer_detail())
            self.customer_search.textChanged.connect(self.refresh_customers)
            self.customer_balance_filter.currentTextChanged.connect(self.refresh_customers)
            layout.addWidget(self.customer_table)
            self.refresh_customers()
        elif page_key == "Ayarlar":
            card = Card("Yerel çalışma modu")
            card.layout.addWidget(QLabel("Bu uygulama internet bağlantısı kullanmaz. Tüm veriler cihazdaki SQLite dosyasında saklanır."))
            layout.addWidget(card)
            layout.addStretch()
        else:
            cards = QHBoxLayout()
            for card_title, value in [("Ürün", "0"), ("Açık Sipariş", "0"), ("Cari", "0")]:
                card = Card(card_title)
                number = QLabel(value)
                number.setStyleSheet("font-size: 32px; font-weight: 700; color: #17A2A4;")
                card.layout.addWidget(number)
                cards.addWidget(card)
            layout.addLayout(cards)
            layout.addStretch()
        return page

    def open_product_dialog(self) -> None:
        dialog = ProductDialog(self.connection, parent=self)
        if dialog.exec():
            self.refresh_catalog()

    def selected_product_id(self) -> int | None:
        selected_items = self.catalog_table.selectedItems()
        if not selected_items:
            return None
        return self.catalog_table.item(selected_items[0].row(), 1).data(Qt.UserRole)

    def update_catalog_actions(self) -> None:
        has_selection = self.selected_product_id() is not None
        self.edit_product_button.setEnabled(has_selection)
        self.delete_product_button.setEnabled(has_selection)

    def edit_selected_product(self) -> None:
        product_id = self.selected_product_id()
        if product_id is None:
            return
        dialog = ProductDialog(self.connection, product_id, self)
        if dialog.exec():
            self.refresh_catalog()

    def open_order_dialog(self) -> None:
        if OrderDialog(self.connection, self).exec():
            self.refresh_orders()

    def selected_order_id(self) -> int | None:
        items = self.order_table.selectedItems()
        return self.order_table.item(items[0].row(), 0).data(Qt.UserRole) if items else None

    def refresh_orders(self) -> None:
        self.order_table.setRowCount(0)
        for order in list_orders(self.connection):
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            values = [order["siparis_no"], order["musteri"], order["siparis_tarihi"], order["durum"], f"{float(order['genel_toplam']):.2f} ₺"]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.UserRole, order["id"])
                self.order_table.setItem(row, column, item)

    def confirm_selected_order(self) -> None:
        order_id = self.selected_order_id()
        if order_id is None:
            return
        try:
            confirm_order(self.connection, order_id)
        except ValueError as error:
            QMessageBox.warning(self, "Sipariş onaylanamadı", str(error))
            return
        self.refresh_orders()
        self.refresh_customers()

    @staticmethod
    def _summary_card(title: str, value: str) -> Card:
        card = Card(title)
        label = QLabel(value)
        label.setObjectName("summaryValue")
        label.setStyleSheet("font-size: 25px; font-weight: 700; color: #17A2A4;")
        card.layout.addWidget(label)
        card.value_label = label
        return card

    def open_customer_dialog(self) -> None:
        if CustomerDialog(self.connection, self).exec():
            self.refresh_customers()

    def selected_customer_id(self) -> int | None:
        items = self.customer_table.selectedItems()
        return self.customer_table.item(items[0].row(), 0).data(Qt.UserRole) if items else None

    def open_customer_detail(self) -> None:
        customer_id = self.selected_customer_id()
        if customer_id is not None:
            CustomerDetailDialog(self.connection, customer_id, self).exec()

    def open_collection_dialog(self) -> None:
        if CollectionDialog(self.connection, self.selected_customer_id(), self).exec():
            self.refresh_customers()

    def open_statement(self) -> None:
        customer_id = self.selected_customer_id()
        if customer_id is not None:
            StatementDialog(self.connection, customer_id, self).exec()

    def refresh_customers(self) -> None:
        customers = list_customers(self.connection, search=self.customer_search.text(),
                                   balance_filter=self.customer_balance_filter.currentText())
        self.customer_table.setRowCount(0)
        for customer in customers:
            row = self.customer_table.rowCount()
            self.customer_table.insertRow(row)
            values = [customer["kod"], customer["unvan"], customer["telefon"] or "-", f"{float(customer['bakiye']):.2f} ₺"]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.UserRole, customer["id"])
                self.customer_table.setItem(row, column, item)
        summary = customer_summary(self.connection)
        self.customer_count_card.value_label.setText(str(summary["count"]))
        self.customer_debt_card.value_label.setText(str(summary["debtors"]))
        self.customer_balance_card.value_label.setText(f"{float(summary['balance']):.2f} ₺")

    def delete_selected_product(self) -> None:
        product_id = self.selected_product_id()
        if product_id is None:
            return
        answer = QMessageBox.question(self, "Ürünü sil", "Ürün katalogdan kaldırılacak. Devam edilsin mi?")
        if answer == QMessageBox.StandardButton.Yes:
            soft_delete_product(self.connection, product_id)
            self.refresh_catalog()

    def refresh_catalog(self) -> None:
        self.catalog_table.setRowCount(0)
        self.catalog_category_filter.blockSignals(True)
        current_category = self.catalog_category_filter.currentText()
        self.catalog_category_filter.clear()
        self.catalog_category_filter.addItem("Tüm kategoriler", "")
        self.catalog_category_filter.addItems(list_categories(self.connection))
        self.catalog_category_filter.setCurrentText(current_category if current_category else "Tüm kategoriler")
        self.catalog_category_filter.blockSignals(False)
        category = self.catalog_category_filter.currentText()
        if category == "Tüm kategoriler":
            category = ""
        for product in list_products(self.connection, search=self.catalog_search.text(), kategori=category,
                                     image_filter=self.catalog_image_filter.currentText()):
            row = self.catalog_table.rowCount()
            self.catalog_table.insertRow(row)
            self.catalog_table.setCellWidget(row, 0, ThumbnailLabel(product["image_path"]))
            values = [product["kod"], product["ad"], product["kategori"] or "-", product["birim"], f"{product['birim_fiyat']:.2f} ₺"]
            for column, value in enumerate(values, 1):
                item = QTableWidgetItem(value)
                if column == 1:
                    item.setData(Qt.UserRole, product["id"])
                self.catalog_table.setItem(row, column, item)
            self.catalog_table.setRowHeight(row, 60)
        self.update_catalog_actions()

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
