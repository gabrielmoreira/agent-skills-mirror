Use local skills as the primary routing layer for skill security audit work.

Use `skill-threat-model` when identifying assets, trust boundaries,
permissions, threat paths, risk ratings, and approval recommendations for
skills, bundles, scripts, MCP presets, or install paths.

Use `prompt-injection-review` when reviewing skill instructions, references,
examples, or untrusted-content workflows for instruction override risk.

Use `data-exfiltration-review` when reviewing file access, network sends,
logs, hidden output channels, or inappropriate data movement.

Use `script-permission-review` when reviewing bundled scripts, command
examples, dependency installs, shell use, file writes, network calls, and
destructive operations.

Use `supply-chain-review` when reviewing third-party sources, dependencies,
remote downloads, provenance, version pins, licenses, and update paths.

Use `secrets-handling-review` when reviewing credentials, env vars, logs,
templates, examples, generated files, and redaction rules.

Use `safe-install-checklist` when producing approve/approve-with-changes/block
or defer recommendations before installing or publishing a skill.

Use `concise-technical-writing` for security reports and maintainer-facing
recommendations.

Default to review-only behavior. Do not run unreviewed scripts, access secrets,
install third-party skills, enable broad MCP/tool scopes, or approve production
write access without explicit user approval.
