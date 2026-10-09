---
name: tool_forge
description: Sovereign runbook for designing, wrapping, and registering dynamic agent tools in Flowork OS
keywords: ["tool forge", "tool creation", "tool_maker", "custom tool building", "manifest generation", "cli tool scaffolding", "executable tool design", "agent tool registry", "dynamic tool binding", "json schema tool", "terminal tool runner", "input schema definition", "tool output formatting", "tool authorization", "sandboxed tool", "tool contract", "agent tool expansion", "reusable tool script", "tool validation", "edge tool integration"]
---
# ⚡ SKILL: TOOL FORGE (NATIVE AGENT TOOL MAKER)

Prosedur Operasi Standar (SOP) resmi pembuatan, pembungkusan, dan registrasi Native Agent Tool di ekosistem Flowork OS:

## 1. DOKTRIN TOOL FORGE
- **Just-In-Time (JIT) Dynamic Architecture**: Tool non-inti tidak dimuat permanen di memori utama. Semua tool baru harus mendukung mekanisme mount & unmount dinamis via `search_tools` gateway.
- **Contract-First Design**: Setiap tool wajib memiliki skema JSON Schema yang valid, deskripsi fungsi yang jelas, dan penamaan parameter yang deterministik.
- **Isolasi Lingkungan**: Seluruh skrip pembantu, helper binaries, atau artefak eksekusi wajib diletakkan di direktori isolasi `.FL_BIN/` atau subfolder tool bersangkutan.

## 2. STRUKTUR SPESIFIKASI TOOL
Setiap tool agen harus mendefinisikan kontrak:
1. `name`: Identifier unik huruf kecil bergaris bawah (`snake_case`), contoh: `custom_transcoder`.
2. `description`: Penjelasan padat mengenai apa yang dilakukan tool dan kapan agen harus memanggilnya.
3. `parameters`: Objek JSON Schema standar (tipe `object`, daftar `properties`, dan array `required`).
4. `handler`: Handler eksekusi yang menghasilkan output terstruktur (`exit_code`, data payload, atau error message terformat).

## 3. STANDAR MULTI-OS PADA TOOL
- Tool yang memanggil proses eksternal wajib mendeteksi OS runtime (Linux, Windows, macOS).
- Jangan memanggil executable dengan path absolut OS host. Gunakan penemuan dinamis via PATH atau relative bundle binary.
- Standar return status: Return `exit_code: 0` jika sukses, sertakan pesan diagnostik bahasa Inggris jika gagal.

## 4. VERIFIKASI & REGISTRASI
1. Buat purwarupa logika di `.FL_BIN/` atau paket tool.
2. Uji tool via runner terminal: pastikan return data bersih dan bebas unhandled promise/panic.
3. Daftarkan skema ke katalog tool Flowork OS.
4. Lakukan verifikasi mounting: uji panggil melalui `search_tools(action: 'mount', tools: ['nama_tool'])`.
