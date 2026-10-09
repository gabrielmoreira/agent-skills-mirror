---
name: git_conflict_resolver
description: Sovereign runbook for multi-branch git merge conflict resolution, interactive rebase, git bisect regression hunting, and tree integrity
keywords: ["git conflict", "merge conflict resolution", "git rebase interactive", "git bisect", "tree integrity", "three way merge", "git cherry pick", "conflict markers", "head resolution", "git stash pop", "working tree status", "git log graph", "commit reordering", "fast forward merge", "merge strategy recursive", "git diff check", "clean commit history", "rebase abort safe", "git checkout ours theirs", "vcs conflict recovery"]
---
# 🔀 SKILL: GIT CONFLICT RESOLVER

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk resolusi konflik branch Git, interactive rebase, dan pelacakan regresi:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Terjadinya merge conflict pada branch, sinkronisasi pull upstream, rebase multi-commit, atau pelacakan commit penyebab bug.
- **Batasan**: Mempertahankan integritas commit history, clean working tree, dan zero-regression pasca-merge.

## 2. Standard Operating Procedures (SOP)
1. **Inspeksi Status Konflik & Marker 3-Way**:
   - Jalankan `git status` untuk memetakan seluruh berkas dalam status `both modified` / unmerged paths.
   - Analisis blok konflik yang ditandai dengan `<<<<<<< HEAD`, `=======`, dan `>>>>>>> branch_name`.
2. **Surgical Conflict Resolution**:
   - Pahami intensi kode dari kedua sisi (incoming vs current change). Jangan menghapus kode penting secara serampangan.
   - Satukan logika secara harmonis atau pilih opsi tegas jika salah satu versi adalah superceding (`--ours` / `--theirs`).
   - Bersihkan seluruh karakter conflict markers dari file target.
3. **Interactive Rebase & Squash**:
   - Gunakan `git rebase -i` untuk merapikan commit history kotor/eksperimental sebelum merger ke branch utama.
   - Pertahankan pesan commit bermakna (Conventional Commits) dan sertakan `Co-authored-by: Flowork OS <agent@floworkos.com>`.
4. **Automated Regression Hunting (Git Bisect)**:
   - Gunakan `git bisect start`, `git bisect bad`, dan `git bisect good <commit_lama>` bersama skrip otomatis `git bisect run <skrip_test>` untuk mengisolasi commit pemecah sistem.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menyisakan conflict marker di codebase yang dapat menyebabkan syntax error.
- **Dilarang**: Menggunakan `git push --force` pada branch bersama/utama tanpa koordinasi.

## 4. Verification & Exit Code 0 Proof
- Jalankan test suite proyek pasca-resolusi konflik.
- Pastikan build dan test lolos verifikasi sempurna (Exit Code 0).
