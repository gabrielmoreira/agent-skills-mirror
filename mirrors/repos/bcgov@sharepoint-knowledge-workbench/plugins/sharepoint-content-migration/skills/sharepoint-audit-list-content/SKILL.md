---
name: sharepoint-audit-list-content
plugin: sharepoint-content-migration
status: active
description: >
  Audit list and library content fidelity between SP2016 On-Premises and SharePoint Online.
  Reconciles multi-value and single-value Person lookup columns against ground truth, detects Item ID
  vs Case ID suffix shifts/skews, flags dropped/missing pointers, and identifies false matches caused
  by string/name collisions. Use when verifying list content integrity, auditing ShareGate migrations,
  or preparing non-destructive lookup backfills.
allowed-tools: Bash, Read, Write
---

# SharePoint List Content Audit

Read-only content-level and lookup reconciliation auditing between SharePoint 2016 On-Premises source and SharePoint Online target.

## Overview
When SharePoint list items or target lookup parent lists (`Persons`) are re-migrated or ID-shifted, lookup pointers can drop (`$null`), point to stale integer IDs, or misbind to the wrong entity due to string-matching collisions.

`sharepoint-audit-list-content` uses a **Case-Keyed Ground Truth** model:
1. Indexes on-premises source data by **immutable natural business keys** (`Case_x0020_ID` / `Title`).
2. Translates source Person IDs into verified SPO target Person IDs via deterministic multi-attribute mapping (`id-mapping-verified.json`).
3. Compares **Expected Ground Truth** vs **Actual Live SPO State**.
4. Outputs zero-PII metrics and exports row-by-row variance reports for targeted in-place healing.

---

## Scripts & Tools
 
| Script | Type | Description |
| :--- | :--- | :--- |
| `scripts/export-persons-sp2016-to-csv.ps1` | PowerShell 7 | Prerequisite: exports SP2016 On-Prem Persons with natural assurance keys (CS Number, FPS, Name, DOB, Role, etc.) to `.agents/scratch/pii-data/persons-sp2016-onprem.csv`. |
| `scripts/export-persons-spo-to-csv.ps1` | PowerShell 7 | Prerequisite: exports live SPO PROD Persons with the same natural assurance keys to `.agents/scratch/pii-data/persons-spo-prod.csv`. |
| `scripts/analyze-persons-mapping-assurance.py` | Python 3 | Prerequisite: performs 4-tier deterministic matching (CS Number → FPS → strict Name+DOB → extended composite) between the two Persons exports, writing the zero-PII `id-mapping-verified.json` consumed by the analyzer below. Supports `--delete-pii-after` to purge the raw PII CSVs once the mapping is built. |
| `scripts/export-list-content-pairs.ps1` | PowerShell 7 | Discovery step: populates paired CSV datasets of current list content from SP2016 and SPO PROD into `.agents/scratch/pii-data/`, for downstream deep variance analysis. |
| `scripts/audit-list-lookup-reconciliation.ps1` | PowerShell 7 | Extracts SP2016 ground truth, queries live SPO, reconciles lookups, and computes Case ID suffix skew into `.agents/scratch/audit-reports/`. |
| `scripts/analyze-lookup-variances.py` (or `analyze-all-variances.py`) | Python 3 | Full-spectrum content, row, and lookup variance auditor generating zero-PII reports in `.agents/scratch/audit-reports/`. Cross-references `known-issues.json` to annotate report output with previously-documented root causes instead of re-analyzing them. |
| `scripts/check-list-id-suffix-skew.ps1` | PowerShell 7 | Standalone diagnostic measuring Item ID vs Case Number suffix shifts. |
| `scripts/backfill-itau-cases-person-lookups.ps1` | PowerShell 7 | High-speed, 2-phase batch healer for `ITAU_Cases` specifically: translates its 8 on-prem Person Lookup columns via `id-mapping-verified.json` and applies non-destructive in-place updates via PnP batching (100 cases per batch). Not generic — hardcoded to `ITAU_Cases`' field set. |
| `known-issues.json` | Data (JSON) | Persistent, version-controlled registry of previously root-caused parity issues (e.g. the Persons Item ID drift from a duplicate ShareGate redeploy) and their sanctioned remediation, so recurring findings are documented once and referenced going forward. |

---

## Usage Workflow — Two Phases

This skill is deliberately split into two phases that must both run, in order, every time:

- **Phase 1 (below)** is 100% deterministic script execution — no interpretation, no judgment calls. It only produces raw, zero-PII data tables (`SITE-FULL-CONTENT-PARITY-REPORT.md`, `site-full-content-parity-audit.csv`). It answers *"what differs"*, never *"why"* or *"does it matter"*.
- **Phase 2 (see section below)** is where Copilot reads the Phase 1 output and does the actual analysis — root-causing variances, flagging false positives, writing/adjusting one-off scratch scripts to dig into a specific column or list when the aggregate numbers alone aren't enough, and fixing bugs in the Phase 1 scripts themselves when the data proves the script (not the migration) is wrong. **Never treat Phase 1 numbers as the final word** — the report has been silently wrong before (see Known Issues Registry) and gets caught only by a human/Copilot actually reading it.

### Phase 1 — Deterministic Script Execution

#### Step 0. Build/Refresh the Persons ID Mapping (Prerequisite — only needed after a Persons re-migration)
Required whenever the SPO Persons list has been wiped/re-migrated (e.g. a ShareGate redeploy), which shifts Item IDs and invalidates the previous `id-mapping-verified.json`.
```powershell
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/export-persons-sp2016-to-csv.ps1 -UseDefaultCredentials
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/export-persons-spo-to-csv.ps1
python -B plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/analyze-persons-mapping-assurance.py --delete-pii-after
```

#### Step 1. Export Fresh Paired List Content (SP2016 + SPO)
```powershell
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/export-list-content-pairs.ps1 -UseDefaultCredentials
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/audit-list-lookup-reconciliation.ps1 -UseDefaultCredentials
```

#### Step 2. Generate the Zero-PII Executive Data Tables
```powershell
python -B plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/analyze-lookup-variances.py --list-name ALL
```
**⚠️ Always pass `--list-name ALL` explicitly for the real run.** If you smoke-test a single list (e.g. `--list-name CMATConfig`), you MUST also override `--output-md`/`--output-csv` to a scratch path — otherwise the default output paths silently overwrite (thin out) the canonical site-wide report. This exact failure happened once already; do not repeat it.

This step produces only raw tables: per-list parity %, root-cause category counts, and per-lookup-column pointer health. It does **not** produce a narrative/root-cause writeup — that is Phase 2.

### Phase 2 — Copilot-Assisted Interpretive Analysis (required after every Phase 1 run)

Phase 1's `SITE-FULL-CONTENT-PARITY-REPORT.md` is intentionally "thin" — it is data, not analysis. The "meat" (why a gap exists, whether it's a real defect vs. a false positive, whether it needs a backfill script) lives in a **separate, Copilot-authored narrative document**: `.agents/scratch/audit-reports/CMAT-COMPREHENSIVE-LIST-BY-LIST-VARIANCE-ANALYSIS.md`. After every Phase 1 run, Copilot must refresh this document (not just leave a stale one-off from a prior session) with at minimum these sections:

1. **Column / Schema Metadata Variance Summary** — which columns were renamed, excluded, or restructured between SP2016 and SPO for each list (sourced from the wave matrix / field renames, not just row-level diffs).
2. **Absolute 100% Match List Roster** — the lists with zero real variance (source rows == co-existing rows == perfect rows). Call out any list where Phase 1's "100.0%" is misleading because `Co-Existing` rows are far below `Source Rows` (i.e. rows missing entirely from SPO are excluded from the Parity Rate denominator — this is a confirmed blind spot, see Known Issues).
3. **Lists With Real Variances — Breakdown** — for every list below 100%, the actual top differing columns with counts, tallied from `site-full-content-parity-audit.csv` (not just the truncated "Top Differing Columns" preview column in the executive table), and a call on whether each is a false positive (cosmetic/expected) or a real gap.
4. **Consolidated Lookup Column Gap Analysis (site-wide, single section)** — one master table of every lookup column across every list (not split list-by-list like the Phase 1 report), each row showing total pointers, % matched, % blank/stale, and root cause, sorted so the biggest real gaps are at the top. This is the section most likely to surface script bugs (see Known Issues — the `Related_to_ITAU_Case`/`Related_to_PIO_Case` bug was only found by scrutinizing this exact table).
5. **Known Script Bugs Found This Pass** — anything discovered where the Phase 1 script itself is wrong (bad column-name guess, stale duplicate lookup definitions, misleading metric), with the fix applied and confirmed by re-running Phase 1.

Use targeted scratch PowerShell/Python (in `.agents/scratch/`) to investigate any specific number that looks suspicious (e.g. compare a raw CSV header against the script's hardcoded column-name guess) — never rely on the aggregate report alone if a number looks off (a `0 Source Pointers in Dataset` row is a signal to check the script, not a real finding).

Findings that are root-caused during Phase 2 and are expected to recur on future runs should be added to `known-issues.json` (see below) so Phase 2 doesn't have to re-derive them from scratch every time.

### Phase 3 — Heal Variances & Dropped Pointers In-Place (Non-Destructive, ITAU_Cases only)
Only run after Phase 2 has confirmed a gap is real (not a script bug or false positive).
```powershell
# Dry run preview first
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/backfill-itau-cases-person-lookups.ps1 -UseDefaultCredentials -Limit 5 -DryRun

# Full execution
pwsh -File plugins/sharepoint-content-migration/skills/sharepoint-audit-list-content/scripts/backfill-itau-cases-person-lookups.ps1 -UseDefaultCredentials
```

---

## Known Issues Registry

`known-issues.json` (in this skill folder) is a persistent, version-controlled log of parity issues that have already been root-caused in Phase 2, so future Phase 2 passes don't re-derive the same explanation from scratch. Each entry documents the affected list(s)/column(s), the observable symptom signature, the confirmed root cause, current status (resolved / accepted-gap / needs-backfill), and the sanctioned remediation.

Add a new entry here whenever Phase 2 confirms a fresh root cause for a recurring variance, instead of leaving the explanation only in a one-off analysis doc that can go stale.
