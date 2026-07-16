"""Müşteri kartları, bakiye özeti ve geçmiş kayıt sorguları."""
import sqlite3
from uuid import uuid4


BALANCE_EXPRESSION = "COALESCE(SUM(CASE WHEN h.hareket_tipi = 'Borç' THEN h.tutar ELSE -h.tutar END), 0)"


def create_customer(connection: sqlite3.Connection, *, unvan: str, telefon: str = "", adres: str = "", notlar: str = "", eposta: str = "", vergi_dairesi: str = "", vergi_no: str = "") -> int:
    cursor = connection.execute(
        """INSERT INTO musteriler (kod, unvan, telefon, adres, notlar, eposta, vergi_dairesi, vergi_no)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (f"CR-{uuid4().hex[:8].upper()}", unvan.strip(), telefon.strip() or None, adres.strip() or None, notlar.strip() or None, eposta.strip() or None, vergi_dairesi.strip() or None, vergi_no.strip() or None),
    )
    connection.commit()
    return cursor.lastrowid


def list_customers(connection: sqlite3.Connection, *, search: str = "", balance_filter: str = "Tümü") -> list[sqlite3.Row]:
    filters = ["m.aktif = 1"]
    values: list[str] = []
    if search.strip():
        filters.append("(m.unvan LIKE ? OR m.kod LIKE ? OR m.telefon LIKE ?)")
        term = f"%{search.strip()}%"
        values.extend([term, term, term])
    having = ""
    if balance_filter == "Borçlu":
        having = f"HAVING {BALANCE_EXPRESSION} > 0"
    elif balance_filter == "Alacaklı":
        having = f"HAVING {BALANCE_EXPRESSION} < 0"
    elif balance_filter == "Bakiyesi Sıfır":
        having = f"HAVING {BALANCE_EXPRESSION} = 0"
    connection.row_factory = sqlite3.Row
    return connection.execute(
        f"""SELECT m.id, m.kod, m.unvan, m.telefon, m.adres, m.notlar, {BALANCE_EXPRESSION} AS bakiye
            FROM musteriler m LEFT JOIN cari_hareketler h ON h.musteri_id = m.id
            WHERE {' AND '.join(filters)} GROUP BY m.id {having} ORDER BY m.unvan""",
        values,
    ).fetchall()


def customer_summary(connection: sqlite3.Connection) -> dict[str, float | int]:
    customers = list_customers(connection)
    return {
        "count": len(customers),
        "debtors": sum(1 for customer in customers if customer["bakiye"] > 0),
        "balance": sum(float(customer["bakiye"]) for customer in customers),
    }


def customer_detail(connection: sqlite3.Connection, customer_id: int) -> tuple[sqlite3.Row | None, list[sqlite3.Row], list[sqlite3.Row]]:
    connection.row_factory = sqlite3.Row
    customer = connection.execute(
        f"""SELECT m.*, {BALANCE_EXPRESSION} AS bakiye FROM musteriler m
            LEFT JOIN cari_hareketler h ON h.musteri_id = m.id WHERE m.id = ? GROUP BY m.id""", (customer_id,)
    ).fetchone()
    orders = connection.execute(
        "SELECT siparis_no, siparis_tarihi, proje_tipi, durum, genel_toplam FROM siparisler WHERE musteri_id = ? ORDER BY created_at DESC",
        (customer_id,),
    ).fetchall()
    movements = connection.execute(
        "SELECT hareket_tarihi, hareket_tipi, tutar, aciklama FROM cari_hareketler WHERE musteri_id = ? ORDER BY hareket_tarihi DESC, id DESC",
        (customer_id,),
    ).fetchall()
    return customer, orders, movements
