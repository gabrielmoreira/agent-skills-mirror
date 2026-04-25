# AGENTS.md

## Gambaran Proyek

Ini adalah repositori kurikulum edukasi untuk mengajarkan dasar-dasar pengembangan web kepada pemula. Kurikulum ini merupakan kursus komprehensif selama 12 minggu yang dikembangkan oleh Microsoft Cloud Advocates, menampilkan 24 pelajaran praktis yang mencakup JavaScript, CSS, dan HTML.

### Komponen Utama

- **Konten Edukasi**: 24 pelajaran terstruktur yang diorganisasi dalam modul berbasis proyek
- **Proyek Praktis**: Terrarium, Permainan Mengetik, Ekstensi Browser, Permainan Luar Angkasa, Aplikasi Perbankan, Editor Kode, dan Asisten Chat AI
- **Kuis Interaktif**: 48 kuis dengan 3 pertanyaan tiap kuis (penilaian sebelum/sesudah pelajaran)
- **Dukungan Multi-bahasa**: Terjemahan otomatis untuk lebih dari 50 bahasa melalui GitHub Actions
- **Teknologi**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (untuk proyek AI)

### Arsitektur

- Repositori edukasi dengan struktur berbasis pelajaran
- Setiap folder pelajaran berisi README, contoh kode, dan solusi
- Proyek mandiri di direktori terpisah (quiz-app, berbagai proyek pelajaran)
- Sistem terjemahan menggunakan GitHub Actions (co-op-translator)
- Dokumentasi disajikan melalui Docsify dan tersedia dalam format PDF

## Perintah Setup

Repositori ini terutama untuk konsumsi konten edukasi. Untuk bekerja dengan proyek khusus:

### Setup Repositori Utama

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Setup Aplikasi Kuis (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Mulai server pengembangan
npm run build      # Bangun untuk produksi
npm run lint       # Jalankan ESLint
```

### API Proyek Bank (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Mulai server API
npm run lint       # Jalankan ESLint
npm run format     # Format dengan Prettier
```

### Proyek Ekstensi Browser

```bash
cd 5-browser-extension/solution
npm install
# Ikuti petunjuk pemuatan ekstensi spesifik browser
```

### Proyek Permainan Luar Angkasa

```bash
cd 6-space-game/solution
npm install
# Buka index.html di browser atau gunakan Live Server
```

### Proyek Chat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Tetapkan variabel lingkungan GITHUB_TOKEN
python api.py
```

## Alur Kerja Pengembangan

### Untuk Kontributor Konten

1. **Fork repositori** ke akun GitHub Anda
2. **Clone fork Anda** secara lokal
3. **Buat cabang baru** untuk perubahan Anda
4. Lakukan perubahan pada konten pelajaran atau contoh kode
5. Uji perubahan kode di direktori proyek terkait
6. Ajukan pull request sesuai panduan kontribusi

### Untuk Pembelajar

1. Fork atau clone repositori
2. Navigasi ke direktori pelajaran secara berurutan
3. Baca file README di setiap pelajaran
4. Selesaikan kuis sebelum pelajaran di https://ff-quizzes.netlify.app/web/
5. Kerjakan contoh kode di folder pelajaran
6. Selesaikan tugas dan tantangan
7. Ikuti kuis sesudah pelajaran

### Pengembangan Langsung

- **Dokumentasi**: Jalankan `docsify serve` di root (port 3000)
- **Aplikasi Kuis**: Jalankan `npm run dev` di direktori quiz-app
- **Proyek-proyek**: Gunakan ekstensi Live Server VS Code untuk proyek HTML
- **Proyek API**: Jalankan `npm start` di direktori API terkait

## Instruksi Pengujian

### Pengujian Aplikasi Kuis

```bash
cd quiz-app
npm run lint       # Periksa masalah gaya kode
npm run build      # Verifikasi keberhasilan build
```

### Pengujian API Bank

```bash
cd 7-bank-project/api
npm run lint       # Periksa masalah gaya kode
node server.js     # Verifikasi server mulai tanpa kesalahan
```

### Pendekatan Pengujian Umum

- Ini adalah repositori edukasi tanpa pengujian otomatis lengkap
- Pengujian manual fokus pada:
  - Contoh kode berjalan tanpa error
  - Link di dokumentasi berfungsi dengan baik
  - Proses build proyek berjalan sukses
  - Contoh sesuai praktik terbaik

### Pemeriksaan Sebelum Pengiriman

- Jalankan `npm run lint` di direktori dengan package.json
- Verifikasi link markdown valid
- Uji contoh kode di browser atau Node.js
- Pastikan terjemahan mempertahankan struktur yang tepat

## Pedoman Gaya Kode

### JavaScript

- Gunakan sintaks ES6+ modern
- Ikuti konfigurasi ESLint standar di proyek
- Gunakan nama variabel dan fungsi yang bermakna untuk kejelasan edukasi
- Tambahkan komentar penjelasan konsep untuk pembelajar
- Format menggunakan Prettier jika dikonfigurasi

### HTML/CSS

- Elemen HTML5 semantik
- Prinsip desain responsif
- Penamaan kelas yang jelas
- Komentar menjelaskan teknik CSS untuk pembelajar

### Python

- Panduan gaya PEP 8
- Contoh kode jelas dan edukatif
- Gunakan type hint bila membantu pembelajaran

### Dokumentasi Markdown

- Hierarki judul yang jelas
- Blok kode dengan penentuan bahasa
- Link ke sumber daya tambahan
- Screenshot dan gambar di direktori `images/`
- Teks alternatif untuk gambar demi aksesibilitas

### Organisasi File

- Pelajaran diberi nomor berurutan (1-getting-started-lessons, 2-js-basics, dll.)
- Setiap proyek memiliki direktori `solution/` dan sering juga `start/` atau `your-work/`
- Gambar disimpan di folder `images/` khusus pelajaran
- Terjemahan disimpan dalam struktur `translations/{language-code}/`

## Build dan Deployment

### Deployment Aplikasi Kuis (Azure Static Web Apps)

quiz-app dikonfigurasi untuk deployment Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Membuat folder dist/
# Menerapkan melalui workflow GitHub Actions saat push ke main
```

Konfigurasi Azure Static Web Apps:
- **Lokasi aplikasi**: `/quiz-app`
- **Lokasi output**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generasi PDF Dokumentasi

```bash
npm install                    # Pasang docsify-to-pdf
npm run convert               # Hasilkan PDF dari docs
```

### Dokumentasi Docsify

```bash
npm install -g docsify-cli    # Pasang Docsify secara global
docsify serve                 # Layani di localhost:3000
```

### Build Spesifik Proyek

Setiap direktori proyek mungkin memiliki proses build sendiri:
- Proyek Vue: `npm run build` untuk membuat bundel produksi
- Proyek statis: Tidak ada langkah build, layani file langsung

## Panduan Pull Request

### Format Judul

Gunakan judul jelas yang menggambarkan area perubahan:
- `[Quiz-app] Tambahkan kuis baru untuk pelajaran X`
- `[Lesson-3] Perbaiki typo di proyek terrarium`
- `[Translation] Tambah terjemahan Spanyol untuk pelajaran 5`
- `[Docs] Perbarui instruksi setup`

### Pemeriksaan Wajib

Sebelum mengirim PR:

1. **Kualitas Kode**:
   - Jalankan `npm run lint` di direktori proyek terkait
   - Perbaiki semua error dan peringatan lint

2. **Verifikasi Build**:
   - Jalankan `npm run build` jika berlaku
   - Pastikan tidak ada error build

3. **Validasi Link**:
   - Uji semua link markdown
   - Verifikasi referensi gambar berfungsi

4. **Tinjau Konten**:
   - Proofreading tata bahasa dan ejaan
   - Pastikan contoh kode benar dan edukatif
   - Verifikasi terjemahan mempertahankan makna asli

### Persyaratan Kontribusi

- Setujui Microsoft CLA (pemeriksaan otomatis pada PR pertama)
- Ikuti [Kode Etik Open Source Microsoft](https://opensource.microsoft.com/codeofconduct/)
- Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk panduan rinci
- Referensikan nomor isu dalam deskripsi PR jika ada

### Proses Review

- PR direview oleh pemelihara dan komunitas
- Prioritaskan kejelasan edukasi
- Contoh kode harus mengikuti praktik terbaik saat ini
- Terjemahan direview untuk akurasi dan kesesuaian budaya

## Sistem Terjemahan

### Terjemahan Otomatis

- Menggunakan GitHub Actions dengan workflow co-op-translator
- Menerjemahkan ke lebih dari 50 bahasa secara otomatis
- File sumber di direktori utama
- File terjemahan di direktori `translations/{language-code}/`

### Menambah Perbaikan Terjemahan Manual

1. Cari file di `translations/{language-code}/`
2. Buat perbaikan sambil mempertahankan struktur
3. Pastikan contoh kode tetap berfungsi
4. Uji konten kuis yang sudah diterjemahkan

### Metadata Terjemahan

File terjemahan termasuk header metadata:
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

## Debugging dan Pemecahan Masalah

### Masalah Umum

**Aplikasi kuis gagal mulai**:
- Periksa versi Node.js (disarankan v14+)
- Hapus `node_modules` dan `package-lock.json`, jalankan `npm install` lagi
- Periksa konflik port (default: Vite menggunakan port 5173)

**Server API tidak mulai**:
- Periksa versi Node.js minimal (node >=10)
- Periksa apakah port sudah digunakan
- Pastikan semua dependensi terinstall dengan `npm install`

**Ekstensi browser tidak dimuat**:
- Periksa format manifest.json sudah benar
- Periksa konsol browser untuk error
- Ikuti instruksi instalasi ekstensi khusus browser

**Masalah proyek chat Python**:
- Pastikan paket OpenAI terinstall: `pip install openai`
- Verifikasi variabel lingkungan GITHUB_TOKEN sudah diset
- Cek izin akses GitHub Models

**Docsify tidak menyajikan dokumentasi**:
- Instal docsify-cli secara global: `npm install -g docsify-cli`
- Jalankan dari direktori root repositori
- Pastikan `docs/_sidebar.md` tersedia

### Tips Lingkungan Pengembangan

- Gunakan VS Code dengan ekstensi Live Server untuk proyek HTML
- Instal ekstensi ESLint dan Prettier untuk format konsisten
- Gunakan DevTools browser untuk debugging JavaScript
- Untuk proyek Vue, pasang ekstensi Vue DevTools browser

### Pertimbangan Performa

- Jumlah file terjemahan besar (50+ bahasa) membuat clone penuh besar
- Gunakan clone shallow jika hanya bekerja dengan konten: `git clone --depth 1`
- Kecualikan terjemahan dari pencarian saat bekerja dengan konten bahasa Inggris
- Proses build mungkin lambat pada run pertama (npm install, build Vite)

## Pertimbangan Keamanan

### Variabel Lingkungan

- API key tidak boleh disimpan di repositori
- Gunakan file `.env` (sudah ada di `.gitignore`)
- Dokumentasikan variabel lingkungan yang diperlukan di README proyek

### Proyek Python

- Gunakan virtual environment: `python -m venv venv`
- Jaga dependensi tetap terupdate
- Token GitHub harus punya izin minimal yang dibutuhkan

### Akses GitHub Models

- Token Akses Pribadi (PAT) diperlukan untuk GitHub Models
- Token harus disimpan sebagai variabel lingkungan
- Jangan pernah commit token atau kredensial

## Catatan Tambahan

### Sasaran Audiens

- Pemula lengkap di pengembangan web
- Pelajar dan pembelajar mandiri
- Guru yang menggunakan kurikulum di kelas
- Konten dirancang untuk aksesibilitas dan peningkatan kemampuan bertahap

### Filosofi Edukasi

- Pendekatan pembelajaran berbasis proyek
- Pemeriksaan pengetahuan yang sering (kuis)
- Latihan coding langsung
- Contoh penerapan dunia nyata
- Fokus pada dasar sebelum framework

### Pemeliharaan Repositori

- Komunitas pembelajar dan kontributor yang aktif
- Pembaruan rutin pada dependensi dan konten
- Masalah dan diskusi dipantau oleh pemelihara
- Update terjemahan otomatis melalui GitHub Actions

### Sumber Daya Terkait

- [Modul Microsoft Learn](https://docs.microsoft.com/learn/)
- [Sumber Daya Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) direkomendasikan untuk pembelajar
- Kursus tambahan: Generative AI, Data Science, ML, kurikulum IoT tersedia

### Bekerja dengan Proyek Spesifik

Untuk instruksi rinci proyek individual, lihat README di:
- `quiz-app/README.md` - aplikasi kuis Vue 3
- `7-bank-project/README.md` - aplikasi perbankan dengan autentikasi
- `5-browser-extension/README.md` - pengembangan ekstensi browser
- `6-space-game/README.md` - pengembangan game berbasis canvas
- `9-chat-project/README.md` - proyek asisten chat AI

### Struktur Monorepo

Meski bukan monorepo tradisional, repositori ini berisi beberapa proyek independen:
- Setiap pelajaran bersifat mandiri
- Proyek tidak berbagi dependensi
- Kerjakan proyek individual tanpa memengaruhi proyek lain
- Clone seluruh repo untuk pengalaman kurikulum lengkap

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Penafian**:  
Dokumen ini telah diterjemahkan menggunakan layanan terjemahan AI [Co-op Translator](https://github.com/Azure/co-op-translator). Meskipun kami berusaha untuk akurasi, harap diingat bahwa terjemahan otomatis mungkin mengandung kesalahan atau ketidakakuratan. Dokumen asli dalam bahasa aslinya harus dianggap sebagai sumber yang sah. Untuk informasi yang penting, disarankan untuk menggunakan terjemahan profesional oleh manusia. Kami tidak bertanggung jawab atas kesalahpahaman atau penafsiran yang salah yang timbul dari penggunaan terjemahan ini.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->