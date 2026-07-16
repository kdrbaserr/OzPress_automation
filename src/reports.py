"""Sipariş/teklif için A4 ve termal PDF üretimi."""
from pathlib import Path
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from customers import customer_detail
from images import resolve_image_path
from settings import get_settings

FONT = "Helvetica"
for font_path in (Path("C:/Windows/Fonts/arial.ttf"),):
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("Ozpress", str(font_path)))
        FONT = "Ozpress"
        break

SIZES = {"A4": A4, "Termal 58 mm": (58 * mm, 220 * mm), "Termal 80 mm": (80 * mm, 220 * mm)}

def create_order_pdf(connection: sqlite3.Connection, order_id: int, *, document_type: str, paper_format: str, destination: Path) -> Path:
    connection.row_factory = sqlite3.Row
    order = connection.execute("SELECT s.*, m.unvan FROM siparisler s JOIN musteriler m ON m.id=s.musteri_id WHERE s.id=?", (order_id,)).fetchone()
    if not order: raise ValueError("Sipariş bulunamadı.")
    lines = connection.execute("SELECT u.ad, k.miktar, k.birim_fiyat, k.satir_toplami FROM siparis_kalemleri k JOIN urunler u ON u.id=k.urun_id WHERE k.siparis_id=?", (order_id,)).fetchall()
    extras = connection.execute("SELECT aciklama, satir_toplami FROM ekstra_kalemler WHERE siparis_id=?", (order_id,)).fetchall()
    company = get_settings(connection)
    _, _, movements = customer_detail(connection, order["musteri_id"])
    balance = sum((m["tutar"] if m["hareket_tipi"] == "Borç" else -m["tutar"]) for m in movements)
    kdv = float(company["kdv_orani"] or 0); subtotal=float(order["genel_toplam"]); tax=subtotal*kdv/100; total=subtotal+tax
    destination.parent.mkdir(parents=True, exist_ok=True); width,height=SIZES[paper_format]; c=canvas.Canvas(str(destination), pagesize=(width,height)); y=height-12*mm
    logo=resolve_image_path(company["logo_path"])
    if logo and logo.suffix.lower() != '.svg': c.drawImage(str(logo), 10*mm, y-16*mm, width=16*mm, height=16*mm, preserveAspectRatio=True); x=30*mm
    else: x=10*mm
    c.setFont(FONT, 14); c.drawString(x,y,company["firma_adi"] or "ÖZPRESS OTOMASYON"); y-=7*mm; c.setFont(FONT,8); c.drawString(x,y,company["telefon"]); y-=5*mm; c.drawString(x,y,company["adres"]); y-=10*mm
    c.setFont(FONT,12); c.drawString(10*mm,y,document_type.upper()); y-=6*mm; c.setFont(FONT,8); c.drawString(10*mm,y,f"No: {order['siparis_no']} | {order['siparis_tarihi']} | {order['proje_tipi']}"); y-=5*mm; c.drawString(10*mm,y,f"Cari: {order['unvan']}"); y-=8*mm
    c.line(10*mm,y,width-10*mm,y); y-=5*mm; c.setFont(FONT,8)
    for line in lines:
        c.drawString(10*mm,y,f"{line['ad']}  {line['miktar']} x {line['birim_fiyat']:.2f}"); c.drawRightString(width-10*mm,y,f"{line['satir_toplami']:.2f} TL"); y-=5*mm
    for line in extras:
        c.drawString(10*mm,y,str(line['aciklama'])); c.drawRightString(width-10*mm,y,f"{line['satir_toplami']:.2f} TL"); y-=5*mm
    y-=3*mm; c.line(10*mm,y,width-10*mm,y); y-=5*mm
    totals = [("Ara Toplam", subtotal)]
    if kdv: totals.append((f"KDV %{kdv:g}", tax))
    totals.extend([("Genel Toplam", total), ("Cari Bakiye", balance)])
    for label, value in totals:
        c.drawString(10*mm,y,label); c.drawRightString(width-10*mm,y,f"{value:.2f} TL"); y-=5*mm
    c.setFont(FONT,7); c.drawString(10*mm,10*mm,"Yerel Özpress Otomasyon çıktısı"); c.save(); return destination
