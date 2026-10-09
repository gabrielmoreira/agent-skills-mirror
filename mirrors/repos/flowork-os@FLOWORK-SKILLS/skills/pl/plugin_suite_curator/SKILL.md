---
name: plugin_suite_curator
description: Sovereign runbook for managing Canvas UI tabs, plugin lifecycles, and edge CDN installations
keywords: ["plugin curator", "plugin catalog", "plugin discovery", "plugin marketplace", "plugin installation", "plugin registry", "suite curation", "plugin ecosystem", "official plugins", "dependency resolution", "plugin updates", "remote registry", "community plugins", "category grouping", "plugin search", "version compatibility", "plugin vetting", "plugin repository", "plugin manager", "edge cdn install"]
---
# 🛠️ SKILL: PLUGIN SUITE CURATOR & CANVAS LIFECYCLE
*Diadaptasi untuk tool Flowork:* `plugin_control` | *Referensi:* ECC Agentic OS & Plugin Management

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk kontrol daur hidup plugin Canvas UI.

## 1. DOKTRIN SIKLUS HIDUP PLUGIN
- **Luncurkan Bersih**: Buka plugin via plugin_control(action: "open", plugin_id: "<id>") dan pantau event bootstrap.
- **Zero-Waste Tabs**: Tutup plugin yang tidak lagi digunakan via plugin_control(action: "close") untuk menghemat memori.
- **CDN Remote Search**: Selalu cari plugin resmi via action: "search_remote" sebelum membangun dari nol.
