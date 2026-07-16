# Özpress Otomasyon

## Teknoloji kararı

Uygulama **Python 3.11+ / PySide6 / SQLite** ile kurulmuştur.

- **PySide6 (Qt):** Windows masaüstünde yerel görünüm, hızlı form geliştirme ve tek paketlenebilir dağıtım sağlar.
- **SQLite:** Tek dosyalı, sunucusuz ve yedeklemesi kolaydır. İlk sürümde katalog, sipariş, cari ve çıktı verileri için yeterlidir.
- **Gelişim yolu:** Çok kullanıcılı/ağ üzerinden eşzamanlı çalışmaya geçilirse veri erişim katmanı PostgreSQL'e taşınabilir; arayüz değişmeden kalır.

## Klasörler

```text
db/         SQLite veritabanı ve şema
Resimler/   Ürün görselleri
src/        Uygulama kaynak kodu
output/     Oluşturulan çıktı dosyaları
docs/       Tasarım dokümanları ve wireframe
```

## Çalıştırma

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

Uygulama ilk açılışta `db/ozpress.db` dosyasını ve tablolarını oluşturur.

## Genel akış

Ana Menü → Katalog → Sipariş → Cari → Çıktı

Detaylı taslak: `docs/wireframe.svg`.
