---
name: autonomous_loop_runner
description: Sovereign runbook for goal-driven autonomous task execution, circuit-breaker loops, state checkpointing, and regression defense
keywords: ["autonomous loop", "loop runner", "long-running task", "circuit breaker", "infinite loop defense", "state checkpointing", "task harness", "goal execution", "self-correcting loop", "autonomous agent", "step iteration", "runaway defense", "budget limit", "resilience loop", "convergence check", "feedback loop", "automated workflow", "recovery checkpoint", "task completion", "autonomous pipeline"]
---
# 🔄 SKILL: AUTONOMOUS LOOP RUNNER & TASK HARNESS

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk eksekusi tugas otonom berdurasi panjang, pemecahan langkah deterministik (*goal decomposition*), dan mitigasi loop tak berujung (*infinite loop breaker*).

## 1. DOKTRIN EKSEKUSI OTONOM
1. **Dekomposisi Sasaran Terukur (Verifiable Goal Formulation)**:
   - Setiap tugas kompleks wajib dipecah menjadi target fisik yang dapat diuji statusnya (Exit Code 0).
   - "Perbaiki bug X" → Tulis uji coba reproduksi di `.FL_BIN/` → Buat kode perbaikan → Pastikan uji coba exit code 0.
   - "Refaktor modul Y" → Pastikan uji kompatibilitas lolos sebelum dan sesudah refaktor.

2. **Protokol Siklus Loop Terstruktur**:
   ```
   [Rencana Tahap] ➔ [Eksekusi Bedah] ➔ [Uji Terminal Fisik] ➔ [Simpan Checkpoint] ➔ [Tahap Selanjutnya]
   ```

3. **Circuit Breaker (Anti-Infinite Loop)**:
   - Batas maksimal retry kegagalan pada langkah yang sama adalah 3 kali.
   - Jika gagal 3 kali berturut-turut:
     a. Berhenti sejenak dan lakukan introspeksi akar masalah (*root-cause analysis*).
     b. Laporkan blokade teknis secara jujur kepada Super Admin tanpa membuat tebakan baru.
     c. Gunakan `ask_question` jika butuh keputusan percabangan arsitektur.

4. **Kubah Ingatan & Checkpointing (.fl_brain/)**:
   - Untuk tugas multi-tahap, rekam progres dan keputusan penting ke `.fl_brain/decisions.md` dan `.fl_brain/solutions.md`.
   - Hindari kehilangan orientasi saat konteks percakapan memanjang.

## 2. PANDUAN PENGUJIAN ISOLASI
- Seluruh skrip runner sementara, mock data, dan uji coba transien WAJIB ditempatkan di `.FL_BIN/`.
- Dilarang mengotori direktori produksi atau plugin aktif dengan file uji coba sampah.
- Bersihkan artefak sementara setelah target terverifikasi tuntas.
