"""Uygulamanın tamamen yerel çalıştığını koruyan kontroller."""
from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parent
NETWORK_MODULES = {"requests", "urllib", "http", "httpx", "socket", "websockets", "aiohttp"}


def verify_offline_only() -> None:
    """Kaynak kodda ağ istemcisi ithali olmadığını doğrular.

    Veriler yalnızca SQLite dosyasına yazılır; uygulama API, web servisi veya
    ağ soketi kullanmaz. Yeni bir ağ bağımlılığı eklenirse uygulama açılırken
    bu kontrol bilinçli olarak hata verir.
    """
    for source_file in ROOT.glob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            prohibited = NETWORK_MODULES.intersection(names)
            if prohibited:
                raise RuntimeError(f"Offline mod ihlali: {source_file.name} içinde {prohibited} bulundu.")
