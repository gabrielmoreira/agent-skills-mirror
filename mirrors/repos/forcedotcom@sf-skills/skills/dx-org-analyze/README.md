# dx-org-analyze

Compare two Salesforce orgs and produce a comprehensive comparison report covering metadata, permissions, org settings, limits, profiles, installed packages, licenses, system permissions, and content-level code differences. Also supports single-org analysis via introspect mode.

## Prerequisites

- **Salesforce CLI** (`sf`) installed and authenticated to both orgs
- Admin-level access on both orgs (needed for Tooling API queries)
- Both orgs authenticated via `sf org login web` or `sf org login jwt`
- Python 3.10+

## Getting Started

### 1. Authenticate your orgs

```bash
# Authenticate via browser (interactive — most common)
sf org login web --alias my-dev-org
sf org login web --alias my-prod-org

# Via JWT for CI/automation
sf org login jwt --alias my-org --client-id <ID> --jwt-key-file <key> --username <user>

# Via access token (for orgs that don't support the standard connected app)
sf org login access-token --instance-url https://myorg.my.salesforce.com --alias my-org
```

### 2. Verify connectivity

```bash
sf org list   # Shows all authenticated orgs
```

### 3. Run a comparison (two orgs)

Invoke the skill and follow the prompts — it will show your authenticated orgs and ask you to pick a source and target.

```yaml
Skill: dx-org-analyze
Request: "Compare my sandbox against production"
```

### 4. Run an analysis (single org)

For a single-org analysis, invoke the skill with one org. It will collect data and produce an Org Analysis Report covering metadata inventory, org settings, limits, packages, licenses, system permissions, and deep data.

```yaml
Skill: dx-org-analyze
Request: "Introspect my production org"
```

## How It Works

### Comparison (two orgs)

1. **List authenticated orgs** — Shows orgs from `sf org list`
2. **Select source and target** — Source is the reference; target is compared against it
3. **Collect data** — Queries metadata via SF CLI and Tooling API, org settings, limits, packages, licenses, system permissions, and deep data (per org, in parallel)
4. **Compute differences** — Set comparisons, field-level diffs, body-hash diffs, CRUD permission diffs, metadata enrichment with content-level differences
5. **Generate Org Comparison Report** — Drift Score → Summary Statistics → Detailed Differences → Package Components → Permissions → Org Values & Limits → Licenses → Deep Data

### Analysis (single org)

1. **Validate connectivity** — Confirms the org is reachable
2. **Collect data** — Same collection as comparison mode, but for one org
3. **Generate Org Analysis Report** — Metadata Inventory → Installed Packages → Org Settings → Org Limits → Licenses → System Permissions → Deep Data

## Report Structure

### Org Comparison Report (two orgs)

1. **Drift Score** — Overall weighted score (0–100%) with severity level
2. **Summary Statistics** — Counts per metadata type (with Identical and Different columns enriched from deep data)
3. **Metadata Components by Type** — Full breakdown of only-in-A, only-in-B, shared per type
4. **Profiles** — Shared, source-only, target-only profiles
5. **Installed Packages** — Version comparison, only-in-A, only-in-B
6. **Package Components** — Namespaced components grouped by namespace; non-namespaced packages flagged separately
7. **Org Permissions** — Boolean enabled/disabled diffs by category, plus non-boolean value diffs
8. **System Permissions** — PermissionsXxx fields on PermissionSet, per-set diffs
9. **Org Values & Limits** — Grouped by Identity, Storage, API, Feature Limits, Other
10. **Licenses** — User licenses, permission set licenses, package licenses with quantity diffs
11. **Deep Data** — Content-level diffs for Apex, Flows, Validation Rules, Custom Fields, etc.

### Org Analysis Report (single org)

1. **Summary** — Org identity, edition, metadata type and component counts
2. **Metadata Inventory** — Component counts per metadata type, org-native vs namespaced
3. **Installed Packages** — Package name, namespace, version
4. **Org Settings** — Enabled/disabled/non-boolean settings grouped by category
5. **Org Limits** — API, storage, feature limits grouped by category
6. **Licenses** — User licenses, permission set licenses, package licenses with usage counts
7. **System Permissions** — Permission sets and their enabled PermissionsXxx fields
8. **Deep Data** — Record counts for Apex classes, flows, custom fields, validation rules, etc.
9. **Collection Warnings** — Any non-fatal issues encountered during data collection

### Drift Score Formula

```text
Overall = 60% × Metadata Drift + 30% × Permission Drift + 10% × Profile Drift
```

| Range | Level | Meaning |
|-------|-------|---------|
| 0–10% | LOW | Nearly identical orgs |
| 11–30% | MODERATE | Some features differ |
| 31–60% | HIGH | Significant divergence |
| 61–100% | CRITICAL | Fundamentally different orgs |

## What's Compared

### Metadata (Name-Level)

All types discovered via `sf org list metadata-types` (typically 100+ types).
Falls back to Tooling API queries if CLI metadata commands are unavailable.
Namespaced (managed-package) components are excluded from the summary table and listed separately under Package Components.

### Deep Data (Content-Level via Tooling API)

| Category | Comparison Depth |
|----------|-----------------|
| Apex Classes | Body hash, API version, LOC, status for shared classes |
| Apex Triggers | Body hash comparison for shared triggers |
| Custom Fields | Per-object field sets + length/precision/scale changes |
| Validation Rules | Active/inactive state differences + per-org-only rules |
| Flows | MasterLabel, process type, API version, status |
| Named Credentials | Endpoint URL comparison |
| Connected Apps | DeveloperName presence comparison |
| Custom Metadata Types | Presence comparison |

Deep data differences are mapped back to the summary statistics table via metadata enrichment, so the Identical/Different columns reflect actual content-level changes, not just name-level overlap.

### Org-Level

| Category | Source | Depth |
|----------|--------|-------|
| Org Settings | Tooling API `OrganizationSettingsDetail` (fallback: `SecurityHealthCheckRisks`) | Enabled/disabled feature comparison + non-boolean value diffs |
| Org Limits | REST `/limits/` endpoint | Max values for API, storage, features |
| Profiles | Tooling API | Name-level (shared/Source-only/Target-only) |
| System Permissions | Tooling API `PermissionSet` | PermissionsXxx field comparison per permission set |
| Installed Packages | Tooling API `InstalledSubscriberPackage` | Name + namespace + version comparison |
| Package Components | Metadata listing | Namespaced components grouped by namespace |
| Licenses | SOQL | User, Permission Set, and Package license counts |

## Scripts

### `collect_org_data.py`

Collects all data from a single org into a **split directory** with per-category JSON files.

```bash
python3 ./scripts/collect_org_data.py \
  --org-alias my-dev-org \
  --output /tmp/org-data
```

| Flag | Purpose |
|------|---------|
| `--org-alias` | SF CLI alias or username for the org (required) |
| `--output` | Output directory path (required) |
| `--skip-deep-data` | Skip Tooling API content-level queries (faster, less detail) |

**Output directory structure:**

```text
/tmp/org-data/
  manifest.json            # Lists category files
  identity.json            # Org ID, name, edition, errors
  metadata.json            # Metadata types and components
  permissions.json         # Org settings (OrganizationSettingsDetail)
  org_values.json          # Org limits
  packages.json            # Installed packages
  licenses.json            # User, PSL, and package licenses
  system_permissions.json  # PermissionsXxx on PermissionSet
  deep_data.json           # Apex bodies, Flow state, etc.
  combined.json            # All-in-one (backward compatibility)
```

Split files enable parallel agent access — each agent loads only the section it needs.

**SOQL pagination:** Queries returning >2000 records are automatically paginated via `nextRecordsUrl`.

**Parallelized collection:** Metadata listing uses 12 workers, deep data queries use 8 workers via `ThreadPoolExecutor`.

Exit codes: `0` success, `1` fatal error, `2` session expired (re-auth and retry).

### `compute_diff.py`

Computes the comparison between two collected org data sets.
Accepts either a split directory or a single JSON file for each org.

```bash
python3 ./scripts/compute_diff.py \
  --org-a /tmp/source \
  --org-b /tmp/target \
  --output /tmp/org-comparison \
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
| `--org-a-label` | Display name for org A in the report (default: "Source") |
| `--org-b-label` | Display name for org B in the report (default: "Target") |
| `--show-shared` | Include shared components in the detailed breakdown |

Outputs `<prefix>.json` (structured data) and `<prefix>.md` (formatted report).

### `introspect_org.py`

Generates a single-org introspection report from a previously collected org data directory (output of `collect_org_data.py`). Covers metadata inventory, org settings, org limits, installed packages, licenses, system permissions, and deep data.

```bash
python3 ./scripts/introspect_org.py \
  --org /tmp/org-data \
  --output /tmp/report \
  --format both \
  --label "My Production Org"
```

| Flag | Purpose |
|------|---------|
| `--org` | Path to collected org data directory or JSON file (required) |
| `--output` | Output path prefix (required) |
| `--format` | `markdown`, `json`, or `both` (default: `both`) |
| `--label` | Display name for the org in the report (default: org alias or directory name) |

Outputs `<prefix>.json` (structured data) and/or `<prefix>.md` (formatted report) depending on `--format`.

## Security

- **Read-only** — Never deploys, modifies, or deletes anything in either org.
- **SF CLI auth only** — All authentication through SF CLI. No raw credentials, session IDs, or access tokens accepted.

## Use Cases

### Compare sandbox against production

Ensure sandbox is in sync before deploying changes.

### Audit org configuration drift

Detect unexpected changes between environments.

### Compare dev org against customer org

Identify what metadata/configuration your package adds or modifies.

### Analyze a single org

Inventory all metadata, settings, permissions, packages, and licenses in an org before making changes or onboarding a new environment.

## Known Limitations

- Deep data body queries may timeout on large orgs (use `--skip-deep-data` to work around)
- Edition differences (DE vs EE) create inherent drift that isn't configuration drift
- Deep data comparison sections are capped at 50 entries in the report (full data in JSON output)
- `OrganizationSettingsDetail` availability varies by org edition — falls back to `SecurityHealthCheckRisks` which preserves raw values but may include non-boolean settings
- Non-namespaced package components (e.g. unlocked 2GP) cannot be distinguished from org-native metadata

## Tips

- **Edition-aware:** DE vs EE orgs will always show permission/profile drift — this is expected
- **Session expiry:** If your session expires, re-run `sf org login web` and retry
- **Large orgs:** Use `--skip-deep-data` for a faster initial pass; run full deep data on targeted follow-ups
- **Custom labels:** Use `--org-a-label` / `--org-b-label` to make the report human-readable
- **Split files:** For large orgs, agents can load individual category files in parallel instead of the full combined.json

## Skill Structure

```text
dx-org-analyze/
├── SKILL.md                              # Workflow, rules, and reference index
├── scripts/
│   ├── collect_org_data.py               # Per-org data collection (SF CLI + Tooling API)
│   ├── compute_diff.py                   # Diff computation, drift scoring, report generation
│   └── introspect_org.py                 # Single-org introspection report generation
├── references/
│   ├── collection-details.md             # What the collection script gathers and how
│   └── report-format.md                  # Drift score formula and report sections
└── tests/
    ├── test_consistency.sh               # SKILL.md and script structural tests
    ├── test_compute_diff.sh              # Diff computation tests with fixture data
    ├── fixtures/                          # Sample org data for testing
    │   ├── org_a.json
    │   └── org_b.json
    └── README.md                         # Test documentation
```

## Tests

```bash
# Run all consistency tests (no credentials needed)
bash tests/test_consistency.sh
# Expected: 74 passed, 0 failed
```

## Contributing

To extend the comparison categories, update:

1. `scripts/collect_org_data.py` — Add a query to `collect_deep_data()` or a new collection function
2. `scripts/compute_diff.py` — Add comparison logic (e.g. in `diff_deep_data()`) and rendering in `render_markdown()`; if adding a new enrichable type, update `enrich_metadata_with_deep_diffs()`
3. `SKILL.md` — Update step descriptions if the workflow changes
4. `tests/test_consistency.sh` — Add assertions for new sections

