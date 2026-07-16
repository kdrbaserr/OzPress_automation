"""Ürün kartlarının SQLite işlemleri."""
import sqlite3

from images import store_product_image


def create_product(
    connection: sqlite3.Connection, *, kod: str, ad: str, birim: str, birim_fiyat: float, source_image: str | None = None
) -> int:
    """Ürünü kaydeder; görsel seçildiyse DB'ye yalnızca göreli image_path yazılır."""
    image_path = store_product_image(source_image) if source_image else None
    cursor = connection.execute(
        """
        INSERT INTO urunler (kod, ad, birim, birim_fiyat, image_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (kod.strip(), ad.strip(), birim.strip() or "Adet", birim_fiyat, image_path),
    )
    connection.commit()
    return cursor.lastrowid


def list_products(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute(
        "SELECT id, kod, ad, birim, birim_fiyat, image_path FROM urunler WHERE aktif = 1 ORDER BY ad"
    ).fetchall()
