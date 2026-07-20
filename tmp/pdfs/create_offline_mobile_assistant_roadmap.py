from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether

OUT = Path("output/pdf/Cevrimdisi_Mobil_Asistan_Gelistirilmis_21_Gunluk_Roadmap.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))

INK = colors.HexColor("#12212B")
NAVY = colors.HexColor("#16324F")
TEAL = colors.HexColor("#00A6A6")
ORANGE = colors.HexColor("#FF9F1C")
PALE = colors.HexColor("#EAF7F7")
LIGHT = colors.HexColor("#F4F7F9")
MID = colors.HexColor("#58717F")
GREEN = colors.HexColor("#25855A")
RED = colors.HexColor("#B34A3C")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="Arial-Bold", fontSize=28, leading=32, textColor=WHITE, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="CoverSub", fontName="Arial", fontSize=12, leading=17, textColor=colors.HexColor("#D8F3F3")))
styles.add(ParagraphStyle(name="H1", fontName="Arial-Bold", fontSize=19, leading=23, textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name="H2", fontName="Arial-Bold", fontSize=12.2, leading=15, textColor=TEAL, spaceBefore=6, spaceAfter=4))
styles.add(ParagraphStyle(name="Body", fontName="Arial", fontSize=8.9, leading=12.7, textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle(name="Small", fontName="Arial", fontSize=7.4, leading=10.2, textColor=MID))
styles.add(ParagraphStyle(name="Cell", fontName="Arial", fontSize=7.6, leading=10.5, textColor=INK))
styles.add(ParagraphStyle(name="CellHead", fontName="Arial-Bold", fontSize=7.7, leading=10.5, textColor=WHITE))
styles.add(ParagraphStyle(name="Day", fontName="Arial-Bold", fontSize=10.8, leading=14, textColor=NAVY, spaceAfter=3))
styles.add(ParagraphStyle(name="Tag", fontName="Arial-Bold", fontSize=8.2, leading=10, textColor=GREEN))
styles.add(ParagraphStyle(name="Quote", fontName="Arial-Bold", fontSize=10.5, leading=15, textColor=NAVY, leftIndent=8, rightIndent=8, alignment=TA_CENTER))

def P(text, style="Body"):
    return Paragraph(text, styles[style])

def bullet(text, color="#00A6A6"):
    return P(f'<font color="{color}">■</font> {text}', "Body")

def check(text):
    return P(f'<font color="#25855A">□</font> {text}', "Body")

def footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 12*mm, w, 12*mm, fill=1, stroke=0)
    canvas.setFont("Arial-Bold", 7.6)
    canvas.setFillColor(WHITE)
    canvas.drawString(15*mm, h - 7.8*mm, "Çevrimdışı Mobil Asistan | 21 Günlük Roadmap")
    canvas.setStrokeColor(colors.HexColor("#D5E1E7"))
    canvas.line(15*mm, 12*mm, w - 15*mm, 12*mm)
    canvas.setFont("Arial", 7.2)
    canvas.setFillColor(MID)
    canvas.drawString(15*mm, 7.5*mm, "Android-first • Offline-first • Battery-aware • Privacy-by-design")
    canvas.drawRightString(w - 15*mm, 7.5*mm, str(doc.page))
    canvas.restoreState()

doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=17*mm, bottomMargin=16*mm,
                      title="Çevrimdışı Mobil Asistan - 21 Günlük Roadmap", author="Codex")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPageEnd=footer))
story = []

def table(rows, widths, header=True):
    converted = []
    for ri, row in enumerate(rows):
        converted.append([P(str(v), "CellHead" if header and ri == 0 else "Cell") for v in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    style = [
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#C8D7DE")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    if header:
        style += [("BACKGROUND", (0,0), (-1,0), NAVY), ("BACKGROUND", (0,1), (-1,-1), WHITE)]
    t.setStyle(TableStyle(style))
    return t

def day_block(day, title, goal, tasks, output, test):
    parts = [P(f"GÜN {day}  |  {title}", "Day"), P(f"<b>Amaç:</b> {goal}")]
    parts += [check(x) for x in tasks]
    parts += [P(f"<b>Gün sonu çıktısı:</b> {output}"), P(f"<b>Geçiş testi:</b> {test}", "Tag"), Spacer(1, 2*mm)]
    return parts

# Cover
cover = Table([
    [P("ÇEVRİMDIŞI<br/>MOBİL ASİSTAN", "CoverTitle")],
    [P("Android-first • Sesle komut • Edge AI • MLOps", "CoverSub")],
    [Spacer(1, 10*mm)],
    [P("21 GÜNLÜK UYGULAMALI ROADMAP", "CoverSub")],
    [P("Fikirden, telefonda çalışan ve ölçülmüş MVP'ye", "CoverSub")],
], colWidths=[doc.width])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), NAVY), ("BOX", (0,0), (-1,-1), 0, NAVY),
    ("LEFTPADDING", (0,0), (-1,-1), 15*mm), ("RIGHTPADDING", (0,0), (-1,-1), 15*mm),
    ("TOPPADDING", (0,0), (-1,0), 20*mm), ("BOTTOMPADDING", (0,-1), (-1,-1), 20*mm),
]))
story += [Spacer(1, 24*mm), cover, Spacer(1, 12*mm), P("HEDEF", "H2"),
          P("21 gün sonunda fiziksel Android telefonda, internet kapalıyken Türkçe komutları algılayan; güvenli yerel aksiyonlar çalıştıran; foreground service, kalıcı bildirim ve ölçülebilir güç/performans bütçesi bulunan bir MVP."),
          Spacer(1, 3*mm), table([
              ["Platform", "Günlük efor", "MVP komut sayısı", "Ana başarı ölçütü"],
              ["Android / Kotlin", "2-4 saat", "12-16", "Doğruluk + gecikme + pil tüketimi"]
          ], [42*mm, 40*mm, 42*mm, 53*mm]),
          Spacer(1, 6*mm), P("ANA İLKE", "H2"),
          P("Önce çalışan ve ölçülen küçük sistem; sonra model büyütme, fine-tuning ve iOS portu.", "Quote"), PageBreak()]

# Logic and architecture
story += [P("1. Nasıl bir mantıkla yapacağız?", "H1"),
          P("Asistanı tek bir büyük model gibi değil, her katmanı ayrı test edilebilen bir olay hattı olarak kuracağız. Mikrofon sürekli ağır STT çalıştırmayacak. Düşük maliyetli wake word katmanı tetiklenince kısa ses penceresi açılacak; VAD konuşmanın bittiğini belirleyecek; STT metni üretecek; intent katmanı yalnızca izinli komutları eşleyecek; action katmanı Android API'lerini çağıracak."),
          table([
              ["Katman", "Görevi", "MVP kararı"],
              ["Wake word", "Düşük güçte tetikleme", "Porcupine veya açık kaynak alternatif; olmazsa push-to-talk fallback"],
              ["Audio + VAD", "16 kHz mono akış, konuşma sınırları", "AudioRecord + Silero VAD/whisper.cpp VAD"],
              ["Offline STT", "Türkçe sesi metne çevirme", "Önce Vosk small-tr; sonra whisper.cpp tiny/base benchmark"],
              ["Intent router", "Metni güvenli komuta dönüştürme", "Regex + synonym sözlüğü + confidence eşiği"],
              ["Action executor", "Telefon üzerinde işlem", "Allowlist, kullanıcı onayı, Android intents/APIs"],
              ["Observability", "Gecikme, hata ve enerji ölçümü", "Yalnızca yerel log/Room; ham sesi varsayılan saklama"],
          ], [32*mm, 65*mm, 80*mm]),
          Spacer(1, 5*mm), P("Olay akışı", "H2"),
          P("IDLE → wake word → LISTENING → VAD stop → TRANSCRIBING → INTENT → CONFIRM (riskliyse) → EXECUTE → FEEDBACK → IDLE"),
          P("Neden bu yaklaşım?", "H2"),
          bullet("Batarya: pahalı STT yalnızca tetiklenince çalışır; idle döngüsü küçük tutulur."),
          bullet("Gizlilik: ham ses cihazdan çıkmaz; telemetri opt-in ve yereldir."),
          bullet("Güvenlik: serbest metin doğrudan işletim sistemi komutuna dönüşmez; allowlist ve onay kapısı kullanılır."),
          bullet("MLOps: model, eşik, komut sözlüğü ve test verisi ayrı sürümlenir; cihaz ölçümleri sürümle ilişkilendirilir."),
          bullet("Gerçekçilik: Android'de sürekli mikrofon için görünür foreground service bildirimi ve doğru izinler gerekir; gizli, sınırsız arka plan dinleme hedeflenmez."),
          PageBreak()]

# Technology stack
story += [P("2. Kullanacağımız teknolojiler", "H1"),
          table([
              ["Alan", "Seçim", "Gerekçe / alternatif"],
              ["Mobil", "Kotlin + Android Studio + Jetpack Compose", "Native ses, servis, izin ve performans kontrolü"],
              ["Ses", "AudioRecord, 16 kHz PCM mono", "Ham akışa ve buffer boyutuna doğrudan erişim"],
              ["STT A", "Vosk small-tr", "35 MB Türkçe mobil model; hızlı MVP, dinamik kelime dağarcığı"],
              ["STT B", "whisper.cpp tiny/base quantized", "Daha genel konuşma için karşılaştırma; ARM/Android ve quantization desteği"],
              ["Wake word", "Porcupine / openWakeWord değerlendirmesi", "Cihaz, lisans ve Türkçe özel kelime kalitesine göre seç; push-to-talk fallback"],
              ["VAD", "Silero VAD veya whisper.cpp VAD", "Boş sesi STT'ye göndermeyerek gecikme ve tüketimi azaltır"],
              ["Intent", "Kotlin regex + synonym map", "12-16 komutta LLM gereksiz; slot tabanlı ve test edilebilir"],
              ["Veri", "Room + DataStore", "Yerel metrikler, ayarlar ve komut geçmişi"],
              ["Test", "JUnit, Robolectric, instrumented tests", "İş mantığı + gerçek cihaz servis/izin kontrolleri"],
              ["MLOps", "Git + DVC + MLflow (PC tarafı)", "Ses test seti, model artifact ve benchmark sürümleme"],
              ["Model runtime", "Önce native Vosk/whisper.cpp; LiteRT yalnız özel model varsa", "Format dönüştürme amacı değil, gerçek benchmark sonucu karar verir"],
              ["CI", "GitHub Actions veya yerel CI", "Build, lint, unit test, APK artifact"],
          ], [31*mm, 54*mm, 92*mm]),
          Spacer(1, 5*mm), P("MVP'de özellikle yapmayacaklarımız", "H2"),
          bullet("İlk günden akustik model fine-tuning; önce vocabulary/grammar adaptasyonu ve hata analizi."),
          bullet("Telefonda Docker; Docker yalnız PC'deki veri/model hazırlama ortamı için."),
          bullet("Her komutu LLM'e gönderme; ilk sürüm deterministik intent router kullanır."),
          bullet("İzinsiz arka plan dinleme, ham sesin otomatik yüklenmesi veya riskli aksiyonların onaysız çalışması.", "#B34A3C"),
          P("Genişletilmiş günlük kullanım kapsamı", "H2"),
          table([
              ["Sesli komut örneği", "Uygulama davranışı", "Güvenlik / bağlantı"],
              ["Kadıköy'e yol tarifi aç", "Google Maps veya seçili haritada navigasyonu açar", "Harita verisi için internet gerekebilir"],
              ["Ahmet'i ara", "Kişiyi rehberden bulur ve arama ekranını açar", "Doğrudan aramada izin + açık onay"],
              ["Ayşe'ye geliyorum yaz", "SMS/WhatsApp mesaj taslağını hazırlar", "Gönder tuşu kullanıcıda kalır"],
              ["Spotify'da Duman aç", "Spotify araması/deep link açar", "İçeriğin çalması için internet ve Spotify gerekir"],
              ["YouTube'da X videosunu aç", "YouTube araması veya içerik sayfasını açar", "İçerik için internet gerekir"],
              ["Feneri aç / 10 dk sayaç", "Yerel Android aksiyonunu çalıştırır", "Tamamen çevrimdışı"],
          ], [46*mm, 79*mm, 52*mm]),
          P("Karar kapısı - Gün 8", "H2"),
          P("Aynı Türkçe test setinde Vosk ve whisper.cpp ölçülür. Hedef telefonda komut doğruluğu, p50/p95 gecikme, RAM, model boyutu ve 10 dakikalık enerji testi birlikte değerlendirilir. Kazanan runtime ana yol olur; diğeri deney dalında kalır."),
          PageBreak()]

story += [P("3. Başarı ölçütleri ve çalışma düzeni", "H1"),
          table([
              ["Ölçüt", "MVP hedefi", "Nasıl ölçülecek?"],
              ["Komut başarı oranı", "Sessiz ortamda ≥ %90; gürültüde başlangıç baseline'ından iyi", "En az 10 komut x 5 tekrar; farklı mesafe ve gürültü"],
              ["Wake false accept", "Kullanılabilir seviyede; sayı raporlanır", "1 saat negatif ses / günlük ortam testi"],
              ["Uçtan uca gecikme", "Kısa komutta p95 ≤ 2.5 sn hedef", "Wake sonrası aksiyon başlangıcına kadar cihaz logu"],
              ["Bellek", "Hedef cihazda çökme/ANR yok", "Android Profiler + düşük bellek senaryosu"],
              ["Enerji", "30 dk idle + 20 komut testi; sürümler arası gerileme yok", "Battery Historian / batterystats + aynı koşullar"],
              ["Gizlilik", "Uçak modunda tam işlev; ham ses varsayılan saklanmaz", "Network kapalı smoke test + veri denetimi"],
              ["Dayanıklılık", "Ekran kilidi, servis yeniden yaratımı ve izin reddi yönetilir", "Gerçek cihaz senaryo testleri"],
          ], [37*mm, 61*mm, 79*mm]),
          Spacer(1, 5*mm), P("Günlük ritim", "H2"),
          bullet("15 dk: gün hedefi ve risk."), bullet("90-180 dk: uygulama/model çalışması."),
          bullet("30 dk: test ve ölçüm."), bullet("15 dk: karar günlüğü, commit ve ertesi gün notu."),
          P("Definition of Done", "H2"),
          check("Temiz checkout'tan build alınabiliyor ve README adımları çalışıyor."),
          check("Telefon uçak modundayken ana senaryo tamamlanıyor."),
          check("Model lisansı, checksum'u, sürümü ve uygulamayla eşleşmesi kayıtlı."),
          check("En az 8 komut; olumlu, olumsuz ve belirsiz örneklerle testli."),
          check("Riskli aksiyonlar onay istiyor; düşük confidence komutu çalıştırmıyor."),
          check("Benchmark raporu gerçek cihaz adı, Android sürümü ve build SHA ile saklanıyor."),
          check("30 dakikalık idle testi ve 20 komutluk aktif test sonucu raporda."),
          PageBreak()]

week1 = [
 (1,"Kapsam ve cihaz baseline'ı","MVP'nin sınırlarını sabitlemek.",["Hedef telefonu, Android/API sürümünü ve donanımı kaydet.","12-16 komut seç: harita, arama, mesaj, Spotify, YouTube, uygulama, fener ve zamanlayıcı.","Tehdit modeli ve veri saklama politikasını yaz.","Kotlin/Compose repo iskeleti, README ve karar günlüğü oluştur."],"Proje iskeleti + komut kataloğu + ölçüm şablonu.","Boş uygulama fiziksel cihazda açılıyor."),
 (2,"Ses yakalama","Kararlı PCM akışı üretmek.",["RECORD_AUDIO izin akışını ve reddedilme durumunu tasarla.","AudioRecord ile 16 kHz mono PCM buffer al.","Başlat/durdur ekranı ve dalga seviyesi göstergesi ekle.","5 kısa örnek kaydet; clipping ve sessizlik kontrolü yap."],"Test sesleri + AudioCapture modülü.","30 saniye kayıtta buffer kaybı/çökme yok."),
 (3,"Foreground service","Kilit ekranında yasal ve görünür çalışma.",["microphone foreground service type ve izinlerini ekle.","Kalıcı bildirimden dinlemeyi durdurma aksiyonu ekle.","Uygulama önden başlatıldıktan sonra ekran kilidi senaryosunu test et.","Servis state machine ve lifecycle loglarını oluştur."],"Çalışan mikrofon foreground service.","Ekran kilidinde 10 dk çalışır; bildirimden durur."),
 (4,"VAD ve ses penceresi","Yalnız konuşmayı STT'ye taşımak.",["RMS tabanlı baseline VAD kur; cihaz gürültü tabanını ölç.","Pre-roll/post-roll ring buffer ekle.","Silero/whisper.cpp VAD entegrasyonu için arayüz tanımla.","Sessiz, konuşmalı ve rüzgarlı 20 klipte sınırları incele."],"SpeechSegmenter arayüzü + baseline.","Konuşma başlangıç/bitişinin çoğunu kırpmadan yakalar."),
 (5,"Vosk Türkçe entegrasyonu","İlk çevrimdışı transkripti almak.",["small-tr modelini lisans, checksum ve sürümle kaydet.","Model asset kopyalama/yükleme akışını kur.","VAD çıktısını Vosk'a ver; partial/final sonuçları UI'da göster.","Model yükleme süresi, RAM ve gecikmeyi logla."],"Vosk ile offline Türkçe transkript.","Uçak modunda 10 test cümlesi işleniyor."),
 (6,"Intent router","Metni güvenli ve deterministik komuta çevirmek.",["Intent, slot, confidence ve reason veri sınıflarını yaz.","Regex, synonym ve normalizasyon katmanı ekle.","Belirsiz/izin dışı komutta no-op davranışı uygula.","Her intent için olumlu, paraphrase ve negatif unit test yaz."],"Testli intent yönlendirici.","Negatif örnekler yanlış aksiyon çalıştırmıyor."),
 (7,"İlk dikey demo","Uçtan uca ilk haftayı kapatmak.",["Wake yerine push-to-talk ile audio → STT → intent → sahte action akışını bağla.","10 komutluk mini değerlendirme çalıştır.","Hataları STT / intent / action olarak etiketle.","v0.1-demo etiketi ve kısa demo videosu/notu oluştur."],"İlk çalışan offline dikey dilim.","En az 5 komut fiziksel cihazda uçtan uca geçer."),
]

week2 = [
 (8,"Vosk vs whisper.cpp","Ana STT motorunu veriyle seçmek.",["whisper.cpp tiny/base quantized Android örneğini derle.","Aynı 50+ kısa Türkçe klipte iki motoru çalıştır.","Komut başarı oranı, p50/p95, RAM, boyut ve sıcaklık ölç.","Kararı ADR-002 olarak kaydet; tek ana runtime seç."],"Karşılaştırma raporu + STT kararı.","Seçim en az beş ölçüte dayanıyor."),
 (9,"Wake word prototipi","Eller serbest tetiklemeyi eklemek.",["Porcupine ve açık kaynak seçeneğin lisans/cihaz uygunluğunu değerlendir.","WakeWordEngine arayüzünü uygula.","Pozitif ve negatif seslerle threshold ayarla.","Çalışmazsa push-to-talk fallback'i koru."],"Wake word prototipi + eşik config'i.","20 pozitif ve 30 negatif denemede sonuç raporlu."),
 (10,"Harita ve medya entegrasyonları","Navigasyon ve içerik açma komutlarını eklemek.",["OPEN_LOCATION(destination) intent'i ve geo/navigation URI üreticisini yaz.","PLAY_MEDIA(platform, query) ile Spotify ve YouTube deep link/arama fallback'i ekle.","Uygulama yüklü değilse güvenli web veya uygulama seçici fallback'i göster.","Konum, platform ve içerik sorgusu slot parser testlerini yaz."],"Harita + Spotify + YouTube entegrasyonu.","Üç platformda doğru sorgu açılıyor; internet yoksa anlaşılır hata var."),
 (11,"Rehber, arama ve mesaj","Kişi tabanlı iletişim komutlarını güvenli kurmak.",["READ_CONTACTS izin akışını ve ContactResolver'ı uygula.","CALL_CONTACT(contact_name) için ACTION_DIAL; doğrudan arama seçeneği için onay kapısı tasarla.","SEND_MESSAGE(contact_name, message, channel) ile SMS/WhatsApp taslağı hazırla.","Aynı isimli kişilerde seçim, kişi bulunamadı ve uygulama yok senaryolarını yönet."],"Arama ekranı + SMS/WhatsApp taslakları.","Mesaj kullanıcı dokunmadan gönderilmez; yanlış kişi otomatik seçilmez."),
 (12,"Aksiyon güvenliği ve tam komut kataloğu","Tüm entegrasyonları ortak güvenlik katmanına bağlamak.",["OPEN_APP, OPEN_LOCATION, PLAY_MEDIA, CALL_CONTACT ve SEND_MESSAGE şemalarını sabitle.","Allowlist, confidence eşiği, tekrar sorma ve confirmation state uygula.","Saat, not, fener, zamanlayıcı ve ayar ekranı aksiyonlarını tamamla.","Her intent için olumlu, paraphrase, belirsiz ve kötü niyetli negatif test ekle."],"12-16 komut + merkezi ActionPolicy.","Belirsiz/riskli komut onaysız çalışmıyor; tüm intent testleri geçiyor."),
 (13,"Yerel telemetri ve entegrasyon tanılama","Sorunu kanıtla teşhis edebilmek.",["Room'a anonim oturum, stage latency, intent, action sonucu ve hata kodu yaz.","Ham ses saklamayı varsayılan kapalı tut; debug opt-in ekle.","Model/config/build ve hedef uygulama sürümünü benchmark'a bağla.","Deep link, kişi çözümleme ve izin hatalarını gösteren tanılama ekranı oluştur."],"Yerel metrik deposu + entegrasyon tanılama ekranı.","Bir komutun tüm aşama süreleri ve fallback nedeni görülebiliyor."),
 (14,"Genişletilmiş ikinci sprint demosu","Eller serbest günlük kullanım akışını stabilize etmek.",["Wake → VAD → STT → intent → policy → action zincirini birleştir.","Harita, arama, mesaj taslağı, Spotify ve YouTube senaryolarını fiziksel cihazda çalıştır.","Ekran açık/kilitli, internet açık/kapalı ve uygulama yok senaryolarını test et.","30 dakikalık soak test ve v0.2-alpha hata listesini üret."],"Günlük kullanım odaklı eller serbest alpha.","12 farklı komut; yanlış arama/mesaj gönderimi olmadan uçtan uca geçer."),
]

week3 = [
 (15,"Enerji profili","Bataryayı neyin tükettiğini bulmak.",["Idle, wake-only ve aktif STT senaryolarını ayrı ölç.","batterystats/Battery Historian ve CPU profiler kullan.","Buffer, thread, wake lock ve model yaşam döngüsünü incele.","En büyük iki tüketim kaynağı için optimizasyon uygula."],"Enerji baseline'ı + optimizasyon notu.","Aynı testte gerileme yok; koşullar kayıtlı."),
 (16,"Performans ve bellek","Gecikme ve OOM riskini azaltmak.",["Cold/warm model yükleme ve p50/p95 uçtan uca gecikmeyi ölç.","Modeli oturum boyunca tutma vs lazy-load kararını ölçerek ver.","Thread sayısı, chunk ve quantization varyantlarını A/B test et.","Düşük bellek callback'i ve güvenli recovery ekle."],"Performans tablosu + seçilmiş profil.","Hedef gecikmeye yaklaşır; OOM/ANR yok."),
 (17,"MLOps hattı","Model ve test verisini yeniden üretilebilir yapmak.",["PC tarafında data/, models/, benchmarks/ yapısı kur.","DVC ile ses test seti ve model artifact'larını sürümle.","MLflow'a model/config/device/build ve metrikleri logla.","Tek komutla benchmark raporu üreten script tanımla."],"Sürümlü benchmark pipeline'ı.","Aynı sürümden aynı rapor yeniden üretilebiliyor."),
 (18,"CI ve paketleme","Her değişiklikte kalite kapısı kurmak.",["Gradle lint, unit test ve debug APK build adımlarını CI'a ekle.","Model checksum ve asset varlığı doğrulaması ekle.","Instrumented smoke test için yerel/emülatör yönergesi yaz.","VersionCode/VersionName ve changelog standardı belirle."],"Yeşil CI + sürümlü APK artifact.","Temiz ortamda build ve unit test başarılı."),
 (19,"Güvenlik ve mahremiyet","Yanlış aksiyon ve veri sızıntısını önlemek.",["Permission, exported component ve intent güvenlik denetimi yap.","Allowlist dışı action'ı reddet; riskli aksiyonda onay zorunlu kıl.","Loglarda transkript/PII maskeleme ve veri silme ekranı ekle.","Uçak modu ve ağ trafiği kontrolüyle offline iddiasını doğrula."],"Gizlilik kontrol listesi + veri silme.","Varsayılan kullanımda ham ses/ağ aktarımı yok."),
 (20,"Saha testi, gürültü ve hata avı","Gerçek günlük kullanımı sınamak.",["Sessiz oda, sokak, araç, kulaklık/Bluetooth, ekran kilidi ve gürültüde test et.","Harita, arama, mesaj, Spotify ve YouTube dahil en az 120 komutluk sonuç tablosu çıkar.","VAD/wake eşiklerini ayarla; top 5 hatayı düzelt ve regresyon testine ekle.","Kurulum, izin, internet fallback'i ve sorun giderme dokümanını tamamla."],"120 komut saha raporu + release candidate.","Yanlış kişi/mesaj yok; metrikler özellik bazında hedeflerle karşılaştırılmış."),
 (21,"Final MVP ve sonraki sprint","Teslim edilebilir sürümü kapatmak.",["30 dk idle + 20 aktif komut enerji testini son kez çalıştır.","DoD checklist, lisanslar, model card ve privacy notunu tamamla.","Release APK, demo senaryosu ve v0.3-mvp etiketi üret.","Sonraki 30 gün backlog'unu verilere göre sırala."],"İmzalanabilir MVP paketi + final rapor.","Uçak modunda canlı demo; tüm kritik kabul maddeleri geçer."),
]

for title, subtitle, days in [
    ("HAFTA 1", "Temel ses hattı ve ilk çalışan dikey dilim", week1),
    ("HAFTA 2", "STT seçimi, wake word ve gerçek Android aksiyonları", week2),
    ("HAFTA 3", "Optimizasyon, MLOps, güvenlik ve final MVP", week3),
]:
    story += [P(title, "Tag"), P(subtitle, "H1")]
    for args in days:
        story.extend(day_block(*args))
    if title != "HAFTA 3":
        story.append(PageBreak())

story += [PageBreak(), P("4. Test matrisi ve karar kayıtları", "H1"),
          table([
              ["Senaryo", "Beklenen davranış", "Kayıt"],
              ["İnternet kapalı", "Wake/STT/intent/aksiyon ana akışı çalışır", "Pass/fail + cihaz/build"],
              ["İzin reddedildi", "Çökmeden açıklama ve ayarlara yönlendirme", "Hata kodu"],
              ["Düşük confidence", "Aksiyon yok; tekrar sorar", "STT + intent confidence"],
              ["Yanlış wake", "Kısa sürede idle'a döner; aksiyon yok", "False accept sayısı"],
              ["Uzun sessizlik", "VAD timeout; model boşuna çalışmaz", "Aktif süre + enerji"],
              ["Ekran kilitli", "Foreground service kullanıcıya görünür şekilde sürer", "10/30 dk soak"],
              ["Servis öldürüldü", "Güvenli state; kullanıcı kontrollü yeniden başlatma", "Lifecycle log"],
              ["Riskli komut", "Açık onay olmadan çalışmaz", "Confirmation audit"],
              ["Model bozuk/eksik", "Hazır değil durumu; anlaşılır hata", "Checksum/load error"],
          ], [43*mm, 86*mm, 48*mm]),
          Spacer(1, 5*mm), P("Zorunlu karar kayıtları (ADR)", "H2"),
          bullet("ADR-001: Android-first ve foreground service çalışma modeli."),
          bullet("ADR-002: Vosk vs whisper.cpp - hedef cihaz ölçümlerine göre STT seçimi."),
          bullet("ADR-003: Wake word motoru, lisans ve push-to-talk fallback."),
          bullet("ADR-004: Ham ses saklama politikası ve telemetri sınırları."),
          bullet("ADR-005: Riskli aksiyon listesi ve kullanıcı onayı."),
          P("Riskler ve önlemler", "H2"),
          table([
              ["Risk", "Önlem"],
              ["Android arka plan/mikrofon kısıtları", "Kullanıcı tarafından önden başlatılan microphone foreground service, kalıcı bildirim ve doğru izin akışı"],
              ["Türkçe wake word kalitesi", "Motorları veriyle test et; threshold ayarla; push-to-talk fallback"],
              ["Whisper gecikmesi/pil", "Tiny/quantized, kısa segment, thread tuning; Vosk ana yol olabilir"],
              ["Gürültüde STT hatası", "VAD, cihaz NS/AGC A/B testi, komut grammar'ı ve tekrar sorma"],
              ["Yanlış aksiyon", "Allowlist, confidence eşiği, confirmation ve no-op default"],
              ["Model lisansı/dağıtım boyutu", "Lisans envanteri, checksum, dinamik indirme veya model flavor seçimi"],
          ], [58*mm, 119*mm]),
          PageBreak()]

story += [P("5. Gün 21 sonrası backlog", "H1"),
          table([
              ["Öncelik", "İş", "Ne zaman?"],
              ["P0", "Gerçek kullanıcı hata setine göre grammar/intent iyileştirme", "MVP ölçümleri stabil olduğunda"],
              ["P0", "Cihaz matrisi: düşük/orta/üst segment Android", "Tek cihazda hedefler geçince"],
              ["P1", "Kişisel wake word ve kontrollü veri toplama", "Lisans/mahremiyet netleşince"],
              ["P1", "TTS yanıtı ve Türkçe ses paketi", "Temel akış batarya hedefini geçince"],
              ["P1", "Daha gelişmiş NLU veya küçük yerel LLM", "Deterministik router kapsamı yetmeyince"],
              ["P2", "LiteRT özel intent modeli / NPU delegate", "Gerçek benchmark fayda gösterirse"],
              ["P2", "iOS portu: Swift, AVAudioEngine, Core ML", "Android mimarisi ve test seti oturunca"],
              ["P2", "Model güncelleme paketi ve imza doğrulama", "Birden fazla model sürümü dağıtılınca"],
          ], [25*mm, 99*mm, 53*mm]),
          Spacer(1, 7*mm), P("İlk gün hemen ne yapıyoruz?", "H2"),
          P("1) Hedef Android telefonunu ve API seviyesini kaydet. 2) Harita, arama, mesaj, Spotify, YouTube ve yerel aksiyonlardan oluşan 12-16 komutu sabitle. 3) Android Studio'da Kotlin/Compose projesini aç. 4) Fiziksel cihazda boş uygulamayı çalıştır. 5) İlk ADR'yi yaz: foreground service, kişi/mesaj güvenliği, offline veri politikası ve başarı metrikleri."),
          Spacer(1, 7*mm), P("Kaynak notları", "H2"),
          P("• Android foreground services: developer.android.com/develop/background-work/services/fgs<br/>"
            "• Android microphone service type: developer.android.com/develop/background-work/services/fgs/service-types<br/>"
            "• Vosk ve Türkçe model listesi: alphacephei.com/vosk/ ve alphacephei.com/vosk/models<br/>"
            "• whisper.cpp: github.com/ggml-org/whisper.cpp<br/>"
            "• LiteRT NPU delegates: ai.google.dev/edge/litert/android/npu", "Small"),
          Spacer(1, 8*mm), P("Başarı formülü", "H2"),
          P("Küçük komut seti + ölçülmüş cihaz performansı + güvenli aksiyonlar + gerçek saha testleri = sağlam Edge AI MVP.", "Quote")]

doc.build(story)
print(OUT.resolve())
