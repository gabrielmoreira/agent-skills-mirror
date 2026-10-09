---
name: sql_query_optimizer
description: Sovereign runbook for slow SQL query profiling, explain query plan analysis, B-tree covering indexes, N+1 query elimination, and WAL tuning
keywords: ["sql query optimizer", "slow query profiling", "explain query plan", "sql index optimization", "btree index", "covering index", "n plus one query", "sqlite wal tuning", "database execution plan", "table scan reduction", "query latency tuning", "database lock contention", "sqlite pragmas", "composite index", "sql performance audit", "database vacuum", "join optimization", "subquery flattening", "deadlock prevention", "database indexing strategy"]
---
# ⚡ SKILL: SQL QUERY OPTIMIZER

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk profiling performa SQL, optimasi query berkecepatan tinggi, dan indexing cerdas:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Latency database tinggi, query berulang (N+1 queries), lock contention, atau scan tabel penuh (Full Table Scan / SCAN TABLE).
- **Batasan**: Agnostik engine relasional (SQLite, PostgreSQL, MySQL), dengan fokus utama pada arsitektur embedded SQLite Flowork OS.

## 2. Standard Operating Procedures (SOP)
1. **Profiling dengan EXPLAIN QUERY PLAN**:
   - Analisis setiap query bermasalah dengan `EXPLAIN QUERY PLAN <query>`.
   - Waspadai tanda bahaya: `SCAN TABLE` pada tabel besar yang mengindikasikan absennya indeks yang tepat.
2. **Indeks B-Tree & Covering Index**:
   - Buat indeks pada kolom yang sering muncul di klausul `WHERE`, `JOIN`, dan `ORDER BY`.
   - Manfaatkan Covering Index (menjadikan kolom select sebagai bagian dari indeks komposit) agar query selesai di B-tree tanpa membaca baris tabel fisik (Search Table using Covering Index).
3. **Eliminasi Pola N+1 Queries**:
   - Hindari looping query individual di dalam perulangan aplikasi host.
   - Gantikan dengan batch fetching via `WHERE id IN (...)` atau `JOIN` gabungan efisien.
4. **SQLite WAL Mode & Pragma Tuning**:
   - Aktifkan mode Write-Ahead Logging: `PRAGMA journal_mode = WAL;`.
   - Optimalkan sinkronisasi disk dan cache: `PRAGMA synchronous = NORMAL;`, `PRAGMA cache_size = -64000;`, `PRAGMA temp_store = MEMORY;`.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menaruh indeks secara berlebihan (over-indexing) pada tabel yang intensif operasi write/insert karena akan memperlambat I/O.
- **Dilarang**: Mengabaikan penutupan statement atau transaksi SQLite yang mengakibatkan database locked.

## 4. Verification & Exit Code 0 Proof
- Jalankan query benchmark sebelum dan sesudah optimasi indeks.
- Buktikan `EXPLAIN QUERY PLAN` menampilkan `SEARCH TABLE ... USING INDEX` (Exit Code 0).
