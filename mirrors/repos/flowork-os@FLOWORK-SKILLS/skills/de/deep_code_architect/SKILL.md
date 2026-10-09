---
name: deep_code_architect
description: Sovereign runbook for designing deep modules with small interfaces, locality, high leverage, and clean seams
keywords: ["deep code architect", "system architecture", "software design", "hexagonal architecture", "clean architecture", "domain driven design", "design patterns", "monolith decomposition", "dependency inversion", "modular boundaries", "interface segregation", "solid principles", "event driven architecture", "microservices design", "scalability patterns", "data layer separation", "cohesion and coupling", "architectural refactoring", "enterprise patterns", "system modeling"]
---
# 🎨 SKILL: DEEP CODE ARCHITECT & SEAM REDUCER
*Diadaptasi dari repositori dunia:* `mattpocock/skills/skills/engineering/codebase-design (278k★) & John Ousterhout`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk arsitektur kode mendalam (*deep modules*), antarmuka ramping, dan pemisahan seam yang kokoh:

## 1. HUKUM DEEP MODULE (SMALL INTERFACE + DEEP IMPLEMENTATION)
- **Deep vs Shallow**:
  - Modul ideal Flowork OS memiliki antarmuka publik yang kecil dan sederhana, namun menyembunyikan kompleksitas eksekusi yang matang di dalamnya.
  - Tolak *shallow module* (modul tipis di mana jumlah baris interface sama banyaknya dengan baris implementasi).

- **Prinsip Locality & Leverage**:
  - **Leverage**: Caller cukup memanggil 1 fungsi sederhana, implementasi mengeksekusi serangkaian validasi dan mekanisme rumit secara aman.
  - **Locality**: Bug dan modifikasi terkonsentrasi di satu modul, bukan merembes (*bleed*) ke seluruh file caller.

- **Nano-Modular Seam (20-80 Baris)**:
  - Batasi radius blast kesalahan: 1 file = 1 alur logika fokus.
  - Pisahkan adapter I/O (akses disk, IPC, shell) dari logika inti data transformasi.
