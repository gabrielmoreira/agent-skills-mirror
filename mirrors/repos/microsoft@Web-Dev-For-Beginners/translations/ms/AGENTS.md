# AGENTS.md

## Gambaran Projek

Ini adalah repositori kurikulum pendidikan untuk mengajar asas pembangunan web kepada pemula. Kurikulum ini merupakan kursus menyeluruh selama 12 minggu yang dibangunkan oleh Microsoft Cloud Advocates, menampilkan 24 pelajaran praktikal yang merangkumi JavaScript, CSS, dan HTML.

### Komponen Utama

- **Kandungan Pendidikan**: 24 pelajaran tersusun yang dianjurkan dalam modul berasaskan projek
- **Projek Praktikal**: Terrarium, Permainan Mengetik, Sambungan Pelayar, Permainan Angkasa, Aplikasi Perbankan, Penyunting Kod, dan Pembantu Chat AI
- **Kuis Interaktif**: 48 kuiz dengan 3 soalan setiap satu (penilaian sebelum/selepas pelajaran)
- **Sokongan Pelbagai Bahasa**: Terjemahan automatik untuk lebih 50 bahasa melalui GitHub Actions
- **Teknologi**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (untuk projek AI)

### Seni Bina

- Repositori pendidikan dengan struktur berasaskan pelajaran
- Setiap folder pelajaran mengandungi README, contoh kod, dan penyelesaian
- Projek bebas di direktori berasingan (quiz-app, pelbagai projek pelajaran)
- Sistem terjemahan menggunakan GitHub Actions (co-op-translator)
- Dokumentasi disajikan melalui Docsify dan tersedia dalam format PDF

## Perintah Persediaan

Repositori ini terutamanya untuk penggunaan kandungan pendidikan. Untuk bekerja dengan projek tertentu:

### Persediaan Repositori Utama

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Persediaan Aplikasi Kuis (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Mula pelayan pembangunan
npm run build      # Bina untuk pengeluaran
npm run lint       # Jalankan ESLint
```

### API Projek Bank (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Mula pelayan API
npm run lint       # Jalankan ESLint
npm run format     # Format dengan Prettier
```

### Projek Sambungan Pelayar

```bash
cd 5-browser-extension/solution
npm install
# Ikuti arahan pemuatan pelanjutan khusus pelayar
```

### Projek Permainan Angkasa

```bash
cd 6-space-game/solution
npm install
# Buka index.html dalam pelayar atau guna Live Server
```

### Projek Chat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Tetapkan pembolehubah persekitaran GITHUB_TOKEN
python api.py
```

## Aliran Kerja Pembangunan

### Untuk Penyumbang Kandungan

1. **Fork repositori** ke akaun GitHub anda
2. **Clone fork anda** secara lokal
3. **Buat cawangan baru** untuk perubahan anda
4. Lakukan perubahan pada kandungan pelajaran atau contoh kod
5. Uji sebarang perubahan kod dalam direktori projek berkaitan
6. Hantar pull request mengikut garis panduan sumbangan

### Untuk Pelajar

1. Fork atau clone repositori
2. Navigasi ke direktori pelajaran secara berurutan
3. Baca fail README untuk setiap pelajaran
4. Selesaikan kuiz pra-pelajaran di https://ff-quizzes.netlify.app/web/
5. Kerjakan contoh kod dalam folder pelajaran
6. Selesaikan tugasan dan cabaran
7. Ambil kuiz pasca-pelajaran

### Pembangunan Langsung

- **Dokumentasi**: Jalankan `docsify serve` di root (port 3000)
- **Aplikasi Kuis**: Jalankan `npm run dev` di direktori quiz-app
- **Projek**: Gunakan sambungan VS Code Live Server untuk projek HTML
- **Projek API**: Jalankan `npm start` di direktori API berkaitan

## Arahan Ujian

### Ujian Aplikasi Kuis

```bash
cd quiz-app
npm run lint       # Periksa isu gaya kod
npm run build      # Sahkan pembinaan berjaya
```

### Ujian API Bank

```bash
cd 7-bank-project/api
npm run lint       # Periksa isu gaya kod
node server.js     # Sahkan pelayan bermula tanpa ralat
```

### Pendekatan Ujian Umum

- Ini adalah repositori pendidikan tanpa ujian automatik menyeluruh
- Ujian manual fokus pada:
  - Contoh kod berjalan tanpa ralat
  - Pautan dalam dokumentasi berfungsi dengan betul
  - Pembinaan projek selesai dengan jayanya
  - Contoh mengikuti amalan terbaik

### Semakan Pra-penghantaran

- Jalankan `npm run lint` di direktori yang mengandungi package.json
- Sahkan pautan markdown sah
- Uji contoh kod dalam pelayar atau Node.js
- Periksa terjemahan mengekalkan struktur betul

## Garis Panduan Gaya Kod

### JavaScript

- Gunakan sintaks ES6+ moden
- Ikuti konfigurasi ESLint standard yang disediakan dalam projek
- Gunakan nama pemboleh ubah dan fungsi yang bermakna untuk kejelasan pendidikan
- Tambah komen yang menerangkan konsep untuk pelajar
- Format menggunakan Prettier di mana dikonfigurasi

### HTML/CSS

- Elemen HTML5 semantik
- Prinsip reka bentuk responsif
- Konvensyen penamaan kelas yang jelas
- Komen menerangkan teknik CSS untuk pelajar

### Python

- Garis panduan gaya PEP 8
- Contoh kod yang jelas dan pendidikan
- Petunjuk jenis di mana berguna untuk pembelajaran

### Dokumentasi Markdown

- Hirarki tajuk yang jelas
- Blok kod dengan spesifikasi bahasa
- Pautan ke sumber tambahan
- Tangkapan skrin dan imej dalam direktori `images/`
- Teks alt untuk imej bagi kebolehcapaian

### Pengurusan Fail

- Pelajaran dinomborkan secara berurutan (1-getting-started-lessons, 2-js-basics, dll.)
- Setiap projek mempunyai direktori `solution/` dan sering `start/` atau `your-work/`
- Imej disimpan dalam folder `images/` khusus pelajaran
- Terjemahan dalam struktur `translations/{language-code}/`

## Pembinaan dan Penghantaran

### Penghantaran Aplikasi Kuis (Azure Static Web Apps)

quiz-app dikonfigurasi untuk penghantaran Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Membuat folder dist/
# Melakukan deploy melalui workflow GitHub Actions apabila ada push ke main
```

Konfigurasi Azure Static Web Apps:
- **Lokasi aplikasi**: `/quiz-app`
- **Lokasi output**: `dist`
- **Aliran kerja**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Penjanaan PDF Dokumentasi

```bash
npm install                    # Pasang docsify-to-pdf
npm run convert               # Hasilkan PDF daripada docs
```

### Dokumentasi Docsify

```bash
npm install -g docsify-cli    # Pasang Docsify secara global
docsify serve                 # Hidangkan pada localhost:3000
```

### Pembinaan Khusus Projek

Setiap direktori projek mungkin mempunyai proses binaan sendiri:
- Projek Vue: `npm run build` menghasilkan bundle pengeluaran
- Projek statik: Tiada langkah binaan, hidangkan fail secara langsung

## Garis Panduan Pull Request

### Format Tajuk

Gunakan tajuk jelas dan deskriptif yang menunjukkan bidang perubahan:
- `[Quiz-app] Tambah kuiz baru untuk pelajaran X`
- `[Lesson-3] Betulkan ejaan dalam projek terrarium`
- `[Translation] Tambah terjemahan Sepanyol untuk pelajaran 5`
- `[Docs] Kemas kini arahan persediaan`

### Semakan Diperlukan

Sebelum menghantar PR:

1. **Kualiti Kod**:
   - Jalankan `npm run lint` di direktori projek terjejas
   - Betulkan semua ralat dan amaran linting

2. **Pengesahan Pembinaan**:
   - Jalankan `npm run build` jika berkaitan
   - Pastikan tiada ralat binaan

3. **Pengesahan Pautan**:
   - Uji semua pautan markdown
   - Sahkan rujukan imej berfungsi

4. **Semakan Kandungan**:
   - Semak ejaan dan tatabahasa
   - Pastikan contoh kod tepat dan pendidikan
   - Sahkan terjemahan mengekalkan maksud asal

### Keperluan Penyumbangan

- Setuju dengan Microsoft CLA (semakan automatik pada PR pertama)
- Ikuti [Kod Etika Sumber Terbuka Microsoft](https://opensource.microsoft.com/codeofconduct/)
- Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk garis panduan terperinci
- Rujuk nombor isu dalam penerangan PR jika berkenaan

### Proses Semakan

- PR disemak oleh penyelenggara dan komuniti
- Kejelasan pendidikan diutamakan
- Contoh kod harus mengikuti amalan terbaik terkini
- Terjemahan disemak ketepatan dan kesesuaian budaya

## Sistem Terjemahan

### Terjemahan Automatik

- Menggunakan GitHub Actions dengan aliran kerja co-op-translator
- Menterjemah ke 50+ bahasa secara automatik
- Fail sumber dalam direktori utama
- Fail terjemahan dalam direktori `translations/{language-code}/`

### Menambah Penambahbaikan Terjemahan Manual

1. Cari fail dalam `translations/{language-code}/`
2. Lakukan penambahbaikan sambil mengekalkan struktur
3. Pastikan contoh kod kekal berfungsi
4. Uji sebarang kandungan kuiz yang dialih bahasa

### Metadata Terjemahan

Fail terjemahan termasuk tajuk metadata:
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

## Pengesanan dan Penyelesaian Masalah

### Isu Biasa

**Aplikasi kuiz gagal dimulakan**:
- Periksa versi Node.js (disyorkan v14+)
- Padamkan `node_modules` dan `package-lock.json`, jalankan `npm install` semula
- Semak konflik port (lalai: Vite guna port 5173)

**Pelayan API tidak mula**:
- Sahkan versi Node.js memenuhi minimum (node >=10)
- Periksa jika port sudah digunakan
- Pastikan semua kebergantungan dipasang dengan `npm install`

**Sambungan pelayar tidak dimuat**:
- Periksa manifest.json diformat dengan betul
- Semak konsol pelayar untuk ralat
- Ikuti arahan pemasangan sambungan khusus pelayar

**Isu projek chat Python**:
- Pastikan pakej OpenAI dipasang: `pip install openai`
- Sahkan pembolehubah persekitaran GITHUB_TOKEN diset
- Periksa kebenaran akses GitHub Models

**Docsify tidak menyajikan dokumen**:
- Pasang docsify-cli secara global: `npm install -g docsify-cli`
- Jalankan dari direktori root repositori
- Semak bahawa `docs/_sidebar.md` wujud

### Tips Persekitaran Pembangunan

- Gunakan VS Code dengan sambungan Live Server untuk projek HTML
- Pasang sambungan ESLint dan Prettier untuk format konsisten
- Gunakan DevTools pelayar untuk debug JavaScript
- Untuk projek Vue, pasang sambungan Vue DevTools pelayar

### Pertimbangan Prestasi

- Bilangan fail terjemahan yang banyak (50+ bahasa) menyebabkan klon penuh besar
- Gunakan clone cetek jika hanya bekerja dengan kandungan: `git clone --depth 1`
- Kecualikan terjemahan dari carian ketika bekerja pada kandungan Inggeris
- Proses binaan mungkin perlahan pada kali pertama (npm install, binaan Vite)

## Pertimbangan Keselamatan

### Pembolehubah Persekitaran

- Kunci API tidak boleh dimuat naik ke repositori
- Gunakan fail `.env` (sudah disenarai dalam `.gitignore`)
- Dokumentasikan pembolehubah persekitaran yang diperlukan dalam README projek

### Projek Python

- Gunakan persekitaran maya: `python -m venv venv`
- Kemas kini kebergantungan secara berkala
- Token GitHub hendaklah mempunyai kebenaran minimum diperlukan

### Akses GitHub Models

- Token Akses Peribadi (PAT) diperlukan untuk GitHub Models
- Token disimpan sebagai pembolehubah persekitaran
- Jangan sesekali memuat naik token atau kelayakan

## Nota Tambahan

### Sasaran Pengguna

- Pemula lengkap dalam pembangunan web
- Pelajar dan pembelajar kendiri
- Guru yang menggunakan kurikulum dalam bilik darjah
- Kandungan direka untuk kebolehcapaian dan pembinaan kemahiran secara berperingkat

### Falsafah Pendidikan

- Pendekatan pembelajaran berasaskan projek
- Pemeriksaan pengetahuan kerap (kuiz)
- Latihan amali pengkodan
- Contoh aplikasi dunia sebenar
- Fokus pada asas sebelum kerangka kerja

### Penyelenggaraan Repositori

- Komuniti pelajar dan penyumbang aktif
- Kemas kini kandungan dan kebergantungan secara berkala
- Isu dan perbincangan dipantau oleh penyelenggara
- Kemas kini terjemahan automatik melalui GitHub Actions

### Sumber Berkaitan

- [Modul Microsoft Learn](https://docs.microsoft.com/learn/)
- [Sumber Pelajar Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) disyorkan untuk pelajar
- Kursus tambahan: AI Generatif, Sains Data, ML, kurikulum IoT tersedia

### Bekerja dengan Projek Tertentu

Untuk arahan terperinci projek individu, rujuk fail README di:
- `quiz-app/README.md` - aplikasi kuiz Vue 3
- `7-bank-project/README.md` - aplikasi perbankan dengan pengesahan
- `5-browser-extension/README.md` - pembangunan sambungan pelayar
- `6-space-game/README.md` - pembangunan permainan berasaskan canvas
- `9-chat-project/README.md` - projek pembantu chat AI

### Struktur Monorepo

Walaupun bukan monorepo tradisional, repositori ini mengandungi pelbagai projek bebas:
- Setiap pelajaran berdiri sendiri
- Projek tidak berkongsi kebergantungan
- Kerja pada projek individu tanpa menjejaskan yang lain
- Clone keseluruhan repositori untuk pengalaman kurikulum penuh

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Penafian**:  
Dokumen ini telah diterjemahkan menggunakan perkhidmatan terjemahan AI [Co-op Translator](https://github.com/Azure/co-op-translator). Walaupun kami berusaha untuk ketepatan, sila maklum bahawa terjemahan automatik mungkin mengandungi kesilapan atau ketidaktepatan. Dokumen asal dalam bahasa asalnya harus dianggap sebagai sumber yang sahih. Untuk maklumat penting, terjemahan profesional oleh manusia adalah disyorkan. Kami tidak bertanggungjawab terhadap sebarang salah faham atau salah tafsir yang timbul daripada penggunaan terjemahan ini.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->