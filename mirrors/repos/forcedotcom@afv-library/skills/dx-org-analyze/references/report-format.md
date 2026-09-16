# Report Format

The `scripts/compute_diff.py` script computes the diff between two collected org data sets.

## Usage

```bash
python3 ./scripts/compute_diff.py \
  --org-a /tmp/source \
  --org-b /tmp/target \
  --output /tmp/org-diff \
  --format both \
  --org-a-label "Source" \
  --org-b-label "Target"
```

| Flag | Purpose |
|------|---------|
| `--org-a` | Path to org A data directory or JSON file (required) |
| `--org-b` | Path to org B data directory or JSON file (required) |
| `--output` | Output path prefix (required) |
| `--format` | `markdown`, `json`, or `both` (default: `both`) |
| `--org-a-label` | Display name for org A (default: "Source") |
| `--org-b-label` | Display name for org B (default: "Target") |
| `--show-shared` | Include shared components in the detailed breakdown |

## Drift Score Formula

```text
Overall = 60% × Metadata Drift + 30% × Permission Drift + 10% × Profile Drift
```

| Range | Level | Meaning |
|-------|-------|---------|
| 0–10% | LOW | Nearly identical orgs |
| 11–30% | MODERATE | Some features differ |
| 31–60% | HIGH | Significant divergence |
| 61–100% | CRITICAL | Fundamentally different orgs |

## Report Sections

1. **Header** — Org IDs, names, editions, discovery method
2. **Drift Score** — Overall weighted score with per-dimension breakdown
3. **Summary Statistics** — Table with per-type counts (A count, B count, Shared, A Only, B Only, Identical, Different)
4. **Key Metrics** — Total unique components, percentages, permission/package summary
5. **Metadata Components by Type** — Detailed per-type listing of only-in-A, only-in-B names
6. **Profiles** — Shared, A-only, B-only profile names
7. **Installed Packages** — A-only, B-only, version mismatches, identical packages
8. **Package Components** — Namespaced components grouped by namespace with per-type breakdown
9. **Org Permissions** — Enabled/disabled diffs categorized (Commerce, Platform/API, Security, Einstein/AI, Service, Data, Sales, etc.), plus non-boolean value diffs
10. **System Permissions** — PermissionsXxx per PermissionSet diffs, aggregate unique permissions
11. **Org Values & Limits** — Categorized (Identity, Storage, Feature Limits, API) value differences
12. **Deep Diff** — Apex body/API version/LOC diffs, custom field type changes, validation rule active state, flow process type, object/field permissions, named credentials
13. **Licenses** — User, Permission Set, Package license quantity diffs
14. **Notes** — Read-only disclaimer, collection warnings

## Deep Data Enrichment

The diff script enriches the summary statistics table with content-level information from deep data. The Identical/Different columns reflect actual body hash, API version, and active state comparisons — not just name-level overlap.

Enrichment mapping:
- `ApexClass` → body hash + API version + LOC
- `ApexTrigger` → body hash
- `Flow` → process type + API version
- `ValidationRule` → active state
- `CustomObject` → custom field set differences
- `NamedCredential` → endpoint URL
