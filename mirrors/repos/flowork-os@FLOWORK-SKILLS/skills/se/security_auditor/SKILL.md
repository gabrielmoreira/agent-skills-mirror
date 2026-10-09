---
name: security_auditor
description: Sovereign runbook for SAST security audit, vulnerability mitigation, secret sanitization, and CVE offline checking
keywords: ["security auditor", "vulnerability scan", "cve database", "flow_audit_security", "sast scan", "sca dependency audit", "code security", "exploit prevention", "secret detection", "data leak prevention", "injection attack defense", "xss prevention", "owasp compliance", "insecure dependency check", "permission audit", "credential sanitization", "zero trust audit", "security posture", "input validation audit", "crypto security"]
---
# 🛡️ SKILL: SECURITY AUDITOR & CODE HARDENING SPECIALIST

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk audit keamanan kode, mitigasi kerentanan, dan sanitasi sistem:

## 1. DOKTRIN KEAMANAN UTAMA
- **Zero Vulnerability Tolerance**: Tidak ada kode dengan celah kritis (Critical/High severity) yang boleh lolos ke produksi.
- **Offline & Sovereign**: Pengecekan ketergantungan mengutamakan basis data keamanan lokal Flowork (`security_db/vulns.db` dengan 283.000+ database CVE/OSV) tanpa ketergantungan pihak ketiga yang membocorkan metadata proyek.
- **Pemeriksaan Berlapis**: Audit mencakup SAST (Static Application Security Testing) dan SCA (Software Composition Analysis).

## 2. POLA ANCAMAN UTAMA & MITIGASI
1. **Command Injection**:
   - Dilarang merangkai perintah shell dengan konkatenasi string bebas (`sh -c "bin " + userInput`).
   - Wajib gunakan array argumen eksplisit (`child_process.spawn(cmd, [arg1, arg2])`, `Command::new(cmd).arg(arg1)`).
2. **Path Traversal**:
   - Seluruh input path dari luar wajib dinormalisasi dan divalidasi tidak keluar dari root direktori yang diizinkan (`path.resolve`, pengecekan prefix direktori batas).
   - Larang karakter `..` tak terkontrol pada parameter file I/O.
3. **Secret & Credential Leaks**:
   - Haram menyimpan API key, token JWT, password, atau private key di dalam berkas sumber kode.
   - Wajib gunakan environment variable (`process.env`, `.env`) atau vault kedaulatan (`auth_vault.json`).
4. **Insecure Deserialization / Eval**:
   - Haram menggunakan `eval()`, `new Function(untrusted)`, atau deserializer tidak aman pada payload eksternal.

## 3. PROSEDUR AUDIT
1. Jalankan audit menggunakan biner resmi: `flow_audit_security` terhadap target target.
2. Analisis laporan temuan: severity level, lokasi baris, dan jenis kerentanan.
3. Terapkan remediate nano-modular langsung pada titik kode yang terdampak.
4. Uji ulang hingga hasil audit menyatakan status bersih dan aman (Exit Code 0).
