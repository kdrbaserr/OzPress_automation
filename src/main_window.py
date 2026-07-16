from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from components import Card, DataTable, FormCard, PrimaryButton, SecondaryButton, page_actions


PAGES = [
    ("Ana Menü", "Genel Bakış", "Yerel veriler ve hızlı işlemler"),
    ("Katalog", "Katalog", "Ürün ve hizmet kartları"),
    ("Sipariş", "Sipariş", "Sipariş oluşturma ve takip"),
    ("Cari", "Cari", "Müşteri hesapları ve hareketleri"),
    ("Ayarlar", "Ayarlar", "Uygulama tercihleri ve yerel dosya yönetimi"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Özpress Otomasyon")
        self.resize(1160, 720)
        self._buttons: list[QPushButton] = []

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._create_sidebar())
        self.pages = QStackedWidget()
        for title, heading, subtitle in PAGES:
            self.pages.addWidget(self._create_page(title, heading, subtitle))
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
        brand = QLabel("ÖZPRESS")
        brand.setObjectName("brandName")
        tagline = QLabel("OTOMASYON")
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
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        description = QLabel(subtitle)
        description.setObjectName("subtitle")
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(18)

        if page_key == "Katalog":
            layout.addWidget(page_actions(SecondaryButton("Filtrele"), PrimaryButton("+ Yeni Ürün")))
            table = DataTable(["Kod", "Ürün adı", "Birim", "Fiyat", "Görsel"])
            table.add_demo_row(["UR-001", "Örnek Ürün", "Adet", "0,00 ₺", "Yok"])
            layout.addWidget(table)
        elif page_key == "Sipariş":
            layout.addWidget(page_actions(SecondaryButton("Taslaklar"), PrimaryButton("+ Yeni Sipariş")))
            table = DataTable(["Sipariş No", "Müşteri", "Tarih", "Durum", "Toplam"])
            layout.addWidget(table)
        elif page_key == "Cari":
            content = QHBoxLayout()
            content.addWidget(FormCard("Yeni Müşteri", ["Kod", "Ünvan", "Telefon"]))
            table = DataTable(["Cari kod", "Ünvan", "Bakiye"])
            content.addWidget(table, 1)
            layout.addLayout(content)
        elif page_key == "Ayarlar":
            card = Card("Yerel çalışma modu")
            card.layout.addWidget(QLabel("Bu uygulama internet bağlantısı kullanmaz. Tüm veriler cihazdaki SQLite dosyasında saklanır."))
            card.layout.addWidget(SecondaryButton("Veritabanı klasörünü aç"))
            layout.addWidget(card)
            layout.addStretch()
        else:
            cards = QHBoxLayout()
            for title_text, value in [("Ürün", "0"), ("Açık Sipariş", "0"), ("Cari", "0")]:
                card = Card(title_text)
                number = QLabel(value)
                number.setStyleSheet("font-size: 32px; font-weight: 700; color: #17A2A4;")
                card.layout.addWidget(number)
                cards.addWidget(card)
            layout.addLayout(cards)
            layout.addStretch()
        return page

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
