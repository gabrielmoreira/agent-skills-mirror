---
name: workbench-initialize-workbench-config
plugin: workbench-setup
description: "Creates the root, git-ignored config.psd1 from this plugin's canonical config.psd1.example template -- Entra ID app-registration details (TenantId, ClientId, AuthenticationMode) and the target SharePoint site (SiteUrl). Generating the file is the default action and never connects to anything; a separate, explicit connector must be supplied to perform a read-only connection test. Mandatory answers: SiteUrl, TenantId, ClientId, AuthenticationMode."
allowed-tools: Bash, Read
examples:
  - "python -c \"import config_setup; config_setup.write_config('.', connection={...}, authentication={}, defaults={})\""
---

# Initialize Workbench Config

## Trigger and Purpose

Use this skill to generate the repository-root `config.psd1` (Layer 1
root connection configuration, per `docs/superpowers/specs/
2026-08-02-multi-document-destination-configuration-design.md`
Section 1) from this plugin's canonical `assets/config.psd1.example`
template — Entra ID app-registration details and the target SharePoint
site. Writing the file is the only action this skill performs by
default — it never connects to SharePoint.

Ask the user for the four mandatory values (`SiteUrl`, `TenantId`,
`ClientId`, `AuthenticationMode`), the two conditional
`Authentication.*` values (only when `AuthenticationMode` needs them —
currently `Certificate` mode requires `CertificateThumbprint`/
`TenantAdminUrl`), and offer the four `Defaults.*` library names with
sensible defaults the user can accept or override.

## Public Interface

```python
from config_setup import validate_connection_answers, write_config, test_connection

issues = validate_connection_answers(connection, authentication)  # [] means valid
output_path = write_config(repo_root, connection, authentication, defaults)
# repo_root / "config.psd1"

# Explicit, opt-in only -- never called by write_config:
test_connection(connection, connector=my_live_connector)  # raises NotImplementedError without one
```

`write_config` validates first (raises `ConfigSetupError` and writes
nothing on failure) and refuses to silently overwrite an existing
`config.psd1` unless `overwrite=True` is passed explicitly.

`test_connection` requires an injected `connector` callable — this
module ships no live SharePoint SDK/PnP connector itself, so calling it
without one raises `NotImplementedError` rather than silently no-op'ing
or faking success. `validate-workbench-environment`'s
`make_device_code_connector(http_client)` builds a real, working
connector for this parameter (device-code auth + `_api/contextinfo`
smoke test) -- wiring it in is still an explicit, opt-in caller choice,
never a default:

```python
from app_registration_validation import make_device_code_connector
connector = make_device_code_connector(http_client)  # caller supplies http_client
test_connection(connection, connector=connector)
```

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library.

