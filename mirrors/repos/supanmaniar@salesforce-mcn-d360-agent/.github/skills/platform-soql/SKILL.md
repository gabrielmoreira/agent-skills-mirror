---
name: platform-soql
description: 'Query and explore a Salesforce org from the CLI: run SOQL, paginate results, list and describe sObjects, call arbitrary REST endpoints, and check org limits. Use when you need to query records, inspect object schemas, explore the REST API, or check API and storage limits without an MCP server.'
---

# Salesforce Platform: SOQL, Describe, REST, Limits

Replaces the MCP server's platform tools: `sf_soql_query`,
`sf_soql_query_more`, `sf_list_objects`, `sf_describe_object`,
`sf_rest_request`, `sf_org_limits`.

## When to Use

- Running a SOQL query or paginating through results
- Listing sObjects or describing an object's fields
- Calling an arbitrary REST endpoint
- Checking org API, storage, or feature limits

## Procedure

### Run a SOQL query

```bash
sf data query --query "SELECT Id, Name FROM Account LIMIT 10" \
  --target-org "$SF_TARGET_ORG" --json
```

Add `--use-tooling-api` to query Tooling API objects (metadata, Apex classes).
Add `--all-rows` to include deleted records.

### Paginate

`sf data query` follows pagination automatically and returns all pages. If you
need manual control, use the REST API and follow `nextRecordsUrl`:

```bash
./scripts/sf-api.sh --path /query --query 'q=SELECT+Id+FROM+Account'
# then follow the returned nextRecordsUrl
./scripts/sf-api.sh --path /query/01g...-2000
```

For result sets over 10,000 records, prefer Bulk API 2.0:

```bash
sf data export bulk --query "SELECT Id, Name FROM Account" \
  --output-file accounts.csv --target-org "$SF_TARGET_ORG"
```

### List sObjects

```bash
sf api request rest "services/data/v66.0/sobjects" -o "$SF_TARGET_ORG" --json
```

This returns ~6,800 objects in a typical org. Filter with `jq` or Python rather
than reading the whole payload:

```bash
sf api request rest "services/data/v66.0/sobjects" -o "$SF_TARGET_ORG" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['sobjects']))"
```

### Describe an object

```bash
sf sobject describe --sobject Account --target-org "$SF_TARGET_ORG" --json
```

Returns every field with type, label, and flags. To find the fields you must
supply on insert:

```bash
sf sobject describe -s Account -o "$SF_TARGET_ORG" --json \
  | python3 -c "
import json,sys
for f in json.load(sys.stdin)['result']['fields']:
    if f['createable'] and not f['nillable']:
        auto = ' (auto-populated)' if f.get('defaultedOnCreate') else ''
        print(f\"{f['name']} ({f['type']}){auto}\")"
```

Fields marked `auto-populated` have a default and can be omitted. Note that a
standard object like Account may have **zero** fields that are both required and
non-defaulted — that is a valid result, not a failed query.

### Call an arbitrary REST endpoint

```bash
./scripts/sf-api.sh --path /limits
./scripts/sf-api.sh --method POST --path /some/endpoint --body '{"key":"value"}'
```

### Check org limits

```bash
sf org list limits --target-org "$SF_TARGET_ORG" --json
```

Or via REST, which returns the same data keyed by limit name:

```bash
./scripts/sf-api.sh --path /limits
```

## Gotchas

- **`--json` is required for machine-readable output.** Without it, `sf` prints
  a human-formatted table that is hard to parse.
- **`sf data query` caps at 10,000 records** before it stops paginating. Use
  `sf data export bulk` beyond that.
- **SOQL has no `SELECT *`.** Enumerate fields explicitly.
- **`sf sobject describe` on a large object is a big payload** (Account has 273
  fields). Filter before printing.
- **Tooling API queries need `--use-tooling-api`**, otherwise you get
  `INVALID_TYPE` for metadata objects.
- **API version matters.** Pass `--api-version` to pin one; the default follows
  the org's version.

## Reference

- [SOQL and describe reference](./references/soql-and-describe.md)
