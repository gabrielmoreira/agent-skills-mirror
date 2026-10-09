---
name: api_contract_architect
description: Sovereign runbook for OpenAPI 3.1 specifications, strict JSON Schema validation, mock server generation, and breaking change prevention
keywords: ["openapi specification", "api contract", "swagger docs", "json schema validation", "rest api contract", "rpc schema", "breaking change detection", "mock server", "api schema linter", "contract testing", "payload serialization", "api versioning", "endpoint documentation", "zod schema inference", "request validation", "response schema", "api gateway contract", "http status codes", "api backwards compatibility", "spectral lint"]
---
# 📜 SKILL: API CONTRACT ARCHITECT

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk perancangan kontrak API, validasi skema payload, dan dokumentasi OpenAPI:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Pembuatan endpoint REST/RPC baru, standarisasi komunikasi client-server, pencegahan breaking changes, dan validasi skema runtime.
- **Batasan**: Skema harus netral bahasa dan mematuhi standar OpenAPI 3.1 atau JSON Schema Draft 2020-12.

## 2. Standard Operating Procedures (SOP)
1. **Contract-First Design**:
   - Definisikan kontrak API dan model schema sebelum menulis baris logika handler backend.
   - Cantumkan tipe data, batasan validasi (`minimum`, `maximum`, `pattern`, `format`), dan status code eksplisit.
2. **Strict Schema Validation**:
   - Seluruh payload request (body, query, headers) wajib divalidasi ketat di boundary handler menggunakan validator skema (Zod, TypeBox, atau Ajv).
   - Strip atau tolak properti tambahan yang tidak diizinkan (`additionalProperties: false`) untuk mencegah injection.
3. **Pencegahan Breaking Changes & Versioning**:
   - Hindari menghapus atau mengganti tipe field yang sudah ada dalam kontrak aktif.
   - Gunakan strategi backward-compatibility: field baru bersifat opsional (`optional`), atau buat prefix endpoint versi baru (`/v2/`).
4. **Mock Testing & Documentation**:
   - Hasilkan mock data otomatis dari skema kontrak untuk memvalidasi integrasi UI sebelum backend selesai.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Mengembalikan raw exception trace atau detail internal database dalam payload error response.
- **Standar Respon**: Wajib gunakan amplop respon terstandarisasi (`status`, `data`, `error`).

## 4. Verification & Exit Code 0 Proof
- Jalankan linting spesifikasi: `spectral lint openapi.yaml` atau test validasi schema runtime.
- Verifikasi parsing skema berhasil tanpa exception (Exit Code 0).
