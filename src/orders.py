"""Sipariş/proje ve sipariş kalemi SQLite işlemleri."""
from datetime import datetime
import sqlite3
from uuid import uuid4


def list_customers(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute("SELECT id, kod, unvan FROM musteriler WHERE aktif = 1 ORDER BY unvan").fetchall()


def create_order(
    connection: sqlite3.Connection, *, musteri_id: int, proje_tipi: str, items: list[dict[str, float | int]]
) -> int:
    """Sepet kalemlerini tek işlemde kalıcı sipariş ve alt kalemlerine dönüştürür."""
    if not items:
        raise ValueError("Sipariş sepeti boş olamaz.")
    total = sum(float(item["miktar"]) * float(item["birim_fiyat"]) for item in items)
    order_number = f"SP-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"
    with connection:
        cursor = connection.execute(
            """INSERT INTO siparisler (siparis_no, musteri_id, proje_tipi, ara_toplam, genel_toplam)
               VALUES (?, ?, ?, ?, ?)""",
            (order_number, musteri_id, proje_tipi, total, total),
        )
        order_id = cursor.lastrowid
        connection.executemany(
            """INSERT INTO siparis_kalemleri (siparis_id, urun_id, miktar, birim_fiyat, satir_toplami)
               VALUES (?, ?, ?, ?, ?)""",
            [(order_id, int(item["urun_id"]), float(item["miktar"]), float(item["birim_fiyat"]),
              float(item["miktar"]) * float(item["birim_fiyat"])) for item in items],
        )
    return order_id
