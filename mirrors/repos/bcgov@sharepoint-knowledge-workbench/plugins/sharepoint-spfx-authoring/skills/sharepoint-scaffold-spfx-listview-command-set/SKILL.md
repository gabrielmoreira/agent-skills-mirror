---
name: sharepoint-scaffold-spfx-listview-command-set
plugin: sharepoint-spfx-authoring
description: Scaffolds, implements, packages, deploys, registers, validates and removes an SPFx ListView Command Set for SharePoint list or library command bars, including commands that open URLs or host React dialogs and panels. Use for custom list commands; not for item forms.
allowed-tools: Bash, Read, Write
---

# SPFx ListView Command Set

Custom commands on a modern list or library command bar. A command set attaches to a list-scoped custom action, not a content type, so do not use a Form Customizer.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Package deployment does not register the command on a list; registration is a separate step.
- Never associate a ListView Command Set with a content type. Omit broad `elements.xml` / `ClientSideInstance.xml` registration when list-scoped activation is required.
- `scripts/register-listview-command-set.ps1` has no `-Execute` switch: it writes unless `-WhatIf` is passed. Preview with `-WhatIf`, work on a non-production site, and let the user run it.
- Treat URL and query values as untrusted; keep component properties valid JSON; prefer supported Fluent UI and SharePoint APIs over command-bar CSS injection.
- Persisting is not proven by a success message: re-query the list's `UserCustomActions` and confirm the stable name and component ID.

## Quick start

```powershell
pwsh -File scripts/register-listview-command-set.ps1 -ListName "<Library>" -Name "<StableActionName>" -Title "<Button label>" -ComponentId "<manifest-guid>" -Sequence 10 -ConfigPath "<config.psd1>" -WhatIf
```

## Workflow

1. Confirm a non-production target and collect the command, target list, action type and URL context. Run `scripts/check-spfx-toolchain.ps1`.
2. Scaffold (Extension, ListView Command Set, React if it hosts UI), implement `onListViewUpdated` and `onExecute`, add tests, build and package, deploy the `.sppkg` and add the app to the test site.
3. Register on the list with the script (drop `-WhatIf` once reviewed), then re-query `UserCustomActions` to confirm.
4. Wait for propagation, hard-refresh and verify. Roll back with the same script and `-Remove`; this removes the registration without touching documents or the package.

## Verification

The command appears with the right label and visibility, the dialog or panel completes, permissions, metadata and URL preselection behave, and `UserCustomActions` holds the stable name and component ID.

## References

- [Workflow and rules](references/listview-command-set-workflow.md): read for the full ten-step workflow, upload semantics and the registration commands.
- [List-scoped registration](references/list-scoped-registration.md) and [validation checklist](references/validation-checklist.md): read for registration details and verification.
- [Acceptance criteria](references/acceptance-criteria.md): read when checking expected behavior.
