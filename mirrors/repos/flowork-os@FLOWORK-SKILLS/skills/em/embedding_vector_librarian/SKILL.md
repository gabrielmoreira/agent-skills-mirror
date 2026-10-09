---
name: embedding_vector_librarian
description: Sovereign runbook for local vector database management, cosine similarity retrieval, semantic chunk overlap indexing, and embedding deduplication
keywords: ["embedding vector librarian", "vector database", "cosine similarity", "semantic search", "rag indexing", "chunking strategy", "chunk overlap", "chromadb lancedb", "qdrant local", "dense retrieval", "embedding dimensions", "vector normalization", "ann index", "semantic deduplication", "hybrid search", "bm25 keyword search", "embedding cache", "text embeddings", "document metadata", "vector search accuracy"]
---

# ⚙️ SKILL: EMBEDDING VECTOR LIBRARIAN

## 1. Intent & Trigger Boundaries
- **Intent**: Manajemen basis data vektor lokal (LanceDB, Chroma, Qdrant, DuckDB vss, SQLite-vec), pembuatan strategi chunking teks cerdas, normalisasi vektor, pencarian kemiripan kosinus (Cosine Similarity), dan deduplikasi semantik.
- **Trigger**: Diminta membangun knowledge base semantik, sistem RAG (Retrieval-Augmented Generation), pencarian dokumen cerdas, indexing koleksi teks besar, atau membersihkan data ganda semantik.
- **Boundaries**: Tidak mengurusi kompresi prompt LLM saat eksekusi panggilan model (gunakan `llm_token_optimizer`). Fokus pada level embedding, kalkulasi dimensi vektor, dan penyimpanan indeks RAG.

## 2. Standard Operating Procedures (SOP)
1. **Intelligent Text Chunking Strategy**:
   - Terapkan chunking berbasis struktur dokumen (Markdown headers, recursive character splitter) daripada memotong teks sembarangan di tengah kalimat.
   - Atur batas chunk yang presisi: ukuran chunk tipikal 300-800 karakter dengan overlap 10-15% (30-80 karakter) untuk menjaga kelangsungan konteks semantik.
2. **Local Vector Engine Setup**:
   - Prioritaskan engine lokal nir-server yang ringan dan portabel (seperti LanceDB file-based atau SQLite-vec) agar bebas ketergantungan cloud.
   - Normalisasikan vektor embedding (L2 Norm) jika engine menggunakan perhitungan Dot Product untuk mempercepat kalkulasi Cosine Similarity.
3. **Hybrid Search & Re-ranking**:
   - Gabungkan pencarian Dense Embedding (vektor semantik) dengan Sparse Search (BM25 kata kunci spesifik/kode program) untuk akurasi optimal.
   - Sertakan metadata terperinci pada tiap chunk (`source_file`, `chunk_index`, `section_title`, `timestamp`).
4. **Semantic Deduplication & Index Hygiene**:
   - Hitung Cosine Distance antar potongan sebelum penambahan ke indeks; jika kemiripan melampaui 0.96, tolak atau satukan potongan guna mencegah polusi indeks.
   - Lakukan vacuum dan re-indexing berkala jika data banyak mengalami pembaruan (upsert/delete).

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang mencampuradukkan model embedding dengan dimensi yang berbeda dalam satu index vektor tunggal (akan memicu crash kalkulasi dot product).
- **PROHIBITION**: Dilarang menyimpan embedding tanpa metadata referensi dokumen sumber yang jelas.
- **EDGE CASE**: Hasil retrieval RAG tidak relevan / halusinasi: periksa apakah teks dipotong di tengah definisi fungsi atau tabel; gunakan recursive separator pembatas baris baru (`\n\n`, `\n`, ` `).

## 4. Verification & Exit Code 0 Proof
- Similarity Query Test: Skrip uji coba query vektor mengembalikan top-K dokumen relevan dengan skor Cosine Similarity > 0.75 dan exit code 0.
- Dimension Consistency Audit: Validasi seluruh vektor memiliki panjang array dimensi yang identik sesuai model (misal 384, 768, atau 1536).
- Database Persistence Check: Vektor tersimpan fisik ke disk lokal dan dapat dibuka ulang tanpa corrupt data (exit code 0).
