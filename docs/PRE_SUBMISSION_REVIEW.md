# Gönderim Öncesi İnceleme — Saros Deniz Üstü Rüzgâr Makalesi

*İncelenen: `off-shore.weibull.pdf` (27 sayfa) + bu repo (config, scripts, results, manuscript).
Tarih: 11 Kasım 2026. Hedef dergi (repo notuna göre): Energies (MDPI).*

Bu belge bir hakemin gözüyle yazıldı. Sayısal iddialar repo'daki dosyalardan
bağımsız olarak yeniden hesaplandı (`docs/review/verify_numbers.py`); dış
iddialar resmî kaynaklardan ve açık veri setlerinden kontrol edildi (kaynaklar
en sonda).

---

## 0. Özet hüküm

**Bu hâliyle göndermeyin.** Hesap zinciri tutarlı ve tekrarlanabilir, ama
makalenin başlık sayılarını ve çerçevesini doğrudan etkileyen sekiz sorun var.
En önemlileri:

1. **Kapasite faktörü (%29,9) büyük olasılıkla düşük taraflı.** Global Wind
   Atlas saha üzerinde 100 m'de ortalama 7,83 m/s veriyor; makaledeki ERA5
   serisi aynı yükseklikte 7,12 m/s (%9 düşük). Resmî YEKA DÜRES‑2026 şartname
   taslağı fiyatı %43 kapasite faktörüne göre kuruyor ve %40'ın altını fesih
   gerekçesi sayıyor. Makale bu farktan hiç söz etmiyor.
2. **Türbin güç eğrisi fiziksel olarak fazla iyimser** (Cp 0,56'ya çıkıyor) ve
   kaynağı yok; türbinin kendisi de 2030'larda kurulacak bir proje için eski.
3. **"Kaçınılan emisyon" başlık sayısı (1525 tCO₂/MW/yıl; 1,52 Mt) metnin
   söylediği hesabın sonucu değil.** Resmî birleşik marjla aynı üretim 1608
   t/MW/yıl ve 1,60 Mt eder.
4. **Saha tarifi yanlış.** Açık batimetri verisine göre poligonun tamamı
   4–57 m derinlikte ve Trakya kıyısına bitişik; makale "~50 – >200 m",
   "körfezin orta‑güney kısmı", "batı kenarı yüzer temel gerektirir" diyor.
5. **Politika çerçevesindeki olgusal hatalar:** DÜRES kısaltmasının açılımı,
   "ilk dört aday saha" iddiası, ilan tarihi ve "kurulu güç henüz belli değil"
   ifadesi güncel resmî belgelerle uyuşmuyor.
6. **"Kış talep piki ile örtüşme" iddiası yanlış.** Türkiye'nin puantı yazın.

Bunların hiçbiri çalışmayı çöpe atmıyor; çoğu, makaleyi daha güçlü yapacak
biçimde düzeltilebilir (bkz. §8 eylem planı).

---

## 1. Doğrulanan ve sağlam çıkan noktalar

| Kontrol | Sonuç |
|---|---|
| Poligon ↔ Bakanlığın yayımladığı `SAROS DÜRES.kml` | 27 köşe, 172,5 km², ağırlık merkezi 40,5571° K / 26,1978° D — birebir |
| Monte Carlo'nun yeniden üretimi (seed 2026) | `monte_carlo_samples.npz` ile fark 1e‑15; P10/P50/P90 aynı |
| Tablo 3, 4, 7 ↔ `results/*.json` | Tutarlı (0,65/1,32/2,62/4,56 TWh; 0,38/0,77/1,52/2,65 Mt; 0,86 M hane; 0,76 M araç; %0,75) |
| 96 432 saat | 11 yıl + 3 artık gün, eksiksiz |
| 7D×5D → 183 türbin | 172,5 / 0,941 km² = 183 ✓ |
| ETKB 2023 şebeke faktörleri | Faaliyet marjı 0,7134, gelişim marjı 0,3567, birleşik marj (güneş+rüzgâr) 0,6242 tCO₂/MWh — ikincil kaynaklardan teyit edildi |
| 2035 hedefi 5 GW | ✓ |

Kontrol edemediğim: 347,9 TWh (2024 tüketimi), 3036 kWh/hane, 434 g/kWh üretim
ortalaması, yakıt bazlı 405/803/1133 g/kWh. Bunların birincil belgesini
arşivleyip atıf verin.

---

## 2. Kritik sorunlar (gönderimden önce çözülmeli)

### K1 — Rüzgâr kaynağı muhtemelen düşük tahmin ediliyor ve resmî beklentiyle çelişiyor

- ERA5 serisinin 100 m ortalaması: 7,17 / 1,05^0,149 = **7,12 m/s**.
- Global Wind Atlas v4 (250 m çözünürlük), poligon içi 2 936 nokta:
  ortalama **7,83 m/s** (aralık 7,19–8,16). ERA5 ızgara noktasında (40,50° K,
  26,25° D) GWA 8,19 m/s.
- GWA sahada kuzeyden güneye belirgin gradyan gösteriyor (kıyıda ~7,2, güney
  kenarda ~8,1 m/s). ERA5 tek hücreyle bunu çözemez.
- Hâkim rüzgâr KD/DKD, yani **karadan denize** esiyor; saha kıyıya 0–10 km.
  Bu, kısa "fetch" ve iç sınır tabakası demek; ERA5'in en zayıf olduğu durum.
- Duyarlılık (bu repo'nun kendi güç eğrisiyle): rüzgâr hızı +%10 → AEP +%18.
  GWA ortalamasına ölçeklenince net KF %29,9 → **≈%35,5**.
- **YEKA DÜRES‑2026 şartname taslağı** (madde 4.3 ve 8.2): teklif fiyatı %43
  kapasite faktörüne göre kabul ediliyor; ölçüm sonrası KF %40'ın altında
  çıkarsa yarışmayı kazanan fesih isteyebiliyor. TÜREB başkanı basında deniz
  üstü için %45–50 diyor.

Makale %29,9 buluyor ve bunu "Akdeniz için rekabetçi" diye sunuyor. Hakem ilk
olarak şunu soracak: *devlet %40–43 varsayarken siz neden %30 buluyorsunuz?*

**Yapılması gereken:** (a) GWA ve/veya NEWA, CERRA ile karşılaştırma tablosu ve
haritası; (b) sapma düzeltilmiş bir senaryo; (c) tartışmada resmî %40–43
eşiğiyle açık karşılaştırma. GWA da "gerçek" değil (kıyıya yakın denizde kendi
belirsizliği var); mesele farkın görmezden gelinememesi. Bu, makaleyi
zayıflatmaz — "ERA5 tek başına bu sahada yetersiz, ölçüm şart" güçlü ve
yayınlanabilir bir bulgudur.

### K2 — Türbin seçimi ve güç eğrisi

- `config/turbine.py:24` güç eğrisinin kaynağı yok. Makale "manufacturer power
  curve" diyor, atıf vermiyor.
- Eğrinin ima ettiği güç katsayısı: 7 m/s'de 0,530; 8'de 0,557; 8,5–9'da
  **0,564**; 10'da 0,545. Betz sınırı 0,593; gerçek türbinlerde elektriksel
  Cp tepe değeri 0,44–0,48 civarıdır. Bu eğri 7–11 m/s bandında (enerjinin
  çoğunun üretildiği yer) gücü %15–25 fazla veriyor.
- Cp'yi 0,48'de kesince AEP **−%6,1**, 0,45'te **−%9,5**.
- V164‑9.5 MW (özgül güç 450 W/m²) 2017 modeli. 2030'larda kurulacak 1 000 MW'lık
  bir projede 15 MW+ sınıfı, düşük özgül güçlü makine beklenir. Kaba bir
  hesapla (15 MW / 240 m rotor / 150 m göbek, Cp ≤ 0,46 idealleştirilmiş eğri)
  aynı ERA5 serisiyle net KF ≈ **%36–37**, GWA'ya ölçekli rüzgârla ≈ **%41–42**.

K1 (aşağı yönlü sapma) ve K2'nin ilk yarısı (yukarı yönlü sapma) birbirini
kısmen götürüyor; yani %29,9 "doğru sebeple doğru" bir sayı değil.

**Yapılması gereken:** güç eğrisini atıf verilebilir bir kaynaktan alın ve Cp
kontrolü yapın; ikinci referans olarak açık kaynaklı IEA 15 MW referans
türbinini (Gaertner vd., 2020, NREL/TP‑5000‑75698) ekleyin.

### K3 — Kaçınılan emisyon başlık sayısı tanımıyla uyuşmuyor

Özet, §4.4, Şekil 2, Şekil 6, Tablo 7: "resmî birleşik marj (624,2), eksi 11
→ MW başına medyan **1525** tCO₂/yıl". Kontrol:

- 1525 / 2,62 = **582 g/kWh**, 624,2 − 11 = **613,2** değil.
- Sebep: MC'de şebeke faktörü Üçgen(434; 624,2; 713,4)'ten örnekleniyor
  (`scripts/06_run_monte_carlo.py:110`). Bu çarpık üçgenin medyanı 597, modu
  624,2. Yani 1525, birleşik marj sonucu değil; üç farklı muhasebe
  yaklaşımının harmanı.
- Aynı üretimle ve gerçekten birleşik marjla: **1608 t/MW/yıl** (P10–P90:
  1478–1738) ve S3 için **1,60 Mt/yıl**.
- Kaçınılan emisyon varyansının ≈%71'i bu tek girdiden geliyor. Üretim
  ortalaması / birleşik marj / faaliyet marjı arasındaki seçim rastlantısal
  bir belirsizlik değil, yöntem tercihidir.

**Yapılması gereken:** şebeke faktörünü MC'den çıkarıp üç senaryo olarak
raporlayın: üretim ortalaması 1109, birleşik marj **1608** (başlık), faaliyet
marjı 1842 t/MW/yıl. Araç eşdeğeri (0,76 M) ve Şekil 5–7 buna göre değişir.

### K4 — Deterministik ve Monte Carlo sonuçları arasındaki tutarsızlık, yöntem anlatımındaki çelişki

- §3.5 ve §4.2: "güç eğrisinin **Weibull yoğunluğuyla** konvolüsyonu 30,4
  GWh, %36,5 brüt KF verir". Kod (`scripts/04_fit_weibull_aep.py`) bunu
  **saatlik ampirik seriden** hesaplıyor. Uydurulmuş Weibull ile aynı hesap
  %35,5 verir (−%2,7).
- §4.3 farkı "Weibull yüksek hız kuyruğunu az temsil ediyor" diye açıklıyor.
  Kendi sayılarınız tersini söylüyor: Weibull güç yoğunluğu 422, ampirik 417
  W/m². Asıl uyumsuzluk 6–12 m/s bandında.
- 2,71 → 2,62 farkının ayrışımı: −%2,7 Weibull uyumu, −%0,7 asimetrik kayıp
  üçgenleri (iz kaybı ortalaması %8,33; emre amadelik ortalaması %94,67).
- Makalede iki ayrı başlık değeri dolaşıyor: özet ve sonuç %29,9 / 2,62; §4.2
  ve §5.1 "yaklaşık %31" / 2,71.
- Özet ve §5.1 güç yoğunluğunu 422 W/m² veriyor; bu Weibull'dan türetilen
  değer. Ölçülen (ampirik) değer 417.

**Yapılması gereken:** enerji hesabından Weibull'u çıkarın. MC'yi ampirik
seri üzerinde kurun (seriyi ölçekleyerek veya yılları yeniden örnekleyerek);
Weibull yalnızca kaynağın betimleyicisi olarak kalsın. Tek bir başlık değeri
kullanın.

### K5 — Monte Carlo tasarımı belirsizliği hem yanlış etiketliyor hem eksik bırakıyor

Tek tek değiştirerek ölçülen katkılar (AEP değişim katsayısı):

| Girdi | Katkı | Not |
|---|---|---|
| Weibull k ~ N(2,04; 0,04) | %0,08 | Etkisiz. 0,04'ün dayanağı yok |
| Weibull c ~ N(8,08; 0,26) | %5,97 | Toplam %6,3'ün neredeyse tamamı |
| İz kaybı | %1,57 | |
| Emre amadelik | %1,09 | |
| Elektrik kaybı | %0,42 | |

- σ_c = 0,26, on bir yıllık c değerlerinin standart sapması. Bu **tek bir
  yılın** değişkenliğidir; uzun dönem ortalamasının belirsizliği
  0,26/√11 = 0,079'dur (AEP'de ≈%1,8). Makale P10–P90'ı hangi anlamda
  verdiğini söylemiyor.
- En büyük belirsizlikler modelde yok: reanaliz sapması (±%10 hız → ∓%18
  AEP), güç eğrisi, kapasite yoğunluğuna bağlı iz kaybı. "Değişim katsayısı
  %6,3, belirsizlik mütevazı" cümlesi bu yüzden savunulamaz.
- k ve c bağımsız örnekleniyor; gerçekte ilişkililer.
- **P10/P90 gösterimi:** rüzgâr sektöründe P90, %90 olasılıkla aşılan (düşük)
  değerdir. Makale istatistiksel yüzdelik kullanıyor (P10 < P50 < P90).
  Tanımı açıkça yazın, yoksa sektörden bir hakem ters okur.

### K6 — Saha tarifi açık veriyle çelişiyor

EMODnet 2018 ve GEBCO 2020, poligon içi 75 nokta:

| | EMODnet | GEBCO |
|---|---|---|
| En sığ / medyan / en derin | 4 / 28 / 54 m | 5 / 33 / 57 m |
| 50 m'den derin pay | %5 | %13 |
| 60 m'den derin pay | %0 | %0 |

- Tablo 1 "~50 – >200 m" diyor; §2.3 "batı kenarı yüzer temel ya da dışlama
  gerektirir" diyor. İkisi de yanlış görünüyor: poligonun güney sınırı ~50 m
  eş derinlik eğrisini izliyor, 600 m'lik çukur poligonun **dışında**,
  güneyinde.
- §2.1 ve §3.1: "körfezin orta‑güney kısmında, yarımada kıyısına paralel
  koridor"; Tablo 1 "en yakın kara: Gelibolu Yarımadası". Kuzey‑güney
  kesitlere göre poligonun kuzey kenarı **Trakya kıyısına bitişik** (kıyı
  40,59–40,60° K; poligon 40,50–40,60° K). Gelibolu kıyısı derin çukurun
  öbür yanında, 15–25 km güneyde. Kendi Şekil 1b'niz de bunu gösteriyor.
- Sonuçlar: (a) sabit temel varsayımı aslında **iyi destekleniyor** — bunu
  veriyle gösterin, makale güçlenir; (b) sahanın bir kısmı 10 m'den sığ ve
  kıyının dibinde: kurulum gemisi, görsel etki ve kullanılabilir alan
  kısıtları var; (c) K1'deki kıyı etkisi daha da önem kazanıyor.
- Çevresel hassasiyetlerden hiç söz edilmiyor. Saros Körfezi'nin Özel Çevre
  Koruma Bölgesi statüsünü (teyit edin), kuş göç yolu ve balıkçılık
  kısıtlarını en azından "Sınırlılıklar"da anın.

### K7 — Politika çerçevesindeki olgusal hatalar

| Makalede | Resmî belgelerde |
|---|---|
| DÜRES = "Deniz Üstü Yenilenebilir Enerji Kaynak Alanları" (§2.2, §3.1) | Şartname taslağı tanım 12: **"Deniz Üstü Rüzgâr Enerjisi Santrali"**. Alanların adı: "Deniz Üstü Rüzgâr Enerjisine Dayalı Aday YEKA" |
| "14 May 2026" (her yerde) | Bakanlık sitesindeki ilan **13.05.2026** tarihli; KML dosyaları da 13 Mayıs. Bakan 12 Mayıs'ta açıkladı, basın 14 Mayıs'ta yazdı |
| "Türkiye designated its **first** four offshore wind candidate zones" | Ağustos 2023'te dört aday deniz üstü YEKA (Bandırma, Bozcaada, Gelibolu, Karabiga) zaten ilan edilmişti |
| "The siting decision has now been made", "committed site" | Statü hâlâ **aday**. Şartname Ek‑7: YEKA, "yayımlanan alanlardan herhangi biri" |
| "as‑yet‑unfinalised installed capacity" | YEKA DÜRES‑2026 taslağı: toplam **1 000 MWe**; yarışma 2027 1. çeyrek; en az 12 ay ölçüm; %25 yerlilik; 27 yıl alım |

Son satır aslında fırsat: S3 senaryonuz (998 MW) resmî 1 000 MWe ile
örtüşüyor. Bunu açıkça kurun; "kapasite belli değil" gerekçesini bırakın.

### K8 — "Kış talep piki" iddiası

Özet, §4.1, §5.2 ve Sonuç'ta dört kez geçiyor: üretim profili "Türkiye'nin
ısıtma kaynaklı kış talep pikiyle" örtüşüyor.

- Türkiye'nin sistem puantı yazın. Rekor 28 Temmuz 2025'te kırıldı; Ember'e
  göre yaz puantı kış puantını ~9 GW aşıyor. Isıtma ağırlıklı olarak doğal
  gazla yapılıyor.
- "Ege için alışılmadık biçimde kış baskın" iddiası da zayıf. Kendi aylık
  verinizde Ağustos'ta ikincil tepe var (7,55 m/s) — etezyen imzası. Aralık–
  Şubat ortalaması 8,20, Haziran–Ağustos 6,55 m/s.

**Yapılması gereken:** iddiayı ya çıkarın ya da TEİAŞ aylık tüketim/puant
verisiyle sayısal olarak sınayın (aylık korelasyon). Dürüst çerçeve: "birincil
kış tepesi + Ağustos'ta ikincil tepe; talep ise çift tepeli ve yaz ağırlıklı".

---

## 3. Önemli sorunlar

**Ö1 — "first peer‑reviewed" ifadesi.** Özet, giriş, §5.3 ve sonuçta
geçiyor. Hakemlikten geçmemiş bir metin kendini böyle tanımlayamaz. "To the
best of our knowledge, the first site‑specific assessment" yeterli.

**Ö2 — "Ölçülmüş" kayma üssü.** α = 0,149 ölçüm değil, reanaliz model
çıktısından türetilmiş. 100 → 105 m için α = 0,149 ile 0,10 arasındaki fark
hızda **%0,24**. Bu, girişte birinci katkı ve "deliberate methodological
refinement" olarak sunuluyor; hakem etkisiz olduğunu hemen görür. Ayrıca
10–100 m katmanından elde edilen α, kara‑deniz karışık bir hücrede 100–105 m
için temsil edici değil. Tonu indirin.

**Ö3 — Senaryolar.** Yalnızca S4, 7D×5D'den türetilmiş; S1–S3 yuvarlak
hedefler. Kapasite yoğunlukları 1,4 / 2,9 / 5,8 / 10,1 MW/km². Hepsine aynı
%8 iz kaybı uygulanamaz; "model kurulu güçte doğrusaldır" cümlesi iz kaybı
için doğru değil. S4 (10 MW/km²) Avrupa pratiğinin (≈4–7) üstünde. Sığ ve
kıyıya yakın kesimler düşülünce kullanılabilir alan da 172,5 km² olmaz.

**Ö4 — Yıllar arası değişkenlik.** Metin %3,2 (ddof=0), Şekil 4d %3,4
(ddof=1). 2014 belirgin aykırı: 6,55 m/s, diğer yılların ortalamasından
%9,5 düşük (z = −2,6); 2014 çıkınca değer %1,8. 2014'ü komşu hücreler veya
MERRA‑2 ile doğrulayın. 11 yıllık pencereyi 30 yıllık ERA5 içinde
konumlandırmak hakem sorusunu baştan kapatır.

**Ö5 — Aynı büyüklük için iki farklı atıf.** §3.2 "%5–8 (Soukissian vd.,
2018)"; §5.1 "%2–8 (Soukissian vd., 2017)".

**Ö6 — Weibull uyum iyiliği.** KS p‑değeri 2×10⁻⁴² (repo'da var, makalede
yok): n = 96 432'de Weibull biçimsel olarak reddediliyor; saatlik veri
otokorelasyonlu olduğu için test zaten geçerli değil. CDF üzerinden R² zayıf
bir ölçüt. "Method of moments" denen şey Justus'un ampirik formülü
(k = (σ/μ)^−1,086).

**Ö7 — Yaşam döngüsü faktörü ve birimler.**
- "IPCC AR5'te deniz üstü için 8–14" (giriş, §3.7) yanlış. Schlömer vd.
  (2014): en düşük 8, medyan 12, **en yüksek 35**. Kendi
  `REFERENCES_VERIFIED.md` dosyanız bunu yazıyor.
- Tablo 5 ve 6 hâlâ "IPCC 2025" kaynak gösteriyor; böyle bir rapor yok.
- ETKB şebeke faktörleri tCO₂/MWh (yalnız CO₂); makale bunları gCO₂‑**eq**
  diye etiketliyor ve CO₂‑eq cinsinden yaşam döngüsü faktörünü bundan
  çıkarıyor. Birimi düzeltin, farkı bir cümleyle belirtin.

**Ö8 — "IPCC Tool07".** Yöntem IPCC'nin değil: UNFCCC Temiz Kalkınma
Mekanizması **TOOL07 v7.0**. Üretim ortalaması (0,434) ayrı bir formdan
geliyor ("Elektrik Üretimi ve Elektrik Tüketim Noktası Emisyon Faktörleri");
ayrı atıf verin.

**Ö9 — Fosil karışım senaryosu ve Şekil 6–7.** Paylar (%36,8 / 33,3 / 29,9)
"yaklaşık" deniyor, kaynak yok; `scripts/09_generate_extra_figures.py:46`
içinde elle yazılmış. "≈69×" yanma emisyonunu yaşam döngüsü emisyonuyla
kıyaslıyor (ihtiyatlı ama elma‑armut; söyleyin). §4.5–4.6 ile Şekil 6–7
popüler bilim üslubunda — Medium yazısının "hero" figürü. Tek tabloya
indirmenizi öneririm. 3036 kWh/hane ve 2 tCO₂/araç atıfsız.

**Ö10 — Literatür ve doğrulama eksikliği.** 23 kaynak bu dergi için az.
Eksik başlıklar: ERA5'in kıyı/açık deniz sapması, rüzgâr atlasları (GWA,
NEWA), iz kaybı–kapasite yoğunluğu ilişkisi, marjinal emisyon yöntemi, modern
referans türbinler.

**Ö11 — Yapı.** §2.2 ile §3.1 aynı bilgiyi tekrar ediyor (saha geometrisi iki
kez). §2.5 sonuçları önceden veriyor.

---

## 4. Küçük ve biçimsel sorunlar

**Şekiller**
- Şekil 1: ağırlık merkezi etiketi "40.551° N, 26.250° E", metin 40.557 /
  26.198 (yıldız ERA5 düğümünün boylamına konmuş). Başlıkta "YEKA" ve "14
  May"; etiketler Türkçe (Trakya, Saros Körfezi, Çanakkale Boğazı); başlıkla
  paneller arasında büyük boşluk. Üreten script repo'da yok.
- Şekil 2: yöntem şemasının içinde sonuç sayıları var; MC kutusu, MC'den
  çıkan sayılardan sonra geliyor.
- Şekil 5d: "1738 MW", metin 1739 (gerçek 1738,5).
- Şekil 6 (`F6_story_v2.png`): üreten script yok; "1.52 Mt (official
  combined margin)" K3 nedeniyle yanlış.
- Tüm şekillerde gömülü başlık var; dergi istemez. Terim karışık: "Saros
  Bay" / "Gulf of Saros".
- Denklemler 200 dpi PNG olarak gömülü ve numarasız; dergi düzenlenebilir
  denklem ister.

**Tablolar ve taslak kalıntıları (PDF'te duruyor)**
- "Working tables for the Saros OWF manuscript… to be formatted".
- "Table 6 (optional)".
- Kaynakça başında "Author–year list (verified 13 June 2026). For Energies
  submission these will be converted…".
- Tablolar sonuçtan sonra; ilk anıldıkları yere taşınmalı.
- Kaynakça numarası 21'den sonra 1'e dönüyor.

**Atıf–kaynakça uyumsuzlukları**
- "Yaltırak et al., 1998, **2008**" (§2.3, Tablo 1): 2008 kaynakçada yok;
  kaynakçadaki Yaltırak vd. 2012 metinde hiç geçmiyor.
- "Yaltırak, 2002" → Yaltırak & Alpar, 2002.
- "Demirci, 2026" → Demirci vd., 2026.
- "Duzcan and Kara (2022)" metinde, kaynakçada 2023.
- "Aksoy et al., 2022" metinde, kaynakçada tek yazar. Doğru künye: Aksoy,
  Meghraoui, Polonia, Çağatay, Yavuzoğlu, Önder, Ülgen (bir kayıtta Gasperini
  de var), *GJI* 229(1), 589 başlangıç sayfası, **doi:10.1093/gji/ggab462**.
  PDF'te ggab481 ve 595–610, repo'da ggab447 yazıyor; ikisi de yanlış.
  Başlık da değiştirilmiş.
- Müller vd. 2013: PDF'te *Tectonophysics* 597–598, repo'da "JGR Solid
  Earth". Birini seçip DOI'den doğrulayın.
- 5,6–8,9 km kilitlenme derinliği atıfsız.

**Dergi biçimi (Energies/MDPI)**
- Özet 307 kelime, iki paragraf; sınır ≈200 kelime, tek paragraf.
- Yazarlar, kurumlar, Author Contributions, Funding, Data Availability
  Statement, Conflicts of Interest, Acknowledgments yok.
- MDPI, metin/veri/görsel üretiminde üretken yapay zekâ kullanıldıysa bunun
  beyan edilmesini istiyor. Kullanıldıysa Acknowledgments'a yazın.
- Kaynakça numaralı [1] biçime çevrilmeli.

---

## 5. Repo ve tekrarlanabilirlik

**R1 — Ana veri repo'da yok.** `README.md:72` ve `data/README.md`
`wind_hub_105m.parquet` dosyasının commit edildiğini söylüyor; `.gitignore:3`
onu dışlıyor ve dosya yok. Sonuç: 04, 05, 06, 09 numaralı script'ler temiz
bir klondan çalışmıyor. `wind_processing_summary.json` da yok; α = 0,149,
aylık ortalamalar ve rüzgâr gülü yüzdelerinin saklı bir çıktısı bulunmuyor.
Dosya küçük (≈1–2 MB): `.gitignore`'a istisna ekleyip commit edin veya
Zenodo'ya koyup DOI verin.

**R2 — İki şeklin script'i yok.** `F1_study_area.png` (Şekil 1) ve
`F6_story_v2.png` (Şekil 6). `F7_comparison.png` üretiliyor ama
kullanılmıyor. `figures/` → `figures_final/` kopyalaması elle yapılmış.
`FIGURE_BRIEFS.md` içinde anılan `data/site/SAROS_DURES.kml` repo'da yok.

**R3 — Repo, gönderilen PDF'in kaynağı değil.** `10_build_docx.py` kaynakça
üretmiyor; PDF'teki liste ("13 June") repo'dakinden ("9 June") farklı.
`manuscript/0*.md` dosyalarının sonunda hâlâ "[verify]", "IPCC (2025)",
"Kurt et al. (2000)", "Müller / Tüysüz (2007)" kalıntıları var (derlemede
kırpılıyor ama repo yayımlanınca görünür).

**R4 — Küçük kod sorunları**
- `scripts/04_fit_weibull_aep.py:196` olmayan bir script'e yönlendiriyor
  (`05_run_monte_carlo.py`).
- `scripts/03_process_era5.py:6,142,178` "log‑law" diyor; uygulanan kuvvet
  yasası.
- ddof tutarsız: `03:196` `np.std` (0), `05:98` pandas `.std()` (1) — Ö4'teki
  %3,2 / %3,4 farkının kaynağı.
- `config/site.py` alanı 172,6 km² hesaplıyor (4 ondalığa yuvarlanmış
  köşeler); makale 172,5 diyor. KML'yi tam hassasiyetle okuyun.
- `config/emissions.py` yorumlarında "IPCC 2025", "AR6/2025".
- `requirements.txt` sürümleri sabitlemiyor; README hızlı başlangıcı 05, 08,
  09, 10'u atlıyor ve `<your-username>` yer tutucusu duruyor;
  `CITATION.cff` yok.
- Fosil payları, hane ve araç sabitleri `config/` yerine script 09'da.

**R5 — İyi taraf.** `config/` tek doğruluk kaynağı olarak düzgün kurulmuş;
MC tohumu sabit ve sonuç bit düzeyinde yeniden üretilebiliyor.

---

## 6. Sayısal özet

| Büyüklük | Makale | Bağımsız kontrol |
|---|---|---|
| Brüt KF, ampirik seri | %36,5 | %36,5 ✓ |
| Brüt KF, Weibull(2,035; 8,080) | "%36,5" (§4.2) | **%35,5** |
| Net özgül verim, MC P50 | 2,62 GWh/MW | 2,622 ✓ |
| Kaçınılan, MC P50 | 1525 t/MW | 1525 ✓ (ama birleşik marj değil) |
| Kaçınılan, birleşik marj − LCA | "1525" | **1608** (1478–1738) |
| S3 kaçınılan, birleşik marj | 1,52 Mt | **1,60 Mt** |
| Güç eğrisi tepe Cp | — | **0,564** |
| AEP, Cp ≤ 0,48 / 0,45 | — | −%6,1 / −%9,5 |
| 100 m ortalama hız, ERA5 | 7,12 m/s | GWA v4: **7,83** (7,19–8,16) |
| Net KF, GWA'ya ölçekli | — | ≈%35,5 (makale eğrisi) |
| Net KF, 15 MW sınıfı (kaba) | — | ≈%36–37 (ERA5), ≈%41–42 (GWA) |
| Su derinliği | "~50 – >200 m" | **4–57 m**, medyan ~30 m |
| YAD | %3,2 (metin) / %3,4 (şekil) | 3,21 (ddof 0) / 3,37 (ddof 1); 2014'süz 1,83 |

15 MW satırı idealleştirilmiş bir eğriye dayanır; yön göstermek içindir,
makaleye bu hâliyle girmemeli.

---

## 7. Güçlü yönler

- Güncel ve politika açısından değerli bir konu; S3 senaryosu resmî 1 000 MWe
  ile örtüşüyor.
- Resmî poligon doğru aktarılmış ve hesaplar ondan türetiliyor.
- MW başına raporlama doğru tercih.
- Resmî birleşik marjın kullanılması doğru; yalnızca uygulaması düzeltilmeli.
- Sınırlılıklar bölümü dürüst; eksik olan, sınırlılıkların sayısal etkisi.
- Kod okunaklı, modüler, tohumlu.

---

## 8. Önerilen eylem planı

**A. Zorunlu (analizi yeniden çalıştırmayı gerektirir)**
1. Güç eğrisini kaynaklı bir eğriyle değiştirin; IEA 15 MW'ı ikinci referans
   yapın (K2).
2. GWA/NEWA/CERRA karşılaştırması ve sapma düzeltilmiş senaryo ekleyin;
   resmî %40–43 eşiğini tartışın (K1).
3. MC'yi ampirik seri üzerine kurun; reanaliz sapmasını ve güç eğrisi
   belirsizliğini girdi yapın; c için hangi belirsizliği (tek yıl / uzun
   dönem) verdiğinizi tanımlayın (K4, K5).
4. Şebeke faktörünü MC'den çıkarıp üç senaryo yapın; başlık 1608 t/MW ve
   1,60 Mt olsun (K3).
5. Batimetriyi EMODnet'ten hesaplayıp §2.3 ve Tablo 1'i yeniden yazın;
   kullanılabilir alanı derinlik ve kıyı mesafesine göre daraltın (K6, Ö3).

**B. Zorunlu (yalnız metin)**
6. DÜRES açılımı, 13 Mayıs tarihi, 2023 aday alanları, "aday" statüsü,
   1 000 MWe şartnamesi (K7).
7. Kış talep iddiasını çıkarın veya veriyle sınayın (K8).
8. "first peer‑reviewed" ve "measured α" ifadelerini düzeltin (Ö1, Ö2).
9. LCA aralığı, "IPCC 2025", "IPCC Tool07", CO₂ / CO₂‑eq (Ö7, Ö8).
10. Atıf–kaynakça uyumsuzlukları, Aksoy DOI, taslak notları (§4).

**C. Gönderim paketi**
11. Özeti 200 kelimeye indirin; arka bölümleri ekleyin.
12. Parquet + özet JSON + eksik iki şekil script'ini repo'ya koyun; Zenodo
    DOI alın; Data Availability Statement'a yazın (R1–R3).
13. Şekillerden gömülü başlıkları kaldırın, denklemleri dizgiye çevirin.

A grubu sonuçları değiştireceği için özet, tartışma ve sonuç en sona
bırakılmalı.

---

## Kaynaklar

- ETKB, Deniz Üstü Rüzgâr Enerjisine Dayalı Aday YEKA İlanı (13.05.2026) ve
  ekindeki KML arşivi: https://enerji.gov.tr/duyuru-detay?id=30615
- ETKB, YEKA DÜRES‑2026 Şartname Taslağı:
  https://enerji.gov.tr/Media/Dizin/ETKB/Duyurular/YEKA_DURES-2026_SARTNAME_TASLAGI.pdf
- ETKB/EVÇED, Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü Bilgi Formu
  (yöntem: UNFCCC CDM Tool 07 v7.0):
  https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/TUESEmisyonFktr/Belgeler/TUESEF_Bilgi_Formu.pdf
- 2023 şebeke faktörleri (ikincil):
  https://yesilekonomi.com/2023-yili-elektrik-sebekesi-emisyon-faktorleri-yayimlandi/
- Capital, şartname taslağı özeti (25.06.2026):
  https://www.capital.com.tr/sektorler/enerji/offshoreda-yeni-donem-turkiye-ilk-1000-mw-icin-yatirim-cercevesini-cizdi
- Capital, 2023 aday deniz üstü YEKA alanları (09.08.2023):
  https://www.capital.com.tr/haberler/tum-haberler/deniz-ustu-res-icin-yeka-buyuklukleri-belirlendi
- CNBC‑e, aday YEKA ilanı (14.05.2026):
  https://www.cnbce.com/enerji/turkiyeden-enerjide-yeni-adim-ilk-deniz-ustu-ruzgar-enerjisi-santralleri-icin-4-aday-yeka-belli-oldu-h30049
- Bloomberg HT, ihale takvimi (12.08.2026):
  https://www.bloomberght.com/denizustu-ruzgar-yeka-ihalesi-2027-nin-ilk-ceyreginde-3785281
- AA/Foreks, 1 000 MW ve kapasite faktörü beklentisi (24.09.2026):
  https://www.foreks.com/haber/detay/6ab4d95ab951084cfae82408/AA/tr/turkiye-nin-ilk-denizustu-ruzgar-yeka-si-3-milyar-dolarlik-yatirim-potansiyeli-tasiyor-24-09-26/
- Ember, Türkiye'de yaz/kış puantı:
  https://ember-energy.org/tr/analizler/artan-sogutma-tuketimi-gunes-enerjisi-ve-esneklik-cozumleri-ile-karsilanabilir/
- Aksoy vd., GJI 229(1):589, https://doi.org/10.1093/gji/ggab462
- Global Wind Atlas v4, Türkiye 100 m rüzgâr hızı rasterı:
  https://globalwindatlas.info/api/gis/country/TUR/wind-speed/100
- Batimetri: EMODnet 2018 ve GEBCO 2020, https://api.opentopodata.org
- Vestas V164‑9.5 MW teknik veriler:
  https://en.wind-turbine-models.com/turbines/1605-mhi-vestas-offshore-v164-9.5-mw
