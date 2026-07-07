<!-- Generated companion to LONG_SKILL_SPLIT_PLAN.md. Source of truth is the
catalog generator; this file is hand-curated. Run `make catalog` and
re-run `python3 scripts/build-skill-status.py` (if installed) or copy the
output of the snippet in §1 to refresh. -->

# Long-Skill Status

This is the **operational status** companion to
[`LONG_SKILL_SPLIT_PLAN.md`](LONG_SKILL_SPLIT_PLAN.md) (the *plan*). The plan
said *split upstream, not in this repo*. This file tracks whether each
problem file has been *split*, *blocked on upstream*, or *intentionally
left as-is* (manual vendor snapshot). It also lists the lowest-hygiene
non-vendored skills so reviewers can see who is actually waiting for
attention.

The two-column [`SKILL_HYGIENE.md`](SKILL_HYGIENE.md) scorecard classifies each
skill on the structural column (form) and the eval column (depth). This
file adds the **operational** column (what is being done about it).

---

## 1. How to refresh this list

The repo's standard build does not write this file — the columns below
are *operational* judgments that change as maintainers act on them. To
regenerate the "blocked on upstream" list from the latest catalog:

```bash
# Lowest-hygiene skills
python3 -c "
import json
data = json.load(open('catalog/skills-enriched.json'))
for sk in sorted(data['skills'], key=lambda x: x['quality_score'])[:30]:
    eval_n = len(sk.get('eval_coverage', []))
    print(f'  {sk[\"quality_score\"]:3d}  lc={sk[\"line_count\"]:4d}  eval={eval_n}  {sk[\"path\"]}')"
```

The output of that one-liner as of the 2026-07-06 catalog is in §3.

---

## 2. Status legend

| Status | Meaning | Action |
|---|---|---|
| **🟢 Split** | Skill's upstream has been split into a lean spine + `references/` | Mirror should be re-vendored on the next sync. |
| **🟡 Blocked on upstream** | First-party auto-synced collection; we cannot edit the mirror without it being overwritten | Open an issue / PR in the upstream repo. |
| **🟠 Manual vendor snapshot** | Faithful third-party mirror; deliberately preserved | Do not restructure here. The right place is the *original* author's repo. |
| **⚪ Not long** | Short skill, nothing to do | — |
| **🟤 Evaluated, keep** | Reviewed; structural quirks are acceptable for this skill's role (e.g. pro-forma reference dump at end) | — |
| **🔴 Replace** | Quality / consistency so low the better fix is to drop the skill or replace it with a maintained alternative | Open a "Skill: replace" issue. |

---

## 3. Long / low-hygiene inventory (top 30 by lowest hygiene)

| Score | Lines | Evals | Path | Status (as of 2026-07-06) |
|---:|---:|---:|---|---|
| 57 | 304 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/scholar-evaluation/SKILL.md` | 🟠 Manual vendor snapshot — Diverga-like pattern, keep as-is. |
| 57 | 230 | 0 | `skills/28-maxwell2732-paper-replicate-agent-demo/dot-claude/skills/replicate-paper/SKILL.md` | 🟠 Manual vendor snapshot. |
| 57 | 181 | 0 | `skills/38-peternka-academic-proofreader/SKILL.md` | 🟠 Manual vendor snapshot. |
| 57 | 381 | 1 | `skills/40-py-econometrics-pyfixest/SKILL.md` | 🟠 Manual vendor snapshot (1 eval scenario — `statspai-rdd-diagnostics`). |
| 85 | 2256 | 15 | `skills/00-Full-empirical-analysis-skill_StatsPAI/SKILL.md` | 🟡 Blocked on upstream — first-party, weekly-synced. StatsPAI is the single highest-leverage split (15 eval scenarios ride on it). |
| 85 | 1215 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/citation-management/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 952 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/research-grants/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 981 | 0 | `skills/20-wenddymacro-python-econ-skill/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 923 | 0 | `skills/25-HosungYou-Diverga/skills/b1/SKILL.md` | 🟠 Manual vendor snapshot (Diverga family). |
| 85 | 1022 | 0 | `skills/25-HosungYou-Diverga/skills/c1/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1308 | 0 | `skills/25-HosungYou-Diverga/skills/c2/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 812 | 0 | `skills/25-HosungYou-Diverga/skills/c3/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1502 | 0 | `skills/25-HosungYou-Diverga/skills/d2/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1000 | 0 | `skills/25-HosungYou-Diverga/skills/d4/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1201 | 0 | `skills/25-HosungYou-Diverga/skills/e1/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 891 | 0 | `skills/25-HosungYou-Diverga/skills/e2/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 809 | 0 | `skills/25-HosungYou-Diverga/skills/memory/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 874 | 0 | `skills/26-Data-Wise-scholar/skills/writing/methods-paper-writer/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 832 | 0 | `skills/33-Galaxy-Dawn-claude-scholar/skills/uv-package-manager/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1097 | 0 | `skills/42-wanshuiyin-ARIS/skills/paper-poster/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1103 | 0 | `skills/42-wanshuiyin-ARIS/skills/skills-codex-gemini-review/paper-poster/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1097 | 0 | `skills/42-wanshuiyin-ARIS/skills/skills-codex/paper-poster/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 840 | 0 | `skills/55-ab604-claude-code-r-skills/skills/tdd-workflow/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 982 | 0 | `skills/63-tondevrel-scientific-agent-skills/dowhy/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 875 | 0 | `skills/67-econfin-workflow-toolkit/China-CF-study/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 1069 | 0 | `skills/67-econfin-workflow-toolkit/Foreign-CF-study/SKILL.md` | 🟠 Manual vendor snapshot. |
| 85 | 881 | 0 | `skills/67-econfin-workflow-toolkit/chinese-ppt/SKILL.md` | 🟠 Manual vendor snapshot. |
| 92 | 656 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/literature-review/SKILL.md` | 🟠 Manual vendor snapshot. |
| 92 | 582 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/peer-review/SKILL.md` | 🟠 Manual vendor snapshot. |
| 92 | 581 | 0 | `skills/04-K-Dense-AI-claude-scientific-writer/scientific-critical-thinking/SKILL.md` | 🟠 Manual vendor snapshot. |

> **Read this as a triage table.** A 🔴 / 🟡 row is an *action* the maintainer team has decided to take. A 🟠 row is **deliberately preserved** — do not "fix" these by editing in place. The repo's value here is faithful mirrors; rewriting them under our own authorship would defeat the provenance chain.

---

## 4. Single highest-leverage action: split StatsPAI upstream

Out of the 1,150 skills in the catalog, only one has both

1. A **first-party auto-synced upstream** we can change in one place, and
2. **>900 lines** of SKILL.md (line count 2256 — second only to a handful of large Diverga / ARIS / Galaxy-Dawn mirrors).

That is `skills/00-Full-empirical-analysis-skill_StatsPAI/SKILL.md`, which also happens to anchor **15 of 17 numeric-benchmark tasks** and one of the largest eval-coverage rows in `SKILL_HYGIENE.md`. Splitting it upstream into a lean spine + `references/` will:

- Halve the time-to-load for any agent that only needs the routing header
- Make the weekly sync diffs smaller and reviewable
- Free us to keep the mirror in this repo as a faithful copy

This is the **one** split the maintainer team should drive upstream. All other long skills in §3 are manual vendor snapshots, where the right action is an upstream issue, not an in-repo edit.

---

## 5. Cross-reference

- **Plan / why split?** → [`LONG_SKILL_SPLIT_PLAN.md`](LONG_SKILL_SPLIT_PLAN.md)
- **Scores by collection** → [`SKILL_HYGIENE.md`](SKILL_HYGIENE.md)
- **Eval coverage** → [`SKILL_HYGIENE.md`](SKILL_HYGIENE.md) (second column)
- **Tooling** → `python3 scripts/split-skill.py <path>` (read-only by default)
- **Skill structure conventions** → `docs/SKILL_SUBMISSION_GUIDE.md`
