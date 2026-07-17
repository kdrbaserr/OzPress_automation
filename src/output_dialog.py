from pathlib import Path
import sqlite3
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QMessageBox, QVBoxLayout
from components import PrimaryButton, SecondaryButton, page_actions
from orders import list_orders
from reports import create_order_pdf

class OutputDialog(QDialog):
    def __init__(self, connection: sqlite3.Connection, parent=None, *, order_id: int | None = None,
                 document_type: str | None = None):
        super().__init__(parent); self.connection=connection; self.setWindowTitle("PDF Çıktı"); layout=QVBoxLayout(self); form=QFormLayout()
        self.order=QComboBox()
        for row in list_orders(connection): self.order.addItem(f"{row['siparis_no']} — {row['musteri']}",row['id'])
        self.doc=QComboBox(); self.doc.addItems(["Fatura", "Sipariş", "Teklif"])
        self.paper=QComboBox(); self.paper.addItems(["A4", "Termal 58 mm", "Termal 80 mm"])
        self.doc.currentTextChanged.connect(self._sync_format)
        form.addRow("Sipariş",self.order); form.addRow("Belge",self.doc); form.addRow("Format",self.paper); layout.addLayout(form)
        cancel=SecondaryButton("Vazgeç"); cancel.clicked.connect(self.reject); save=PrimaryButton("Masaüstüne PDF Kaydet"); save.clicked.connect(self.save); layout.addWidget(page_actions(cancel,save))
        if order_id is not None:
            selected_index = self.order.findData(order_id)
            if selected_index >= 0: self.order.setCurrentIndex(selected_index)
        if document_type: self.doc.setCurrentText(document_type)
        self._sync_format(self.doc.currentText())
    def _sync_format(self, document_type):
        is_invoice = document_type == "Fatura"
        if is_invoice: self.paper.setCurrentText("A4")
        self.paper.setEnabled(not is_invoice)
    def save(self):
        if self.order.currentData() is None: return
        desktop=Path.home()/"Desktop"; path=desktop/f"{self.doc.currentText()}_{self.order.currentData()}.pdf"
        try: create_order_pdf(self.connection,self.order.currentData(),document_type=self.doc.currentText(),paper_format=self.paper.currentText(),destination=path)
        except Exception as error: QMessageBox.warning(self,"PDF oluşturulamadı",str(error)); return
        QMessageBox.information(self,"PDF hazır",f"Masaüstüne kaydedildi:\n{path}"); self.accept()
