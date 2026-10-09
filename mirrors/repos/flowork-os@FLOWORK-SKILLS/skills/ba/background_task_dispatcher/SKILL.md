---
name: background_task_dispatcher
description: Sovereign runbook for dispatching, monitoring, and supervising long-running background tasks
keywords: ["background task", "task dispatcher", "manage_task", "daemon process", "async supervisor", "background job", "task worker", "process supervisor", "job queue", "detached process", "long running service", "task status", "kill task", "process monitoring", "async execution", "worker thread", "background polling", "task lifecycle", "subagent supervisor", "concurrency manager"]
---
# 🛠️ SKILL: BACKGROUND TASK DISPATCHER & ASYNC SUPERVISOR
*Diadaptasi untuk tool Flowork:* `manage_task` | *Referensi:* ECC Autonomous Loops & Worker Queue

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk memantau proses asinkron latar belakang.

## 1. DOKTRIN BACKGROUND PROCESS
- **Handoff Berdisiplin**: Tugas panjang (kompilasi biner, deep crawl, transcode) wajib dilempar ke background via manage_task atau async execution.
- **No Idle Polling**: Dilarang melakukan busy-wait loop di terminal; pantau sinyal event IPC secara efisien.
- **Graceful Termination**: Pastikan worker latar belakang menangani sinyal SIGTERM dengan bersih.
