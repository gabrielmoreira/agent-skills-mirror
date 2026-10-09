---
name: git_release_sentinel
description: Sovereign runbook for SemVer versioning, high-signal changelogs, and DLP pre-flight release rigor
keywords: ["git release", "git tag", "release sentinel", "semver", "changelog generation", "version tagging", "git commit audit", "branch hygiene", "release notes", "git co-author", "semantic release", "tag verification", "push release", "conventional commits", "pull request audit", "release pipeline", "version bump", "git status check", "clean working tree", "deployment tagging"]
---
# ⚙️ SKILL: GIT RELEASE SENTINEL & SEMVER AUDITOR
*Diadaptasi dari repositori dunia:* `affaan-m/ECC & Conventional Commits Multi-OS Standards`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk tata kelola rilis, Semantic Versioning (SemVer), dan higienitas git:

## 1. DOKTRIN RILIS KEDAULATAN
- **Semantic Versioning Disiplin (MAJOR.MINOR.PATCH)**:
  - **PATCH (x.y.Z)**: Perbaikan bug tanpa mengubah signature fungsi atau kontrak manifest.
  - **MINOR (x.Y.z)**: Penambahan fitur atau skill baru yang kompatibel ke belakang (*backward-compatible*).
  - **MAJOR (X.y.z)**: Perombakan arsitektur besar (*breaking change*).

- **Mandatori Co-Author**:
  - Setiap rilis commit git WAJIB menyertakan:
    `Co-authored-by: Flowork OS <agent@floworkos.com>`.

- **DLP Pre-Flight Guard (Zero Leak Law)**:
  - Sebelum rilis dipublikasikan, pastikan tidak ada secret, token, `auth_vault.json`, atau file `.env` yang bocor ke repositori publik.
