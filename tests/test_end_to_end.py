"""Yerel Özpress iş akışının uçtan uca senaryo testi."""
from datetime import date
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ledger import account_statement, record_collection
from offline import verify_offline_only
from orders import confirm_order, create_order
from products import create_product, update_catalog_price
from reports import create_order_pdf
from settings import save_settings
from weight_calculator import calculate_weight_kg, calculate_weight_price


def run_scenario() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
    customer_id = connection.execute("INSERT INTO musteriler (kod, unvan) VALUES ('C-001', 'Örnek Firma')").lastrowid
    panel_id = create_product(connection, kod="PNL-01", ad="Panel", kategori="Panel", birim="Adet", birim_fiyat=500)
    kilo_id = create_product(connection, kod="SAC-KG", ad="Galvaniz Sac", kategori="Sac", birim="KG", birim_fiyat=480)

    # Siparişte fiyat ezilir (500 -> 480); katalog fiyatı kullanıcı onayıyla ayrıca güncellenir.
    update_catalog_price(connection, panel_id, 480)
    weight = calculate_weight_kg(1000, 2000, 1, 2)
    calculated_total = calculate_weight_price(weight, 480)
    assert weight == 31.4 and calculated_total == 15072

    order_id = create_order(connection, musteri_id=customer_id, proje_tipi="Panel Çatı", items=[
        {"tip": "urun", "urun_id": panel_id, "miktar": 2, "birim_fiyat": 480},
        {"tip": "ekstra", "aciklama": "Baca şapkası ağırlık hesabı", "tutar": calculated_total},
    ])
    confirm_order(connection, order_id)
    confirm_order(connection, order_id)  # Mükerrer borç yazılmamalı.
    assert connection.execute("SELECT COUNT(*) FROM cari_hareketler WHERE siparis_id = ?", (order_id,)).fetchone()[0] == 1

    record_collection(connection, customer_id=customer_id, amount=32, payment_date=date(2026, 7, 16), payment_method="Havale")
    statement = account_statement(connection, customer_id)
    assert statement[-1]["bakiye"] == 16000

    save_settings(connection, {"firma_adi": "Özpress", "telefon": "0555 000 00 00", "adres": "Antalya", "kdv_orani": "20"})
    with tempfile.TemporaryDirectory() as temp:
        pdf_path = create_order_pdf(connection, order_id, document_type="Sipariş", paper_format="A4", destination=Path(temp) / "siparis.pdf")
        assert pdf_path.read_bytes().startswith(b"%PDF-")


if __name__ == "__main__":
    verify_offline_only()
    run_scenario()
    print("Uçtan uca senaryo ve offline denetimi başarılı")
