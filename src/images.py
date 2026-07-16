"""Ürün görsellerinin yalnızca yerel diskte saklanması."""
from pathlib import Path
import shutil
from uuid import uuid4


APP_DIRECTORY = Path(__file__).resolve().parent.parent
IMAGES_DIRECTORY = APP_DIRECTORY / "Resimler"
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg"}


def store_product_image(source_path: str | Path) -> str:
    """Görseli benzersiz adla Resimler'e kopyalar ve göreli yolunu döndürür."""
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(f"Görsel dosyası bulunamadı: {source}")
    extension = source.suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Desteklenen görsel türleri: PNG, JPG, JPEG, WEBP, BMP, SVG")

    IMAGES_DIRECTORY.mkdir(parents=True, exist_ok=True)
    unique_name = f"urun_{uuid4().hex}{extension}"
    destination = IMAGES_DIRECTORY / unique_name
    shutil.copy2(source, destination)

    # Veritabanı taşınabilir kalsın: tam disk yolu yerine yalnızca göreli yol saklanır.
    return destination.relative_to(APP_DIRECTORY).as_posix()


def store_company_logo(source_path: str | Path) -> str:
    """Firma logosunu yerel Resimler klasörüne benzersiz adla kopyalar."""
    source = Path(source_path)
    if not source.is_file() or source.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Geçerli bir logo görseli seçin.")
    IMAGES_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = IMAGES_DIRECTORY / f"firma_logo_{uuid4().hex}{source.suffix.lower()}"
    shutil.copy2(source, destination)
    return destination.relative_to(APP_DIRECTORY).as_posix()


def resolve_image_path(stored_path: str | None) -> Path | None:
    """Veritabanındaki göreli görsel yolunu güvenli bir yerel dosya yoluna çevirir."""
    if not stored_path:
        return None
    candidate = (APP_DIRECTORY / stored_path).resolve()
    images_root = IMAGES_DIRECTORY.resolve()
    if images_root not in candidate.parents or not candidate.is_file():
        return None
    return candidate
