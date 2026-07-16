from pathlib import Path
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from components import Card, DataTable, FormCard, PrimaryButton, SecondaryButton, ThumbnailLabel, page_actions
from images import resolve_image_path
from products import create_product, list_products


PAGES = [
    ("Ana Menü", "Genel Bakış", "Yerel veriler ve hızlı işlemler"),
    ("Katalog", "Katalog", "Ürün ve hizmet kartları"),
    ("Sipariş", "Sipariş", "Sipariş oluşturma ve takip"),
    ("Cari", "Cari", "Müşteri hesapları ve hareketleri"),
    ("Ayarlar", "Ayarlar", "Uygulama tercihleri ve yerel dosya yönetimi"),
]


class ProductDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.image_source: str | None = None
        self.setWindowTitle("Yeni Ürün")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code_input, self.name_input = QLineEdit(), QLineEdit()
        self.unit_input, self.price_input = QLineEdit("Adet"), QLineEdit("0")
        form.addRow("Ürün kodu", self.code_input)
        form.addRow("Ürün adı", self.name_input)
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
            product_id = create_product(
                self.connection,
                kod=self.code_input.text(), ad=self.name_input.text(), birim=self.unit_input.text(),
                birim_fiyat=float(self.price_input.text().replace(",", ".")), source_image=self.image_source,
            )
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
            layout.addWidget(page_actions(SecondaryButton("Filtrele"), new_product))
            self.catalog_table = DataTable(["Görsel", "Kod", "Ürün adı", "Birim", "Fiyat"])
            self.catalog_table.setColumnWidth(0, 72)
            layout.addWidget(self.catalog_table)
            self.refresh_catalog()
        elif page_key == "Sipariş":
            layout.addWidget(page_actions(SecondaryButton("Taslaklar"), PrimaryButton("+ Yeni Sipariş")))
            layout.addWidget(DataTable(["Sipariş No", "Müşteri", "Tarih", "Durum", "Toplam"]))
        elif page_key == "Cari":
            content = QHBoxLayout()
            content.addWidget(FormCard("Yeni Müşteri", ["Kod", "Ünvan", "Telefon"]))
            content.addWidget(DataTable(["Cari kod", "Ünvan", "Bakiye"]), 1)
            layout.addLayout(content)
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
        dialog = ProductDialog(self.connection, self)
        if dialog.exec():
            self.refresh_catalog()

    def refresh_catalog(self) -> None:
        self.catalog_table.setRowCount(0)
        for product in list_products(self.connection):
            row = self.catalog_table.rowCount()
            self.catalog_table.insertRow(row)
            self.catalog_table.setCellWidget(row, 0, ThumbnailLabel(product["image_path"]))
            values = [product["kod"], product["ad"], product["birim"], f"{product['birim_fiyat']:.2f} ₺"]
            for column, value in enumerate(values, 1):
                from PySide6.QtWidgets import QTableWidgetItem
                self.catalog_table.setItem(row, column, QTableWidgetItem(value))
            self.catalog_table.setRowHeight(row, 60)

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
