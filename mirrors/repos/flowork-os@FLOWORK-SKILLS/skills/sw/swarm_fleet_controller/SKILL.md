---
name: swarm_fleet_controller
description: Sovereign runbook for monitoring, cancelling, and reconciling multi-agent concurrent swarms
keywords: ["swarm fleet", "fleet controller", "parallel subagents", "multi-agent swarm", "worker fleet", "distributed subagents", "swarm topology", "agent concurrency", "fleet monitoring", "agent health status", "swarm lifecycle", "multi-agent scaling", "worker pool management", "fleet supervisor", "inter-subagent bus", "swarm rate limiting", "collective intelligence", "agent heartbeat", "fleet kill switch", "swarm consensus"]
---
# 🛠️ SKILL: SWARM FLEET CONTROLLER & WORKER SUPERVISOR
*Diadaptasi untuk tool Flowork:* `manage_subagents` | *Referensi:* Superpowers Dispatching Parallel Agents

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk mengawasi armada subagen yang berjalan paralel.

## 1. DOKTRIN PENGAWASAN SWARM
- **Concurrency Rigor**: Batasi armada subagen aktif agar tidak menghabiskan kuota thread atau resource sistem.
- **Circuit Breaker Armada**: Batalkan subagen yang macet atau mengalami infinite loop via manage_subagents(action: "cancel").
- **Konsensus Output**: Rekonsiliasi hasil pekerjaan subagen ke status terverifikasi.
