---
name: records-crud
description: 'Create, read, update, and delete Salesforce records from the CLI, including bulk operations and composite requests. Use when inserting or modifying sObject records, doing bulk data loads, deleting records, or batching multiple operations into one API call without an MCP server. Note that Data 360 data objects (__dlm, __dll) and CMS content (ManagedContent) reject all DML and must be written through their own APIs instead.'
---

# Record CRUD and Bulk Operations

Replaces the MCP server's record tools: `sf_create_record`, `sf_get_record`,
`sf_update_record`, `sf_delete_record`, `sf_bulk_create_records`,
`sf_bulk_update_records`, `sf_bulk_delete_records`, `sf_composite`.

## When to Use

- Creating, reading, updating, or deleting a single record
- Loading or modifying many records at once
- Deleting records in bulk
- Batching heterogeneous operations into one API call

## Procedure

### Single record

```bash
# Create
sf data create record --sobject Account \
  --values "Name='Acme Corp' Industry='Technology'" \
  --target-org "$SF_TARGET_ORG" --json

# Read
sf data get record --sobject Account --record-id 001Hp000041N2PUIA0 \
  --target-org "$SF_TARGET_ORG" --json

# Update
sf data update record --sobject Account --record-id 001Hp000041N2PUIA0 \
  --values "Industry='Manufacturing'" --target-org "$SF_TARGET_ORG" --json

# Delete
sf data delete record --sobject Account --record-id 001Hp000041N2PUIA0 \
  --target-org "$SF_TARGET_ORG" --json
```

`--values` uses `Field='value'` pairs separated by spaces. For values
containing spaces or quotes, prefer the REST API with a JSON body:

```bash
./scripts/sf-api.sh --method POST --path /sobjects/Account \
  --body '{"Name":"Acme Corp","Industry":"Technology"}'
```

### Bulk operations

The composite API handles up to **200 records per call**:

```bash
# Bulk create
./scripts/sf-api.sh --method POST --path /composite/sobjects \
  --body '{"allOrNone":false,"records":[
    {"attributes":{"type":"Account"},"Name":"Acme 1"},
    {"attributes":{"type":"Account"},"Name":"Acme 2"}]}'

# Bulk update
./scripts/sf-api.sh --method PATCH --path /composite/sobjects \
  --body '{"allOrNone":false,"records":[
    {"attributes":{"type":"Account"},"Id":"001...","Name":"Renamed"}]}'

# Bulk delete (up to 200 ids)
./scripts/sf-api.sh --method DELETE \
  --path '/composite/sobjects?ids=001...,001...&allOrNone=false'
```

For larger volumes, use Bulk API 2.0:

```bash
sf data import bulk --sobject Account --file accounts.csv \
  --target-org "$SF_TARGET_ORG" --json
sf data upsert bulk --sobject Account --file accounts.csv \
  --external-id My_External_Id__c --target-org "$SF_TARGET_ORG" --json
```

### Composite (mixed operations)

`POST /composite` runs up to **25 subrequests** in one call, each with its own
method and URL:

```bash
./scripts/sf-api.sh --method POST --path /composite \
  --body '{"allOrNone":false,"compositeRequest":[
    {"method":"POST","url":"/services/data/v66.0/sobjects/Account",
     "referenceId":"newAccount","body":{"Name":"Acme"}},
    {"method":"GET","url":"/services/data/v66.0/sobjects/Account/001...",
     "referenceId":"existing"}]}'
```

Subrequests can reference each other's results with `@{referenceId.id}`.

## Gotchas

- **Not every object accepts DML. Two families are read-only by design.**
  Before attempting a write, check the describe flags:

  ```bash
  sf sobject describe -s <Object> -o "$SF_TARGET_ORG" --json \
    | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; \
        print({k: r.get(k) for k in ('createable','updateable','deletable','queryable')})"
  ```

  | Family | Objects | Writable |
  | --- | --- | --- |
  | Data 360 unified data | data model objects (`__dlm`), data lake objects (`__dll`) | ❌ |
  | CMS content | `ManagedContent`, `ManagedContentVariant` | ❌ |

  Every verb is rejected server-side:

  ```text
  POST   /sobjects/ssot__Individual__dlm       -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  PATCH  /sobjects/ssot__Individual__dlm/{Id}  -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  DELETE /sobjects/ssot__Individual__dlm/{Id}  -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  ```

  **This is a property of the object, not of your permissions** — an admin sees the
  same flags, so do not retry with elevated access. Their data arrives through a
  purpose-built API instead:

  | To write | Use | Skill |
  | --- | --- | --- |
  | Data 360 records | Ingestion API (`/api/v1/ingest/*`) | [data360-api](../data360-api/SKILL.md) |
  | CMS content | `/connect/cms/contents`, `/connect/cms/spaces` | [mc-next-api](../mc-next-api/SKILL.md) |

  Config and setup objects behave normally: `DataStream`, `Account`, `Contact` and
  `Lead` are all `createable/updateable/deletable = true`. So the rule is about
  *data* objects, not about the org or the API version.
- **`allOrNone: true` rolls back the entire batch** if any record fails. Use it
  when partial success would leave inconsistent data; leave it `false` for
  best-effort loads.
- **Composite caps at 200 records** (`/composite/sobjects`) and **25
  subrequests** (`/composite`). Chunk larger inputs.
- **Deletes are destructive and irreversible** through the API. Confirm with
  the user, and prefer checking the record exists first.
- **`sf data delete record` requires `--record-id` or `--where`.** Passing
  neither errors.
- **Bulk API 2.0 is asynchronous.** `sf data import bulk` waits by default; use
  `--async` to return a job id and poll with `sf data resume`.
- **Field-level security applies.** A field you can see in the UI may not be
  writable by the integration user.

## Reference

- [Bulk and composite reference](./references/bulk-and-composite.md)
