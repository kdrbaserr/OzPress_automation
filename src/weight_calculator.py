"""Sac/çelik parça ağırlığını milimetre cinsinden hesaplayan arayüz."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDoubleSpinBox, QFormLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from components import Card, SecondaryButton, page_actions


STEEL_DENSITY = 7.85


def calculate_weight_kg(width_mm: float, length_mm: float, thickness_mm: float, quantity: int) -> float:
    """(En × Boy × Kalınlık × 7.85) / 1.000.000 × Adet formülünü uygular."""
    if width_mm <= 0 or length_mm <= 0 or thickness_mm <= 0 or quantity <= 0:
        raise ValueError("En, boy, kalınlık ve adet sıfırdan büyük olmalıdır.")
    return (width_mm * length_mm * thickness_mm * STEEL_DENSITY) / 1_000_000 * quantity


class WeightCalculatorDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
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
        self.quantity.setSpecialValueText("Geçerli adet girin")
        form.addRow("En (mm)", self.width)
        form.addRow("Boy (mm)", self.length)
        form.addRow("Kalınlık (mm)", self.thickness)
        form.addRow("Adet", self.quantity)
        layout.addLayout(form)

        result_card = Card("Hesap sonucu")
        self.result = QLabel("0,000 KG")
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setStyleSheet("font-size: 28px; font-weight: 700; color: #17A2A4;")
        self.validation = QLabel("En, boy, kalınlık ve adet sıfırdan büyük olmalıdır.")
        self.validation.setAlignment(Qt.AlignCenter)
        self.validation.setStyleSheet("color: #C44536;")
        result_card.layout.addWidget(self.result)
        result_card.layout.addWidget(self.validation)
        layout.addWidget(result_card)
        close_button = SecondaryButton("Kapat")
        close_button.clicked.connect(self.accept)
        layout.addWidget(page_actions(close_button))

        for input_widget in (self.width, self.length, self.thickness, self.quantity):
            input_widget.valueChanged.connect(self.update_result)
        self.update_result()

    @staticmethod
    def _dimension_input() -> QDoubleSpinBox:
        input_widget = QDoubleSpinBox()
        input_widget.setRange(0, 10_000_000)
        input_widget.setDecimals(2)
        input_widget.setSuffix(" mm")
        input_widget.setSpecialValueText("Geçerli ölçü girin")
        input_widget.setToolTip("Negatif değer kabul edilmez; sıfırdan büyük bir ölçü girin.")
        return input_widget

    def update_result(self) -> None:
        try:
            weight = calculate_weight_kg(self.width.value(), self.length.value(), self.thickness.value(), self.quantity.value())
        except ValueError as error:
            self.result.setText("0,000 KG")
            self.validation.setText(str(error))
            self.validation.setStyleSheet("color: #C44536;")
            return
        self.result.setText(f"{weight:,.3f} KG".replace(",", "X").replace(".", ",").replace("X", "."))
        self.validation.setText("Geçerli ölçüler girildi.")
        self.validation.setStyleSheet("color: #5C6B76;")
