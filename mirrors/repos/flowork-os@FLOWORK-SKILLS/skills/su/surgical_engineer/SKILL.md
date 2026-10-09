---
name: surgical_engineer
description: Sovereign runbook for surgical precision coding, zero-bloat nano-modularity, anti-hallucination, and Karpathy minimalist implementation law
keywords: ["surgical engineer", "code refactoring", "bug fixing", "anti-zombie purge", "atomic code edit", "dead code elimination", "1-file-1-logic", "code hygiene", "replace_file_content", "minimal diff", "precision editing", "regression avoidance", "uncluttered code", "surgical patching", "scope preservation", "clean code refactor", "unused import removal", "targeted modification", "code clarity", "deterministic code fix"]
---
# 🔬 SKILL: SURGICAL ENGINEER & MINIMALIST IMPLEMENTATION

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk modifikasi kode presisi bedah (*surgical edits*), eliminasi spekulasi (*zero-bloat*), dan pencegahan halusinasi arsitektur.

## 1. DOKTRIN BEDAH PRESISI (SURGICAL LAWS)
1. **Pikir Sebelum Mengetik (Think Before Coding)**:
   - Paparkan asumsi secara transparan sebelum menulis kode.
   - Bila kebutuhan ambigu atau memiliki multi-tafsir, tanyakan via modal resmi (`ask_question`). Jangan menebak diam-diam.
   - Jika terdapat solusi yang jauh lebih sederhana, tolak over-engineering secara teknis.

2. **Hukum Kesederhanaan Mutlak (Simplicity First)**:
   - Tulis kode seminimal mungkin untuk menuntaskan masalah. Pantang menambahkan fitur di luar permintaan.
   - Dilarang membuat abstraksi berlapis untuk kode yang hanya dipanggil satu kali.
   - Dilarang menambahkan "fleksibilitas/konfigurasi" spekulatif yang tidak diminta.
   - Standar nano-modular Flowork: 1 berkas = 1 alur logika (20-80 baris). Jika 30 baris cukup, haram ditulis 100 baris.

3. **Perubahan Bedah (Touch Only What You Must)**:
   - Dilarang "merapikan" kode, komentar, atau formatting tetangga yang sedang berfungsi stabil.
   - Dilarang me-refactor modul yang tidak rusak.
   - Cocokkan gaya kode lokal yang ada, hindari perubahan style kosmetik.
   - Setiap baris yang diubah dalam diff wajib terlacak langsung pada instruksi User.

4. **Higienitas Pembersihan Sampah Sendiri**:
   - Jika modifikasi Anda menyebabkan import/variabel/fungsi lama menjadi yatim (*orphan/unused*), wajib bersihkan seketika.
   - Jangan menghapus dead-code warisan lama di luar lingkup tugas kecuali diminta secara tertulis.

## 2. WORKFLOW OPERASIONAL
1. **Fase Diagnosis**: Telaah file sasaran menggunakan `view_file` secara presisi.
2. **Fase Bedah**: Gunakan `replace_file_content` untuk membedah blok baris kontigu. Hindari menimpa seluruh berkas jika hanya mengubah beberapa baris.
3. **Fase Verifikasi**: Jalankan pengujian mandiri di terminal (`run_command`) hingga lolos empiris status Exit Code 0.
