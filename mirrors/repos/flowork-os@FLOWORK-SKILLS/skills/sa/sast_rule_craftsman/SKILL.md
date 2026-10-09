---
name: sast_rule_craftsman
description: Sovereign runbook for authoring SAST detection rules, AST semantic pattern matching, taint tracking, and eliminating false positives in source code audits
keywords: ["sast rule", "static application security", "semgrep rules", "codeql query", "ast pattern matching", "source code vulnerability", "taint analysis", "owasp static analysis", "cwe pattern detection", "false positive reduction", "security linter", "code audit automation", "sink and source tracing", "static code scanner", "rule syntax validation", "vulnerability pattern", "regex anti pattern", "semantic code audit", "custom sast ruleset", "secure code review"]
---
# 📜 SKILL: SAST RULE CRAFTSMAN

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk perancangan aturan analisis kode statis (SAST), pelacakan taint (source-to-sink), dan deteksi kerentanan kode berbasis pola AST semantik:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Audit keamanan source code berkala, pencegahan regresi celah keamanan di pipeline CI/CD, deteksi pola anti-pattern OWASP/CWE secara otomatis, dan eliminasi false positive pada linter keamanan.
- **Batasan**: Analisis statis terhadap kode sumber (Python, JavaScript/TypeScript, Rust, Go, C/C++) tanpa mengeksekusi biner secara aktif di lingkungan produksi.

## 2. Standard Operating Procedures (SOP)
1. **Source & Sink Identification (Taint Analysis)**:
   - Petakan titik masuk input tak tepercaya (*source*): `req.query`, `req.body`, argumen CLI, atau environment variables.
   - Petakan titik eksekusi berbahaya (*sink*): query database (`eval`, `child_process.exec`, `db.raw`, `fs.readFile`).
2. **Semantic AST Pattern Matching**:
   - Hindari pencarian berbasis regex naif yang rentan false-positive akibat spasi atau komentar.
   - Manfaatkan semantic engine (seperti Semgrep rules YAML atau CodeQL) yang menguraikan kode ke dalam Abstract Syntax Tree (AST).
3. **Authoring Precision Rules**:
   - Tentukan pola positif (`pattern: $SINK($...ARGS)`) dan pola pembersih sanitasi (`pattern-not: $SINK(sanitize($...ARGS))`).
   - Berikan metadata deskriptif: kode CWE (misal CWE-89 untuk SQLi, CWE-78 untuk Command Injection), tingkat severity, dan rekomendasi perbaikan kode.
4. **Testing & False-Positive Elimination**:
   - Jalankan ruleset terhadap fixture berkas positif (harus terdeteksi) dan berkas negatif (kode yang sudah disanitasi harus bersih tanpa alert).

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menerbitkan rule dengan laju false-positive tinggi yang menyebabkan cognitive fatigue pada tim developer.
- **Dilarang**: Menyembunyikan temuan security level Critical/High tanpa persetujuan arsitek sistem.

## 4. Verification & Exit Code 0 Proof
- Uji ruleset dengan command engine linter: `semgrep --validate --config <rule.yaml>`
- Validasi sintaks aturan lolos 100% tanpa error (Exit Code 0).
