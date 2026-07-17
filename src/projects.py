"""Proje kayıtlarının veri erişim işlemleri."""
import sqlite3


def list_projects(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute(
        """SELECT p.id, p.ad, p.proje_tipi, p.musteri_id, p.aciklama, m.unvan AS musteri
           FROM projeler p LEFT JOIN musteriler m ON m.id = p.musteri_id
           WHERE p.aktif = 1 ORDER BY p.created_at DESC, p.id DESC"""
    ).fetchall()


def create_project(connection: sqlite3.Connection, *, ad: str, proje_tipi: str,
                   musteri_id: int | None = None, aciklama: str = "") -> int:
    ad, proje_tipi = ad.strip(), proje_tipi.strip()
    if not ad or not proje_tipi:
        raise ValueError("Proje adı ve proje türü zorunludur.")
    with connection:
        cursor = connection.execute(
            "INSERT INTO projeler (ad, proje_tipi, musteri_id, aciklama) VALUES (?, ?, ?, ?)",
            (ad, proje_tipi, musteri_id, aciklama.strip()),
        )
    return int(cursor.lastrowid)


def soft_delete_project(connection: sqlite3.Connection, project_id: int) -> None:
    """Projeyi ilişkili siparişleri bozmadan aktif listeden kaldırır."""
    cursor = connection.execute(
        "UPDATE projeler SET aktif = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND aktif = 1",
        (project_id,),
    )
    if cursor.rowcount == 0:
        raise ValueError("Proje bulunamadı.")
    connection.commit()
