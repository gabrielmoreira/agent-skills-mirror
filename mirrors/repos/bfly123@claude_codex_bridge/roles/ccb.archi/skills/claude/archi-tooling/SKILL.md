---
name: archi-tooling
description: Manage and diagnose the Architec toolchain for the ccb.archi role. Use when the user asks to install, update, repair, verify, or troubleshoot Architec, Hippo, llmgateway, ccb-archi, or role tool readiness.
---

# Archi Tooling

Use `ccb roles doctor ccb.archi` for readiness. Use
`ccb roles install ccb.archi` to install the Role Pack and CCB-owned Architec
venv/wrapper. Use `ccb roles update ccb.archi` to refresh role assets and tool
dependencies.

Use `ccb-archi --check . || archi --check .` for project route checks. Do not
print API keys or llmgateway secret values.
