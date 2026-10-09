---
name: systematic_debugger
description: Sovereign runbook for root cause tracing, isolated feedback loops, and zero-symptom-patching debugging
keywords: ["systematic debugger", "root cause analysis", "debugging", "stack trace analysis", "error tracing", "bug triage", "reproduction steps", "hypothesis testing", "scientific debugging", "log inspection", "breakpoint logic", "isolation testing", "failure state analysis", "edge case recreation", "bug verification", "call stack analysis", "fault localization", "defensive debugging", "regression diagnosis", "systematic isolation"]
---
# 🔍 SKILL: SYSTEMATIC DEBUGGER & ROOT CAUSE TRACER

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk investigasi bug mendalam, pelacakan alur data sistem multi-komponen, dan pencegahan tambal-gejala (*symptom patching*).

## 1. HUKUM BESI DEBUGGING (THE IRON LAW)
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```
DILARANG KERAS mengusulkan atau menerapkan perbaikan sebelum Phase 1 (Investigasi Akar Masalah) selesai secara empiris!

## 2. EMPAT FASE DEBUGGING SISTEMATIS
### Phase 1: Bangun Feedback Loop Terisolasi (Tight Loop)
1. **Redaksi Kredensial**: Sensor token/kunci rahasia sebelum mencetak payload diagnostik.
2. **Bangun Runner Minimal**: Buat skrip reproduksi terisolasi di `.FL_BIN/` (unit runner, curl HTTP test ke backend port dinamis, mock payload).
3. **Periksa Pesan Error & Traceback**: Baca nomor baris, call stack, dan kode error secara utuh. Pantang menebak tanpa membaca traceback.
4. **Lacak Batas Komponen (Component Boundary)**:
   - Pada alur multi-layer (UI ➔ IPC Canvas ➔ Backend Plugin ➔ Host OS):
   - Pasang log diagnostik data masuk dan data keluar di setiap perbatasan.
   - Temukan di lapisan mana data pertama kali rusak atau melenceng.

### Phase 2: Pelacakan Alur Data Mundur (Backward Tracing)
- Dari mana nilai rusak berasal?
- Siapa fungsi pemanggil yang menyuplai nilai tersebut?
- Lacak mundur ke atas sampai sumber awal ditemukan.
- Perbaiki di akar sumber (*root cause*), BUKAN di lapisan hilir gejala (*symptom*).

### Phase 3: Perbaikan Bedah (Surgical Fix)
- Terapkan perbaikan seminimal mungkin menggunakan `replace_file_content`.
- Jangan mengubah modul atau fungsi tetangga yang sedang sehat.

### Phase 4: Verifikasi Regresi Empiris
- Jalankan kembali feedback loop di `.FL_BIN/`.
- Buktikan bahwa kegagalan hilang dan menghasilkan status fisik **Exit Code 0**.
- Bersihkan skrip diagnostik sementara pasca-uji (`/CLEAN`).
