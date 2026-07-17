"""Sipariş/teklif için A4 ve termal PDF üretimi."""
from pathlib import Path
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
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
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "OZSAHIN_METAL_Fatura_Sablonu.pdf"

def create_order_pdf(connection: sqlite3.Connection, order_id: int, *, document_type: str, paper_format: str, destination: Path) -> Path:
    connection.row_factory = sqlite3.Row
    order = connection.execute("SELECT s.*, m.unvan, m.adres, m.telefon, m.eposta, m.vergi_dairesi, m.vergi_no FROM siparisler s JOIN musteriler m ON m.id=s.musteri_id WHERE s.id=?", (order_id,)).fetchone()
    if not order: raise ValueError("Sipariş bulunamadı.")
    lines = connection.execute(
        """SELECT u.ad, k.miktar, k.birim_fiyat, k.kdv_orani, k.satir_toplami
           FROM siparis_kalemleri k JOIN urunler u ON u.id=k.urun_id WHERE k.siparis_id=?""",
        (order_id,),
    ).fetchall()
    extras = connection.execute("SELECT aciklama, satir_toplami FROM ekstra_kalemler WHERE siparis_id=?", (order_id,)).fetchall()
    company = get_settings(connection)
    _, _, movements = customer_detail(connection, order["musteri_id"])
    balance = sum((m["tutar"] if m["hareket_tipi"] == "Borç" else -m["tutar"]) for m in movements)
    product_net = sum(float(line["satir_toplami"]) for line in lines)
    tax = sum(float(line["satir_toplami"]) * float(line["kdv_orani"]) / 100 for line in lines)
    extra_total = sum(float(line["satir_toplami"]) for line in extras)
    subtotal = product_net + extra_total
    total = subtotal + tax
    if document_type == "Fatura" and TEMPLATE.exists():
        return _fill_invoice_template(order, lines, extras, company, tax, total, destination)
    destination.parent.mkdir(parents=True, exist_ok=True); width,height=SIZES[paper_format]; c=canvas.Canvas(str(destination), pagesize=(width,height)); y=height-12*mm
    logo=resolve_image_path(company["logo_path"])
    if logo and logo.suffix.lower() != '.svg': c.drawImage(str(logo), 10*mm, y-16*mm, width=16*mm, height=16*mm, preserveAspectRatio=True); x=30*mm
    else: x=10*mm
    c.setFont(FONT, 14); c.drawString(x,y,company["firma_adi"] or "ÖZPRESS OTOMASYON"); y-=7*mm; c.setFont(FONT,8); c.drawString(x,y,company["telefon"]); y-=5*mm; c.drawString(x,y,company["adres"]); y-=10*mm
    c.setFont(FONT,12); c.drawString(10*mm,y,document_type.upper()); y-=6*mm; c.setFont(FONT,8); c.drawString(10*mm,y,f"No: {order['siparis_no']} | {order['siparis_tarihi']} | {order['proje_tipi']}"); y-=5*mm; c.drawString(10*mm,y,f"Cari: {order['unvan']}"); y-=8*mm
    c.line(10*mm,y,width-10*mm,y); y-=5*mm; c.setFont(FONT,8)
    for line in lines:
        line_tax = float(line['satir_toplami']) * float(line['kdv_orani']) / 100
        c.drawString(10*mm,y,f"{line['ad']}  {line['miktar']} x {line['birim_fiyat']:.2f} + %{line['kdv_orani']:g} KDV")
        c.drawRightString(width-10*mm,y,f"{float(line['satir_toplami']) + line_tax:.2f} TL"); y-=5*mm
    for line in extras:
        c.drawString(10*mm,y,str(line['aciklama'])); c.drawRightString(width-10*mm,y,f"{line['satir_toplami']:.2f} TL"); y-=5*mm
    y-=3*mm; c.line(10*mm,y,width-10*mm,y); y-=5*mm
    totals = [("KDV'siz Toplam", subtotal)]
    for rate in sorted({float(line["kdv_orani"]) for line in lines if float(line["kdv_orani"])}):
        rate_tax = sum(float(line["satir_toplami"]) * rate / 100 for line in lines if float(line["kdv_orani"]) == rate)
        totals.append((f"KDV %{rate:g}", rate_tax))
    totals.extend([("Genel Toplam", total), ("Cari Bakiye", balance)])
    for label, value in totals:
        c.drawString(10*mm,y,label); c.drawRightString(width-10*mm,y,f"{value:.2f} TL"); y-=5*mm
    c.setFont(FONT,7); c.drawString(10*mm,10*mm,"Yerel Özpress Otomasyon çıktısı"); c.save(); return destination

def _fill_invoice_template(order, lines, extras, company, tax, total, destination: Path) -> Path:
    """Kullanıcının PDF şablonunun üstüne girilmiş alanları işleyen katmanı ekler."""
    from io import BytesIO
    destination.parent.mkdir(parents=True, exist_ok=True)
    buffer=BytesIO(); c=canvas.Canvas(buffer,pagesize=A4); c.setFont(FONT,8)
    def put(x,y,text):
        if text: c.drawString(x,y,str(text))
    # Koordinatlar, OZSAHIN_METAL_Fatura_Sablonu.pdf üzerindeki çizgilerle hizalıdır.
    put(500,735,f"FAT-{order['siparis_no']}"); put(500,722,order['siparis_tarihi'])
    # Satıcı sol, alıcı sağ blok.
    seller=[company['firma_adi'],company['adres'],company['vergi_dairesi'],company['vergi_no'],f"{company['telefon']} {company['eposta']}".strip()]
    buyer=[order['unvan'],order['adres'],order['vergi_dairesi'],order['vergi_no'],f"{order['telefon'] or ''} {order['eposta'] or ''}".strip()]
    for i,(left,right) in enumerate(zip(seller,buyer)):
        put(95,613-i*10,left); put(365,613-i*10,right)
    put(92,525,order['siparis_no']); put(490,525,'TL')
    row_y=470
    all_lines=[(x['ad'],x['miktar'],x['birim_fiyat'],x['kdv_orani'],x['satir_toplami']) for x in lines]+[(x['aciklama'],1,x['satir_toplami'],0,x['satir_toplami']) for x in extras]
    for index,line in enumerate(all_lines[:7],1):
        y=row_y-(index-1)*17; put(72,y,index); put(112,y,line[0]); put(220,y,line[1]); put(310,y,'Adet'); put(400,y,f"{float(line[2]):.2f}"); put(465,y,f"%{float(line[3]):g}"); put(530,y,f"{float(line[4]):.2f}")
    put(530,287,f"{total-tax:.2f}"); put(530,266,f"{tax:.2f}"); put(530,224,f"{total:.2f}"); put(140,244, company['iban'] or '')
    c.save(); overlay=PdfReader(buffer).pages[0]; base=PdfReader(str(TEMPLATE)); base.pages[0].merge_page(overlay); writer=PdfWriter(); writer.add_page(base.pages[0])
    with open(destination,'wb') as output: writer.write(output)
    return destination
