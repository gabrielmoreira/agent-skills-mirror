---
name: managing-sharepoint-lists-and-libraries
description: "Create, configure, and manage SharePoint lists, document libraries, list views, library settings, and list items. Use when asked to 'create list', 'create document library', 'add library', 'add list column', 'update list column', 'upload file', 'download file', 'create list view', or 'configure library settings'."
---

# Managing SharePoint Lists and Libraries

Route the request to the matching mode in `references/modes/`. Each mode preserves
its operation-specific flags, plan shape, dry-run behavior, and confirmation token.
All scripts are local copies under `scripts/`; they do not depend on another skill.

## Modes

- `create-list`, `remove-list`, `create-library`
- `library-settings`, `list-settings`
- `add-list-column`, `update-list-column`, `remove-list-column`
- `create-list-view`, `add-list-item`, `reconcile-calendar`
- `file-transfer`
- [Library upload orchestration & ledger](references/modes/library-upload-orchestration.md)

Use the exact script and token named by the selected mode. Writing operations remain
dry-run by default and require the mode's explicit `-Execute` and `-ConfirmToken`.
