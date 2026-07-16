"""Tahsilat ve cari hesap ekstresi işlemleri."""
from datetime import date
import sqlite3


def record_collection(
    connection: sqlite3.Connection, *, customer_id: int, amount: float, payment_date: date, payment_method: str
) -> int:
    if amount <= 0:
        raise ValueError("Tahsilat tutarı sıfırdan büyük olmalıdır.")
    cursor = connection.execute(
        """INSERT INTO cari_hareketler (musteri_id, hareket_tarihi, hareket_tipi, tutar, odeme_sekli, aciklama)
           VALUES (?, ?, 'Alacak', ?, ?, ?)""",
        (customer_id, payment_date.isoformat(), amount, payment_method, f"Tahsilat ({payment_method})"),
    )
    connection.commit()
    return cursor.lastrowid


def account_statement(connection: sqlite3.Connection, customer_id: int) -> list[sqlite3.Row]:
    """Cari hareketleri zaman sıralı ve her satırda güncel bakiye ile döndürür."""
    connection.row_factory = sqlite3.Row
    movements = connection.execute(
        """SELECT hareket_tarihi, hareket_tipi, tutar, odeme_sekli, aciklama
           FROM cari_hareketler WHERE musteri_id = ? ORDER BY hareket_tarihi, id""", (customer_id,)
    ).fetchall()
    balance = 0.0
    statement: list[dict[str, object]] = []
    for movement in movements:
        amount = float(movement["tutar"])
        debt = amount if movement["hareket_tipi"] == "Borç" else 0.0
        credit = amount if movement["hareket_tipi"] == "Alacak" else 0.0
        balance += debt - credit
        statement.append({**dict(movement), "borc": debt, "alacak": credit, "bakiye": balance})
    return statement
