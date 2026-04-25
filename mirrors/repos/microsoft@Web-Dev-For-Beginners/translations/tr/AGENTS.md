# AGENTS.md

## Proje Genel Bakışı

Bu, yeni başlayanlara web geliştirme temellerini öğretmek için hazırlanmış eğitim amaçlı bir müfredat deposudur. Müfredat, Microsoft Cloud Advocates tarafından geliştirilen kapsamlı 12 haftalık bir kurstur ve JavaScript, CSS ve HTML'i kapsayan 24 uygulamalı dersten oluşur.

### Ana Bileşenler

- **Eğitim İçeriği**: Proje tabanlı modüllerde düzenlenmiş 24 yapılandırılmış ders
- **Pratik Projeler**: Terrarium, Yazma Oyunu, Tarayıcı Uzantısı, Uzay Oyunu, Banka Uygulaması, Kod Editörü ve AI Sohbet Asistanı
- **Etkileşimli Testler**: Her biri 3 sorudan oluşan 48 test (ders öncesi/sonrası değerlendirmeleri)
- **Çok Dilli Destek**: GitHub Actions aracılığıyla 50+ dilde otomatik çeviriler
- **Teknolojiler**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI projeleri için)

### Mimari

- Ders tabanlı yapıya sahip eğitim deposu
- Her ders klasörü README, kod örnekleri ve çözümler içerir
- Bağımsız projeler ayrı dizinlerde (quiz-app, çeşitli ders projeleri)
- GitHub Actions kullanan çeviri sistemi (co-op-translator)
- Docsify ile sunulan ve PDF olarak da erişilebilir belge

## Kurulum Komutları

Bu depo öncelikle eğitim içeriklerini tüketmek içindir. Belirli projelerle çalışmak için:

### Ana Depo Kurulumu

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz Uygulaması Kurulumu (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Geliştirme sunucusunu başlat
npm run build      # Üretim için derle
npm run lint       # ESLint'i çalıştır
```

### Banka Projesi API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # API sunucusunu başlat
npm run lint       # ESLint çalıştır
npm run format     # Prettier ile biçimlendir
```

### Tarayıcı Uzantısı Projeleri

```bash
cd 5-browser-extension/solution
npm install
# Tarayıcıya özgü eklenti yükleme talimatlarını izleyin
```

### Uzay Oyunu Projeleri

```bash
cd 6-space-game/solution
npm install
# index.html dosyasını tarayıcıda açın veya Canlı Sunucu'yu kullanın
```

### Sohbet Projesi (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# GITHUB_TOKEN ortam değişkenini ayarlayın
python api.py
```

## Geliştirme İş Akışı

### İçerik Katkı Sağlayıcılar için

1. Depoyu GitHub hesabınıza **forklayın**
2. Forkladığınız depoyu **yerel olarak klonlayın**
3. Değişiklikleriniz için **yeni bir dal oluşturun**
4. Ders içeriği veya kod örneklerinde değişiklik yapın
5. İlgili proje dizinlerinde kod değişikliklerini test edin
6. Katkı yönergelerine uygun şekilde pull request gönderin

### Öğrenenler için

1. Depoyu forklayın veya klonlayın
2. Ders dizinlerinde sırasıyla gezin
3. Her ders için README dosyalarını okuyun
4. https://ff-quizzes.netlify.app/web/ adresinde ders öncesi testleri tamamlayın
5. Ders klasörlerindeki kod örneklerinde çalışın
6. Ödevleri ve zorlukları tamamlayın
7. Ders sonrası testleri yapın

### Canlı Geliştirme

- **Dokümantasyon**: Kök dizinde `docsify serve` komutunu çalıştırın (port 3000)
- **Quiz Uygulaması**: `quiz-app` dizininde `npm run dev` komutunu çalıştırın
- **Projeler**: HTML projeleri için VS Code Live Server uzantısını kullanın
- **API Projeleri**: İlgili API dizinlerinde `npm start` komutunu çalıştırın

## Test Talimatları

### Quiz Uygulaması Testi

```bash
cd quiz-app
npm run lint       # Kod stil sorunlarını kontrol et
npm run build      # Derlemenin başarılı olduğunu doğrula
```

### Bank API Testi

```bash
cd 7-bank-project/api
npm run lint       # Kod stili sorunlarını kontrol et
node server.js     # Sunucunun hatasız başlayıp başlamadığını doğrula
```

### Genel Test Yaklaşımı

- Bu eğitim deposunda kapsamlı otomatik testler yoktur
- Manuel testler şunlara odaklanır:
  - Kod örneklerinin hatasız çalışması
  - Dokümantasyondaki bağlantıların doğru çalışması
  - Proje derlemelerinin başarıyla tamamlanması
  - Örneklerin en iyi uygulamalara uygunluğu

### Gönderim Öncesi Kontroller

- Paket.json içeren dizinlerde `npm run lint` komutunu çalıştırın
- Markdown bağlantılarını doğrulayın
- Kod örneklerini tarayıcı veya Node.js'de test edin
- Çevirilerin yapısını düzgün koruduğunu kontrol edin

## Kod Stili Kılavuzu

### JavaScript

- Modern ES6+ sözdizimi kullanın
- Projelerde sağlanan standart ESLint yapılandırmalarına uyun
- Eğitim amaçlı anlamlı değişken ve fonksiyon adları kullanın
- Öğrenenler için kavramları açıklayan yorumlar ekleyin
- Yapılandırılmış yerlerde Prettier kullanarak biçimlendirin

### HTML/CSS

- Anlamsal HTML5 elemanları
- Duyarlı tasarım prensipleri
- Açık sınıf isimlendirme kuralları
- CSS tekniklerini açıklayan yorumlar

### Python

- PEP 8 stil yönergeleri
- Açık, eğitim odaklı kod örnekleri
- Öğrenme için yardımcı olduğunda tür ipuçları

### Markdown Dokümantasyonu

- Açık başlık hiyerarşisi
- Dil belirtmeli kod blokları
- Ek kaynaklara bağlantılar
- `images/` dizinlerinde ekran görüntüleri ve resimler
- Erişilebilirlik için resimlere alt metin

### Dosya Organizasyonu

- Dersler sırasıyla numaralandırılmış (1-getting-started-lessons, 2-js-basics vb.)
- Her projenin `solution/` ve genellikle `start/` veya `your-work/` dizinleri var
- Derslere özgü `images/` klasörlerinde görseller saklanır
- Çeviriler `translations/{language-code}/` yapısındadır

## Derleme ve Yayınlama

### Quiz Uygulaması Yayınlama (Azure Static Web Apps)

quiz-app Azure Static Web Apps yayını için yapılandırılmıştır:

```bash
cd quiz-app
npm run build      # dist/ klasörü oluşturur
# Ana dala push yapıldığında GitHub Actions iş akışı ile dağıtım yapar
```

Azure Static Web Apps yapılandırması:
- **Uygulama konumu**: `/quiz-app`
- **Çıktı konumu**: `dist`
- **İş akışı**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Dokümantasyon PDF Oluşturma

```bash
npm install                    # docsify-to-pdf yükle
npm run convert               # Belgelerden PDF oluştur
```

### Docsify Dokümantasyonu

```bash
npm install -g docsify-cli    # Docsify'i global olarak kur
docsify serve                 # localhost:3000 üzerinde sun
```

### Proje Bazlı Derlemeler

Her proje dizininin kendi derleme süreci olabilir:
- Vue projeleri: `npm run build` ile prodüksiyon paketleri oluşturur
- Statik projeler: Derleme adımı yok, dosyalar doğrudan sunulur

## Pull Request Yönergeleri

### Başlık Formatı

Değişiklik alanını belirten net, açıklayıcı başlıklar kullanın:
- `[Quiz-app] Ders X için yeni quiz ekle`
- `[Lesson-3] Terrarium projesindeki yazım hatasını düzelt`
- `[Translation] Ders 5 için İspanyolca çeviri ekle`
- `[Docs] Kurulum talimatlarını güncelle`

### Gerekli Kontroller

PR göndermeden önce:

1. **Kod Kalitesi**:
   - Etkilenen proje dizinlerinde `npm run lint` çalıştırın
   - Tüm lint hatalarını ve uyarılarını düzeltin

2. **Derleme Doğrulaması**:
   - Varsa `npm run build` komutunu çalıştırın
   - Derleme hatası olmadığından emin olun

3. **Link Doğrulama**:
   - Tüm markdown bağlantılarını test edin
   - Resim referanslarının çalıştığını kontrol edin

4. **İçerik İncelemesi**:
   - Yazım ve dilbilgisini gözden geçirin
   - Kod örneklerinin doğru ve eğitici olduğundan emin olun
   - Çevirilerin orijinal anlamı koruduğunu doğrulayın

### Katkı Gereksinimleri

- Microsoft CLA'ya (ilk PR'de otomatik kontrol)
- [Microsoft Açık Kaynak Davranış Kuralları](https://opensource.microsoft.com/codeofconduct/) uyumu
- Detaylı yönergeler için [CONTRIBUTING.md](./CONTRIBUTING.md)
- PR açıklamasında ilgili sorun numarasına referans verin (varsa)

### İnceleme Süreci

- PR'lar bakımcılar ve topluluk tarafından incelenir
- Eğitim açıklığı ön plandadır
- Kod örnekleri güncel en iyi uygulamalara uygun olmalıdır
- Çeviriler doğruluk ve kültürel uygunluk açısından gözden geçirilir

## Çeviri Sistemi

### Otomatik Çeviri

- GitHub Actions ile co-op-translator iş akışı kullanılır
- 50+ dile otomatik çeviri yapılır
- Kaynak dosyalar ana dizinlerde
- Çevrilmiş dosyalar `translations/{language-code}/` dizinlerinde

### Manuel Çeviri İyileştirmeleri Ekleme

1. `translations/{language-code}/` içinde dosyayı bulun
2. Yapıyı koruyarak iyileştirmeler yapın
3. Kod örneklerinin işlevselliğini sağlayın
4. Yerelleştirilmiş test içeriklerini test edin

### Çeviri Meta Verisi

Çevrilmiş dosyalar meta veri başlığı içerir:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Hata Ayıklama ve Sorun Giderme

### Yaygın Sorunlar

**Quiz uygulaması başlamıyor**:
- Node.js sürümünü kontrol edin (v14+ önerilir)
- `node_modules` ve `package-lock.json` dosyalarını silip tekrar `npm install` yapın
- Port çakışmalarını kontrol edin (varsayılan: Vite 5173 portunu kullanır)

**API sunucusu başlamıyor**:
- Node.js sürümünün minimum şartları sağladığını kontrol edin (node >=10)
- Portun kullanımda olup olmadığını kontrol edin
- Tüm bağımlılıkların `npm install` ile yüklendiğinden emin olun

**Tarayıcı uzantısı yüklenmiyor**:
- manifest.json dosyasının doğru formatta olduğunu doğrulayın
- Tarayıcı konsolunda hata olup olmadığını kontrol edin
- Tarayıcıya özgü uzantı yükleme talimatlarını izleyin

**Python sohbet projesi sorunları**:
- OpenAI paketi kurulu mu: `pip install openai`
- GITHUB_TOKEN ortam değişkeni ayarlı mı kontrol edin
- GitHub Modeller erişim izinlerini doğrulayın

**Docsify dokümanları sunmuyor**:
- docsify-cli global olarak kurun: `npm install -g docsify-cli`
- Depo kök dizininden çalıştırın
- `docs/_sidebar.md` dosyasının var olduğundan emin olun

### Geliştirme Ortamı İpuçları

- HTML projeleri için VS Code Live Server uzantısı kullanın
- Tutarlı biçimlendirme için ESLint ve Prettier uzantılarını kurun
- JavaScript hata ayıklama için tarayıcı Geliştirici Araçlarını kullanın
- Vue projeleri için Vue DevTools tarayıcı uzantısını yükleyin

### Performans Dikkatleri

- Çok sayıda çeviri dosyası (50+ dil) tam klonları büyük yapar
- Sadece içerikle çalışıyorsanız derinliği 1 olan klon kullanın: `git clone --depth 1`
- İngilizce içerik üzerinde çalışırken çevirileri aramalardan hariç tutun
- İlk çalıştırmada derleme ve yükleme işlemleri yavaş olabilir (npm install, Vite build)

## Güvenlik Dikkatleri

### Ortam Değişkenleri

- API anahtarları asla depoya gönderilmemelidir
- `.env` dosyalarını kullanın (zaten `.gitignore` içinde)
- Gerekli ortam değişkenlerini proje README'lerinde belgeleyin

### Python Projeleri

- Sanal ortam kullanın: `python -m venv venv`
- Bağımlılıkları güncel tutun
- GitHub tokenları minimum gerekli izinlere sahip olmalıdır

### GitHub Modeller Erişimi

- GitHub Modeller için Kişisel Erişim Tokenları (PAT) gereklidir
- Tokenlar ortam değişkeni olarak saklanmalıdır
- Tokenlar veya kimlik bilgileri asla depoya gönderilmemelidir

## Ek Notlar

### Hedef Kitle

- Web geliştirmeye tamamen yeni başlayanlar
- Öğrenciler ve kendi kendine öğrenenler
- Müfredatı sınıflarında kullanan öğretmenler
- İçerik erişilebilirlik ve kademeli beceri geliştirmeye yönelik

### Eğitim Felsefesi

- Proje tabanlı öğrenme yaklaşımı
- Sık bilgi ölçme testleri (quizler)
- Uygulamalı kodlama egzersizleri
- Gerçek dünya uygulama örnekleri
- Frameworklerden önce temel bilgilere odaklanma

### Depo Bakımı

- Aktif öğrenci ve katkı sağlayıcı topluluğu
- Bağımlılıklar ve içerik düzenli olarak güncellenir
- Sorunlar ve tartışmalar bakımcılar tarafından izlenir
- Çeviri güncellemeleri GitHub Actions ile otomatik yapılır

### İlgili Kaynaklar

- [Microsoft Learn modülleri](https://docs.microsoft.com/learn/)
- [Student Hub kaynakları](https://docs.microsoft.com/learn/student-hub/)
- Öğrenenler için önerilen [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- Ek dersler: Üretken AI, Veri Bilimi, ML, IoT müfredatları mevcut

### Belirli Projeler ile Çalışma

Bireysel projeler için ayrıntılı talimatlar aşağıdaki README dosyalarında:
- `quiz-app/README.md` - Vue 3 quiz uygulaması
- `7-bank-project/README.md` - Kimlik doğrulamalı banka uygulaması
- `5-browser-extension/README.md` - Tarayıcı uzantısı geliştirme
- `6-space-game/README.md` - Canvas tabanlı oyun geliştirme
- `9-chat-project/README.md` - AI sohbet asistanı projesi

### Monorepo Yapısı

Geleneksel bir monorepo olmasa da, bu depo birden çok bağımsız proje içerir:
- Her ders kendi başına tamamlanabilir
- Projeler bağımlılık paylaşmaz
- Bireysel projeler üzerinde diğerlerini etkilemeden çalışabilirsiniz
- Tam müfredat deneyimi için tüm depo klonlanabilir

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Feragatname**:  
Bu belge [Co-op Translator](https://github.com/Azure/co-op-translator) adlı AI çeviri hizmeti kullanılarak çevrilmiştir. Doğruluk için çaba göstersek de, otomatik çevirilerin hata veya yanlışlık içerebileceğini lütfen unutmayın. Orijinal belge, kendi ana dilinde yetkili kaynak olarak kabul edilmelidir. Kritik bilgiler için profesyonel insan çevirisi önerilir. Bu çevirinin kullanımı sonucu oluşabilecek yanlış anlamalar veya yorum hatalarından sorumlu değiliz.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->