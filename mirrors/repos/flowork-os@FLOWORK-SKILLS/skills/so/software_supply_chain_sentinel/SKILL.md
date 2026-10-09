---
name: software_supply_chain_sentinel
description: Sovereign runbook for Software Bill of Materials (SBOM) generation, dependency vulnerability audits, typosquatting detection, and package integrity verification
keywords: ["supply chain security", "software bill of materials", "sbom generation", "dependency audit", "typosquatting detection", "dependency confusion", "package lock integrity", "vulnerable dependency scan", "cyclonedx sbom", "spdx standard", "hash verification", "oss security audit", "dependency provenance", "compromised package alert", "open source risks", "license compliance audit", "software supply chain", "transitive dependency check", "third party code hardening", "security patch tracking"]
---
# 📦 SKILL: SOFTWARE SUPPLY CHAIN SENTINEL

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk keamanan rantai pasok perangkat lunak (*software supply chain security*), audit SBOM, dan proteksi integritas dependensi open-source:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Penambahan pustaka pihak ketiga baru, verifikasi integritas lockfile (`package-lock.json`, `Cargo.lock`, `go.sum`), deteksi kerentanan transitif, dan kepatuhan lisensi.
- **Batasan**: Audit defensif dan verifikasi hash dependensi sebelum proses kompilasi atau deployment produksi.

## 2. Standard Operating Procedures (SOP)
1. **Software Bill of Materials (SBOM) Inventory**:
   - Ekstrak daftar seluruh dependensi langsung dan transitif ke format standar industri (CycloneDX atau SPDX).
   - Catat versi presisi, hash SHA-256, lisensi software, dan URL repositori sumber.
2. **Package Lock Integrity & Hash Pinning**:
   - Selalu komit berkas lockfile ke version control untuk memastikan build reproducible.
   - Wajib gunakan instalasi berbasis lockfile deterministik (`npm ci`, `cargo --locked`, atau `go mod verify`) daripada instalasi toleran pembaruan versi minor (`npm install`).
3. **Typosquatting & Dependency Confusion Defense**:
   - Verifikasi ejaan nama paket sebelum instalasi guna menghindari namespace pembajak (*typosquatting*).
   - Konfigurasi registry internal secara eksplisit untuk mencegah *dependency confusion* dari registry publik.
4. **Vulnerability Scanning & Automated Patching**:
   - Jalankan audit dependensi berkala terhadap basis data offline CVE/OSV.
   - Terapkan perbaikan minor segera setelah patch keamanan diterbitkan oleh pemelihara resmi tanpa merusak API contracts.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menggunakan dependensi tak terawat (*abandoned packages*) yang memiliki riwayat celah keamanan tanpa perbaikan.
- **Dilarang**: Mengabaikan peringatan integrity hash mismatch saat mengunduh package tarball.

## 4. Verification & Exit Code 0 Proof
- Jalankan verifikasi integritas dependensi: `flow_audit_security` atau `npm audit --audit-level=high`
- Audit lolos tanpa temuan vulnerability level tinggi/kritis (Exit Code 0).
