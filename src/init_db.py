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
    connection.commit()
    return connection


if __name__ == "__main__":
    connection = create_database()
    connection.close()
    print(f"Veritabanı hazır: {DATABASE_PATH}")
