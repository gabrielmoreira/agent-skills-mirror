# Step G — Flow activation / deactivation (`Flows`)

`Flows` entries in the post-copy config mutate
`FlowDefinition.Metadata.activeVersionNumber` via the same
compound-`Metadata` PATCH transport as Steps D-1/D-3, but Step D-2's
mutation-key derivation does **not** apply — the mutation key is
always the literal `activeVersionNumber`. Follow G-1 → G-4 below
**instead of** Step D for `Flows` entries. Steps A + B still apply
(`FlowDefinition` is the pinned sobject; Step B confirms the
`Metadata` compound field exists on this org).

## Fields shape

Every `Flows` entry carries these keys under `Fields`:

| Key | Meaning |
|-----|---------|
| `FlowApiName` | `DeveloperName` of the parent `FlowDefinition`. Required. |
| `Action` | `"Activate"` or `"Deactivate"`. Required. |
| `VersionNumber` | Integer. Required for `Activate` only when pinning a specific saved version; omit to activate the latest saved version. Ignored for `Deactivate`. |

Reject `FlowApiName` that doesn't match `^[A-Za-z_][A-Za-z0-9_]*$`
before any SOQL — the queries below interpolate it unescaped; a
malformed name is a SOQL-injection risk. Fail-closed on mismatch
(`API_NOT_IDENTIFIED`).

## G-1 — Look up the FlowDefinition + current active version

```bash
FLOW_API_NAME='<Fields.FlowApiName>'
SOQL="SELECT Id, DeveloperName, ActiveVersion.VersionNumber FROM FlowDefinition WHERE DeveloperName = '$FLOW_API_NAME'"
sf data query --use-tooling-api --json --query "$SOQL" \
  > /tmp/entry-<Slug>-flow-lookup.json
ID=$(jq -r '.result.records[0].Id // empty' /tmp/entry-<Slug>-flow-lookup.json)
CURRENT_ACTIVE=$(jq -r '.result.records[0].ActiveVersion.VersionNumber // empty' /tmp/entry-<Slug>-flow-lookup.json)
```

- Zero rows → `NOT_FOUND` (add Follow-ups bullet; skip PATCH).
- `CURRENT_ACTIVE` is the currently-active version number, or empty
  if the flow is inactive. `DeveloperName` is unique, so multiple rows
  should not occur; guard with `AMBIGUOUS` if they do.

## G-2 — Resolve target `activeVersionNumber` + apply pre-flight

- If `Fields.Action == "Deactivate"`:
  - Target = `null`.
  - If `CURRENT_ACTIVE` is empty → record `ALREADY_INACTIVE`, skip
    PATCH, add a Follow-ups bullet.
- If `Fields.Action == "Activate"`:
  - If `Fields.VersionNumber` is present → target = that integer.
  - Otherwise → query the latest saved version:
    ```bash
    SOQL="SELECT VersionNumber FROM Flow WHERE DefinitionId = '$ID' ORDER BY VersionNumber DESC LIMIT 1"
    sf data query --use-tooling-api --json --query "$SOQL" \
      > /tmp/entry-<Slug>-flow-latest.json
    TARGET=$(jq -r '.result.records[0].VersionNumber // empty' /tmp/entry-<Slug>-flow-latest.json)
    ```
    Empty result → `NOT_FOUND` (flow has no saved versions).
  - If `CURRENT_ACTIVE == TARGET` → record `ALREADY_ACTIVE`, skip
    PATCH, add a Follow-ups bullet.

## G-3 — GET current Metadata, mutate, PATCH back

Same compound-`Metadata` transport as Step D-3, with the mutation
fixed to `activeVersionNumber`. Do NOT run
`scripts/map-metadata-key.mjs` — the mutation key is always the
literal `activeVersionNumber`. Preserve every other key from the GET
below; overlay only `activeVersionNumber`. Never substitute
`ActiveVersion`, `activeVersionId`, `Status`, or `IsActive` — they
look like candidate keys but all fail with 400 or silent no-op.

The GET returns the complete Tooling API record (`Id`, `attributes`,
`Metadata`, …). Narrow with `?fields=Metadata` and extract the
`Metadata` object with `jq '.Metadata'` **before** the Step D-3
merge — the merge wraps its input as `{"Metadata": …}`, so if the
raw record is piped in, non-metadata keys end up inside `Metadata`
and the PATCH is rejected.

```bash
sf api request rest \
  "/services/data/v<apiVersion>/tooling/sobjects/FlowDefinition/$ID?fields=Metadata" \
  | jq '.Metadata' > /tmp/entry-$ID-meta.json

# Build /tmp/entry-$ID-mutation.json with {"activeVersionNumber": <TARGET or null>},
# merge with /tmp/entry-$ID-meta.json using `jq --slurpfile`, PATCH the
# merged result. Full recipe: references/api_endpoints.md §Step D.
```

Dry-run: resolve the plan via G-1 + G-2; skip the G-3 GET + PATCH;
record `DRY_RUN`. The plan prints the fixed mutation key
(`activeVersionNumber`) and the resolved target without reading or
mutating the current Metadata payload.

## G-4 — Verify the change landed

Re-run the G-1 SOQL and confirm `ActiveVersion.VersionNumber` matches
the target (or is empty after Deactivate). Mismatch → `FAILED_VERIFY`.

## Summary shape for a Flows entry

The generic `Planned request:` block from SKILL.md's canonical output
shape does **not** apply to a Flows entry — the Flows path dispatches
across four distinct sub-steps (SOQL lookup, target resolution, GET+
PATCH, verify), so the summary must record evidence that each
sub-step ran, not just the final PATCH body. Replace the
`Planned request:` block with the narrative below, keeping the
single-row phase table and the Totals / Follow-ups sections unchanged.

For each Flows entry's phase block, emit (in this order):

1. A one-line route header:
   ```text
   Route: **Step G — Flows (compound-`Metadata` PATCH with fixed `activeVersionNumber` mutation)**. Mutation key is fixed, NOT derived from the describe payload — `scripts/map-metadata-key.mjs` is skipped for Flows.
   ```

2. `Pre-flight lookup (G-1):` — the G-1 SOQL and the single-row result
   (`ActiveVersion.VersionNumber = <value or null>`), ending with the
   decision (`Not already active → proceed to G-2` /
   `ALREADY_INACTIVE short-circuit` / `AMBIGUOUS` / `NOT_FOUND`).

3. `Target resolution (G-2):` — the branch taken (`Action = Activate`
   with `Fields.VersionNumber` present / absent → latest-version SOQL;
   `Action = Deactivate` → target `null`), the resolved target
   `activeVersionNumber`, and a one-line comparison vs the pre-flight
   state justifying no short-circuit. For `Activate` without
   `Fields.VersionNumber`, include the latest-version SOQL verbatim
   and its returned `VersionNumber = <N>`.

4. `Request executed (G-3):` — the GET and PATCH as **two separate
   bullets** (not a Method/Path/Body sub-structure), each with the
   full Tooling path, then the PATCH body as
   `{ "Metadata": { …retrieved keys preserved…, "activeVersionNumber": <target> } }`,
   then the `204 No Content` response line. On dry-run, rename this
   section to `Planned request (G-3, dry-run):`, drop the GET bullet,
   render the PATCH body as the fixed-key-only
   `{ "Metadata": { "activeVersionNumber": <target> } }` (no retrieved
   keys — the GET is skipped), omit the response line, row Outcome is
   `DRY_RUN`, and skip section 6 below.

5. The single-row phase table (unchanged from SKILL.md's canonical
   shape; `Describe` column may be `—` for Flows since Step B's
   describe is prod-parity only).

6. `Read-back verification (G-4):` — the re-run G-1 SOQL and the
   observed `ActiveVersion.VersionNumber` (or `ActiveVersion = null`
   after Deactivate), confirming the mutation landed.

Short-circuit cases (`ALREADY_ACTIVE` / `ALREADY_INACTIVE` /
`NOT_FOUND` / `AMBIGUOUS` / `API_NOT_IDENTIFIED`) emit G-1 (and G-2
if the short-circuit is only visible after target resolution) and
stop — skip G-3, G-4, and the row's `HTTP` column renders `—`.
