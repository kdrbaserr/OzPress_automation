"""Proje kayıtlarının veri erişim işlemleri."""
import sqlite3


def list_projects(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    return connection.execute(
        """SELECT p.id, p.ad, p.proje_tipi, p.musteri_id, p.aciklama, p.maliyet, p.proje_degeri,
                  m.unvan AS musteri
           FROM projeler p LEFT JOIN musteriler m ON m.id = p.musteri_id
           WHERE p.aktif = 1 ORDER BY p.created_at DESC, p.id DESC"""
    ).fetchall()


def create_project(connection: sqlite3.Connection, *, ad: str, proje_tipi: str,
                   musteri_id: int | None = None, aciklama: str = "", maliyet: float | None = None,
                   proje_degeri: float | None = None) -> int:
    ad, proje_tipi = ad.strip(), proje_tipi.strip()
    if not ad or not proje_tipi:
        raise ValueError("Proje adı ve proje türü zorunludur.")
    with connection:
        if maliyet is not None and maliyet < 0 or proje_degeri is not None and proje_degeri < 0:
            raise ValueError("Maliyet ve proje değeri negatif olamaz.")
        cursor = connection.execute(
            """INSERT INTO projeler (ad, proje_tipi, musteri_id, aciklama, maliyet, proje_degeri)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (ad, proje_tipi, musteri_id, aciklama.strip(), maliyet, proje_degeri),
        )
    return int(cursor.lastrowid)


def get_project(connection: sqlite3.Connection, project_id: int) -> sqlite3.Row | None:
    connection.row_factory = sqlite3.Row
    return connection.execute("SELECT * FROM projeler WHERE id = ? AND aktif = 1", (project_id,)).fetchone()


def update_project(connection: sqlite3.Connection, *, project_id: int, ad: str, proje_tipi: str,
                   musteri_id: int | None = None, aciklama: str = "", maliyet: float | None = None,
                   proje_degeri: float | None = None) -> None:
    ad, proje_tipi = ad.strip(), proje_tipi.strip()
    if not ad or not proje_tipi:
        raise ValueError("Proje adı ve proje türü zorunludur.")
    if (maliyet is not None and maliyet < 0) or (proje_degeri is not None and proje_degeri < 0):
        raise ValueError("Maliyet ve proje değeri negatif olamaz.")
    with connection:
        cursor = connection.execute(
            """UPDATE projeler SET ad=?, proje_tipi=?, musteri_id=?, aciklama=?, maliyet=?, proje_degeri=?,
                      updated_at=CURRENT_TIMESTAMP WHERE id=? AND aktif=1""",
            (ad, proje_tipi, musteri_id, aciklama.strip(), maliyet, proje_degeri, project_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("Proje bulunamadı.")


def soft_delete_project(connection: sqlite3.Connection, project_id: int) -> None:
    """Projeyi ilişkili siparişleri bozmadan aktif listeden kaldırır."""
    cursor = connection.execute(
        "UPDATE projeler SET aktif = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND aktif = 1",
        (project_id,),
    )
    if cursor.rowcount == 0:
        raise ValueError("Proje bulunamadı.")
    connection.commit()
