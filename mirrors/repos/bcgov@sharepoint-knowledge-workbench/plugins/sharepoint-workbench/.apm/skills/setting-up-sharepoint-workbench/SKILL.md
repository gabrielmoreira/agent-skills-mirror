---
name: setting-up-sharepoint-workbench
description: "Set up and validate the SharePoint Knowledge Workbench: request Entra app registration, initialize connection and document-workflow profiles, resolve document paths, and validate tenant readiness. Use the mode that matches the setup step; live tenant probes are always operator-run."
---

# Set Up SharePoint Workbench

Use this hub for the five setup modes below. Read the linked mode instructions before
running a mode; they preserve the original prompts, flags, examples, constraints, and
verification requirements.

## Quick start

1. Choose a mode from the table.
2. Read its instruction file under `references/modes/`.
3. Run from this skill's root with `scripts/` on `sys.path` for Python helpers.
4. Validate outputs before handing them to another plugin.

| Mode | Purpose and implementation |
| --- | --- |
| `init-connection` | Read or generate `config.psd1` with `Get-WorkbenchConnectionConfig.ps1` and `config_setup.py`. |
| `validate-connection` | Validate tenant connectivity with `Test-SharePointConnection.ps1` / `test-spo-connection.ps1`, `validate_sharepoint_connection.py` / `workflow_validation.py`, and injected validation helpers. |
| `app-registration` | Prepare Microsoft Entra ID app-registration requests with `request_app_registration.py` / `app_registration_request.py` and `New-WorkbenchEntraAppRegistration.ps1` where available. |
| `resolve-paths` | Resolve local document paths with `resolve_document_paths.py` / `path_resolution.py`. |
| `workflow-intake` | Bootstrap document workflow profiles with `initialize_workflow.py` / `document_workflow.py`. |

## Constraints

- Default operations are local and read-only with zero tenant I/O.
- Live PowerShell probes prompt for authentication and must be run by the operator.
- Never overwrite existing configuration or profiles without the mode's explicit
  overwrite option.
- Never execute downstream analysis, extraction, rendering, publishing, or provisioning.
- Report failures explicitly; do not convert unavailable paths or failed validation into
  success-shaped output.

## Mode instructions

- [Init connection](references/modes/init-connection.md)
- [Validate connection](references/modes/validate-connection.md)
- [App registration](references/modes/app-registration.md)
- [Resolve paths](references/modes/resolve-paths.md)
- [Workflow intake](references/modes/workflow-intake.md)

## Acceptance criteria

The preserved acceptance criteria are in `references/workbench-*-acceptance-criteria.md`.
