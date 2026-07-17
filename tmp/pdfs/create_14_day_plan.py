from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
import os

OUT = r"output/pdf/emlak_projesi_14_gunluk_tasklist.pdf"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

pdfmetrics.registerFont(TTFont("UI", r"C:\Windows\Fonts\segoeui.ttf"))
pdfmetrics.registerFont(TTFont("UIB", r"C:\Windows\Fonts\segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Serif", r"C:\Windows\Fonts\georgia.ttf"))
pdfmetrics.registerFont(TTFont("SerifB", r"C:\Windows\Fonts\georgiab.ttf"))

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#2F6BFF")
CYAN = colors.HexColor("#18A6B8")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
PALE = colors.HexColor("#F3F7FC")
LINE = colors.HexColor("#D9E2EC")
GREEN = colors.HexColor("#14966A")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverKicker", fontName="UIB", fontSize=10, leading=14, textColor=CYAN, spaceAfter=8, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CoverTitle", fontName="SerifB", fontSize=29, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", fontName="UI", fontSize=12, leading=18, textColor=MUTED, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="H1x", fontName="SerifB", fontSize=22, leading=27, textColor=NAVY, spaceAfter=10))
styles.add(ParagraphStyle(name="H2x", fontName="UIB", fontSize=14, leading=18, textColor=NAVY, spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="Day", fontName="SerifB", fontSize=17, leading=21, textColor=NAVY, spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx", fontName="UI", fontSize=9.3, leading=14, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx", fontName="UI", fontSize=8, leading=11, textColor=MUTED))
styles.add(ParagraphStyle(name="Taskx", fontName="UI", fontSize=9, leading=13, textColor=INK, leftIndent=12, firstLineIndent=-10, spaceAfter=3))
styles.add(ParagraphStyle(name="Labelx", fontName="UIB", fontSize=8.2, leading=11, textColor=BLUE, spaceAfter=3))
styles.add(ParagraphStyle(name="Wh", fontName="UIB", fontSize=9, leading=12, textColor=WHITE))
styles.add(ParagraphStyle(name="Cell", fontName="UI", fontSize=7.7, leading=10, textColor=INK))
styles.add(ParagraphStyle(name="CellB", fontName="UIB", fontSize=7.7, leading=10, textColor=NAVY))

def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LINE); canvas.line(18*mm, 282*mm, 192*mm, 282*mm)
        canvas.setFont("UI", 7.5); canvas.setFillColor(MUTED)
        canvas.drawString(18*mm, 287*mm, "ÖZPRESS • EMLAK PLATFORMU")
        canvas.drawRightString(192*mm, 12*mm, f"14 günlük ürün sprinti  •  {doc.page}")
    canvas.restoreState()

def pill(text, bg=BLUE):
    t = Table([[Paragraph(text, styles["Wh"])]], colWidths=[44*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0,bg),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return t

def tasks(items):
    return [Paragraph("☐  " + x, styles["Taskx"]) for x in items]

def info_box(title, body, color=PALE):
    t=Table([[Paragraph(title,styles["Labelx"])],[Paragraph(body,styles["Bodyx"])]], colWidths=[170*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),color),("BOX",(0,0),(-1,-1),0.7,LINE),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

days = [
(1,"Ürün vizyonu, kapsam ve teknik temel","Planlama",[
"Hedef kullanıcıları netleştir: alıcı/kiracı, ziyaretçi ve ilan yöneticisi.","MVP kapsamını dondur: listeleme, filtre, detay, admin ilan ekleme, çoklu görsel yükleme.","Monorepo veya iki repo kararını ver; frontend ve backend klasör yapısını tanımla.","Git repo(lar)ını oluştur; README, .gitignore, örnek .env ve branch akışını ekle.","Ürün dili, para birimi, lokasyon alanları ve iletişim CTA'sını kararlaştır."],"Onaylı MVP kapsamı + çalışan boş proje iskeleti","Kapsam dışı: ödeme, kullanıcı hesabı, favoriler ve gelişmiş CRM."),
(2,"Bulut servisleri ve güvenli yapılandırma","Altyapı",[
"MongoDB Atlas hesabı ve ücretsiz cluster oluştur; database user ve network access ayarla.","Cloudinary hesabını oluştur; Cloud Name, API Key ve API Secret değerlerini güvenli sakla.","Backend .env: MONGODB_URI, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, PORT.","Frontend .env: VITE_API_BASE_URL (veya seçilen framework karşılığı).","Secret değerlerin Git'e girmediğini kontrol et; .env.example yalnızca anahtar adlarını içersin."],"Atlas + Cloudinary bağlantı testi başarılı","Connection string ve API Secret hiçbir ekran görüntüsü ya da commit içinde paylaşılmayacak."),
(3,"Express API ve veri modelinin kurulması","Backend",[
"Express, mongoose, dotenv, cors, multer ve cloudinary paketlerini kur.","Katmanları oluştur: config, models, controllers, routes, middleware.","Property şeması: title, price, rooms, images; ayrıca location, description ve timestamps eklemeyi değerlendir.","Merkezi hata yakalama, 404 cevabı ve health endpoint'i ekle.","MongoDB bağlantısını uygulama başlangıcında doğrula; anlaşılır log üret."],"GET /api/health 200 döner; Property modeli test edilir","API yanıtları tutarlı: success, data, message ve error alanları."),
(4,"Çoklu görsel yükleme ve ilan oluşturma API'si","Backend",[
"Multer memoryStorage kullan; images alanında dosya sayısı ve boyut limiti belirle.","Yalnızca güvenli görsel MIME türlerini kabul et.","Buffer verilerini Cloudinary upload_stream ile yükle; klasör ve dönüşüm politikası tanımla.","Dönen secure_url değerlerini Property.images dizisine kaydet.","POST /api/properties rotasını Postman/Bruno ile 1, çoklu ve hatalı dosya senaryolarında test et."],"FormData ile ilan ve çoklu görsel MongoDB'ye kaydolur","Kısmi yükleme hatasında yetim Cloudinary görsellerini temizleme stratejisi bulunmalı."),
(5,"Listeleme, detay ve filtre API'leri","Backend",[
"GET /api/properties: sayfalama, sıralama ve boş sonuç davranışı.","GET /api/properties/:id: geçerli/geçersiz ID ve bulunamadı durumları.","Fiyat aralığı, oda sayısı ve metin araması için query parametreleri.","Query değerlerini doğrula; fiyat ve limit için güvenli sınırlar koy.","Örnek ilanlarla seed verisi oluştur ve API sözleşmesini README'ye yaz."],"Liste, detay ve filtre uçları örnek veride doğrulanır","Frontend ekibi API yanıtlarını tahmin etmeden kullanabilmeli."),
(6,"Görsel yön, tasarım sistemi ve UX mimarisi","UI/UX",[
"Marka yönü: güven veren premium emlak estetiği; lacivert, sıcak nötrler ve tek vurgu rengi.","8px spacing sistemi; container genişlikleri; 12 kolon grid; breakpoint'ler.","Tipografi ölçeği, butonlar, inputlar, chip'ler, badge'ler, kartlar, modal ve skeleton durumları.","Site haritası ve ana kullanıcı akışları: keşfet → filtrele → ilan detayı → iletişim.","Figma seviyesinde düşük/yüksek sadakatli wireframe: ana sayfa, liste, detay, admin."],"Tasarım tokenları + dört ana ekranın onaylı taslağı","Her bileşen hover, focus, disabled, error ve loading durumuna sahip olacak."),
(7,"Frontend temeli ve tekrar kullanılabilir UI kütüphanesi","Frontend",[
"React projesini kur; router, API istemcisi ve klasör mimarisini oluştur.","CSS yaklaşımını seç; renk, ölçü, radius, gölge ve motion tokenlarını tanımla.","Button, Input, Select, PriceInput, Badge, Container, EmptyState, Skeleton bileşenleri.","Global reset, odak görünürlüğü, reduced-motion ve erişilebilir form etiketleri.","Story/demo sayfasında bileşen varyantlarını görsel olarak kontrol et."],"Responsive UI çekirdeği ve component showcase","Rastgele CSS değerleri yerine token; kopyala-yapıştır bileşen yerine ortak API."),
(8,"Ana sayfa ve ilan kartları - premium vitrin","UI/UX + Frontend",[
"Hero: güçlü değer önerisi, lokasyon/arama alanı ve net CTA.","İlan kartı: 4:3 görsel, fiyat hiyerarşisi, oda/lokasyon metası ve favori için ayrılmış alan.","Öne çıkan ilanlar, güven göstergeleri ve sade footer tasarla.","Cloudinary responsive görseller, lazy loading ve sabit aspect-ratio kullan.","Skeleton, boş liste, API hata ve yeniden dene durumlarını tasarla."],"Mobil ve masaüstünde piksel düzeni güçlü çalışan ana sayfa","Kart grid'i: mobil 1, tablet 2, masaüstü 3-4 kolon; layout shift oluşmamalı."),
(9,"Filtreleme ve listeleme deneyimi","UI/UX + Frontend",[
"Desktop sidebar/topbar; mobil bottom sheet veya drawer filtre düzeni.","Fiyat aralığı, oda sayısı, arama, sıralama ve aktif filtre chip'leri.","Filtreleri URL query string ile senkronla; sayfa yenilenince durum korunsun.","Sonuç sayısı, tümünü temizle ve filtre uygulanıyor geri bildirimi.","Klavye erişimi, görünür focus ve 44px minimum dokunma alanı."],"Paylaşılabilir URL'li, responsive ve erişilebilir filtre akışı","Filtre değişimlerinde gereksiz istekleri debounce et; loading sırasında arayüz zıplamasın."),
(10,"İlan detay sayfası ve dönüşüm tasarımı","UI/UX + Frontend",[
"Responsive galeri: büyük kapak, thumbnail'ler ve tam ekran lightbox.","Başlık, fiyat, lokasyon, özellikler ve açıklamada güçlü bilgi hiyerarşisi.","Desktop sticky iletişim kartı; mobil sticky alt CTA.","Breadcrumb, geri dönüş, görsel sayacı ve benzer ilan alanı.","Kırık görsel fallback'i, uzun metin ve tek görsel senaryolarını test et."],"Detay sayfası güven veren, hızlı ve iletişime yönlendiren yapıda","Ana içerik ilk viewport'ta anlaşılır; CTA görünür fakat içeriği bastırmaz."),
(11,"Admin paneli ve FormData ilan akışı","Admin",[
"Admin shell: sade navigasyon, sayfa başlığı ve ilan formu.","Başlık, fiyat, oda sayısı, açıklama ve diğer alanlarda client-side validation.","<input type='file' multiple> için sürükle-bırak, önizleme, silme ve sıralama deneyimi.","FormData'ya metin alanlarını ve her görseli aynı images anahtarıyla append et.","Upload progress/loading, başarı bildirimi, hata özeti ve çift gönderim koruması."],"Gerçek API'ye çoklu görselli ilan başarıyla eklenir","Dosya tip/boyut hatası seçim anında gösterilir; form verisi hatada kaybolmaz."),
(12,"Kalite, erişilebilirlik ve performans günü","QA",[
"Chrome/Firefox; 360, 768, 1024 ve 1440px responsive kontroller.","Klavye ile tam gezinme; label, alt text, landmark ve renk kontrastı denetimi.","Lighthouse hedefleri: Performance ≥ 85; Accessibility/Best Practices/SEO ≥ 90.","Görsellerde optimize boyut, srcset yaklaşımı, lazy loading ve LCP önceliği.","API hata, yavaş ağ, boş veri, uzun başlık ve çoklu upload uç durumları."],"Kritik hata yok; kalite hedefleri ölçülüp raporlanır","UI polish turu: hizalama, tipografi, boşluk, hover/focus ve mikro animasyon tutarlılığı."),
(13,"Güvenlik, deployment ve ortamlar","Release",[
"Backend'i Render'a bağla; env değerlerini panelden gir; health endpoint ile doğrula.","Frontend'i Vercel/Netlify'a bağla; canlı API adresini environment variable olarak tanımla.","CORS'u yalnızca canlı frontend domainine izin verecek şekilde sınırla.","Production build, SPA route fallback, Cloudinary ve MongoDB erişimlerini test et.","Secret taraması yap; loglarda bağlantı adresi veya API key olmadığını doğrula."],"Canlı frontend, canlı backend'e güvenli şekilde bağlanır","Ücretsiz servislerin cold start davranışı kabul edilir ve kullanıcıya uygun loading gösterilir."),
(14,"Uçtan uca kabul, içerik ve teslim","Launch",[
"Admin'den 5-10 gerçekçi ilan ve optimize görseller yükle.","Uçtan uca test: ilan ekle → listede gör → filtrele → detaya git → iletişim CTA.","Mobil gerçek cihaz kontrolü ve son görsel polish turu.","README: kurulum, env anahtarları, komutlar, API rotaları, deployment ve bakım notları.","Domain/DNS bağlantısı, SSL ve temel SEO meta etiketlerini kontrol et; lansman checklist'ini kapat."],"MVP canlı, dokümante, test edilmiş ve gösterime hazır","Arkadaşın teknik destek almadan ilan ekleyebilmeli; geri dönüş planı yazılı olmalı."),
]

story=[]
story += [Spacer(1,25*mm), Paragraph("14 GÜNLÜK ÜRÜN SPRINTİ",styles["CoverKicker"]), Paragraph("Modern Emlak Platformu<br/>Proje Tasklist'i",styles["CoverTitle"]), Paragraph("React + Express + MongoDB Atlas + Cloudinary",styles["CoverSub"]), Spacer(1,18*mm)]
cover_table=Table([["14","GÜN"],["3","ANA EKRAN"],["1","CANLI MVP"]],colWidths=[22*mm,32*mm],rowHeights=[16*mm]*3)
cover_table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),NAVY),("TEXTCOLOR",(0,0),(0,-1),WHITE),("FONTNAME",(0,0),(0,-1),"SerifB"),("FONTSIZE",(0,0),(0,-1),17),("ALIGN",(0,0),(0,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("FONTNAME",(1,0),(1,-1),"UIB"),("FONTSIZE",(1,0),(1,-1),8),("TEXTCOLOR",(1,0),(1,-1),MUTED),("BACKGROUND",(1,0),(1,-1),PALE),("BOX",(0,0),(-1,-1),0.6,LINE),("INNERGRID",(0,0),(-1,-1),0.4,LINE)]))
story += [cover_table, Spacer(1,22*mm), info_box("HEDEF", "14 gün sonunda ilanların filtrelenebildiği, detaylarının incelenebildiği ve yöneticinin çoklu görselle ilan ekleyebildiği; responsive, erişilebilir ve yayına alınmış bir MVP.", colors.HexColor("#EAF7F4")), Spacer(1,22*mm), Paragraph("Hazırlanma tarihi: 17 Temmuz 2026  •  Europe/Istanbul",styles["Smallx"]), PageBreak()]

story += [Paragraph("Sprint özeti",styles["H1x"]), Paragraph("Plan, altyapıyı erken doğrulayıp UI kalitesine yeterli zaman ayıracak biçimde sıralandı. Gün 6-12 arasındaki çalışmalar ürünün görsel dili, kullanılabilirliği ve profesyonel hissi için ayrılmıştır.",styles["Bodyx"]), Spacer(1,4*mm)]
phase_data=[[Paragraph("FAZ",styles["Wh"]),Paragraph("GÜNLER",styles["Wh"]),Paragraph("ÇIKTI",styles["Wh"])],
[Paragraph("Temel & bulut",styles["CellB"]),Paragraph("1-2",styles["Cell"]),Paragraph("Kapsam, repo, Atlas ve Cloudinary",styles["Cell"])],
[Paragraph("API",styles["CellB"]),Paragraph("3-5",styles["Cell"]),Paragraph("İlan, görsel yükleme, liste, detay ve filtre",styles["Cell"])],
[Paragraph("Premium UI",styles["CellB"]),Paragraph("6-11",styles["Cell"]),Paragraph("Tasarım sistemi, vitrin, filtre, detay ve admin",styles["Cell"])],
[Paragraph("Kalite & yayın",styles["CellB"]),Paragraph("12-14",styles["Cell"]),Paragraph("QA, deployment, içerik ve kabul",styles["Cell"])]]
tbl=Table(phase_data,colWidths=[35*mm,23*mm,112*mm],repeatRows=1)
tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.5,LINE),("BACKGROUND",(0,1),(-1,-1),WHITE),("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,PALE]),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
story += [tbl, Spacer(1,8*mm), Paragraph("UI kalite ilkeleri",styles["H2x"])]
story += tasks(["Net hiyerarşi: her ekranda tek birincil amaç ve tek baskın CTA.","Tutarlı sistem: token tabanlı renk, tipografi, spacing, radius, gölge ve motion.","Responsive by default: tasarım 360px'ten başlar, geniş ekrana kontrollü büyür.","Erişilebilirlik: klavye, görünür focus, semantik HTML, kontrast ve anlaşılır hata mesajları.","Performans: doğru Cloudinary dönüşümleri, sabit görsel oranları, skeleton ve minimum layout shift.","Güven: gerçekçi içerik, temiz ilan bilgisi, net fiyat/lokasyon ve sade iletişim akışı."])
story += [Spacer(1,7*mm), info_box("GÜNLÜK RİTİM", "Her gün: 15 dk planlama • odaklı üretim • gün sonunda çalışan demo • checklist güncelleme • küçük ve anlamlı commit'ler."), PageBreak()]

for idx,(day,title,track,items,deliverable,note) in enumerate(days):
    block=[pill(f"GÜN {day}  •  {track}", CYAN if "UI" in track or track in ("Frontend","Admin") else BLUE), Spacer(1,3*mm), Paragraph(title,styles["Day"]), Paragraph("Görevler",styles["Labelx"])] + tasks(items) + [Spacer(1,2*mm), info_box("GÜN SONU TESLİMATI",deliverable,colors.HexColor("#EAF7F4")), Spacer(1,2*mm), info_box("KALİTE KAPISI",note)]
    story += block
    if day % 2 == 0 and day != 14: story.append(PageBreak())
    else: story.append(Spacer(1,8*mm))

story += [PageBreak(), Paragraph("Definition of Done",styles["H1x"]), Paragraph("Bir iş ancak aşağıdaki koşulları sağladığında tamamlanmış sayılır.",styles["Bodyx"])]
story += tasks(["Kabul kriterleri sağlandı ve ana kullanıcı akışı gerçek veride çalışıyor.","Mobil ve masaüstü görsel kontrol yapıldı; taşma, kırılma veya layout shift yok.","Loading, empty, error ve success durumları tasarlandı ve test edildi.","Klavye odağı görünür; form alanları etiketli; görseller anlamlı alt metne sahip.","Console hatası yok; secret veya kişisel veri loglanmıyor.","Kod okunabilir, ortak bileşenler kullanılıyor ve gerekli dokümantasyon güncel.","Production build başarılı ve değişiklik Git'e anlamlı commit ile kaydedildi."])
story += [Spacer(1,7*mm), Paragraph("Lansman kontrol listesi",styles["H2x"])]
launch=["Atlas production bağlantısı ve erişim kuralları","Cloudinary güvenli yükleme ve optimizasyon","Render health check ve environment variables","Vercel/Netlify production API URL","CORS yalnızca izinli origin'ler","HTTPS ve domain DNS","Responsive gerçek cihaz testi","Temel SEO: title, description, OG image","404, API hata ve boş durum ekranları","Admin ilan ekleme eğitimi","README ve bakım notları","Geri dönüş / rollback notu"]
rows=[]
for i in range(0,len(launch),2): rows.append([Paragraph("☐ "+launch[i],styles["Cell"]),Paragraph("☐ "+launch[i+1],styles["Cell"])])
lt=Table(rows,colWidths=[85*mm,85*mm])
lt.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,LINE),("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,PALE]),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story += [lt, Spacer(1,8*mm), info_box("MVP BAŞARI ÖLÇÜTÜ", "Ziyaretçi 30 saniye içinde uygun ilanları filtreleyebilmeli, ilan detayındaki temel bilgileri anlayabilmeli ve iletişim aksiyonuna ulaşabilmeli. Yönetici ise teknik yardım almadan çoklu görselli yeni ilan yayınlayabilmeli.", colors.HexColor("#EAF7F4"))]

doc=SimpleDocTemplate(OUT,pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=19*mm,bottomMargin=18*mm,title="Emlak Projesi - 14 Günlük Tasklist",author="Codex")
doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print(OUT)
