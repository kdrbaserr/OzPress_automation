"""İlk çalıştırmada SQLite şemasını kuran başlangıç scripti."""
from pathlib import Path
import sqlite3


APP_DIRECTORY = Path(__file__).resolve().parent.parent
DATABASE_DIRECTORY = APP_DIRECTORY / "db"
DATABASE_PATH = DATABASE_DIRECTORY / "ozpress.db"
SCHEMA_PATH = DATABASE_DIRECTORY / "schema.sql"


def create_database() -> sqlite3.Connection:
    """Veritabanı dosyasını ve eksik tabloları güvenli biçimde oluşturur."""
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    _apply_schema_upgrades(connection)
    connection.commit()
    return connection


def _apply_schema_upgrades(connection: sqlite3.Connection) -> None:
    """Mevcut kullanıcı verisini silmeden küçük şema güncellemelerini uygular."""
    columns = {row[1] for row in connection.execute("PRAGMA table_info(siparisler)")}
    if "proje_tipi" not in columns:
        connection.execute("ALTER TABLE siparisler ADD COLUMN proje_tipi TEXT NOT NULL DEFAULT 'Diğer'")
    customer_columns = {row[1] for row in connection.execute("PRAGMA table_info(musteriler)")}
    if "notlar" not in customer_columns:
        connection.execute("ALTER TABLE musteriler ADD COLUMN notlar TEXT")
    ledger_columns = {row[1] for row in connection.execute("PRAGMA table_info(cari_hareketler)")}
    if "odeme_sekli" not in ledger_columns:
        connection.execute("ALTER TABLE cari_hareketler ADD COLUMN odeme_sekli TEXT")


if __name__ == "__main__":
    connection = create_database()
    connection.close()
    print(f"Veritabanı hazır: {DATABASE_PATH}")
