# Sandbox Definition File — Approach B (Create & Refresh)

The DX-native path for creating and refreshing a sandbox: write a JSON definition file (a reusable blueprint), then create or refresh the sandbox from it with the Salesforce CLI. Prefer this when the user wants a checked-in, repeatable config or name-based Apex/group references (no ID lookups). Default to Approach A (Tooling API record) unless the user asks for this.

## Create

```json
// config/dev-sandbox-def.json
{
  "sandboxName": "mybox",
  "licenseType": "Developer"
}
```

```bash
sf org create sandbox --definition-file config/dev-sandbox-def.json --alias mybox --target-org prod
```

## Refresh

Use the existing sandbox's name; the definition file supplies any changed settings (e.g., `autoActivate`, `apexClassName`).

```json
// config/dev-sandbox-def.json
{
  "sandboxName": "mybox",
  "licenseType": "Developer",
  "autoActivate": true
}
```

```bash
sf org refresh sandbox --name mybox --definition-file config/dev-sandbox-def.json --target-org prod
```

## Definition File Fields

| Field | Required | Notes |
|-------|----------|-------|
| `sandboxName` | Yes | Alphanumeric, max 10 chars |
| `licenseType` | Yes | `Developer`, `Developer_Pro`, `Partial`, `Full` — **note: `Partial`, not `Partial_Copy`** in the definition file |
| `description` | No | Purpose of the sandbox (≤1000 chars) |
| `apexClassName` / `apexClassId` | No | Apex class implementing `SandboxPostCopy`; the definition file adds the *Name* variant so no ID lookup is needed |
| `activationUserGroupName` / `activationUserGroupId` | No | Public group controlling sandbox access; *Name* variant avoids an ID lookup. Default (omitted): All Active Users |
| `features` | No | `"['SandboxStorage']"` to upgrade data storage (Developer → 400 MB, Dev Pro → 2 GB); not for Partial/Full |
| `templateId` | Partial (required), Full (optional) | Sandbox template (15-char ID beginning `1ps`) selecting which objects to copy — shown to the user as "Object Data Included: All / Template-based" |
| `historyDays` | No | Full sandboxes only. Numeric (not a checkbox): `-1` (all available days), `0` (default, none), `10`, `20`, `30`, `60`, `90`, `120`, `150`, `180`. Shown to the user as "Include Field Tracking History Data" with these day-count choices |
| `copyChatter` | No | Full sandboxes only — shown to the user as "Include Chatter Data" |
| `copyArchivedActivities` | No | Full sandboxes only, and only visible if the org purchased the archived-activities add-on (most orgs haven't — contact Support to obtain it). Don't show this in the default confirmation; only offer it if the user specifically asks about archived activities |

## Additional Confirmation Fields by License — Create

When confirming a Create with the user (SKILL.md Section 7), show the common fields for every license, plus the additional fields for the one selected:

| License | Additional fields |
|---|---|
| All licenses (common) | Name, Description, Create From, License |
| Developer | Data Storage (Standard / →400 MB, irreversible), Apex Class, Sandbox Access (default: All Active Users) |
| Developer_Pro | Data Storage (Standard / →2 GB, irreversible), Apex Class, Sandbox Access (default: All Active Users) |
| Partial_Copy | Object Data Included (template required), Apex Class, Sandbox Access (default: All Active Users) |
| Full | Object Data Included (All / Template-based), Include Field Tracking History Data, Include Chatter Data, Apex Class, Sandbox Access (default: All Active Users) |

## Additional Confirmation Fields by License — Refresh

Same idea for Refresh (SKILL.md Section 8). `SandboxPostCopy` (Apex Class) is Create-only — it cannot be set or changed on a refresh.

| License | Additional fields |
|---|---|
| All licenses (common) | Rename to, Description, Auto-Activate, Sandbox Access (default: All Active Users) |
| Developer | Data Storage (Standard / →400 MB, irreversible) |
| Developer_Pro | Data Storage (Standard / →2 GB, irreversible) |
| Partial_Copy | Object Data Included (template) |
| Full | Object Data Included (All / Template-based), Include Field Tracking History Data, Include Chatter Data |
