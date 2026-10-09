---
name: cron_cadence_operator
description: Sovereign runbook for precision cron jobs, timer scheduling, and non-blocking recurring workflows
keywords: ["cron operator", "scheduled jobs", "schedule", "cadence", "recurring task", "cron syntax", "interval execution", "timer daemon", "periodic triggers", "job scheduler", "heartbeat monitor", "time based dispatch", "one shot timer", "cron workflow", "scheduled backup", "polling interval", "automation cadence", "temporal scheduling", "calendar trigger", "cron lifecycle"]
---
# 🛠️ SKILL: CRON CADENCE OPERATOR & RECURRING SCHEDULER
*Diadaptasi untuk tool Flowork:* `schedule` | *Referensi:* ECC Automation Audit Ops & Scheduler

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk menjadwalkan timer dan tugas recurring periodik.

## 1. DOKTRIN PENJADWALAN
- **Non-Blocking Cadence**: Jadwal waktu tidak boleh memblokir thread eksekusi utama.
- **Idempotent Actions**: Setiap tugas recurring yang dijadwalkan via schedule wajib bersifat idempotent (aman dijalankan berkali-kali).
- **Cleanup Cadence**: Hapus timer kadaluarsa saat proses telah selesai.
