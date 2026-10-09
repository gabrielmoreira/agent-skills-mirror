---
name: hot_reload_supervisor
description: Sovereign runbook for autonomous engine hot-restarts, state checkpointing, and zero-downtime conversation recovery
keywords: ["hot reload", "live reload", "dev server watch", "auto reload", "file watcher", "instant feedback loop", "hot module replacement", "hmr supervisor", "vite watch", "browser auto refresh", "inotify polling", "asset rebundling", "dev environment", "fast refresh", "incremental build", "live server", "change detection", "rapid iteration", "css injection", "zero restart workflow"]
---
# 🛠️ SKILL: HOT RELOAD SUPERVISOR & ZERO-DOWNTIME RESTART
*Diadaptasi untuk tool Flowork:* `system_restart` | *Referensi:* ECC Canary Watch & System Lifecycle

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk me-restart biner Flowork secara mandiri tanpa kehilangan konteks percakapan.

## 1. DOKTRIN HOT-RELOAD
- **Simpan Status Terlebih Dahulu (Checkpoint State)**: Sebelum memanggil system_restart, selalu simpan keputusan dan state aktif ke .fl_brain/.
- **Zero-Downtime Session**: Biner Flowork memiliki mekanisme auto-resume chat. Jangan panik saat socket terputus sesaat.
- **Validasi Pasca-Restart**: Pastikan engine kembali melayani request dengan exit code 0.
