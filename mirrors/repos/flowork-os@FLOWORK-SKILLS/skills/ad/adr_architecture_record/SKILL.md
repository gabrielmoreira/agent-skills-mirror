---
name: adr_architecture_record
description: Sovereign runbook for documenting architectural decisions, sync FL_MIND.MD, and preventing architectural drift
keywords: ["adr", "architecture decision record", "architectural decisions", "decision log", "system design record", "technical debt record", "design rationale", "architecture history", "fl_mind sync", "architecture drift", "software design document", "rfc proposal", "engineering decision", "system blueprint", "tech stack rationale", "tradeoff analysis", "design pattern selection", "legacy migration record", "consequence evaluation", "architectural governance"]
---
# ⚙️ SKILL: ADR ARCHITECTURE RECORD & SACRED SYNC
*Diadaptasi dari repositori dunia:* `affaan-m/ECC/skills/architecture-decision-records (274k★) & Michael Nygard Standard`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pencatatan keputusan arsitektur, pemetaan nalar, dan sinkronisasi hierarki:

## 1. DOKTRIN KEPUTUSAN ARSITEKTUR (ADR RIGOR)
- **Struktur Baku Dokumen Keputusan**:
  - **Context**: Masalah teknis dan kendala sistem yang melatarbelakangi.
  - **Decision**: Pilihan arsitektur yang diambil (library, pola antarmuka, protokol).
  - **Consequences**: Dampak positif, trade-off, dan mitigasi kelemahan.

- **Sinkronisasi Otomatis ke Dokumen Kedaulatan**:
  - Setiap keputusan desain besar WAJIB disinkronkan ke `.fl_brain/decisions.md` dan `FL_MIND.MD` pada workspace aktif.
  - Mencegah *architectural drift* (deviasi kode dari cetak biru yang telah disetujui Sovereign Master).
