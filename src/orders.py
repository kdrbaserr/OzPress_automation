"""Sipariş/proje ve sipariş kalemi SQLite işlemleri."""
from datetime import datetime
import sqlite3
from uuid import uuid4


def list_customers(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute("SELECT id, kod, unvan FROM musteriler WHERE aktif = 1 ORDER BY unvan").fetchall()


def create_order(
    connection: sqlite3.Connection, *, musteri_id: int, proje_tipi: str, items: list[dict[str, float | int | str]],
    proje_id: int | None = None,
) -> int:
    """Sepet kalemlerini tek işlemde kalıcı sipariş ve alt kalemlerine dönüştürür."""
    if not items:
        raise ValueError("Sipariş sepeti boş olamaz.")
    product_items = [item for item in items if item["tip"] == "urun"]
    extra_items = [item for item in items if item["tip"] == "ekstra"]
    product_total = sum(float(item["miktar"]) * float(item["birim_fiyat"]) for item in product_items)
    vat_total = sum(
        float(item["miktar"]) * float(item["birim_fiyat"]) * float(item.get("kdv_orani", 0)) / 100
        for item in product_items
    )
    extra_total = sum(float(item["tutar"]) for item in extra_items)
    total = product_total + vat_total + extra_total
    order_number = f"SP-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"
    with connection:
        cursor = connection.execute(
            """INSERT INTO siparisler
               (siparis_no, musteri_id, proje_id, proje_tipi, ara_toplam, ekstra_toplam, kdv_toplam, genel_toplam)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_number, musteri_id, proje_id, proje_tipi, product_total, extra_total, vat_total, total),
        )
        order_id = cursor.lastrowid
        connection.executemany(
            """INSERT INTO siparis_kalemleri (siparis_id, urun_id, miktar, birim_fiyat, kdv_orani, satir_toplami)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [(order_id, int(item["urun_id"]), float(item["miktar"]), float(item["birim_fiyat"]),
              float(item.get("kdv_orani", 0)),
              float(item["miktar"]) * float(item["birim_fiyat"])) for item in product_items],
        )
        connection.executemany(
            """INSERT INTO ekstra_kalemler (siparis_id, aciklama, miktar, birim_fiyat, satir_toplami)
               VALUES (?, ?, 1, ?, ?)""",
            [(order_id, str(item["aciklama"]), float(item["tutar"]), float(item["tutar"])) for item in extra_items],
        )
    return order_id


def list_orders(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute(
        """SELECT s.id, s.siparis_no, m.unvan AS musteri, s.siparis_tarihi, s.durum, s.genel_toplam
           FROM siparisler s JOIN musteriler m ON m.id = s.musteri_id
           ORDER BY s.created_at DESC, s.id DESC"""
    ).fetchall()


def delete_order(connection: sqlite3.Connection, order_id: int) -> None:
    """Siparişi ve bu siparişin oluşturduğu cari hareketleri birlikte siler."""
    exists = connection.execute("SELECT 1 FROM siparisler WHERE id = ?", (order_id,)).fetchone()
    if not exists:
        raise ValueError("Sipariş bulunamadı.")
    with connection:
        connection.execute("DELETE FROM cari_hareketler WHERE siparis_id = ?", (order_id,))
        connection.execute("DELETE FROM siparisler WHERE id = ?", (order_id,))


def confirm_order(connection: sqlite3.Connection, order_id: int) -> None:
    """Siparişi onaylar ve tek seferlik Borç cari hareketini oluşturur."""
    connection.row_factory = sqlite3.Row
    order = connection.execute(
        "SELECT id, musteri_id, siparis_no, genel_toplam FROM siparisler WHERE id = ?", (order_id,)
    ).fetchone()
    if not order:
        raise ValueError("Sipariş bulunamadı.")
    if float(order["genel_toplam"]) <= 0:
        raise ValueError("Toplamı sıfır olan sipariş onaylanamaz.")
    with connection:
        connection.execute("UPDATE siparisler SET durum = 'Onaylandı', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
        exists = connection.execute(
            "SELECT 1 FROM cari_hareketler WHERE siparis_id = ? AND hareket_tipi = 'Borç'", (order_id,)
        ).fetchone()
        if not exists:
            connection.execute(
                """INSERT INTO cari_hareketler (musteri_id, siparis_id, hareket_tipi, tutar, aciklama)
                   VALUES (?, ?, 'Borç', ?, ?)""",
                (order["musteri_id"], order_id, order["genel_toplam"], f"Onaylanan sipariş: {order['siparis_no']}"),
            )
