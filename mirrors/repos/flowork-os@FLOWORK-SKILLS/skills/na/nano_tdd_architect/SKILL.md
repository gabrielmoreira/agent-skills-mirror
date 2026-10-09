---
name: nano_tdd_architect
description: Sovereign runbook for nano-modular Test-Driven Development (Red-Green-Refactor) and isolated test suites
keywords: ["nano tdd", "test driven development", "red green refactor", "unit test harness", "atomic test", "test first", "micro test suite", "regression test", "mocking assertions", "test coverage", "fail early test", "test fixture", "isolated tests", "quick test cycle", "cargo test", "jest runner", "behavior driven design", "test spec", "boundary condition tests", "reproducible assertions"]
---
# 🧪 SKILL: NANO TDD ARCHITECT & RED-GREEN-REFACTOR

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pengembangan berbasis tes (Test-Driven Development) yang diselaraskan dengan arsitektur nano-modular 20–80 baris.

## 1. HUKUM BESI NANO TDD (THE IRON LAW)
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```
Jika Anda tidak melihat tes gagal secara fisik, Anda TIDAK TAHU apakah tes tersebut benar-benar menguji logika yang tepat atau hanya ilusi lulus!

Menulis kode produksi sebelum tes? HAPUS. Mulai ulang dari tes!

## 2. SIKLUS TIGA FASE KEDAULATAN (RED ➔ GREEN ➔ REFACTOR)

### Fase 1: RED (Tulis Tes Gagal di .FL_BIN/)
1. Buat skrip uji isolasi di `.FL_BIN/test_<target>.js` / `.py` / `.sh`.
2. Tulis kasus uji sespesifik mungkin terhadap kebutuhan (hindari menguji hal sepele seperti validasi compiler/tipe bawaan bahasa).
3. Jalankan tes via `run_command` dan BUKTIKAN secara empiris bahwa statusnya GAGAL (Exit Code != 0).

### Fase 2: GREEN (Kode Produksi Minimalis)
1. Tulis kode produksi seminimal mungkin HANYA untuk membuat tes lolos.
2. Patuhi arsitektur nano-modular: 1 file 1 fungsi (20–80 baris).
3. Jalankan kembali tes di `.FL_BIN/` hingga membuktikan status Exit Code 0 (HIJAU).

### Fase 3: REFACTOR (Pembersihan Nano-Modular)
1. Bedah kode untuk keterbacaan dan performa tanpa merusak status hijau.
2. Hapus variabel atau import yatim yang tidak lagi digunakan.
3. Jalankan kembali tes fisik untuk memastikan ketiadaan regresi.
4. Bersihkan skrip tes sementara di `.FL_BIN/` bila tugas selesai.
