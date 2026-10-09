---
name: swarm_orchestrator
description: Sovereign runbook for multi-agent delegation, role coordination, consensus protocol, and artifact aggregation
keywords: ["swarm orchestrator", "coordinator agent", "workflow orchestration", "multi-agent pipeline", "subagent coordination", "swarm pipeline", "task federation", "master agent logic", "agent dependency graph", "choreography vs orchestration", "agent feedback loop", "multi-step swarm", "subagent aggregation", "consensus synthesis", "swarm execution plan", "orchestration engine", "agent mesh routing", "distributed task queue", "subagent error handling", "end-to-end swarm flow"]
---
# 🐝 SKILL: SWARM ORCHESTRATOR (MULTI-AGENT WEAVER)

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk orkestrasi kolaborasi multi-agen, delegasi tugas otonom, dan penyatuan artefak sistem:

## 1. DOKTRIN MULTI-AGEN FLOWORK
- **Spesialisasi Berdaulat**: Setiap sub-agen diberikan persona, peran, dan lingkup instruksi yang fokus (Single Responsibility Task). Hindari memberikan prompt umum tanpa batas tugas yang jelas.
- **Isolasi Konteks & Hemat Token**: Sub-agen berjalan pada konteks terisolasi. Hanya serahkan ringkasan konteks atau file path yang relevan, jangan menduplikasi seluruh histori chat.
- **Agregasi Deterministik**: Agen utama (Master Weaver) bertanggung jawab menguji, memvalidasi sintaksis, dan mengintegrasikan seluruh output sub-agen sebelum melaporkan status selesai ke User.

## 2. POLA DISTRIBUSI PERAN (SUB-AGENT MATRIX)
1. **Architect / Planner**: Merancang struktur berkas, spesifikasi API, dan kontrak JSON Schema.
2. **Implementer / Coder**: Menulis kode nano-modular (1 file 1 logika, 20-80 baris) berdasarkan spesifikasi arsitek.
3. **Tester / Security Auditor**: Menguji eksekusi runtime terminal (Exit Code 0) dan memindai celah keamanan kode.
4. **Docs / Chronicler**: Mencatat keputusan arsitektur ke `.fl_brain/decisions.md` dan `FLOW_MIND.MD`.

## 3. PROSEDUR DELEGASI & EKSEKUSI
1. Identifikasi subtugas yang dapat diparalelkan atau memerlukan spesialisasi mendalam.
2. Definisikan payload `Subagents` pada tool `invoke_subagent` / mekanisme dispatch:
   - `Role`: Penjelasan peran padat (2-5 kata).
   - `TypeName`: Tipe agen yang sesuai peran.
   - `Prompt`: Instruksi terperinci, batasan tugas, dan target output yang diharapkan.
3. Monitor eksekusi sub-agen hingga seluruh proses background menyelesaikan pekerjaannya.
4. Periksa hasil kerja fisik di workspace. Uji keutuhan kode secara empiris di terminal.
