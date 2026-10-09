---
name: llm_token_optimizer
description: Sovereign runbook for LLM token budget management, prompt compression, context window pruning, semantic prompt caching, and structured JSON outputs
keywords: ["llm token optimizer", "token budget", "prompt compression", "context window pruning", "semantic prompt caching", "token counting", "structured json output", "context truncation", "prompt hygiene", "system prompt reduction", "tiktoken tokenizer", "llm cost reduction", "sliding context window", "rag context filter", "prompt engineering", "few shot distillation", "json schema enforcement", "context distillation", "stop sequence", "token throughput"]
---

# ⚙️ SKILL: LLM TOKEN OPTIMIZER

## 1. Intent & Trigger Boundaries
- **Intent**: Mengoptimalkan konsumsi token LLM, memangkas prompt bloat, menerapkan kompresi teks matematis/semantik, merancang sliding context windows, caching prompt, dan penegakan skema output JSON ketat.
- **Trigger**: Diminta mengurangi biaya token LLM, mencegah error context length exceeded, mempercepat latency inferensi LLM, mendesain prompt ringkas padat, atau membatasi ukuran memori prompt agen.
- **Boundaries**: Tidak mengurusi pencarian vektor lokal dan manajemen index database embedding (gunakan `embedding_vector_librarian`). Fokus pada payload prompt, token budget, dan skema output model AI.

## 2. Standard Operating Procedures (SOP)
1. **Token Profiling & Budget Allocation**:
   - Hitung estimasi token secara presisi sebelum inferensi (menggunakan tokenizer library seperti `tiktoken` untuk OpenAI atau tokenizer native model terkait).
   - Terapkan alokasi token budget ketat: contoh 20% system prompt, 50% dynamic context/RAG, 30% reservasi completion buffer.
2. **Context Pruning & Distillation**:
   - Singkirkan karakter whitespace berlebih, komentar boilerplate, dan redundant delimiters dari prompt input.
   - Gunakan teknik ringkasan bertahap (incremental compression) atau prioritaskan hanya diff perubahan terbaru daripada menyertakan seluruh histori percakapan mentah.
   - Terapkan sliding window: pertahankan pesan sistem permanen + N interaksi terbaru, arsipkan sisanya ke storage luar.
3. **Semantic Prompt Caching Optimization**:
   - Letakkan blok teks statis (instruksi sistem, definisi tools, schema baku) persis di awal urutan prompt (prefix position) agar memenuhi syarat context caching engine (Anthropic / OpenAI prompt cache).
   - Hindari menyisipkan timestamp dinamis atau data berubah-ubah di baris pertama system prompt yang merusak cache prefix.
4. **Strict JSON Schema Enforcement**:
   - Paksa format JSON terstruktur via parameter `response_format: { type: "json_object" }` atau Native Function Calling Schema.
   - Berikan skema ringkas tanpa deskripsi bertele-tele pada property nama yang sudah self-explanatory.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang menyisipkan log error ratusan baris mentah tanpa pemangkasan stack trace yang relevan ke dalam prompt LLM.
- **PROHIBITION**: Dilarang mengubah urutan instruksi statis utama karena akan menggugurkan efektivitas prompt caching di sisi API.
- **EDGE CASE**: Output LLM terpotong di tengah jalan (finish_reason: "length"): perbesar `max_tokens` completion atau pecah tugas menjadi dua giliran (multi-step delegation).

## 4. Verification & Exit Code 0 Proof
- Token Count Verification: Script verifikasi tokenizer (`python -m tiktoken` atau test validator) memvalidasi token berada di bawah batas target budget.
- JSON Output Schema Validation: Skema respon JSON LLM berhasil diparsing tanpa syntax error oleh validator runtime (exit code 0).
- Latency & Cost Reduction Proof: Bukti empiris perbandingan jumlah token sebelum vs sesudah optimasi menunjukkan reduksi token minimal 20-40%.
