---
name: empirical_verifier
description: Sovereign runbook for physical terminal evidence verification, Exit Code 0 enforcement, and zero-overclaim validation
keywords: ["empirical verifier", "terminal verification", "exit code 0", "test proof", "empirical evidence", "ground truth verification", "sanity check", "proof of execution", "reproducible results", "system audit", "runtime assertion", "error code verification", "deterministic testing", "output inspection", "validation pass", "zero guess assertion", "command exit code", "stdout inspection", "real world validation", "automated verification"]
---
# ⚖️ SKILL: EMPIRICAL VERIFIER & PHYSICAL EVIDENCE DEFENDER

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk verifikasi bukti fisik terminal sebelum mengklaim tugas selesai, pembelaan Exit Code 0, dan eliminasi overclaim semu.

## 1. HUKUM BESI VERIFIKASI (THE IRON LAW)
```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```
Jika Anda belum mengeksekusi perintah verifikasi fisik di pesan yang sama dan membuktikan hasilnya secara nyata, Anda DILARANG KERAS mengklaim bahwa tugas berhasil, selesai, atau lolos uji!

## 2. GERBANG PINTU VERIFIKASI (THE GATE FUNCTION)
Sebelum menyatakan kepuasan atau mengklaim status selesai ke User:
1. **IDENTIFIKASI**: Perintah terminal apa yang membuktikan klaim ini secara objektif?
2. **EKSEKUSI**: Jalankan perintah lengkap menggunakan `run_command` (segar, fresh, bukan mengandalkan memori lampau).
3. **BACA**: Periksa seluruh output terminal, pastikan 0 error, dan status fisik Exit Code 0.
4. **VERIFIKASI TAMPILAN**: Jika menyangkut UI/Canvas/CSS, wajib sertakan gambar bukti nyata via native tool `flow_screenshot`.
5. **KLAIM DENGAN BUKTI**: Paparkan status kepada User HANYA dengan melampirkan log terminal dan exit status-nya.

Melewatkan salah satu langkah di atas = kebohongan halusinasi teknis (*lying, not verifying*).

## 3. TABEL KEPASTIAN BUKTI (EVIDENCE RIGOR)

| Klaim Status | Syarat Wajib | Yang Diharamkan / Tidak Sah |
| :--- | :--- | :--- |
| **Tes Lolos** | Eksekusi terminal exit code 0, 0 failure | Mengasumsikan "seharusnya lolos" |
| **Lint / Format Bersih** | Output linter 0 error | Mengira kode terlihat rapi |
| **Portabilitas Multi-OS** | `flow_audit_portability` exit code 0 | Merasa path sudah benar |
| **Keamanan Terjamin** | `flow_audit_security` exit code 0 | Merasa input sudah aman |
| **UI Sempurna** | Tangkapan layar nyata via `flow_screenshot` | Klaim selesai tanpa bukti gambar pixel |
