---
name: agent_mesh_communicator
description: Sovereign runbook for peer-to-peer message routing and synchronization across active agent workers
keywords: ["agent mesh", "inter-agent communication", "send_message", "agent messaging", "peer communication", "worker synchronization", "agent bus", "agent coordination", "message routing", "distributed agents", "agent topology", "ipc messaging", "agent conversation", "agent handshake", "subagent sync", "agent mailbox", "asynchronous dispatch", "event bus", "agent protocol", "multi-agent networking"]
---
# 🛠️ SKILL: AGENT MESH COMMUNICATOR & INTER-AGENT IPC
*Diadaptasi untuk tool Flowork:* `send_message` | *Referensi:* ECC Agentic Engineering & Messages Ops

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk koordinasi pesan antar-agen.

## 1. DOKTRIN PERTUKARAN PESAN
- **High Signal Inter-Agent Payload**: Pesan antar-agen wajib berupa fakta terstruktur (JSON / ringkasan teknis padat), nol basa-basi.
- **Deadlock Defense**: Jangan buat komunikasi sirkular blocking antar dua agen aktif.
- **Event Acknowledgment**: Pastikan pesan konfirmasi tersampaikan.
