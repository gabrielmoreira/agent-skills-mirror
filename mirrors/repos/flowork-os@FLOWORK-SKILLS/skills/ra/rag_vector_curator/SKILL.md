---
name: rag_vector_curator
description: Sovereign runbook for document chunking strategies, embedding pipeline optimization, hybrid BM25 vector search, and reranking calibration
keywords: ["rag vector", "document chunking", "vector search", "embedding pipeline", "hybrid search", "bm25 ranking", "cross encoder reranking", "semantic similarity", "context retrieval", "vector database", "chunk overlap tuning", "metadata filtering", "retrieval augmented generation", "hnsw index", "cosine similarity", "dense retrieval", "token split strategy", "knowledge retrieval", "query expansion", "retrieval evaluation"]
---
# 📚 SKILL: RAG VECTOR CURATOR

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk kurasi dokumen RAG, strategi chunking presisi, dan kalibrasi retrieval hybrid:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Pembangunan pipeline knowledge base RAG, optimasi pencarian konteks, penanganan dokumen panjang, dan peningkatan recall semantic search.
- **Batasan**: Optimasi efisiensi token dan akurasi grounding jawaban model tanpa halusinasi.

## 2. Standard Operating Procedures (SOP)
1. **Deterministic Document Chunking**:
   - Gunakan strategi recursive character atau markdown header chunking (bukan fixed token splitting buta) untuk menjaga batas semantik paragraf.
   - Tetapkan overlap adaptif (10-15%) agar konteks sambungan antar-chunk tidak terputus.
2. **Metadata Enrichment**:
   - Sertakan metadata terstruktur pada setiap chunk: source path, header parent, timestamp, kategori, dan ID dokumen unik.
3. **Hybrid Search Architecture (Dense + Sparse)**:
   - Kombinasikan pencarian dense vector (embedding model) untuk konteks semantik dengan sparse search (BM25) untuk exact keyword matching (nama fungsi, ID, kode error).
   - Terapkan Reciprocal Rank Fusion (RRF) untuk menggabungkan skor relevansi kedua metode.
4. **Reranking & Context Pruning**:
   - Lewatkan kandidat top-K (15-20 chunk) ke Cross-Encoder Reranker untuk menghasilkan 3-5 chunk paling presisi.
   - Eliminasi teks boilerplate dan chunk duplikat sebelum disuntikkan ke prompt LLM.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menyimpan chunk raksasa (>1000 token per chunk) yang mengaburkan fokus semantic embedding.
- **Dilarang**: Mengabaikan pembaruan index saat berkas sumber diubah.

## 4. Verification & Exit Code 0 Proof
- Uji retrieval benchmark dengan set query uji.
- Pastikan precision@k memenuhi target evaluasi dan index query menghasilkan output valid (Exit Code 0).
