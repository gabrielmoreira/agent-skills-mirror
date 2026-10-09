---
name: web_appsec_auditor
description: Sovereign runbook for OWASP Top 10 web application security auditing, security headers hardening, access control review, and vulnerability mitigation
keywords: ["web appsec", "application security audit", "owasp top ten", "xss prevention", "sql injection defense", "csrf token verification", "cors header hardening", "security headers audit", "ssrf defense", "broken access control", "session fixation defense", "jwt validation security", "content security policy", "input sanitization", "open redirect defense", "rate limit defense", "clickjacking defense", "security posture review", "vulnerability mitigation", "secure web architecture"]
---
# 🛡️ SKILL: WEB APPSEC AUDITOR

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk audit keamanan aplikasi web, mitigasi risiko OWASP Top 10, dan penegakan arsitektur web defensif:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Audit kesiapan rilis modul web/Canvas, peninjauan header keamanan HTTP, verifikasi integritas otentikasi/sesi, dan mitigasi risiko injeksi data.
- **Batasan**: Audit defensif dan hardening internal sistem host dan web endpoints.

## 2. Standard Operating Procedures (SOP)
1. **Broken Access Control & Authorization Audit**:
   - Verifikasi bahwa setiap endpoint yang menangani data sensitif memeriksa otorisasi berbasis peran (Role-Based Access Control / RBAC) di sisi server, bukan mengandalkan penyembunyian elemen UI klien.
   - Cegah Insecure Direct Object Reference (IDOR) dengan memvalidasi kepemilikan resource terhadap ID user aktif.
2. **Injection Defense & Parameterized Handlers**:
   - Wajib gunakan parameter binding atau ORM teruji untuk seluruh interaksi SQL/NoSQL.
   - Terapkan context-aware output encoding pada seluruh data dinamis sebelum dirender ke DOM guna mengeliminasi Cross-Site Scripting (XSS).
3. **HTTP Security Headers Hardening**:
   - Konfigurasi header pertahanan browser wajib:
     - `Content-Security-Policy`: Batasi domain script dan resource yang diizinkan (`default-src 'self'`).
     - `X-Frame-Options: DENY` atau `SAMEORIGIN` untuk mencegah Clickjacking.
     - `X-Content-Type-Options: nosniff`.
     - `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
     - `Referrer-Policy: strict-origin-when-cross-origin`.
4. **CORS & CSRF Mitigation**:
   - Hindari header permissif `Access-Control-Allow-Origin: *` pada endpoint yang membawa cookie kredensial.
   - Terapkan cookie dengan atribut `SameSite=Lax` atau `SameSite=Strict` dan token anti-CSRF pada mutasi state (POST, PUT, DELETE).

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menyimpan token otentikasi rahasia di `localStorage` jika aplikasi rentan terhadap XSS (prioritaskan HttpOnly cookie).
- **Dilarang**: Menonaktifkan validasi TLS/SSL (`rejectUnauthorized: false`) di komunikasi microservice internal.

## 4. Verification & Exit Code 0 Proof
- Audit konfigurasi header dan endpoint menggunakan skrip inspeksi HTTP lokal.
- Verifikasi seluruh security headers aktif dan respon berstatus aman (Exit Code 0).
