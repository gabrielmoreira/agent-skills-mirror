---
name: metadata-crud
description: 'Create, list, and delete custom objects and custom fields in a Salesforce org via the Tooling API from the CLI. Use when adding a custom object, adding a custom field to an existing object, listing custom objects or fields, or removing custom metadata without an MCP server.'
---

# Custom Object and Field Management

Replaces the MCP server's metadata tools: `sf_create_custom_object`,
`sf_create_custom_field`, `sf_delete_custom_field`, `sf_delete_custom_object`,
`sf_list_custom_objects`, `sf_list_custom_fields`.

All of these go through the **Tooling API**, which is why they use
`/tooling/sobjects/...` paths rather than `/sobjects/...`.

## When to Use

- Creating a custom object
- Adding a custom field to a standard or custom object
- Listing custom objects or the custom fields on an object
- Deleting a custom field or custom object

## Procedure

### List custom objects

```bash
sf data query --use-tooling-api \
  --query "SELECT Id, DeveloperName, Label FROM CustomObject WHERE ManageableState = 'unmanaged'" \
  --target-org "$SF_TARGET_ORG" --json
```

Or via the Tooling REST API:

```bash
./scripts/sf-api.sh --path "/tooling/query" \
  --query "q=SELECT+Id,DeveloperName+FROM+CustomObject"
```

### List custom fields on an object

```bash
sf data query --use-tooling-api \
  --query "SELECT Id, DeveloperName, DataType FROM CustomField WHERE TableEnumOrId = 'Account'" \
  --target-org "$SF_TARGET_ORG" --json
```

### Create a custom object

```bash
./scripts/sf-api.sh --method POST --path /tooling/sobjects/CustomObject \
  --body '{
    "FullName": "Invoice__c",
    "Metadata": {
      "label": "Invoice",
      "pluralLabel": "Invoices",
      "nameField": { "label": "Invoice Number", "type": "AutoNumber", "displayFormat": "INV-{0000}" },
      "deploymentStatus": "Deployed",
      "sharingModel": "ReadWrite"
    }
  }'
```

### Create a custom field

```bash
./scripts/sf-api.sh --method POST --path /tooling/sobjects/CustomField \
  --body '{
    "FullName": "Account.Priority__c",
    "Metadata": {
      "label": "Priority",
      "type": "Picklist",
      "valueSet": {
        "restricted": false,
        "valueSetDefinition": {
          "sorted": false,
          "value": [
            { "fullName": "High", "default": true, "label": "High" },
            { "fullName": "Low", "default": false, "label": "Low" }
          ]
        }
      }
    }
  }'
```

### Delete a custom field or object

```bash
# Find the Tooling API id first
sf data query --use-tooling-api \
  --query "SELECT Id FROM CustomField WHERE DeveloperName = 'Priority__c'" \
  --target-org "$SF_TARGET_ORG" --json

./scripts/sf-api.sh --method DELETE --path /tooling/sobjects/CustomField/<id>
./scripts/sf-api.sh --method DELETE --path /tooling/sobjects/CustomObject/<id>
```

## Gotchas

- **`FullName` for a field is `Object.Field__c`**, not just the field name.
- **Custom object and field API names must end in `__c`.** Omitting the suffix
  fails validation.
- **Deletion is destructive and cascades.** Deleting a custom object removes its
  fields and data. Deleting a field removes its data. Always confirm with the
  user and check for dependencies first.
- **`deploymentStatus: "Deployed"`** is required for the object to be usable
  immediately; `"InDevelopment"` keeps it hidden from most users.
- **Tooling API requires `--use-tooling-api`** on `sf data query`, otherwise the
  query fails with `INVALID_TYPE`.
- **Metadata changes may need a permission check.** The integration user needs
  "Customize Application" or equivalent.
- **Field creation is asynchronous in some orgs.** A describe immediately after
  creation may not show the field yet.

## Reference

- [Tooling API reference](./references/tooling-api.md)
