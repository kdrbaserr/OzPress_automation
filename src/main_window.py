from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)


PAGES = [
    ("Ana Menü", "Özet", "Hızlı erişim ve güncel durum"),
    ("Katalog", "Katalog", "Ürün ve hizmet kartları"),
    ("Sipariş", "Sipariş", "Sipariş oluşturma ve takip"),
    ("Cari", "Cari", "Müşteri hesapları ve hareketleri"),
    ("Çıktı", "Çıktı", "Teklif, sipariş ve rapor çıktıları"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Özpress Otomasyon")
        self.resize(1100, 700)
        self._buttons: list[QPushButton] = []

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        menu = QFrame()
        menu.setObjectName("menu")
        menu.setFixedWidth(230)
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(18, 24, 18, 24)
        title = QLabel("ÖZPRESS\nOTOMASYON")
        title.setObjectName("brand")
        menu_layout.addWidget(title)
        menu_layout.addSpacing(34)

        self.pages = QStackedWidget()
        for index, (button_text, title_text, subtitle) in enumerate(PAGES):
            button = QPushButton(button_text)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, i=index: self.show_page(i))
            self._buttons.append(button)
            menu_layout.addWidget(button)
            self.pages.addWidget(self._create_page(title_text, subtitle))
        menu_layout.addStretch()

        layout.addWidget(menu)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.show_page(0)
        self.setStyleSheet("""
            #menu { background: #132638; }
            #brand { color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: 1px; }
            QPushButton { color: #d7e3ec; border: 0; text-align: left; padding: 12px; border-radius: 6px; font-size: 14px; }
            QPushButton:hover { background: #21425e; }
            QPushButton:checked { background: #17a2a4; color: white; font-weight: 600; }
            #page { background: #f5f7fa; }
            #pageTitle { color: #132638; font-size: 28px; font-weight: 700; }
            #subtitle { color: #5c6b76; font-size: 15px; }
            #placeholder { background: white; border: 1px solid #dde4ea; border-radius: 10px; color: #72808b; }
        """)

    def _create_page(self, title: str, subtitle: str) -> QWidget:
        page = QFrame()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 36, 42, 36)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        description = QLabel(subtitle)
        description.setObjectName("subtitle")
        placeholder = QLabel("Bu alan sonraki aşamada ilgili liste, form ve işlemlerle doldurulacaktır.")
        placeholder.setObjectName("placeholder")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(22)
        layout.addWidget(placeholder, 1)
        return page

    def show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
