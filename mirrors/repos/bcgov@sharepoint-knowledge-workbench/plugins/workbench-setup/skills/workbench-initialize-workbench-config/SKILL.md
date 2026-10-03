---
name: workbench-initialize-workbench-config
plugin: workbench-setup
description: "Creates the root, git-ignored config.psd1 from the canonical config.psd1.example template: Entra ID app-registration details (TenantId, ClientId, AuthenticationMode) and the target SharePoint site (SiteUrl). Use when setting up a workbench connection for the first time. Generating the file is the default action and never connects to anything; a separate, explicit connector is needed for a read-only connection test. Mandatory answers: SiteUrl, TenantId, ClientId, AuthenticationMode."
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import config_setup; config_setup.write_config('.', connection={...}, authentication={}, defaults={})\""
---

# Initialize Workbench Config

Generate the repository-root `config.psd1` (Layer 1 root connection configuration) from
`assets/config.psd1.example`. Writing the file is the only default action.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Never connect to SharePoint by default. A connection test runs only when the caller
  explicitly supplies a connector.
- Never overwrite an existing `config.psd1` unless `overwrite=True` is passed explicitly.
- Run from this skill's root. Helpers are `scripts/config_setup.py` and
  `scripts/psd1_writer.py`; standard library only, no other plugin required.

## Quick start

Put `scripts/` on `sys.path`, then call `validate_connection_answers` and `write_config`;
signatures are in [the API reference](references/config-setup-api.md).

## Workflow

1. Ask for the four mandatory values: `SiteUrl`, `TenantId`, `ClientId`, `AuthenticationMode`.
2. Ask for the two conditional `Authentication.*` values only when the mode needs them.
   `Certificate` mode requires `CertificateThumbprint` and `TenantAdminUrl`.
3. Offer the four `Defaults.*` library names with sensible defaults the user can accept
   or override.
4. Call `validate_connection_answers`; an empty list means valid.
5. Call `write_config`. It validates first and writes nothing on failure.

## Verification

Confirm `config.psd1` exists at the repository root with the supplied values. If a
connection test was requested, confirm it used an explicitly supplied connector; invoke
the `workbench-validate-workbench-environment` skill to supply one.

## References

- [API reference](references/config-setup-api.md): read before calling `write_config` or
  `test_connection`, or when validation, overwrite or connector errors occur.
