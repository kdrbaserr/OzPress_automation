"""Ürün kartlarının kalıcı SQLite işlemleri."""
import sqlite3
from uuid import uuid4

from images import store_product_image


def create_product(
    connection: sqlite3.Connection, *, kod: str = "", ad: str, kategori: str | None, birim: str, birim_fiyat: float,
    kdv_orani: float = 0, source_image: str | None = None,
) -> int:
    """Ürünü kaydeder; görsel seçilmişse yalnızca göreli image_path saklanır."""
    image_path = store_product_image(source_image) if source_image else None
    with connection:
        temporary_code = kod.strip() or f"AUTO-{uuid4().hex}"
        cursor = connection.execute(
            """INSERT INTO urunler (kod, ad, kategori, birim, birim_fiyat, kdv_orani, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (temporary_code, ad.strip(), (kategori or "").strip() or None, birim.strip() or "Adet", birim_fiyat,
             kdv_orani, image_path),
        )
        product_id = int(cursor.lastrowid)
        if not kod.strip():
            connection.execute("UPDATE urunler SET kod = ? WHERE id = ?", (f"URN-{product_id:06d}", product_id))
    return product_id


def update_product(
    connection: sqlite3.Connection, *, product_id: int, kod: str, ad: str, kategori: str | None, birim: str,
    birim_fiyat: float, kdv_orani: float = 0, source_image: str | None = None,
) -> None:
    """Ürün bilgilerini günceller; yeni görsel seçilmezse mevcut yol korunur."""
    if source_image:
        image_path = store_product_image(source_image)
        image_sql = ", image_path = ?"
        image_values: tuple[object, ...] = (image_path,)
    else:
        image_sql = ""
        image_values = ()
    connection.execute(
        f"""UPDATE urunler
            SET kod = ?, ad = ?, kategori = ?, birim = ?, birim_fiyat = ?, kdv_orani = ?, updated_at = CURRENT_TIMESTAMP{image_sql}
            WHERE id = ? AND aktif = 1""",
        (kod.strip(), ad.strip(), (kategori or "").strip() or None, birim.strip() or "Adet", birim_fiyat,
         kdv_orani, *image_values, product_id),
    )
    connection.commit()


def soft_delete_product(connection: sqlite3.Connection, product_id: int) -> None:
    """Ürünü ilişkileri bozmadan katalogdan kaldırır."""
    connection.execute(
        "UPDATE urunler SET aktif = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (product_id,)
    )
    connection.commit()


def update_catalog_price(connection: sqlite3.Connection, product_id: int, birim_fiyat: float) -> None:
    """Yalnızca kullanıcı onayıyla ürün kartının sabit fiyatını günceller."""
    connection.execute(
        "UPDATE urunler SET birim_fiyat = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND aktif = 1",
        (birim_fiyat, product_id),
    )
    connection.commit()


def get_product(connection: sqlite3.Connection, product_id: int) -> sqlite3.Row | None:
    connection.row_factory = sqlite3.Row
    return connection.execute("SELECT * FROM urunler WHERE id = ? AND aktif = 1", (product_id,)).fetchone()


def list_categories(connection: sqlite3.Connection) -> list[str]:
    return [
        row[0] for row in connection.execute(
            "SELECT DISTINCT kategori FROM urunler WHERE aktif = 1 AND kategori IS NOT NULL ORDER BY kategori"
        )
    ]


def list_products(
    connection: sqlite3.Connection, *, search: str = "", kategori: str = "", image_filter: str = "Tümü"
) -> list[sqlite3.Row]:
    """Katalog listesini arama, kategori ve görsel durumuna göre getirir."""
    filters = ["aktif = 1"]
    values: list[str] = []
    if search.strip():
        filters.append("(kod LIKE ? OR ad LIKE ?)")
        term = f"%{search.strip()}%"
        values.extend([term, term])
    if kategori:
        filters.append("kategori = ?")
        values.append(kategori)
    if image_filter == "Görselli":
        filters.append("image_path IS NOT NULL AND image_path <> ''")
    elif image_filter == "Görselsiz":
        filters.append("(image_path IS NULL OR image_path = '')")
    connection.row_factory = sqlite3.Row
    return connection.execute(
        f"SELECT id, kod, ad, kategori, birim, birim_fiyat, kdv_orani, image_path FROM urunler WHERE {' AND '.join(filters)} ORDER BY ad",
        values,
    ).fetchall()
