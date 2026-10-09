---
name: sqlite_vault_migrator
description: Sovereign runbook for zero-data-loss SQLite schema migrations, WAL mode concurrency, and IPC state persistence
keywords: ["sqlite migrator", "database migration", "schema migration", "sqlite vault", "data persistence", "sql table indexing", "database vacuum", "sqlite transactions", "wal mode", "relational database", "schema versioning", "foreign keys", "upsert operations", "sql query optimization", "database backup", "acid compliance", "sqlite connection pool", "local storage engine", "migration rollback", "database integrity check"]
---
# ⚙️ SKILL: SQLITE VAULT MIGRATOR & IPC STATE SPECIALIST
*Diadaptasi dari repositori dunia:* `affaan-m/ECC/skills/backend-patterns (274k★) & SQLite WAL Rigor`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk tata kelola database lokal, migrasi skema tabel atomik, dan persistensi state runtime:

## 1. DOKTRIN PERSISTENSI & MIGRASI SQLITE
- **Mode Konkurensi WAL (Write-Ahead Logging)**:
  - Setiap inisialisasi koneksi SQLite (`.db` / `.sqlite`) WAJIB mengeksekusi `PRAGMA journal_mode=WAL;` dan `PRAGMA synchronous=NORMAL;`.
  - Hal ini mencegah deadlock dan locking contention antara subagent, plugin background, dan engine utama.

- **Migrasi Bertahap Zero Data Loss**:
  - Dilarang keras melakukan `DROP TABLE` pada tabel data produksi yang sudah berisi informasi pengguna.
  - Setiap penambahan kolom atau modifikasi tabel wajib dibungkus dalam transaksi atomik (`BEGIN TRANSACTION ... COMMIT`) dengan versi skema eksplisit (`PRAGMA user_version`).

- **Sanitasi Kueri Anti-SQL Injection**:
  - Wajib menggunakan parameterized queries (`?1, ?2` atau prepared statements).
  - Dilarang melakukan string concatenation mentah saat menyusun SQL query.
