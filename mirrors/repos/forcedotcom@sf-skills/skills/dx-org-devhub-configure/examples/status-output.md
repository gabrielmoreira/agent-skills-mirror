# Output examples

Sample `devhub.sh` transcripts to calibrate what to expect and how to relay it.
These are reference only — the script prints the authoritative output at runtime.

## Dev Hub is ON (status + allocation)

`status` mode prints the enablement line, the org edition, the signup-record
count, a one-line summary of which preferences are on, and the allocation table.

```text
Dev Hub status for 'MyDevHub':
  Dev Hub: ENABLED  (ScratchOrgInfo is queryable)
  Edition: Developer Edition
  Scratch org signup records: 3
  Enabled preferences: enableScratchOrgManagementPref enableScratchOrgSnapshotPref

Scratch org allocation for 'MyDevHub':
  Limit                        Used  Remaining        Max
  Active scratch orgs             2          1          3
  Daily scratch orgs              5          1          6
  WARN: only 1 active scratch org(s) remaining.
  NOTE: Daily scratch org usage at 83% (5/6).

  Active = orgs alive right now; Daily = successful creations in a rolling 24h window.
  Allocation is set by the Dev Hub's edition (e.g. Developer/trial 3 & 6;
  Enterprise 40 & 80; Unlimited/Performance 100 & 200) plus any purchased add-on.
```

## Current preferences (`--show-settings`)

`--show-settings` prints every `DevHubSettings` preference with an explicit
ON/OFF, one per line (requires Dev Hub to already be enabled).

```text
DevHub preferences for 'MyDevHub':
  enableScratchOrgManagementPref     ON
  enablePackaging2                   OFF
  enableScratchOrgSnapshotPref       ON
  enableShapeExportPref              OFF
```

## Dev Hub is OFF (prints how to enable it)

```text
Dev Hub status for 'my-org':
  Dev Hub: NOT ENABLED
  Detection: ScratchOrgInfo is queryable only when Dev Hub is on. A successful count means ENABLED. An INVALID_TYPE error means NOT ENABLED. Scratch org limits are not used, because they are reported even when Dev Hub is off.

  Scratch org allocation, Dev Hub preferences, and the scratch org list are not available until Dev Hub is enabled. An empty allocation or a failed exit from those modes means Dev Hub is off, not that the org is unauthenticated.

  Enable it (deploys enableScratchOrgManagementPref=true; irreversible):
    devhub.sh "my-org" --enable            # validate first (dry run)
    devhub.sh "my-org" --enable --apply    # actually enable
  Requires ModifyAllData or ModifyMetadata (System Administrator);
  not allowed in a sandbox or an org with a registered namespace.

  Manual alternative (Setup UI):
    1. Log in as a System Administrator.
    2. Setup > Quick Find > "Dev Hub" > Dev Hub > turn Enable Dev Hub On.
    Open it directly: sf org open --path "lightning/setup/DevHub/home" --target-org "my-org"
```
