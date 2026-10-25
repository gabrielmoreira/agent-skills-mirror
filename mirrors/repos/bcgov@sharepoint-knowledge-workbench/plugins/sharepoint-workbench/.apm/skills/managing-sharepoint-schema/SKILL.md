---
name: managing-sharepoint-schema
description: "Create, configure, and provision SharePoint site collection information architecture: site columns, site content types, column formatting, and PnP provisioning templates. Use when asked to 'create site column', 'create content type', 'format column', 'provision site schema', or 'compare schema drift'."
---

# Managing SharePoint Schema

Route the request to the matching mode in `references/modes/`. Modes preserve the
legacy plan schemas, flags, reconciliation outcomes, and confirmation-token gates.
All executors and planning modules are in the self-contained `scripts/` directory.

## Modes

- `create-site-column`, `update-site-column`, `remove-site-column`
- `create-content-type`, `update-content-type`, `remove-content-type`, `detach-content-type`
- `column-formatting`, `plan-columns`, `plan-content-types`
- `compare-schema`, `scaffold-schema`, `reconcile-schema`, `export-schema`
- `apply-provisioning`

Planning is offline. Tenant writes remain dry-run by default and require the exact
operation-specific `-Execute` and `-ConfirmToken` values documented by the mode.
