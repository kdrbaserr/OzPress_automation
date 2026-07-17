from pathlib import Path
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QHeaderView, QMainWindow, QMessageBox, QPushButton, QScrollArea, QStackedWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from components import Card, DataTable, FormCard, PrimaryButton, SecondaryButton, ThumbnailLabel, page_actions
from customer_dialog import CustomerDetailDialog, CustomerDialog
from customers import customer_summary, format_customer_balance, list_customers, soft_delete_customer
from images import resolve_image_path
from order_dialog import OrderDialog
from ledger_dialogs import CollectionDialog, StatementDialog
from orders import confirm_order, delete_order, list_orders
from output_dialog import OutputDialog
from settings import get_settings, save_settings
from products import create_product, get_product, list_categories, list_products, soft_delete_product, update_product
from projects import create_project, list_projects
from weight_calculator import WeightCalculatorDialog


PAGES = [
    ("Ana Menü", "Genel Bakış", "Yerel veriler ve hızlı işlemler"),
    ("Katalog", "Katalog", "Ürün ve hizmet kartları"),
    ("Sipariş", "Sipariş", "Sipariş oluşturma ve takip"),
    ("Projeler", "Projeler", "Kayıtlı projeleri oluşturma ve takip"),
    ("Hesaplama", "Hesaplama", "Sac ve çelik parçalar için ağırlık ve fiyat hesabı"),
    ("Cari", "Cari", "Müşteri hesapları ve hareketleri"),
    ("Çıktı", "Çıktı", "Sipariş ve teklif PDF çıktıları"),
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


class ProjectDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Yeni Proje")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.setEditable(True)
        self.type_input.addItems(OrderDialog.PROJECT_TYPES)
        self.customer_input = QComboBox()
        self.customer_input.addItem("Müşteri seçilmedi", None)
        for customer in list_customers(connection):
            self.customer_input.addItem(f"{customer['kod']} — {customer['unvan']}", customer["id"])
        self.description_input = QLineEdit()
        form.addRow("Proje adı", self.name_input)
        form.addRow("Proje türü", self.type_input)
        form.addRow("Müşteri", self.customer_input)
        form.addRow("Açıklama", self.description_input)
        layout.addLayout(form)
        cancel, save = SecondaryButton("Vazgeç"), PrimaryButton("Projeyi Kaydet")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.save_project)
        layout.addWidget(page_actions(cancel, save))

    def save_project(self) -> None:
        try:
            project_id = create_project(
                self.connection, ad=self.name_input.text(), proje_tipi=self.type_input.currentText(),
                musteri_id=self.customer_input.currentData(), aciklama=self.description_input.text(),
            )
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Proje kaydedilemedi", str(error))
            return
        self.done(project_id)


class MainWindow(QMainWindow):
    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__()
        self.connection = connection
        self.setWindowTitle("Özşahin Metal Otomasyon")
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
        logo.setPixmap(QPixmap(str(Path(__file__).resolve().parent.parent / "Resimler" / "ozsahinLogo.png")).scaled(92, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo)
        brand, tagline = QLabel("ÖZŞAHİN METAL"), QLabel("OTOMASYON")
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
            layout.addWidget(page_actions(new_order))
            self.delete_order_button = SecondaryButton("Siparişi Sil")
            self.delete_order_button.clicked.connect(self.delete_selected_order)
            self.invoice_button = PrimaryButton("Fatura PDF Oluştur")
            self.invoice_button.clicked.connect(lambda: self.open_selected_order_output("Fatura"))
            self.order_pdf_button = PrimaryButton("Sipariş PDF Oluştur")
            self.order_pdf_button.clicked.connect(lambda: self.open_selected_order_output("Sipariş"))
            self.confirm_order_button = SecondaryButton("Siparişi Onayla")
            self.confirm_order_button.clicked.connect(self.confirm_selected_order)
            self.order_actions = page_actions(
                self.delete_order_button, self.confirm_order_button, self.order_pdf_button, self.invoice_button
            )
            self.order_actions.setVisible(False)
            layout.addWidget(self.order_actions)
            self.order_table = DataTable(["Sipariş No", "Müşteri", "Tarih", "Durum", "Toplam"])
            self.order_table.itemSelectionChanged.connect(self.update_order_actions)
            self.order_table.itemDoubleClicked.connect(lambda _: self.open_selected_order_output("Sipariş"))
            layout.addWidget(self.order_table)
            self.refresh_orders()
        elif page_key == "Projeler":
            new_project = PrimaryButton("+ Yeni Proje")
            new_project.clicked.connect(self.open_project_dialog)
            layout.addWidget(page_actions(new_project))
            self.project_table = DataTable(["Proje adı", "Proje türü", "Müşteri", "Açıklama"])
            layout.addWidget(self.project_table)
            self.refresh_projects()
        elif page_key == "Hesaplama":
            card = Card("Sac / Çelik Ağırlık Hesaplayıcı")
            card.layout.addWidget(QLabel(
                "En, boy, kalınlık ve adet bilgileriyle toplam ağırlığı; kilo fiyatıyla da tutarı hesaplayın."
            ))
            calculator_button = PrimaryButton("Hesaplama Motorunu Aç")
            calculator_button.clicked.connect(self.open_weight_calculator)
            card.layout.addWidget(calculator_button)
            layout.addWidget(card)
            layout.addStretch()
        elif page_key == "Cari":
            new_customer = PrimaryButton("+ Yeni Müşteri")
            new_customer.clicked.connect(self.open_customer_dialog)
            edit_customer = SecondaryButton("Düzenle")
            edit_customer.clicked.connect(self.edit_selected_customer)
            delete_customer = SecondaryButton("Sil")
            delete_customer.clicked.connect(self.delete_selected_customer)
            detail = SecondaryButton("Detay")
            detail.clicked.connect(self.open_customer_detail)
            collection = SecondaryButton("Tahsilat Gir")
            collection.clicked.connect(self.open_collection_dialog)
            statement = SecondaryButton("Ekstre")
            statement.clicked.connect(self.open_statement)
            layout.addWidget(page_actions(delete_customer, edit_customer, statement, collection, detail, new_customer))
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
            self.customer_balance_filter.addItems(["Tüm müşteriler", "Borçlu", "Alacaklı", "Bakiyesi Sıfır"])
            filters.addWidget(self.customer_search, 1)
            filters.addWidget(self.customer_balance_filter)
            layout.addLayout(filters)
            self.customer_table = DataTable(["Kod", "Müşteri", "Telefon", "Güncel Bakiye"])
            customer_header = self.customer_table.horizontalHeader()
            customer_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            customer_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            customer_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            customer_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            self.customer_table.setColumnWidth(3, 280)
            self.customer_table.itemDoubleClicked.connect(lambda _: self.open_customer_detail())
            self.customer_search.textChanged.connect(self.refresh_customers)
            self.customer_balance_filter.currentTextChanged.connect(self.refresh_customers)
            layout.addWidget(self.customer_table)
            self.refresh_customers()
        elif page_key == "Ayarlar":
            values=get_settings(self.connection); card = Card("Firma bilgileri")
            self.firma_adi, self.firma_tel, self.firma_eposta, self.firma_adres, self.firma_vergi_dairesi, self.firma_vergi_no, self.firma_iban, self.firma_kdv = QLineEdit(values['firma_adi']), QLineEdit(values['telefon']), QLineEdit(values['eposta']), QLineEdit(values['adres']), QLineEdit(values['vergi_dairesi']), QLineEdit(values['vergi_no']), QLineEdit(values['iban']), QLineEdit(values['kdv_orani'])
            for label,field in [("Firma adı",self.firma_adi),("Telefon",self.firma_tel),("E-posta",self.firma_eposta),("Adres",self.firma_adres),("Vergi dairesi",self.firma_vergi_dairesi),("VKN",self.firma_vergi_no),("IBAN",self.firma_iban),("KDV oranı (%)",self.firma_kdv)]: card.layout.addWidget(QLabel(label)); card.layout.addWidget(field)
            logo=SecondaryButton("Logo Yükle"); logo.clicked.connect(self.select_company_logo); save=PrimaryButton("Ayarları Kaydet"); save.clicked.connect(self.save_company_settings); card.layout.addWidget(page_actions(logo,save))
            layout.addWidget(card)
            layout.addStretch()
        elif page_key == "Çıktı":
            card=Card("Sipariş / teklif çıktısı"); card.layout.addWidget(QLabel("A4, 58 mm ve 80 mm termal PDF şablonları desteklenir.")); button=PrimaryButton("Masaüstüne PDF Kaydet"); button.clicked.connect(self.open_output_dialog); card.layout.addWidget(button); layout.addWidget(card); layout.addStretch()
        else:
            cards = QHBoxLayout()
            self.dashboard_values: dict[str, QLabel] = {}
            for card_title in ("Ürün", "Açık Sipariş", "Cari"):
                card = Card(card_title)
                number = QLabel("0")
                number.setStyleSheet("font-size: 32px; font-weight: 700; color: #17A2A4;")
                card.layout.addWidget(number)
                cards.addWidget(card)
                self.dashboard_values[card_title] = number
            layout.addLayout(cards)
            layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setObjectName("pageScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(page)
        return scroll_area

    def open_product_dialog(self) -> None:
        dialog = ProductDialog(self.connection, parent=self)
        if dialog.exec():
            self.refresh_catalog()
            self.refresh_dashboard()

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
            self.refresh_dashboard()

    def open_project_dialog(self) -> None:
        if ProjectDialog(self.connection, self).exec():
            self.refresh_projects()

    def refresh_projects(self) -> None:
        self.project_table.setRowCount(0)
        for project in list_projects(self.connection):
            row = self.project_table.rowCount()
            self.project_table.insertRow(row)
            for column, value in enumerate((project["ad"], project["proje_tipi"], project["musteri"] or "-", project["aciklama"] or "-")):
                item = QTableWidgetItem(str(value))
                if column == 0:
                    item.setData(Qt.UserRole, project["id"])
                self.project_table.setItem(row, column, item)

    def open_weight_calculator(self) -> None:
        WeightCalculatorDialog(self.connection, self, allow_add_to_cart=False).exec()

    def selected_order_id(self) -> int | None:
        items = self.order_table.selectedItems()
        return self.order_table.item(items[0].row(), 0).data(Qt.UserRole) if items else None

    def update_order_actions(self) -> None:
        self.order_actions.setVisible(self.selected_order_id() is not None)

    def open_selected_order_output(self, document_type: str) -> None:
        order_id = self.selected_order_id()
        if order_id is not None:
            OutputDialog(self.connection, self, order_id=order_id, document_type=document_type).exec()

    def delete_selected_order(self) -> None:
        order_id = self.selected_order_id()
        if order_id is None:
            return
        answer = QMessageBox.question(
            self, "Siparişi sil",
            "Seçili sipariş ve bu siparişin oluşturduğu cari hareket silinecek. Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_order(self.connection, order_id)
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Sipariş silinemedi", str(error))
            return
        self.refresh_orders()
        self.refresh_customers()
        self.refresh_dashboard()

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
        self.update_order_actions()

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
        self.refresh_dashboard()

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
        if CustomerDialog(self.connection, parent=self).exec():
            self.refresh_customers()
            self.refresh_dashboard()

    def edit_selected_customer(self) -> None:
        customer_id = self.selected_customer_id()
        if customer_id is not None and CustomerDialog(self.connection, customer_id, self).exec():
            self.refresh_customers()

    def delete_selected_customer(self) -> None:
        customer_id = self.selected_customer_id()
        if customer_id is None:
            return
        if QMessageBox.question(self, "Müşteriyi sil", "Müşteri listeden kaldırılacak. Devam edilsin mi?") == QMessageBox.StandardButton.Yes:
            soft_delete_customer(self.connection, customer_id)
            self.refresh_customers()
            self.refresh_dashboard()

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

    def open_output_dialog(self) -> None:
        OutputDialog(self.connection, self).exec()

    def select_company_logo(self) -> None:
        path,_=QFileDialog.getOpenFileName(self,"Firma logosu seç","","Görseller (*.png *.jpg *.jpeg *.webp *.bmp *.svg)")
        self.company_logo_source=path or None

    def save_company_settings(self) -> None:
        try: kdv=float(self.firma_kdv.text().replace(',','.')); assert kdv>=0
        except (ValueError,AssertionError): QMessageBox.warning(self,"Geçersiz KDV","KDV oranı negatif olamaz."); return
        save_settings(self.connection,{"firma_adi":self.firma_adi.text(),"telefon":self.firma_tel.text(),"eposta":self.firma_eposta.text(),"adres":self.firma_adres.text(),"vergi_dairesi":self.firma_vergi_dairesi.text(),"vergi_no":self.firma_vergi_no.text(),"iban":self.firma_iban.text(),"kdv_orani":str(kdv)},getattr(self,'company_logo_source',None))

    def refresh_customers(self) -> None:
        customers = list_customers(self.connection, search=self.customer_search.text(),
                                   balance_filter=self.customer_balance_filter.currentText())
        self.customer_table.setRowCount(0)
        for customer in customers:
            row = self.customer_table.rowCount()
            self.customer_table.insertRow(row)
            values = [customer["kod"], customer["unvan"], customer["telefon"] or "-",
                      format_customer_balance(float(customer["bakiye"]))]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.UserRole, customer["id"])
                self.customer_table.setItem(row, column, item)
        summary = customer_summary(self.connection)
        self.customer_count_card.value_label.setText(str(summary["count"]))
        self.customer_debt_card.value_label.setText(str(summary["debtors"]))
        self.customer_balance_card.value_label.setText(format_customer_balance(float(summary["balance"])))

    def delete_selected_product(self) -> None:
        product_id = self.selected_product_id()
        if product_id is None:
            return
        answer = QMessageBox.question(self, "Ürünü sil", "Ürün katalogdan kaldırılacak. Devam edilsin mi?")
        if answer == QMessageBox.StandardButton.Yes:
            soft_delete_product(self.connection, product_id)
            self.refresh_catalog()
            self.refresh_dashboard()

    def refresh_dashboard(self) -> None:
        """Ana menü kartlarını güncel veritabanı kayıtlarıyla yeniler."""
        if not hasattr(self, "dashboard_values"):
            return
        product_count = self.connection.execute(
            "SELECT COUNT(*) FROM urunler WHERE aktif = 1"
        ).fetchone()[0]
        open_order_count = self.connection.execute(
            "SELECT COUNT(*) FROM siparisler WHERE durum NOT IN ('Tamamlandı', 'İptal')"
        ).fetchone()[0]
        customer_count = self.connection.execute(
            "SELECT COUNT(*) FROM musteriler WHERE aktif = 1"
        ).fetchone()[0]
        self.dashboard_values["Ürün"].setText(str(product_count))
        self.dashboard_values["Açık Sipariş"].setText(str(open_order_count))
        self.dashboard_values["Cari"].setText(str(customer_count))

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
        if index == 0:
            self.refresh_dashboard()
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setChecked(button_index == index)
