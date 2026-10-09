---
name: system_vitals_auditor
description: Sovereign runbook for inspecting host metrics, RAM/CPU load, disk capacity, and listening network ports
keywords: ["system vitals", "health check", "memory usage", "disk space", "process monitor", "system diagnostics", "resource consumption", "vitals audit", "cpu utilization", "filesystem capacity", "zombie process detection", "open file descriptors", "load average", "hardware metrics", "system triage", "resource bottleneck", "system stability", "process lifecycle audit", "system alerts", "runtime health telemetry"]
---
# 🛠️ SKILL: SYSTEM VITALS AUDITOR & RESOURCE DIAGNOSTICIAN
*Diadaptasi untuk tool Flowork:* `sys_health` | *Referensi:* ECC Network Interface Health & Host Diagnostics

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk memantau kesehatan host dan sumber daya sistem.

## 1. DOKTRIN DIAGNOSTIK KESEHATAN
- **Deteksi Bottleneck**: Periksa beban RAM dan CPU sebelum menjalankan proses berat (seperti build Go/Rust atau kompresi video).
- **Konflik Port**: Gunakan sys_health untuk memastikan tidak ada zombie process yang menahan port FLOWORK_APP_PORT.
- **Lapor Objektif**: Paparkan statistik metrik apa adanya tanpa spekulasi.
