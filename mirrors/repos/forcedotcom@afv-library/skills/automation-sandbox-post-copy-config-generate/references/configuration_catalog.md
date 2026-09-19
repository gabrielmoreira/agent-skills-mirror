# Configuration Catalog

The fixed catalog of supported `ConfigurationName` values for the post-copy
automation config. **Never invent a new value** — if an SOP step does not
fit a row below, raise it to the user.

The catalog currently covers three types only:

1. `OutboundMessages`
2. `RemoteSiteSettings`
3. `ScheduledApex`

Anything else (Custom Labels, Connected Apps, Named Credentials, SSO, etc.)
is out of scope for this skill at present — surface them to the user and
recommend a follow-up to extend the catalog.

## How to use this catalog

For each post-copy action extracted from the SOP:

1. Find the row whose **SOP signal** phrases match the action.
2. Use the `ConfigurationName` from that row.
3. Use one of the listed **Field keys** in your entry's `Fields` object.
4. Put the **concrete value** from the SOP (literal URL, name, etc.) as
   the value. If the SOP does not state a concrete value, **skip the
   entry** entirely and list it in the response.

## Catalog

### OutboundMessages

- **SOP signal phrases**: "outbound message", "OBM", "endpoint URL",
  "Workflow Actions > Outbound Messages".
- **Field keys** (both required for non-delete entries):
  - `EndpointUrl` — value is the literal post-refresh URL the SOP gives
    for that outbound message.
  - `Object` — the SObject the outbound message targets (e.g., `Account`,
    `Contact`, `Asset`, `Lead`). This is mandatory because the same
    `Label` may apply to multiple OBMs that differ only by entity, and
    the post-copy tool needs the Object to disambiguate. Infer from the
    OBM name (e.g., `IR_Account_OBM_PROD` → `Account`,
    `IR_Contact_OBM_PROD` → `Contact`) or from explicit text in the SOP.
    If the entity is genuinely ambiguous and the SOP gives no signal,
    skip the entry and surface it.
- **Skip when**: the SOP only names the outbound message but does not
  give a new endpoint URL, OR the target Object cannot be determined.
- **Special action**: deletion. When the SOP says "delete all endpoints",
  use `Fields: { "Action": "Delete", "Object": "<entity>" }`. (`"Delete"`
  is a literal instruction the tool understands, not a placeholder.)

### RemoteSiteSettings

- **SOP signal phrases**: "remote site setting", "remote site", "trusted
  URL", "Setup > Security > Remote Site Settings".
- **Field keys**:
  - `RemoteSiteUrl` — value is the literal post-refresh URL. The key must
    be spelled **exactly** `RemoteSiteUrl`. Do **not** use `Url`,
    `RemoteSiteURL`, `SiteUrl`, or `EndpointUrl` (that last one is the OBM
    key, not the remote-site key). The post-copy tool matches the field by
    exact API name, so any other spelling silently no-ops at runtime.
- **Do NOT add**:
  - `RemoteSiteName` — the name lives in the top-level `Label` field.
  - `IsActive` — the active flag lives at the top level of the entry.
  Putting either inside `Fields` duplicates information the tool already
  has and creates ambiguity.
- **Skip when**: the SOP names the remote site but does not give a new
  URL.

### ScheduledApex

- **SOP signal phrases**: "scheduled apex", "scheduled job", "cron
  trigger", "System.schedule", "Setup > Scheduled Jobs", "re-schedule
  the nightly job", "schedule the batch class after refresh".
- **Field keys** (all three required):
  - `ApexClassName` — the bare Apex identifier of the class that
    implements `Schedulable`. Must match `^[A-Za-z_][A-Za-z0-9_]*$` —
    no dots, no spaces, no namespace prefix in this field, no `.cls`
    suffix. Example: `NightlyDataSyncScheduler`.
  - `CronExpression` — a 6- or 7-field Salesforce cron expression. The
    apply-side skill validates the shape, but do not emit a
    single-word / malformed value here. Example: `0 0 2 * * ?`
    (every day at 2:00 AM).
  - `JobName` — the human-readable job name that appears in Setup >
    Scheduled Jobs. Post-schedule this equals
    `CronTrigger.CronJobDetail.Name`; the apply-side skill uses it
    both as the `System.schedule` argument and as the SOQL key when
    verifying the job materialized. Typically the same string the
    customer uses to refer to the job.
- **Do NOT add**:
  - Any other Field key (e.g. `NextFireTime`, `State`, `CronTriggerId`)
    — `CronTrigger` is read-only and computed by the platform, so only
    the three inputs to `System.schedule` belong in `Fields`.
- **Skip when**: the SOP names a scheduled job but does not give all
  three of `ApexClassName`, `CronExpression`, and `JobName`. Never
  fabricate one from the others (for example, do not derive a JobName
  from the class name or vice versa) — surface the incomplete entry
  in the response so the user can supply the missing piece.

## Adding a new ConfigurationName

If a customer SOP introduces a configuration type not in the list above,
**stop and ask the user**. Adding a new value requires:

1. Update the `enum` in `assets/json_schema.json`.
2. Add a new section to this file.
3. Update `examples/sample_sop_to_config.json` if relevant.
4. Update the description in `SKILL.md` to include the new type.
