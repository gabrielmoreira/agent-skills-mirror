---
name: archi-tooling
description: Manage and diagnose the Architec toolchain for the ccb.archi role. Use when the user asks to install, update, repair, verify, or troubleshoot Architec, Hippo, llmgateway, ccb-archi, or role tool readiness.
---

# Archi Tooling

Use this skill for the role's toolchain, not for architecture review itself.

## Commands

Check role and tool readiness:

```bash
ccb roles doctor ccb.archi
```

Install role assets plus the CCB-owned Architec wrapper and venv:

```bash
ccb roles install ccb.archi
```

Update role assets plus tool dependencies:

```bash
ccb roles update ccb.archi
```

Skip tool dependency provisioning only when explicitly diagnosing role assets:

```bash
ccb roles install ccb.archi --skip-tools
```

Check local Architec route:

```bash
ccb-archi --check . || archi --check .
```

## Diagnostics

Report:

- whether `ccb-archi` or `archi` exists
- Python version and venv path when CCB-managed
- whether `llmgateway` config is detected
- whether `archi --check .` succeeds

Do not print API keys or llmgateway secret values.
