from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from pathlib import Path

OUT = Path('output/pdf/RadarIQOps_4_Haftalik_Proje_Plani.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))

NAVY = colors.HexColor('#0B1F33')
BLUE = colors.HexColor('#1976D2')
CYAN = colors.HexColor('#00B8D9')
PALE = colors.HexColor('#EAF4FB')
LIGHT = colors.HexColor('#F4F7FA')
MID = colors.HexColor('#607D8B')
GREEN = colors.HexColor('#138A72')
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX', fontName='Arial-Bold', fontSize=28, leading=32, textColor=WHITE, alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name='SubX', fontName='Arial', fontSize=12, leading=18, textColor=colors.HexColor('#CDE8F5')))
styles.add(ParagraphStyle(name='H1X', fontName='Arial-Bold', fontSize=20, leading=24, textColor=NAVY, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name='H2X', fontName='Arial-Bold', fontSize=13, leading=17, textColor=BLUE, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name='BodyX', fontName='Arial', fontSize=9.2, leading=13.2, textColor=NAVY, spaceAfter=5))
styles.add(ParagraphStyle(name='SmallX', fontName='Arial', fontSize=7.8, leading=10.5, textColor=MID))
styles.add(ParagraphStyle(name='TaskX', fontName='Arial', fontSize=8.6, leading=12, textColor=NAVY))
styles.add(ParagraphStyle(name='TaskBold', fontName='Arial-Bold', fontSize=8.6, leading=12, textColor=NAVY))
styles.add(ParagraphStyle(name='Callout', fontName='Arial-Bold', fontSize=10, leading=14, textColor=GREEN))

def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h-14*mm, w, 14*mm, fill=1, stroke=0)
    canvas.setFont('Arial-Bold', 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(16*mm, h-9*mm, 'RadarIQOps | 4 Haftalık Profesyonel Geliştirme Planı')
    canvas.setStrokeColor(colors.HexColor('#D9E4EC'))
    canvas.line(16*mm, 13*mm, w-16*mm, 13*mm)
    canvas.setFont('Arial', 7.5)
    canvas.setFillColor(MID)
    canvas.drawString(16*mm, 8*mm, 'Radar Signal Classification MLOps Platform')
    canvas.drawRightString(w-16*mm, 8*mm, f'{doc.page}')
    canvas.restoreState()

doc = BaseDocTemplate(str(OUT), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=20*mm, bottomMargin=17*mm,
                      title='RadarIQOps - 4 Haftalık Proje Planı', author='RadarIQOps')
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
doc.addPageTemplates(PageTemplate(id='main', frames=frame, onPage=header_footer))
story = []

def P(text, style='BodyX'): return Paragraph(text, styles[style])
def bullet(text): return P(f'<font color="#1976D2">■</font> {text}', 'TaskX')
def task(text): return P(f'<font color="#1976D2">□</font> {text}', 'TaskX')
def section(title, body=None):
    story.append(P(title, 'H1X'))
    if body: story.append(P(body))

def info_table(rows, widths=None):
    t = Table([[P(str(c), 'TaskX') for c in row] for row in rows], colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),WHITE),
        ('FONTNAME',(0,0),(-1,0),'Arial-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#C8D5DF')),
        ('BACKGROUND',(0,1),(-1,-1),WHITE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    return t

# Cover
cover = Table([[P('RadarIQOps', 'TitleX')], [P('Radar Signal Classification MLOps Platform', 'SubX')],
               [Spacer(1,8*mm)], [P('4 Haftalık Profesyonel Geliştirme Planı', 'SubX')],
               [P('Veriden üretim ortamına: ölçülebilir, izlenebilir ve yeniden eğitilebilir bir IQ sinyal sınıflandırma sistemi.', 'SubX')]],
              colWidths=[doc.width], rowHeights=[None,None,18*mm,None,None])
cover.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY),('BOX',(0,0),(-1,-1),0,NAVY),
                           ('LEFTPADDING',(0,0),(-1,-1),16*mm),('RIGHTPADDING',(0,0),(-1,-1),16*mm),
                           ('TOPPADDING',(0,0),(-1,0),22*mm),('BOTTOMPADDING',(0,-1),(-1,-1),22*mm)]))
story += [Spacer(1,25*mm), cover, Spacer(1,14*mm),
          P('HEDEF', 'H2X'), P('Dört hafta sonunda; versiyonlanmış veri hattı, tekrarlanabilir eğitim, MLflow model kaydı, FastAPI servisi, Docker/Kubernetes dağıtımı, Prometheus-Grafana gözlemlenebilirliği, Evidently drift raporu ve kontrollü yeniden eğitim akışı bulunan çalışan bir MVP üretmek.'),
          Spacer(1,4*mm), P('ÇALIŞMA RİTMİ', 'H2X'),
          info_table([['Süre','Önerilen efor','Sprint yapısı'],['4 hafta','Haftada 20-30 saat','5 geliştirme günü + 1 demo/iyileştirme günü']], [35*mm,55*mm,70*mm]),
          PageBreak()]

section('1. Proje kapsamı ve başarı tanımı')
story += [P('<b>MVP kapsamı:</b> IQ örneklerini kabul eden, hedef/modülasyon sınıfı üreten ve üretim davranışı izlenebilen uçtan uca bir platform. Seçilen açık veri seti gerçek hedef etiketleri içermiyorsa sınıflar veri setinin modülasyon sınıfları olarak tutulacak; “drone/kuş/araç” iddiası sentetik veya radar hedef verisi bulunana kadar yapılmayacak.'),
          P('<b>Önemli gerçeklik kontrolü:</b> RadioML/DeepSig veri setleri çoğunlukla sinyal modülasyonu sınıflandırması içindir; radar hedef sınıflandırmasıyla birebir aynı problem değildir. İlk haftada veri uygunluğu bir “go/no-go” kapısıdır.'),
          P('Dört haftalık MVP için %90+ doğruluk bir hedef olabilir; ancak kabul kriteri veri seti, SNR dağılımı ve sınıf dengesine göre belirlenir. Sadece toplam accuracy değil macro-F1, sınıf bazlı recall ve SNR dilimi performansı da raporlanır.'),
          P('Teslimat ilkeleri', 'H2X'), bullet('Her hafta sonunda çalıştırılabilir bir sürüm ve kısa demo.'), bullet('Kod, konfigürasyon ve veri sürümleri birbirine bağlanır.'), bullet('Notebook yalnızca keşif içindir; üretim mantığı src/ altında test edilebilir modüllerdedir.'), bullet('Önce yerel Docker Compose, sonra minimal Kubernetes; zaman yetmezse bulut dağıtımı kapsam dışıdır.'),
          P('Definition of Done - tüm proje', 'H2X'),
          task('Temiz ortamda kurulum ve hızlı başlangıç komutları README içinde çalışıyor.'), task('Veri kaynağı, lisans, checksum, bölme yöntemi ve şema dokümante.'), task('Eğitim aynı seed ve config ile tekrarlanabiliyor; metrik ve artifact MLflow’a yazılıyor.'), task('API sağlık, tahmin ve metrik uçlarını sunuyor; giriş doğrulaması ve hata yanıtları testli.'), task('Container non-root çalışıyor; image sürümlenmiş ve zafiyet taraması CI’da.'), task('Kubernetes manifestleri hazır; readiness/liveness ve kaynak limitleri tanımlı.'), task('Dashboard ve drift raporu örnek trafik/veriyle doğrulanmış.'), task('Yeniden eğitim tetikleyicisi otomatik veya onay kapılı; başarısız model production’a geçmiyor.'),
          PageBreak()]

section('2. Dört haftalık üst düzey yol haritası')
story.append(info_table([
 ['Hafta','Odak','Hafta sonu çalışan sürüm','Çıkış kapısı'],
 ['1','Veri temeli ve proje iskeleti','DVC ile sürümlü ham/işlenmiş veri, doğrulama ve baseline EDA','Veri uygunluğu onaylı; pipeline testleri geçiyor'],
 ['2','Model, eğitim ve MLflow','Tek komutla eğitim, değerlendirme, MLflow experiment ve registry adayı','Baseline ile CNN kıyaslandı; kabul metrikleri raporlu'],
 ['3','Servis, container ve CI/CD','FastAPI + Docker Compose + CI; minimal Kubernetes deployment','API testleri, image build ve smoke test başarılı'],
 ['4','Monitoring, drift ve retraining','Prometheus/Grafana, Evidently raporu, kontrollü yeniden eğitim akışı','Uçtan uca demo ve operasyon runbook’u tamam'],
], [18*mm,39*mm,70*mm,50*mm]))
story += [Spacer(1,5*mm), P('Önerilen repo hedefi', 'H2X'), P('data/{raw,interim,processed,validation}, notebooks/, src/{data,features,training,inference,monitoring,utils}, api/, configs/, mlruns/ veya harici backend, docker/, kubernetes/, monitoring/{prometheus,grafana,evidently}, tests/{unit,integration,smoke}, docs/, .github/workflows/, dvc.yaml, params.yaml, Makefile, pyproject.toml, README.md.'),
          P('Kapsam koruması', 'H2X'), P('GPU zorunluluğu, gerçek zamanlı radar donanımı entegrasyonu, feature store, service mesh, çok kümeli Kubernetes ve tam otomatik production promotion bu dört haftalık MVP’nin dışındadır. Bunlar sonraki sürüm backlog’una alınır.'), PageBreak()]

weeks = [
('HAFTA 1', 'Veri, doğrulama ve tekrarlanabilir pipeline', 'Amaç: Doğru problemi doğru veriyle tanımlamak ve her sonraki fazın güveneceği veri sözleşmesini kurmak.', [
('Gün 1 - Kapsam, mimari ve repo', ['Radar hedefi mi modülasyon sınıflandırması mı olduğuna karar ver; veri etiketlerini doğrula.','RadioML 2016/2018, DeepSig ve uygun radar hedef veri setlerini lisans, boyut, sınıf, SNR ve format açısından karşılaştır.','Dataset karar kaydı (ADR-001) oluştur; lisans ve atıf gereksinimlerini yaz.','Git repo iskeleti, .gitignore, pyproject/requirements, pre-commit, Makefile ve temel README oluştur.','Python sürümünü ve bağımlılıkları sabitle; CPU/GPU çalışma profilini tanımla.','Mimari diyagram, risk kaydı ve kabul metriklerini oluştur.']),
('Gün 2 - Veri edinme ve DVC', ['İndirme/ingestion scripti yaz; URL/erişim yöntemi ve checksum doğrulaması ekle.','Ham veriyi değişmez kabul et; data/raw içeriğini DVC ile izle, büyük dosyaları Git’e alma.','DVC remote stratejisini tanımla (yerel MVP; opsiyonel S3/MinIO).','Veri manifesti üret: örnek sayısı, shape, dtype, sınıflar, SNR aralığı, hash ve kaynak sürümü.','Küçük, lisans açısından güvenli test fixture’ı oluştur.']),
('Gün 3 - Validation ve EDA', ['Beklenen IQ şemasını tanımla: [N, 2, L] veya complex64; label ve SNR alanları.','Shape, NaN/Inf, boş sinyal, sabit sinyal, amplitude sınırı, duplicate ve label kontrolü ekle.','Sınıf/SNR dağılımı, sinyal uzunluğu, I/Q istatistikleri ve örnek spektrumları raporla.','Bozuk kayıt karantina ve validation raporu üret.','Veri sızıntısı riskini incele; aynı kaynak/sequence parçalarının bölmeler arasında kalmasını engelle.']),
('Gün 4 - Preprocessing ve features', ['DC offset giderme ve amplitude/power normalizasyonunu config kontrollü uygula.','IQ tensor, amplitude-phase ve opsiyonel FFT/spectrogram temsillerini modüler tasarla.','Stratified/group-aware train-validation-test split üret; seed ve split indekslerini kaydet.','Transform’ları yalnız train istatistikleriyle fit et; leakage testi yaz.','dvc.yaml ve params.yaml ile raw -> validate -> preprocess -> split aşamalarını bağla.']),
('Gün 5/6 - Test, baseline ve demo', ['Unit testler: loader, validator, normalizer, split ve feature shape.','Pipeline smoke testi: küçük örnekte dvc repro.','Basit baseline (logistic regression veya küçük MLP) kur; macro-F1 ve confusion matrix çıkar.','Data card ve Week-1 demo komutlarını dokümante et.','Git etiketi/release adayı: v0.1-data-pipeline.'])]),
('HAFTA 2', 'PyTorch modelleme, değerlendirme ve MLflow', 'Amaç: Tek komutla tekrarlanabilir eğitim ve kanıtlanabilir model karşılaştırması.', [
('Gün 1 - Eğitim altyapısı', ['PyTorch Dataset/DataLoader oluştur; deterministik seed ve worker ayarlarını yap.','Config tabanlı training CLI yaz: model, lr, batch size, epoch, optimizer, scheduler.','CPU/GPU seçimi, checkpoint, early stopping ve resume desteği ekle.','Class imbalance için weighted loss/sampler kararını veriyle ver.']),
('Gün 2 - 1D CNN', ['1D CNN mimarisi kur: Conv1D, normalization, activation, pooling, dropout, classifier.','Input/output shape kontrolleri ve model unit testleri yaz.','Overfit-one-batch testi ile eğitim döngüsünü doğrula.','İlk hiperparametre koşularını küçük veri üzerinde çalıştır.']),
('Gün 3 - MLflow entegrasyonu', ['Experiment ve run isimlendirme standardı belirle.','Parametreleri, Git commit, data/DVC revision, seed ve ortam bilgisini logla.','Accuracy, macro/micro-F1, precision, recall, loss ve epoch sürelerini logla.','Model checkpoint, confusion matrix, classification report ve config artifact’larını kaydet.','Model signature ve input example ile MLflow model formatını oluştur.']),
('Gün 4 - Değerlendirme', ['Test setini tuning sırasında kilitli tut; validation ile model seç.','Genel ve sınıf bazlı metrikleri çıkar.','SNR dilimlerine göre performans eğrisi ve hata analizi oluştur.','Baseline ile CNN’i aynı split üzerinde kıyasla.','Latency, model boyutu ve batch throughput ölç.']),
('Gün 5/6 - Registry ve kalite kapısı', ['En iyi modeli registry’ye candidate/champion yaklaşımıyla kaydet.','Promotion kriteri tanımla: macro-F1, kritik sınıf recall, latency ve boyut.','Model card yaz: amaç, veri, sınırlamalar, etik/operasyonel riskler.','Training integration testi ve temiz ortam reproducibility testi çalıştır.','Git etiketi/release adayı: v0.2-trained-model.'])]),
('HAFTA 3', 'FastAPI, Docker, Kubernetes ve CI/CD', 'Amaç: Modeli güvenli, ölçülebilir ve taşınabilir bir servis haline getirmek.', [
('Gün 1 - Inference paketi', ['Model yükleme, preprocessing ve label mapping’i tek inference pipeline’da birleştir.','Registry/model URI veya sabit artifact üzerinden sürüm kontrollü yükleme ekle.','Tekli ve batch prediction sözleşmesini belirle.','Golden sample testiyle training-serving skew kontrolü yap.']),
('Gün 2 - FastAPI', ['GET /health/live, GET /health/ready, POST /predict, POST /predict/batch ve GET /metrics uçlarını kur.','Pydantic ile IQ uzunluğu, dtype, limit ve NaN/Inf doğrulaması yap.','Yanıtta prediction, confidence, model_version, request_id ve işlem süresi döndür.','Tutarlı hata kodları, structured JSON logging ve hassas veri maskeleme ekle.','OpenAPI örneklerini ve curl kullanımını dokümante et.']),
('Gün 3 - API kalite ve güvenlik', ['Unit/integration testleri: başarı, bozuk payload, aşırı payload, model yok, timeout benzeri hatalar.','Tahmin tutarlılığı ve latency smoke testi oluştur.','CORS’u varsayılan kapalı/sınırlı tut; debug modunu production’da kapat.','Request size limiti ve opsiyonel API key yaklaşımını dokümante et.']),
('Gün 4 - Docker', ['Multi-stage/minimal Dockerfile; pinned base image ve non-root kullanıcı.','Model artifact edinme stratejisini seç: image içine sabitle veya startup’ta registry’den al.','HEALTHCHECK, environment config ve graceful shutdown ekle.','Docker Compose ile API + MLflow (ve gerekirse artifact store) yerel yığını kur.','Image boyutu, SBOM/dependency ve zafiyet taraması yap.']),
('Gün 5/6 - Kubernetes ve CI', ['Deployment, Service, ConfigMap/Secret referansları, readiness/liveness probe ve resource request/limit yaz.','RollingUpdate, replica sayısı ve opsiyonel HPA taslağı ekle.','CI: lint, format check, unit/integration test, image build ve smoke test.','Main branch için version/tag tabanlı image üretimi; registry push/deploy için secret ve environment kapısı tanımla.','Manifest lint/dry-run ve yerel kind/minikube testi (mümkünse).','Git etiketi/release adayı: v0.3-serving.'])]),
('HAFTA 4', 'Monitoring, drift, yeniden eğitim ve final ürün', 'Amaç: Sistemin ne yaptığını görmek, bozulmayı saptamak ve güvenli iyileştirme döngüsü kurmak.', [
('Gün 1 - Prometheus metrikleri', ['Request count, error count, latency histogram, in-flight request ve prediction count ekle.','Model version ve endpoint gibi düşük cardinality label kullan; request_id/user gibi label’lardan kaçın.','CPU/RAM/container metriklerini platform exporter üzerinden topla.','Prometheus scrape config ve alert rule’ları yaz.']),
('Gün 2 - Grafana ve alarmlar', ['Dashboard: trafik, p50/p95/p99 latency, hata oranı, kaynak kullanımı, sınıf dağılımı.','SLO taslağı: availability, p95 latency ve hata bütçesi.','Alarm eşikleri ve runbook bağlantıları ekle.','Örnek yük testi ile dashboard panellerini doğrula.']),
('Gün 3 - Evidently drift', ['Referans veri setini train/validation’dan versiyonlu snapshot olarak üret.','Production payload’larını mahremiyet ve saklama politikasıyla logging/feature store benzeri dosyada biriktir.','IQ için izlenecek özet özellikleri seç: I/Q mean/std, power, amplitude, phase, SNR ve prediction dağılımı.','Evidently data quality/drift raporu oluştur; eşik ve minimum örnek sayısını belirle.','Etiket gecikmeli geliyorsa data/prediction drift; geliyorsa performans drift ayrımını dokümante et.']),
('Gün 4 - Kontrollü auto-retraining', ['Tetikleyici tasarla: drift eşiği + yeterli veri + cooldown; yalnız drift ile kör retraining yapma.','Retraining pipeline: validate -> preprocess -> train -> evaluate -> registry candidate.','Champion-challenger kalite kapısı ekle; regresyonda promotion’ı reddet.','Production promotion’ı MVP’de manuel onaylı yap; rollback prosedürü yaz.','Audit trail: veri sürümü, kod commit’i, model run’ı ve onay kaydı.']),
('Gün 5/6 - Uçtan uca doğrulama ve sunum', ['Sentetik/örnek trafik üret; metrik, log, dashboard ve drift raporunu göster.','Model değişimi ve rollback smoke testi yap.','README’yi ürün odaklı tamamla: mimari, quickstart, demo, API, metrikler, sınırlamalar.','docs/ altında runbook, troubleshooting, model card, data card ve ADR’leri tamamla.','CI yeşil; test coverage raporu; temiz makinede kurulum provası.','2-3 dakikalık demo akışı ve mülakat anlatısı hazırla.','Git etiketi/release: v1.0.0-mvp.'])])]

for wi,(tag,title,goal,days) in enumerate(weeks):
    story += [P(tag, 'Callout'), P(title, 'H1X'), P(goal)]
    for day, items in days:
        block = [P(day, 'H2X')] + [task(x) for x in items]
        story.append(KeepTogether(block))
    story += [Spacer(1,3*mm), P('Hafta çıkış kriterleri', 'H2X')]
    exits = {
      'HAFTA 1':['Veri lisansı ve problem uyumu doğrulandı.','DVC pipeline temiz ortamda yeniden üretilebiliyor.','Validation raporu, data card ve baseline hazır.'],
      'HAFTA 2':['En iyi run MLflow’da tam izlenebilir.','Model kabul metrikleri ve SNR bazlı analiz hazır.','Registry candidate ve model card mevcut.'],
      'HAFTA 3':['Docker image ayağa kalkıyor ve API smoke test geçiyor.','CI tüm kalite kapılarını çalıştırıyor.','Kubernetes deployment health probe ve limitlerle doğrulanmış.'],
      'HAFTA 4':['Dashboard gerçek örnek trafikle veri gösteriyor.','Drift raporu ve alarm senaryosu çalışıyor.','Retraining kalite kapısı, rollback ve final dokümantasyon tamam.']}
    story += [bullet(x) for x in exits[tag]]
    if wi < 3: story.append(PageBreak())

story += [PageBreak()]
section('3. Teknik kabul kriterleri ve test matrisi')
story.append(info_table([
 ['Alan','Minimum kabul kriteri','Doğrulama'],
 ['Veri','Şema hataları raporlu; split leakage yok; data revision kayıtlı','Validation testleri + manifest + DVC repro'],
 ['Model','Baseline’dan anlamlı iyi; macro-F1 ve sınıf recall raporlu','Sabit test spliti + MLflow artifacts'],
 ['API','Geçerli/bozuk girişler doğru yanıt; model sürümü görünür','Pytest integration + golden samples'],
 ['Performans','Hedef donanımda ölçülmüş p95 latency ve throughput','Yük/smoke testi; sonuç README’de'],
 ['Container','Non-root; healthcheck; pinned dependency/base','Docker inspect + image scan'],
 ['Kubernetes','Probe, limit, config ve rollout tanımlı','Manifest lint + dry-run/kind'],
 ['Monitoring','Trafik, latency, hata, kaynak ve tahmin dağılımı görünür','Örnek yük + dashboard kontrolü'],
 ['Drift','Referans/current pencereler ve eşikler versiyonlu','Evidently raporu + sentetik shift testi'],
 ['Retraining','Kötü challenger production’a geçemez; rollback mümkün','Pipeline test + onay/ret senaryosu'],
], [28*mm,92*mm,57*mm]))
story += [Spacer(1,5*mm), P('Önerilen metrik hedefleri (veri keşfinden sonra kesinleştir)', 'H2X'),
          bullet('Model: macro-F1 öncelikli; accuracy ikincil. Kritik sınıflar için minimum recall.'),
          bullet('Servis: yerel hedef donanımda p95 latency ve hata oranı için ölçülmüş başlangıç baseline’ı.'),
          bullet('Kalite: kritik modüllerde yüksek test kapsamı; toplam coverage tek başına hedef değildir.'),
          bullet('Drift: minimum pencere büyüklüğü olmadan alarm yok; art arda ihlal veya cooldown uygulanır.'),
          PageBreak()]

section('4. Riskler, kararlar ve 4 hafta sonrası backlog')
story.append(info_table([
 ['Risk','Etkisi','Azaltma'],
 ['Dataset hedef sınıfları içermiyor','Proje iddiası yanlış olur','Hafta 1 go/no-go; problemi modülasyon olarak yeniden adlandır veya radar hedef datası seç'],
 ['%90 hedefi veri nedeniyle gerçekçi değil','Gereksiz tuning / yanıltıcı sonuç','Macro-F1, SNR dilimleri ve baseline’a göre iyileşme kullan'],
 ['GPU veya büyük veri darboğazı','Sprint gecikir','Örneklemli MVP, küçük CNN, config ile ölçekleme'],
 ['Training-serving skew','Production tahmini bozulur','Ortak preprocessing paketi ve golden test'],
 ['Drift alarmı gürültülü','Gereksiz retraining','Min örnek, eşik, ardışık pencere ve cooldown'],
 ['Otomatik kötü model promotion','Production regresyonu','Champion-challenger, manuel onay, rollback'],
 ['Kubernetes kapsamı büyür','Ana ürün gecikir','Minimal manifest; cloud/IaC sonraki backlog'],
], [40*mm,55*mm,82*mm]))
story += [Spacer(1,5*mm), P('4 hafta sonrası backlog', 'H2X'),
          task('Gerçek radar donanımından streaming ingestion (Kafka/Redpanda) ve online feature pipeline.'),
          task('MinIO/S3 artifact store, PostgreSQL MLflow backend ve merkezi secrets yönetimi.'),
          task('GPU inference, ONNX/TensorRT optimizasyonu ve canary deployment.'),
          task('Feature store, model açıklanabilirliği ve etiket geri-besleme arayüzü.'),
          task('Terraform/Helm, cloud Kubernetes, GitOps (Argo CD) ve çok ortamlı promotion.'),
          task('Güvenlik: auth/RBAC, TLS, rate limiting, imzalı image, SBOM politikası.'),
          task('Gerçek performans drift’i için ground-truth toplama ve aktif öğrenme.'),
          Spacer(1,5*mm), P('Final demo senaryosu', 'H2X'),
          P('1) DVC ile veri sürümünü göster. 2) Tek komutla training run başlat ve MLflow’da metrik/artifact aç. 3) Registry modelini API ile servis et. 4) Örnek IQ isteği gönder. 5) Grafana’da latency ve prediction sayısını göster. 6) Dağılımı kaydırılmış veri gönderip Evidently raporunu üret. 7) Retraining candidate oluştur; kalite kapısının promotion/ret kararını göster. 8) Kubernetes rollout ve rollback akışını anlat.'),
          Spacer(1,5*mm), P('İlk başlangıç noktası', 'Callout'),
          P('Proje başlarken ilk somut iş: veri seti karar matrisi ve problem tanımını kesinleştirmek. Bu karar verilmeden model sınıfları, başarı hedefi ve API sözleşmesi sabitlenmemelidir.')]

doc.build(story)
print(OUT.resolve())
