# Medium Yazısı — Figür Brief'leri

*Her figür için: mesaj (tek cümle), içerik (veri), kompozisyon önerisi, stil notu.
Veriler kesin — tasarım tamamen sende/araçta serbest.*

---

## FİGÜR 1 — Saha Haritası
**Mesaj:** "Saros nerede ve saha nasıl bir şekil?"
**İçerik:**
- Kuzey Ege konteksti: Gelibolu Yarımadası, Çanakkale Boğazı ağzı, Gökçeada, Trakya kıyısı
- Saha polygonu: kıyıya paralel, 35,7 × 10,5 km, 172,5 km², merkez 40.557°N 26.198°E
- (Opsiyonel gerilim öğesi) Ganos Fayı çizgisi sahadan geçerken — kırmızı kesikli hat
**Kompozisyon:** Tek panel yeter (Medium'da iki panelli harita küçük kalır). Zoom: körfez + yarımada. Saha dolgulu vurgu rengi, fay kesikli.
**Stil:** Düz renkler, az etiket. "İstanbul buradan 250 km" gibi tek bir ölçek çapası iyi olur.
**Ham veri:** `data/site/SAROS_DURES.kml` (polygon), `figures_final/figure1.png` (referans)

## FİGÜR 2 — 11 Yıl Rüzgar
**Mesaj:** "On bir yıl dinledik: istikrarlı + kış-pikli."
**İçerik (iki mini panel veya tek birleşik):**
- Yıllık ortalamalar (2014→2024): 6.55, 7.17, 7.41, 6.97, 7.37, 7.19, 7.39, 7.26, 7.17, 7.23, 7.18 m/s — dar bantta salınan çizgi; ±1σ bandı (CoV %3,2)
- Aylık desen: Oca 8.24, Şub 8.42, Mar 7.43, Nis 6.40, May 6.15, Haz 5.62, Tem 6.49, Ağu 7.55, Eyl 7.03, Eki 7.04, Kas 7.79, Ara 7.94
**Kompozisyon:** Aylık desende kış aylarını koyu/sıcak renkle vurgula; yanına Türkiye elektrik talebinin kış piki ikonu/mini eğrisi (örtüşme hissi).
**Stil:** Eksen minimal; "kış %50 daha hızlı" gibi tek bir anotasyon yeter.

## FİGÜR 3 — Rüzgar Gülü + Zamanlama
**Mesaj:** "Rüzgar kuzeydoğudan ve kışın geliyor — talep de kışın."
**İçerik:**
- Yön dağılımı: NE %25,8 + ENE %18,4 + NNE %12,0 (≈%56 kuzeydoğu çeyreği); ikincil SW lobu küçük
- Hız sınıfları: 0–3,5 / 3,5–7 / 7–10,5 / 10,5–14 / 14+ m/s
**Kompozisyon:** Polar gül; NE lobu vurgulu. Köşeye mini rozet: "üretim piki: Oca–Şub • talep piki: Oca–Şub ✓"
**Ham veri:** `data/processed/wind_hub_105m.parquet` (wdir + U_hub), referans: `figures_final/figure3.png`

## FİGÜR 4 — HERO: 69× Karşılaştırması ⭐ (yazının kalbi)
**Mesaj:** "Aynı 2,62 TWh: fosil yol 1,98 Mt, rüzgar yolu 0,029 Mt → 69×."
**İçerik (kesin sayılar):**
- Ortak kaynak rozeti: "2,62 TWh/yıl"
- Fosil yol istifi: Linyit 0,89 + İthal kömür 0,70 + Doğal gaz 0,39 = **1,98 Mt CO₂/yıl**
- Rüzgar yolu: **0,029 Mt** (yaşam döngüsü, imalat+kurulum+söküm dahil)
- Oran: **≈69×**
- Alt şerit: Önlenen **1,52 Mt/yıl** (resmî; aralık 1,27–1,75; fosil-ikame üst sınır 1,95) • ≈760 bin araba • ≈860 bin hane
**Kompozisyon:** Akış/sankey hissi: tek kaynaktan ayrılan iki yol; solda kalın koyu istif, sağda incecik yeşil çizgi; ortada dev "69×". Görsel oranlar gerçek olmalı (rüzgar barı fosilin 1/69'u — neredeyse görünmez olması mesajın kendisi).
**Stil:** Bu figür paylaşılabilir/alıntılanabilir olmalı — başlıksız da anlaşılır, tek bakışta.
**Referans:** `figures_final/figure6.png` (benim taslağım — kompozisyon fikri için)

## FİGÜR 5 — Somut Eşdeğerler / Senaryo Merdiveni
**Mesaj:** "Ölçek büyüdükçe etki: pilottan tavana."
**İçerik (P50 değerleri):**
| Senaryo | Güç | Üretim | Önlenen CO₂ | Araba | Hane |
|---|---|---|---|---|---|
| Pilot | 247 MW | 0,65 TWh | 0,38 Mt | 190 bin | 210 bin |
| Faz-1 | 504 MW | 1,32 TWh | 0,77 Mt | 380 bin | 440 bin |
| **Faz-2** | **998 MW** | **2,62 TWh** | **1,52 Mt** | **760 bin** | **860 bin** |
| Tavan | 1739 MW | 4,56 TWh | 2,65 Mt | 1,33 M | 1,50 M |
**Kompozisyon:** Merdiven/büyüyen ikonlar (araba ve ev piktogramları çoğalarak). Faz-2 vurgulu (ana senaryo).
**Stil:** İnfografik dili; sayılar büyük, eksen yok denecek kadar az.

## (Opsiyonel FİGÜR 6 — Monte Carlo "paralel evrenler")
**Mesaj:** "10.000 kez hesapladık; hikaye hiçbirinde değişmedi."
**İçerik:** Önlenen CO₂ dağılımı; P10=1,27 / P50=1,52 / P90=1,75 Mt işaretli.
**Kompozisyon:** Yumuşak tek tepe (violin/density), üç dikey çizgi. Minimalist.
**Ham veri:** `results/monte_carlo_samples.npz`

---

## Genel stil önerileri (hepsi için)
- Tek tutarlı palet: fosil = kahve/koyu tonlar, rüzgar = yeşil/teal, vurgu = turuncu
- Türkçe etiketler, kısa; ondalıkta virgül (2,62)
- Her figür tek mesaj — ikinci mesajı yeni figüre at
- Medium genişliği ~1400 px; yazı boyutları telefonda okunacak kadar büyük
