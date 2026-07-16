"""Firma ayarlarının SQLite içinde kalıcı tutulması."""
import sqlite3
from images import store_company_logo

DEFAULTS = {"firma_adi": "", "telefon": "", "adres": "", "logo_path": "", "kdv_orani": "0"}

def get_settings(connection: sqlite3.Connection) -> dict[str, str]:
    values = DEFAULTS.copy()
    values.update(dict(connection.execute("SELECT anahtar, deger FROM ayarlar")))
    return values

def save_settings(connection: sqlite3.Connection, values: dict[str, str], logo_source: str | None = None) -> None:
    if logo_source:
        values["logo_path"] = store_company_logo(logo_source)
    connection.executemany("INSERT INTO ayarlar(anahtar,deger) VALUES (?,?) ON CONFLICT(anahtar) DO UPDATE SET deger=excluded.deger", values.items())
    connection.commit()
