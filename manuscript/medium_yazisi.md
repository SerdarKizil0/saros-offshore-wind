# Aynı Elektrik, 69 Kat Fark: Saros Körfezi'nde Rüzgarın Matematiği

*Türkiye ilk deniz üstü rüzgar sahalarını ilan etti. Biz de oturduk, içlerinden birinin gerçekte ne üreteceğini ve havaya ne salmayacağını hesapladık. Çıkan sayı, bu yazının başlığında.*

---

14 Mayıs 2026'da Enerji ve Tabii Kaynaklar Bakanlığı dört ismi duyurdu: **Saros, Gökçeada, Bozcaada, Edremit.** Türkiye'nin ilk deniz üstü rüzgar enerjisi aday sahaları. Üç tarafı denizlerle çevrili bir ülke için tarihî bir eşik — çünkü bugüne kadar Türkiye denizlerinde dönen tek bir rüzgar türbini yok.

Haberler "en yüksek potansiyel Saros'ta" diye yazdı. Güzel. Peki "en yüksek potansiyel" tam olarak kaç kilovat-saat eder? O sahaya türbin dikilirse yılda ne üretir? Ve asıl sorumuz: **aynı elektriği bugünkü yöntemle — yani gazla, kömürle — üretmeye kıyasla atmosfer ne kazanır?**

Bu soruların cevabı hiçbir yerde yoktu. İlan yeni, hakemli literatür boş. Biz de cevabı kendimiz hesaplamaya karar verdik.

Bu yazı, o hesabın hikayesi.

---

## Önce tablo: Türkiye elektriğinin karnesi

Hesaba girmeden önce, neyin yerine ne koyduğumuzu bilmek lazım.

Türkiye 2024'te **347,9 milyar kilovat-saat** elektrik tüketti — ve bu sayı her yıl büyüyor. Bu elektriğin yarıdan fazlası hâlâ fosil yakıtlardan geliyor: doğal gaz, ithal kömür, yerli linyit. İşin can sıkıcı kısmı şu: gazın neredeyse tamamı, kömürün de önemli bölümü **ithal**. Yani her kilovat-saatin içinde hem karbon hem döviz var.

Rüzgara dönmenin iki ayrı getirisi tam burada birleşiyor: atmosfere salınmayan karbon ve yurt dışına ödenmeyen fatura. Türkiye karada rüzgarı çoktan keşfetti — kurulu güç 13 GW'ı aştı. Ama deniz tarafı, üç denize kıyısı olan bir ülke için garip biçimde, bugüne dek boş kaldı. Dünya Bankası'nın 2024 tarihli yol haritası Türkiye denizlerinde **75 GW'lık teknik potansiyel** hesaplıyor; devletin 2035 hedefi bunun 5 GW'ını devreye almak.

14 Mayıs ilanı, o 5 GW'ın ilk somut adresi. Saros da listenin başındaki isim.

`[FİGÜR 1 — Saros sahasının haritası: Kuzey Ege'de konum + sahanın şekli]`

---

## Sahne: Gelibolu'nun kuzeyinde uzun ince bir koridor

Saros Körfezi'ni haritada bulmak kolay: Gelibolu Yarımadası'nın hemen kuzeyi, Çanakkale Boğazı'nın Ege'ye açılan kapısının yanı başı. Bakanlığın ilan ettiği saha, kıyıya paralel uzanan **172,5 kilometrekarelik** bir koridor — yaklaşık 36 kilometre uzunluğunda, 10 kilometre genişliğinde. Kabaca İstanbul'un Adalar ilçesinin on beş katı büyüklüğünde bir deniz parçası.

Konum tesadüf değil. Körfez huni gibi: Trakya üzerinden inen kuzey rüzgarları bu koridorda sıkışıp hızlanıyor. Rüzgar enerjisi için aradığınız şey tam olarak bu.

Ama bu sahnenin bir de gerilim öğesi var: sahanın altından **Kuzey Anadolu Fayı'nın batı ucu** — jeologların Ganos Fayı dediği segment — geçiyor. 1912'de Mürefte-Şarköy depremini (büyüklük 7,4) üreten fay bu. Yılda yaklaşık 21 milimetre kayıyor ve hâlâ aktif. Yani Saros'ta türbin dikmek isteyen herkes, önce zemin mühendisliğine ciddi para harcayacak. Bunu not edip devam ediyoruz — çünkü bizim sorumuz enerji ve karbon tarafında.

---

## 11 yıl boyunca rüzgar dinlemek

Bir sahanın rüzgarını ölçmenin altın standardı, denize ölçüm direği dikmektir. Türkiye denizlerinde henüz bir tane bile yok. Peki ne yapacağız?

Burada devreye **ERA5** giriyor: Avrupa Orta Vadeli Hava Tahminleri Merkezi'nin (ECMWF) ürettiği, gezegenin son kırk yılının atmosferini saat saat yeniden kuran dev bir veri seti. Uydu gözlemleri, yer istasyonları, balonlar, gemiler — hepsi tek bir fizik modelinde birleştirilmiş. Bilim dünyasında rüzgar analizi için fiilî standart.

Saros'un üzerindeki grid noktasından **2014'ten 2024'e, on bir yılın her saatini** çektik. Toplam **96.432 saatlik** rüzgar kaydı.

Neden on bir yıl? Çünkü rüzgar yıldan yıla değişir. Tek bir yıla bakıp karar verirseniz, şanslı bir yıla denk gelmiş olabilirsiniz — ya da şanssız birine. On bir yıl, bu kumar payını yüzde ikinin altına indiriyor.

`[FİGÜR 2 — 11 yıllık rüzgar verisi: yıllık ortalamalar şeridi + mevsim deseni]`

---

## Rüzgarın parmak izi

96 bin saatlik ham kayıt, tek başına bir sayı yığını. Onu kullanılabilir bilgiye çeviren şey, rüzgar biliminin en sevdiği araç: **Weibull dağılımı.**

Şöyle düşünün: bir sahada rüzgarın kaç saatini hangi hızda geçirdiğini çizerseniz, karakteristik bir tepe çıkar — düşük hızlarda çok saat, orta hızlarda zirve, yüksek hızlarda incelen bir kuyruk. Bu eğrinin şekli, iki parametreyle özetlenebilir ve bu iki sayı sahanın âdeta parmak izidir. Dünyanın her rüzgar mühendisi bu iki sayıyla konuşur.

Saros'un parmak izi: **k = 2,04, c = 8,08 m/s.** Çevirisi: düzenli, savrulmayan, orta-iyi sınıf bir rüzgar rejimi. Ve uyum kalitesi etkileyici — eğri, 96 bin saatlik gerçek veriyi %99,8 doğrulukla temsil ediyor. Hesabın geri kalanı bu sağlam zemin üzerine kuruluyor.

Bu arada veride küçük bir sürpriz de yakaladık. Rüzgar yükseklikle hızlanır; ne kadar hızlandığını anlatan katsayıyı literatür açık deniz için "0,10 alın, geçin" der. Biz almadık — elimizde iki ayrı yükseklikte ölçüm olduğu için katsayıyı **veriden ölçtük: 0,149 çıktı.** Bariz biçimde "açık deniz" değil; Gelibolu kıyısının izini taşıyan, yarı-kıyısal bir profil. Küçük bir detay gibi görünüyor ama ezber yerine ölçüm kullanmak, 105 metredeki hız tahminini sistematik hatadan kurtarıyor. (Ve hakeme "biz varsaymadık, ölçtük" diyebilmek paha biçilmez.)

---

## Rüzgarın karakteri: Sakin ama güvenilir bir işçi

Verileri işleyince Saros'un rüzgar kişiliği ortaya çıktı. Üç özellik dikkat çekiyor.

**Birincisi: hız.** Türbin yüksekliğinde (105 metre) ortalama **7,17 m/s**. Bu, Kuzey Denizi'nin 9–10 m/s'lik fırtına koridorları değil; ama Akdeniz havzası ortalamasının üzerinde ve deniz üstü rüzgar için "ekonomik olarak anlamlı" eşiğin rahatça üstünde.

**İkincisi: istikrar.** On bir yılın en rüzgarlı yılı ile en durgun yılı arasında topu topu yüzde birkaç fark var — yıllar arası değişkenlik **%3,2**. Bu, bir yatırımcının duymak isteyeceği türden bir sayı: "bu saha her yıl aşağı yukarı aynı şeyi üretir" demek.

**Üçüncüsü ve en ilgincisi: zamanlama.** Ege'nin meşhur rüzgarı meltemdir (etezyen) ve yazın eser. Saros tam tersini yapıyor: **kışın coşuyor.** Ocak-Şubat ortalaması 8,4 m/s'ye tırmanırken, Haziran 5,6'ya düşüyor. Sahanın körfezin başındaki korunaklı konumu onu yaz meltemlerinden uzaklaştırıyor, ama Trakya'dan inen kış sistemlerine tam maruz bırakıyor.

Bu neden önemli? Çünkü Türkiye'de elektrik talebi de **kışın zirve yapar** — ısınma yükü. Üretimin pik yaptığı mevsimle talebin pik yaptığı mevsim örtüşüyor. Çoğu Ege sahası için söylenemeyecek bir uyum.

Rüzgarın yönü de hikayeye uyuyor: saatlerin neredeyse yarısında rüzgar **kuzeydoğudan** esiyor. Türbinleri buna göre dizerseniz, birbirlerinin rüzgarını çalmalarını (wake etkisi) en aza indirebilirsiniz.

`[FİGÜR 3 — Rüzgar gülü + "kış üretimi / kış talebi" örtüşmesi]`

---

## Türbinleri sahaya dikelim (kâğıt üzerinde)

Hesap için referans makinemiz, Akdeniz akademik literatürünün gözde türbini: **Vestas V164-9,5 MW.** Rotoru 164 metre — yan yana iki futbol sahası. Göbeği denizden 105 metre yukarıda.

Bir türbinin üretimi şöyle hesaplanır: rüzgar hızı dağılımını (bizim 96 bin saatlik kaydımız) türbinin güç eğrisiyle çarparsınız. Rüzgar 3,5 m/s altındaysa türbin durur; 14 m/s'de tam güce ulaşır; 25 üstünde kendini korumaya alır ve yine durur.

Sahaya kaç türbin sığar? Standart aralıklarla teorik tavan ~183 türbin (1,7 GW). Biz ana senaryomuzu daha gerçekçi tuttuk: **105 türbin, yaklaşık 1 gigavat** — devletin 2035 için koyduğu 5 GW'lık deniz üstü hedefinin beşte biri.

Kayıpları da düştük: türbinlerin birbirini gölgelemesi, bakım duruşları, kablo kayıpları. Net sonuç:

> **1 GW'lık Saros sahası yılda ~2,62 milyar kilovat-saat (2,62 TWh) elektrik üretir.**

Burada bir kavramı açmakta fayda var: **kapasite faktörü.** 1 GW'lık santral yılın her saati tam güç çalışsaydı 8,77 TWh üretirdi; bizim 2,62'miz bunun yaklaşık **%30'u**. "Sadece %30 mu?" demeyin — rüzgar her saat esmiyor ve bu gayet normal. Kara santralleri Türkiye'de tipik olarak %30'un altında kalır; Kuzey Denizi'nin devleri %45–50'ye çıkar; Saros %30'uyla "Akdeniz için sağlam" kategorisinde. Üstelik bizim %30'umuzun arkasında on bir yıllık veri ve on bin simülasyon var — pazarlama broşürü değil, dağılımıyla birlikte verilmiş bir mühendislik tahmini.

Soyut mu? Şöyle diyelim: bu, **yaklaşık 860 bin hanenin** yıllık elektriği. Eskişehir'in tamamı artı Trabzon'un tamamı, bir körfezin rüzgarından besleniyor gibi düşünün.

---

## Ve asıl soru: 69 kat

Şimdi yazının kalbine geliyoruz.

Türkiye'nin elektriğinin önemli bölümü hâlâ fosil yakıtlardan geliyor: doğal gaz, ithal kömür ve yerli linyit. Diyelim ki Saros'un üreteceği o 2,62 TWh'i, bugün yaptığımız gibi bu üçlüyle ürettik. Atmosfere ne gider?

Resmî emisyon katsayılarıyla hesap ortada:

- Linyit payı: **0,89 milyon ton CO₂**
- İthal kömür payı: **0,70 milyon ton**
- Doğal gaz payı: **0,39 milyon ton**
- **Toplam: yılda 1,98 milyon ton CO₂.**

Peki aynı elektriği Saros'un rüzgarından üretirsek?

Burada dürüst olmak lazım: rüzgar türbini de gökten inmiyor. Çeliği dökülüyor, kanatları üretiliyor, gemilerle taşınıp denize çakılıyor, 25 yıl bakımı yapılıyor, ömrü bitince sökülüyor. Bütün bu yaşam döngüsünün karbon faturası, üretilen her kilovat-saate bölündüğünde **~11 gram CO₂** ediyor. (Kömürün aynı rakamı 1.000 gramın üzerinde.)

Yani 2,62 TWh'lik rüzgar üretiminin toplam yaşam döngüsü yükü: **yılda 0,029 milyon ton.**

İki sayıyı yan yana koyun:

> **Fosil yol: 1,98 milyon ton. Rüzgar yolu: 0,029 milyon ton.**
> **Aradaki fark: yaklaşık 69 kat.**

Aynı ampulleri yakan, aynı buzdolaplarını çalıştıran, aynı fabrikaları döndüren elektrik. Tek fark üretim yolu — ve atmosferdeki 69 katlık iz farkı.

`[FİGÜR 4 — "Hero" karşılaştırma görseli: aynı 2,62 TWh'ten ayrılan iki yol, fosil istif vs rüzgarın ince çizgisi, ortada 69×]`

---

## Peki "kaçınılan emisyon" resmen kaç?

Dikkatli okur burada itiraz edebilir: "Rüzgar devreye girince birebir kömür santrali kapanmıyor ki — şebekede hidrosu da var, güneşi de."

Tamamen haklı bir itiraz, ve bunun resmî bir cevabı var. Enerji Bakanlığı her yıl, yeni rüzgar/güneş santrallerinin şebekede neyin yerini aldığını hesaplayan resmî bir katsayı yayınlıyor (IPCC metodolojisiyle hesaplanan "birleşik marj"). O katsayıyla hesap:

> **1 GW'lık Saros sahası yılda 1,52 milyon ton CO₂ emisyonunu önler.**
> (Belirsizlik aralığı: 1,27 – 1,75 milyon ton. Saf fosil ikamesi varsayılırsa üst sınır: 1,95 milyon ton.)

Yani elinizde iki sayı var ve ikisi de doğru — sadece farklı soruların cevapları. **1,98 → 0,029 (69×)** karşılaştırması "fosille üretseydik ne olurdu?" sorusunun cevabı; fiziksel ve çarpıcı. **1,52** ise "Türkiye şebekesinin bugünkü gerçek karmasında ne önlenir?" sorusunun cevabı; resmî ve muhasebeleştirilebilir. Makalemizde manşet ikincisi — çünkü hakem ve politika dünyası o dili konuşuyor. Ama atmosferin diliyle konuşacaksanız, 69× gerçeği orada duruyor.

1,52 milyon ton ne demek? **Yaklaşık 760 bin otomobili** trafikten kalıcı olarak çekmek demek. İstanbul'daki her dört arabadan birini yoldan kaldırdığınızı hayal edin — her yıl, yeniden.

Ve bu sadece *bir* saha. İlan edilen dört sahadan biri. Türkiye 2035 hedefinin (5 GW) tamamına Saros kalitesinde sahalarla ulaşırsa, yıllık önlenen emisyon 7,5 milyon tonu aşıyor.

`[FİGÜR 5 — Kaçınılan emisyonun somut karşılığı: araba/hane eşdeğerleri, senaryo merdiveni]`

---

## "10.000 paralel evren" — sayılara ne kadar güvenelim?

Buraya kadar verdiğimiz her sayının yanında aslında görünmez bir soru işareti var. Rüzgar tahmini kusursuz değil. Türbin kayıpları değişebilir. Emisyon katsayıları aralık içinde oynar.

Bu yüzden hesabı bir kez yapmadık — **on bin kez yaptık.**

Yöntemin adı Monte Carlo simülasyonu, ama şöyle düşünmek daha keyifli: her belirsiz parametrenin (rüzgar dağılımı, kayıplar, emisyon katsayıları...) makul aralığından rastgele bir değer çekip hesabı baştan koşturuyorsunuz. Sonra bir daha. On bin "paralel evrende" Saros sahasını işletiyorsunuz.

Sonuç güven verici çıktı: evrenlerin yüzde sekseninde yıllık üretim **2,40 ile 2,83 TWh** arasında, önlenen emisyon **1,27 ile 1,75 milyon ton** arasında kaldı. Yani kötümser senaryoda bile hikaye değişmiyor; sadece rakamın virgülden sonrası oynuyor.

Bu yaklaşımın güzelliği şu: tek bir "kesin" sayı vaat etmek yerine, sayının **ne kadar oynayabileceğini** de söylüyorsunuz. Enerji yatırımcıları bu dili çok iyi bilir — "P90" dedikleri, on senaryodan dokuzunda aşılan güvenli taban değerdir ve banka finansmanı o sayıya bakar. Saros'un P90'ı bile (yılda 2,40 TWh) yarım milyondan fazla hanenin elektriğine denk geliyor. En kötü gününde bile bu saha, küçümsenecek bir santral değil.

Bir de işin dürüstlük tarafı var: belirsizliği saklamak yerine raporlamak, "bu sayılar nereden çıktı?" sorusunu daha sorulmadan cevaplıyor. On bin evrenin hepsinde aynı hikaye anlatılıyorsa, hikaye sağlamdır.

---

## Dünya bu işin neresinde, biz neresindeyiz?

Bir parantez de dünya için açalım. Deniz üstü rüzgar artık deneysel bir teknoloji değil: küresel kurulu güç 75 GW'ı aştı, Çin tek başına yarıdan fazlasını taşıyor, İngiltere ve Danimarka on yıllardır denizden elektrik sağıyor. Maliyetler son on yılda öyle düştü ki, bazı Avrupa ihalelerinde deniz üstü rüzgar artık devlet desteksiz fiyat veriyor.

Türkiye bu trene geç biniyor — ama geç binmenin az konuşulan bir avantajı var: **olgunlaşmış teknolojiyi devralıyorsunuz.** İlk nesil deniz türbinleri 2–3 MW'lık makinelerdi; bugün referans makineler 9,5–15 MW arası. Aynı sahadan, on yıl önce kurulsaydı alınacak enerjinin neredeyse iki katı alınabiliyor. Üstelik kurulum gemileri, temel teknolojileri, bakım pratikleri — hepsi başkalarının pahalı derslerinden geçmiş durumda.

Bir de yerlilik boyutu var: Türkiye kara rüzgarında kanat ve kule üretimini büyük ölçüde yerlileştirdi. Deniz tarafında devletin "yerli türbin" arayışı şimdiden konuşuluyor. Bu hesabın güzel yanı, sonuçlarımızın **megavat başına** verilmiş olması — yarın sahaya hangi türbin dikilirse dikilsin, hangi kapasite tahsis edilirse edilsin, sayılar basit bir çarpmayla güncelleniyor.

---

## Dürüstlük köşesi: Bu hesabın bilmedikleri

Her hesap gibi bizimkinin de sınırları var, ve bunları söylemeden bitirmek olmaz:

**Fay orada duruyor.** Ganos Fayı sahadan geçiyor. Biz enerji ve karbon hesabı yaptık; deprem mühendisliği, temel tasarımı, zemin etüdü bambaşka ve zorunlu bir çalışma alanı.

**Derinlik her yerde uygun değil.** Sahanın doğusu sığ ve klasik deniz temeline (monopile) uygun; batı ucu hızla derinleşiyor. Oralar ya dışarıda kalır ya da yüzer türbin ister.

**ERA5'in çözünürlüğü kaba.** Veri noktaları ~28 km aralıklı; 36 km'lik sahanın içindeki yerel rüzgar farklarını göremiyoruz. Kıyı etkilerini çözmek için daha ince modelleme gerekir.

**Denizde ölçüm yok.** Türkiye sularında ölçüm direği olmadığı için hesabı yerinde ölçümle doğrulayamadık. (Bu, sadece bizim değil, Türkiye deniz üstü rüzgar literatürünün ortak eksiği.)

Bunların hiçbiri ana sonucu devirmiyor — ama "1 GW dikin, yarın 1,52 milyon ton tasarruf edin" diyen pembe bir reklam metni de yazmıyoruz. Sayılar koşullu; koşullar şeffaf.

---

## Kapanış: Bir körfezin teklifi

Saros'un rüzgarı dünya rekoru kırmıyor. Kapasite faktörü Kuzey Denizi devlerinin altında. Ama elinde üç şey var:

1. **Güvenilirlik** — yıldan yıla %3 oynayan, finanse edilebilir bir kaynak.
2. **Zamanlama** — tam da Türkiye'nin elektriğe en aç olduğu kış aylarında coşan bir rüzgar.
3. **Ve o oran** — aynı elektriği 69 kat daha az karbonla üretme teklifi.

14 Mayıs'ta atılan imza bir niyetti. Sayılar, o niyetin arkasını dolduruyor: tek bir saha, ülke elektriğinin %1'ine yakınını üretebilir ve her yıl yüz binlerce arabalık emisyonu havadan silebilir.

Geriye kalan kısım — fay etüdü, temel tasarımı, ihale, finansman — mühendislerin ve karar vericilerin masasında. Bizim masamızdan çıkan cevap netti:

**Rüzgar orada. Sayılar tutuyor.**

---

*Bu yazıdaki tüm hesaplar, 2014–2024 ERA5 saatlik verisi, resmî Türk şebeke emisyon katsayıları ve hakemli yaşam döngüsü literatürü kullanılarak yapılmıştır. Yöntemin ve sonuçların tam dökümü, hakemli dergiye gönderilen makalemizde yer alıyor — yayınlandığında bağlantısını buraya ekleyeceğiz.*
