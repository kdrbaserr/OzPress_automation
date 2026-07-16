"""Sac/çelik parça ağırlığını milimetre cinsinden hesaplayan arayüz."""
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QWidget

from components import Card, PrimaryButton, SecondaryButton, page_actions
from products import list_products


STEEL_DENSITY = 7.85


def calculate_weight_kg(width_mm: float, length_mm: float, thickness_mm: float, quantity: int) -> float:
    """(En × Boy × Kalınlık × 7.85) / 1.000.000 × Adet formülünü uygular."""
    if width_mm <= 0 or length_mm <= 0 or thickness_mm <= 0 or quantity <= 0:
        raise ValueError("En, boy, kalınlık ve adet sıfırdan büyük olmalıdır.")
    return (width_mm * length_mm * thickness_mm * STEEL_DENSITY) / 1_000_000 * quantity


def calculate_weight_price(weight_kg: float, unit_price: float) -> float:
    """Hesaplanan kilogramı geçerli kilo fiyatıyla çarpar."""
    if weight_kg <= 0 or unit_price < 0:
        raise ValueError("Ağırlık sıfırdan büyük, kilo fiyatı negatif olmayan bir değer olmalıdır.")
    return weight_kg * unit_price


class WeightCalculatorDialog(QDialog):
    def __init__(
        self,
        connection: sqlite3.Connection,
        parent: QWidget | None = None,
        allow_add_to_cart: bool = True,
    ) -> None:
        super().__init__(parent)
        self.connection = connection
        self.cart_item: dict[str, float | str] | None = None
        self.setWindowTitle("Ağırlık Hesaplayıcı")
        self.setMinimumWidth(390)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Çelik yoğunluğu: 7,85 g/cm³"))
        form = QFormLayout()
        self.width = self._dimension_input()
        self.length = self._dimension_input()
        self.thickness = self._dimension_input()
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 1_000_000)
        self.quantity.setSingleStep(1)
        self.quantity.setSpecialValueText("Geçerli adet girin")
        form.addRow("En (mm)", self.width)
        form.addRow("Boy (mm)", self.length)
        form.addRow("Kalınlık (mm)", self.thickness)
        form.addRow("Adet", self.quantity)
        self.description = QLineEdit()
        self.description.setPlaceholderText("Baca şapkası, özel büküm vb.")
        form.addRow("Kalem açıklaması", self.description)
        self.price_source = QComboBox()
        self.price_source.addItem("Kilo fiyatını elle gir", None)
        for product in list_products(connection):
            if product["birim"].strip().lower() in {"kg", "kilogram"}:
                self.price_source.addItem(
                    f"Katalog: {product['kod']} — {product['ad']} ({product['birim_fiyat']:.2f} ₺/KG)",
                    float(product["birim_fiyat"]),
                )
        self.kilo_price = QDoubleSpinBox()
        self.kilo_price.setRange(0, 10_000_000)
        self.kilo_price.setDecimals(2)
        self.kilo_price.setSingleStep(1.0)
        self.kilo_price.setPrefix("₺ ")
        form.addRow("Kilo fiyatı kaynağı", self.price_source)
        form.addRow("Kilo fiyatı", self.kilo_price)
        layout.addLayout(form)

        result_card = Card("Hesap sonucu")
        self.result = QLabel("0,000 KG")
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setStyleSheet("font-size: 28px; font-weight: 700; color: #17A2A4;")
        self.validation = QLabel("En, boy, kalınlık ve adet sıfırdan büyük olmalıdır.")
        self.validation.setAlignment(Qt.AlignCenter)
        self.validation.setStyleSheet("color: #C44536;")
        result_card.layout.addWidget(self.result)
        self.price_result = QLabel("Tutar: 0,00 ₺")
        self.price_result.setAlignment(Qt.AlignCenter)
        self.price_result.setStyleSheet("font-size: 18px; font-weight: 600; color: #132638;")
        result_card.layout.addWidget(self.price_result)
        result_card.layout.addWidget(self.validation)
        layout.addWidget(result_card)
        close_button = SecondaryButton("Kapat")
        close_button.clicked.connect(self.accept)
        if allow_add_to_cart:
            add_button = PrimaryButton("Hesapla ve Sepete Ekle")
            add_button.clicked.connect(self.add_to_cart)
            layout.addWidget(page_actions(close_button, add_button))
        else:
            layout.addWidget(page_actions(close_button))

        for input_widget in (self.width, self.length, self.thickness, self.quantity):
            input_widget.valueChanged.connect(self.update_result)
        self.kilo_price.valueChanged.connect(self.update_result)
        self.price_source.currentIndexChanged.connect(self.apply_price_source)
        self.update_result()

    @staticmethod
    def _dimension_input() -> QDoubleSpinBox:
        input_widget = QDoubleSpinBox()
        input_widget.setRange(0, 10_000_000)
        input_widget.setDecimals(2)
        input_widget.setSingleStep(1.0)
        input_widget.setSuffix(" mm")
        input_widget.setSpecialValueText("Geçerli ölçü girin")
        input_widget.setToolTip("Negatif değer kabul edilmez; sıfırdan büyük bir ölçü girin.")
        return input_widget

    def update_result(self) -> None:
        try:
            weight = calculate_weight_kg(self.width.value(), self.length.value(), self.thickness.value(), self.quantity.value())
            total = calculate_weight_price(weight, self.kilo_price.value())
        except ValueError as error:
            self.result.setText("0,000 KG")
            self.price_result.setText("Tutar: 0,00 ₺")
            self.validation.setText(str(error))
            self.validation.setStyleSheet("color: #C44536;")
            return
        self.result.setText(f"{weight:,.3f} KG".replace(",", "X").replace(".", ",").replace("X", "."))
        self.price_result.setText(f"Tutar: {total:,.2f} ₺".replace(",", "X").replace(".", ",").replace("X", "."))
        self.validation.setText("Geçerli ölçüler girildi.")
        self.validation.setStyleSheet("color: #5C6B76;")

    def apply_price_source(self) -> None:
        catalog_price = self.price_source.currentData()
        is_manual = catalog_price is None
        self.kilo_price.setEnabled(is_manual)
        if not is_manual:
            self.kilo_price.setValue(float(catalog_price))

    def add_to_cart(self) -> None:
        try:
            weight = calculate_weight_kg(self.width.value(), self.length.value(), self.thickness.value(), self.quantity.value())
            total = calculate_weight_price(weight, self.kilo_price.value())
        except ValueError as error:
            self.validation.setText(str(error))
            self.validation.setStyleSheet("color: #C44536;")
            return
        description = self.description.text().strip() or "Özel ağırlık hesabı"
        self.cart_item = {
            "tip": "ekstra",
            "aciklama": f"{description} ({weight:.3f} KG × {self.kilo_price.value():.2f} ₺/KG)",
            "tutar": total,
        }
        self.accept()
