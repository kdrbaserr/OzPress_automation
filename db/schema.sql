PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ayarlar (
    anahtar TEXT PRIMARY KEY,
    deger TEXT
);

-- Ürün kartları. image_path, Resimler klasörüne göre göreli veya tam yol tutabilir.
CREATE TABLE IF NOT EXISTS urunler (
    id INTEGER PRIMARY KEY,
    kod TEXT NOT NULL UNIQUE,
    ad TEXT NOT NULL,
    kategori TEXT,
    birim TEXT NOT NULL DEFAULT 'Adet',
    birim_fiyat REAL NOT NULL DEFAULT 0 CHECK (birim_fiyat >= 0),
    kdv_orani REAL NOT NULL DEFAULT 0 CHECK (kdv_orani >= 0),
    image_path TEXT,
    aktif INTEGER NOT NULL DEFAULT 1 CHECK (aktif IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Cari kartlar / müşteriler.
CREATE TABLE IF NOT EXISTS musteriler (
    id INTEGER PRIMARY KEY,
    kod TEXT NOT NULL UNIQUE,
    unvan TEXT NOT NULL,
    yetkili_kisi TEXT,
    telefon TEXT,
    eposta TEXT,
    vergi_dairesi TEXT,
    vergi_no TEXT,
    adres TEXT,
    notlar TEXT,
    aktif INTEGER NOT NULL DEFAULT 1 CHECK (aktif IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projeler (
    id INTEGER PRIMARY KEY,
    ad TEXT NOT NULL,
    proje_tipi TEXT NOT NULL,
    musteri_id INTEGER,
    aciklama TEXT,
    aktif INTEGER NOT NULL DEFAULT 1 CHECK (aktif IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS siparisler (
    id INTEGER PRIMARY KEY,
    siparis_no TEXT NOT NULL UNIQUE,
    musteri_id INTEGER NOT NULL,
    proje_id INTEGER,
    siparis_tarihi TEXT NOT NULL DEFAULT CURRENT_DATE,
    proje_tipi TEXT NOT NULL DEFAULT 'Diğer',
    durum TEXT NOT NULL DEFAULT 'Taslak'
        CHECK (durum IN ('Taslak', 'Onaylandı', 'Üretimde', 'Tamamlandı', 'İptal')),
    ara_toplam REAL NOT NULL DEFAULT 0 CHECK (ara_toplam >= 0),
    ekstra_toplam REAL NOT NULL DEFAULT 0 CHECK (ekstra_toplam >= 0),
    kdv_toplam REAL NOT NULL DEFAULT 0 CHECK (kdv_toplam >= 0),
    genel_toplam REAL NOT NULL DEFAULT 0 CHECK (genel_toplam >= 0),
    aciklama TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (proje_id) REFERENCES projeler(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS siparis_kalemleri (
    id INTEGER PRIMARY KEY,
    siparis_id INTEGER NOT NULL,
    urun_id INTEGER NOT NULL,
    miktar REAL NOT NULL CHECK (miktar > 0),
    birim_fiyat REAL NOT NULL CHECK (birim_fiyat >= 0),
    kdv_orani REAL NOT NULL DEFAULT 0 CHECK (kdv_orani >= 0),
    iskonto_orani REAL NOT NULL DEFAULT 0 CHECK (iskonto_orani BETWEEN 0 AND 100),
    satir_toplami REAL NOT NULL DEFAULT 0 CHECK (satir_toplami >= 0),
    aciklama TEXT,
    FOREIGN KEY (siparis_id) REFERENCES siparisler(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (urun_id) REFERENCES urunler(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Ürün dışı işçilik, nakliye vb. satırlar.
CREATE TABLE IF NOT EXISTS ekstra_kalemler (
    id INTEGER PRIMARY KEY,
    siparis_id INTEGER NOT NULL,
    aciklama TEXT NOT NULL,
    miktar REAL NOT NULL DEFAULT 1 CHECK (miktar > 0),
    birim_fiyat REAL NOT NULL DEFAULT 0 CHECK (birim_fiyat >= 0),
    satir_toplami REAL NOT NULL DEFAULT 0 CHECK (satir_toplami >= 0),
    FOREIGN KEY (siparis_id) REFERENCES siparisler(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS cari_hareketler (
    id INTEGER PRIMARY KEY,
    musteri_id INTEGER NOT NULL,
    siparis_id INTEGER,
    hareket_tarihi TEXT NOT NULL DEFAULT CURRENT_DATE,
    hareket_tipi TEXT NOT NULL CHECK (hareket_tipi IN ('Borç', 'Alacak')),
    tutar REAL NOT NULL CHECK (tutar > 0),
    odeme_sekli TEXT,
    aciklama TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (siparis_id) REFERENCES siparisler(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Sorgu ve ilişki alanı indeksleri.
CREATE INDEX IF NOT EXISTS idx_urunler_ad ON urunler(ad);
CREATE INDEX IF NOT EXISTS idx_urunler_kategori ON urunler(kategori);
CREATE INDEX IF NOT EXISTS idx_musteriler_unvan ON musteriler(unvan);
CREATE INDEX IF NOT EXISTS idx_siparisler_musteri_id ON siparisler(musteri_id);
CREATE INDEX IF NOT EXISTS idx_projeler_musteri_id ON projeler(musteri_id);
CREATE INDEX IF NOT EXISTS idx_siparisler_tarih ON siparisler(siparis_tarihi);
CREATE INDEX IF NOT EXISTS idx_siparisler_durum ON siparisler(durum);
CREATE INDEX IF NOT EXISTS idx_siparis_kalemleri_siparis_id ON siparis_kalemleri(siparis_id);
CREATE INDEX IF NOT EXISTS idx_siparis_kalemleri_urun_id ON siparis_kalemleri(urun_id);
CREATE INDEX IF NOT EXISTS idx_ekstra_kalemler_siparis_id ON ekstra_kalemler(siparis_id);
CREATE INDEX IF NOT EXISTS idx_cari_hareketler_musteri_tarih ON cari_hareketler(musteri_id, hareket_tarihi);
CREATE INDEX IF NOT EXISTS idx_cari_hareketler_siparis_id ON cari_hareketler(siparis_id);
