---
name: plugin_architect
description: Sovereign runbook for creating, modifying, and refactoring Flowork OS plugins
keywords: ["plugin architect", "manifest.json", "canvas plugin", "plugin development", "micro frontend", "1-file-1-logic", "modular plugin", "plugin lifecycle", "plugin api", "canvas iframe", "plugin ipc", "plugin state management", "plugin configuration", "plugin scaffold", "portable plugin", "plugin ui", "plugin package", "plugin loader", "plugin manifest validation", "plugin distribution"]
---
# 🔌 SKILL: FLOWORK OS PLUGIN ARCHITECT

SOP resmi pembuatan dan refaktorisasi plugin Flowork OS / X-Flow:
1. **PANDUAN UTAMA**: Baca dan patuhi berkas [`plugins/FLOW_SKILL.MD`](file:///home/mrflow/Music/flowork/xflow/plugins/FLOW_SKILL.MD).
2. **KONTRAK MANIFEST**: Setiap plugin wajib memiliki `plugin.manifest.json` yang valid (id, name, version, category, backend entry, frontend index).
3. **PORT DINAMIS**: Backend (Node.js, Python, Rust, Go) wajib mendengarkan pada `process.env.FLOWORK_APP_PORT || process.env.PORT`. Dilarang hardcode port statis.
4. **NANO-MODULAR**: Kode backend dan frontend wajib menerapkan 1 file 1 fungsi (20-80 baris) untuk membatasi efek domino.
5. **ZERO-ZOMBIE**: Proses backend wajib keluar bersih saat menerima sinyal SIGTERM atau SIGKILL.
