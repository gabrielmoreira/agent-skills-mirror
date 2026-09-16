# Collection Details

The `scripts/collect_org_data.py` script collects all data from a single org into a split directory with per-category JSON files.

## Usage

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

## Output Directory Structure

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

## What Gets Collected

### Metadata (Name-Level)

All types discovered via `sf org list metadata-types` (typically 100+ types). Falls back to Tooling API queries if CLI metadata commands are unavailable. Namespaced (managed-package) components are tracked separately.

Metadata listing uses 12 parallel workers via `ThreadPoolExecutor`.

### Deep Data (Content-Level via Tooling API)

| Category | Fields Collected |
|----------|-----------------|
| Apex Classes | Body hash (SHA-256), API version, LOC, status |
| Apex Triggers | Body hash comparison |
| Custom Fields | Per-object field sets, data type, length, precision, required |
| Validation Rules | Active/inactive state, error message |
| Flows | Process type, API version, active version ID |
| Named Credentials | Endpoint URL |
| Object Permissions | Per-profile CRUD (Create/Read/Edit/Delete) per object |
| Field Permissions | Per-profile Read/Edit per field (FLS) |
| Connected Apps | Presence |
| Custom Metadata Types | Presence |

Deep data queries use 8 parallel workers. SOQL pagination handles >2000 records automatically.

### Org Settings

Queries `OrganizationSettingsDetail` via Tooling API (enabled/disabled features). Falls back to `SecurityHealthCheckRisks` if unavailable.

### Org Limits

Uses `sf limits api display` (preferred) or REST `/limits/` endpoint (fallback). Captures max values for API calls, storage, features.

### System Permissions

Dynamically discovers `PermissionsXxx` boolean fields via `sf sobject describe --sobject PermissionSet`, then queries all custom and profile-owned PermissionSet records. Filters out auto-generated permission sets (ID-based names).

### Installed Packages

Queries `InstalledSubscriberPackage` via Tooling API. Captures name, namespace, and version.

### Licenses

Queries `UserLicense`, `PermissionSetLicense`, and `PackageLicense` with total/used counts.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Fatal error (bad args, network failure, sf CLI not available) |
| `2` | Session expired (caller should re-authenticate and retry) |
