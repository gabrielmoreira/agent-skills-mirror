---
name: fuzz_testing_harness
description: Sovereign runbook for coverage-guided fuzz testing, automated bug hunting, crash reproduction, memory safety validation, and corpus management
keywords: ["fuzz testing", "coverage guided fuzzing", "crash reproduction", "bug hunting", "libfuzzer", "afl fuzzing", "cargo fuzz", "edge case discovery", "memory safety audit", "fuzz target design", "corpus minimization", "sanitizer address", "crash triage", "mutation testing", "boundary test generator", "parser robustness", "hang detection", "differential fuzzing", "fuzz harness", "automated bug hunting"]
---
# 🪲 SKILL: FUZZ TESTING HARNESS

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pengujian fuzzing otomatis (*automated bug hunting*), deteksi crash memory safety, dan kalibrasi corpus parser:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Pengujian ketahanan parser data (JSON, YAML, skema biner), pencarian bug tersembunyi (panics, infinite loops, out-of-memory), dan verifikasi stabilitas API terhadap input acak ekstrim.
- **Batasan**: Ditujukan untuk pengujian QA defensif dan hardening keandalan software.

## 2. Standard Operating Procedures (SOP)
1. **Fuzz Target Definition**:
   - Isolasi fungsi parser atau handler yang ingin diuji ke dalam fungsi harness atomik (`fuzz_target!(|data: &[u8]| { ... })` atau sepadan di Python/Go/C++).
   - Pastikan target tidak menjalankan operasi I/O jaringan atau disk lambat yang menurunkan throughput eksekusi fuzzing.
2. **Sanitizer Integration**:
   - Kompilasi harness dengan address sanitizer (`ASan`), undefined behavior sanitizer (`UBSan`), atau memory leak tracker untuk menangkap error yang tidak memicu abort standar.
3. **Seed Corpus Seeding & Mutation**:
   - Berikan input awal yang valid (*seed corpus*) dari data transaksi/payload nyata agar engine fuzzer dapat bermutasi secara efektif melintasi jalur cabang kode (code branches).
   - Jalankan coverage-guided fuzzer (`cargo-fuzz`, `libFuzzer`, atau `AFL++`) untuk memperluas cakupan eksekusi secara dinamis.
4. **Crash Reproduction & Root-Cause Triage**:
   - Simpan setiap payload yang memicu abort, timeout, atau panic ke direktori crash artifacts.
   - Buat regression test unit otomatis dari file crash tersebut untuk memastikan bug tidak berulang setelah perbaikan kode diterapkan.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Mengabaikan crash non-fatal atau memory leaks berulang selama siklus fuzzing berjalan.
- **Dilarang**: Menjalankan fuzzer tanpa batasan memori atau timeout per eksekusi (cegah OOM host exhaustion).

## 4. Verification & Exit Code 0 Proof
- Jalankan fuzz harness regression test terhadap crash payload yang telah diperbaiki.
- Unit test wajib lolos tanpa panic atau memory error (Exit Code 0).
