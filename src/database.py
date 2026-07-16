"""Uygulamanın SQLite bağlantı erişimi."""
from init_db import DATABASE_PATH as DB_PATH
from init_db import create_database


def initialize_database():
    """İlk çalıştırmada şemayı kurar ve foreign key açık bağlantı döndürür."""
    return create_database()
