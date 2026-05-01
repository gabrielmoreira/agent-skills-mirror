# VCO Mirror Topology Reference

This reference is the human-readable mirror map for `config/version-governance.json`.

## Targets

| Target ID | Path | Role | Required | Presence Policy | Sync Enabled |
| --- | --- | --- | --- | --- | --- |
| `canonical` | `.` | canonical source | yes | `required` | no |

## Topology Rules

- `canonical` is the only source of truth.
- Repo-tracked `bundled/skills/vibe` and `bundled/skills/vibe/bundled/skills/vibe` targets are retired.
- Install/runtime compatibility may still materialize `skills/vibe/bundled/skills/vibe`, but that surface is generated from installed canonical payload and is not a repo mirror target.
- Installed runtime is governed separately by the runtime freshness contract and is not part of repo parity.
- Legacy gate names remain for continuity, but they now protect canonical-only repo truth and block mirror reintroduction.

## Packaging Scope

The canonical topology still governs the package payload copied into installed/runtime surfaces:

- top-level files: `SKILL.md`, `check.ps1`, `check.sh`, `install.ps1`, `install.sh`
- top-level directories: `config`, `protocols`, `references`, `docs`, `scripts`, `mcp`
- approved installed-only exception: `docs/CODEX_ECOSYSTEM_MAINTENANCE_PRINCIPLES.md`

`mcp` is governed because install-time payload assembly copies it into the runtime target and the routine checks require `mcp/servers.template.json` to exist.

## Governance Gates

Topology-aware gates:

- `scripts/verify/vibe-version-packaging-gate.ps1`
- `scripts/verify/vibe-nested-bundled-parity-gate.ps1`
- `scripts/verify/vibe-mirror-edit-hygiene-gate.ps1`
- `scripts/verify/vibe-release-install-runtime-coherence-gate.ps1`
- `scripts/verify/vibe-config-parity-gate.ps1`

## Execution Notes

- Always run topology-aware governance scripts from the canonical repo root.
- Never treat generated compatibility paths as governance owners.
- If a legacy bundled path reappears inside the repo, treat it as a regression and remove it instead of syncing into it.
