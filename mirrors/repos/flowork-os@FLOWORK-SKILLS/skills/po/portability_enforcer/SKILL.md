---
name: portability_enforcer
description: Sovereign runbook for cross-platform Multi-OS code normalization and zero-hardcoding enforcement
keywords: ["portability enforcer", "multi-os portability", "cross platform", "flow_audit_portability", "zero hardcoded paths", "windows posix compatibility", "path normalization", "path separator", "environment variables", "filesystem neutrality", "portable home directory", "symlink handling", "os agnostic scripts", "newline carriage return", "shell abstraction", "cross compilation", "portable architecture", "multi-platform testing", "relative path enforcement", "portable runtime"]
---
# 🌐 SKILL: PORTABILITY ENFORCER (MULTI-OS NORMALIZER)

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk penjaminan kompatibilitas multi-platform (Linux, Windows, macOS) dan pemberantasan hardcoded path:

## 1. DOKTRIN KEDAULATAN PORTABILITAS
- **Zero-Hardcoding Law**: Dilarang keras menuliskan path absolut host sistem (misal `/home/...`, `/Users/...`, `C:\...`) di seluruh baris kode produksi.
- **Relocation Resilience**: Proyek Flowork OS dan setiap sub-komponennya harus tetap berjalan 100% normal tanpa error saat dipindahkan ke PC lain atau saat nama folder diubah (relocatable workspace).
- **Agnostik Separator**: Wajib menggunakan pembangun path cross-platform (`path.join()`, `PathBuf`, `pathlib.Path`, `filepath.Join`).

## 2. PANDUAN NORMALISASI KODE BERDASARKAN BAHASA
1. **Node.js / TypeScript**:
   - Ganti `__dirname + '/sub'` dengan `path.join(__dirname, 'sub')` atau `path.resolve(...)`.
   - Gunakan `os.homedir()` atau runtime config root, jangan berasumsi `/root` atau `C:\Users`.
2. **Python**:
   - Gunakan `pathlib.Path(__file__).resolve().parent` atau `os.path.join()`.
   - Hindari pemisahan string berbasis `/` atau `\\`.
3. **Rust**:
   - Gunakan `std::path::PathBuf` dan method `.push()`.
4. **Shell / Batch**:
   - Untuk bash: gunakan referensi direktori dinamis `DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`.
   - Untuk Windows batch/cmd: gunakan `%~dp0`.
   - Untuk PowerShell: gunakan `$PSScriptRoot`.

## 3. PROSEDUR VERIFIKASI MULTI-OS
1. Jalankan audit portabilitas biner: `flow_audit_portability`.
2. Jika ditemukan pelanggaran (hardcoded pattern atau non-portable separator), bedah dan lakukan refactoring seketika.
3. Pastikan eksekusi terminal audit menghasilkan Exit Code 0 sebelum menyatakan tugas selesai.
