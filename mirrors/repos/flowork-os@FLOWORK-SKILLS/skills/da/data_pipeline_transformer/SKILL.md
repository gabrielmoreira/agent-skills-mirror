---
name: data_pipeline_transformer
description: Sovereign runbook for high-throughput streaming data pipelines, Polars DuckDB dataframes, zero-OOM memory batching, schema validation, and Parquet conversions
keywords: ["data pipeline transformer", "streaming data", "polars dataframe", "duckdb processing", "zero oom batching", "parquet conversion", "csv parsing", "jsonl processing", "data sanitization", "schema inference", "chunked etl", "memory mapped io", "out of core processing", "data deduplication", "null value cleaning", "type casting", "columnar storage", "batch generator", "pipeline backpressure", "data integrity audit"]
---

# ⚙️ SKILL: DATA PIPELINE TRANSFORMER

## 1. Intent & Trigger Boundaries
- **Intent**: Ekstraksi, transformasi, dan pemrosesan dataset berskala besar (CSV, JSONL, Parquet) tanpa menyebabkan kehabisan memori (Zero-OOM), konversi format data teroptimasi, sanitasi skema, dan komputasi berbasis Polars / DuckDB.
- **Trigger**: Diminta memproses file dump data berukuran gigabyte, migrasi dataset tabular, konversi format JSONL/CSV ke columnar Parquet, pembersihan missing values masif, atau pipeline ETL batching.
- **Boundaries**: Tidak mengurusi web crawling atau scraping HTTP mentah (gunakan `web_deep_scraper`). Fokus pada data engine di memory/disk, transformasi dataframe, dan stream ETL.

## 2. Standard Operating Procedures (SOP)
1. **Out-of-Core & Lazy Execution Architecture**:
   - Dilarang keras memuat (load) seluruh berkas besar ke RAM sekaligus menggunakan `pandas.read_csv()` atau `json.loads()`.
   - Gunakan evaluasi malas (Lazy Execution) via Polars (`pl.scan_csv()`, `pl.scan_parquet()`) atau engine DuckDB streaming queries.
   - Untuk data JSONL masif, baca per baris secara streaming (line-by-line generator) atau batch chunking terukur (misal 10.000 record per batch).
2. **Columnar Format Conversion (Parquet / Arrow)**:
   - Konversikan data mentah teks (CSV/JSONL) ke format columnar Snappy/ZSTD compressed Parquet untuk menghemat ruang disk hingga 80% dan mempercepat query hingga 10x.
   - Tetapkan tipe data kolom (schema casting) secara eksplisit untuk mencegah overhead deteksi tipe dinamis.
3. **Data Sanitization & Schema Validation**:
   - Filter dan tangani inkonsistensi nilai null, empty strings, atau invalid timestamps di awal pipeline.
   - Validasi batas nilai (range check, regex validation untuk ID/email, duplikasi key).
4. **Memory Guard & Batching Pipelines**:
   - Batasi konsumsi RAM dengan menetapkan batas alokasi memori buffer maksimum.
   - Buat fungsi pipeline idempotent: output ditulis ke direktori staging temporer sebelum proses rename atomik ke target final.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang menggunakan pemrosesan in-memory tanpa batas chunking pada dataset yang melebihi 25% kapasitas RAM sistem.
- **PROHIBITION**: Dilarang mengubah skema data produksi secara diam-diam tanpa mencatat log perubahan tipe data.
- **EDGE CASE**: Baris corrupt atau parser error di tengah-tengah jutaan data: tangkap exception per record, isolasi baris cacat ke `dead_letter_queue.jsonl`, dan teruskan pipeline tanpa membuat seluruh batch crash.

## 4. Verification & Exit Code 0 Proof
- Schema Integrity Verification: Skema output Parquet/CSV sesuai persis dengan kontrak tipe data tujuan.
- Memory Ceiling Test: Proses selesai tanpa memicu sinyal SIGKILL (Out-Of-Memory) oleh kernel OS (exit code 0).
- Row Count Reconciliation: Jumlah total baris input sama dengan jumlah (baris sukses + baris rejected di dead-letter queue).
