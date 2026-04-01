# Repository Guidelines

## Project Scope

This repository builds the **OpenClaw Assistant (DEV)** Home Assistant add-on.
The add-on packages OpenClaw + nginx + ttyd and manages startup/configuration glue.

## Architecture at a Glance

- Add-on root metadata/docs:
  - `README.md`
  - `DOCS.md`
  - `SECURITY.md`
  - `repository.yaml`
- Runtime implementation (all add-on behavior lives here):
  - `openclaw_assistant_dev/run.sh` (PID 1 orchestrator)
  - `openclaw_assistant_dev/oc_config_helper.py` (safe JSON config edits)
  - `openclaw_assistant_dev/render_nginx.py` (template rendering)
  - `openclaw_assistant_dev/nginx.conf.tpl`
  - `openclaw_assistant_dev/landing.html.tpl`
  - `openclaw_assistant_dev/config.yaml` (HA options + schema)
  - `openclaw_assistant_dev/translations/*.yaml` (all locale UI strings)
  - `openclaw_assistant_dev/Dockerfile`
  - `openclaw_assistant_dev/CHANGELOG.md`

## Core Rules

- Fix root causes, not symptoms.
- Keep edits surgical; do not refactor unrelated code.
- Never introduce insecure defaults.
- Never log secrets or auth tokens.
- Keep behavior backward-compatible unless the change explicitly requires a migration.

## Add-on Config Coupling Rules (Critical)

When adding/changing any add-on option, update **all** of the following in one change:

1. `openclaw_assistant_dev/config.yaml`
   - `options:` default
   - `schema:` validation entry
   - comments/help text
2. `openclaw_assistant_dev/translations/en.yaml`
3. `openclaw_assistant_dev/translations/bg.yaml`
4. `openclaw_assistant_dev/translations/de.yaml`
5. `openclaw_assistant_dev/translations/es.yaml`
6. `openclaw_assistant_dev/translations/pl.yaml`
7. `openclaw_assistant_dev/translations/pt-BR.yaml`
8. `DOCS.md` configuration reference / troubleshooting if user-facing
9. `openclaw_assistant_dev/CHANGELOG.md`

If any of these are skipped, the UX becomes inconsistent in HA.

## Runtime Safety Rules

- `run.sh` runs with `set -euo pipefail`; avoid constructs that fail unexpectedly under `set -e`.
- Validate all user-provided values from `/data/options.json` before injecting into shell/nginx/openclaw config.
- Keep `run.sh` idempotent on restart (multiple starts must not corrupt state).
- Treat `/config/` as persistent state; never wipe user data unless explicitly requested.

## Gateway/Auth/Security Rules

- OpenClaw v2026.2.22+ redacts sensitive values in `openclaw config get`.
  - For token retrieval guidance, prefer: `jq -r '.gateway.auth.token' /config/.openclaw/openclaw.json`.
- `trusted-proxy` mode may reject direct local CLI WS calls (`trusted_proxy_user_missing`); document this clearly instead of hiding it.
- For `lan_https` certificate logic, keep SAN generation deterministic and regeneration-triggered on SAN/IP changes.

## Template Coupling Rules

- If adding placeholders in `landing.html.tpl` or `nginx.conf.tpl`, update `render_nginx.py` in the same change.
- If landing-page guidance changes (commands/errors), sync corresponding troubleshooting text in `DOCS.md`.

## Versioning and Changelog

- User-visible changes should update:
  - `openclaw_assistant_dev/CHANGELOG.md`
  - `openclaw_assistant_dev/config.yaml` version
- Keep changelog entries user-facing and action-oriented.

## Coding Style

- Shell: POSIX-friendly Bash, explicit quoting, descriptive variable names.
- Python: small focused helpers, explicit error handling, no hidden side effects.
- YAML/Markdown: preserve existing style and structure.
- Avoid adding dependencies unless necessary.

## Validation Checklist (Run After Relevant Changes)

From repo root:

```sh
bash -n openclaw_assistant_dev/run.sh
python3 -m py_compile openclaw_assistant_dev/oc_config_helper.py
python3 -m py_compile openclaw_assistant_dev/render_nginx.py
```

For option changes:
- verify `config.yaml` option + schema + all translations exist
- verify `DOCS.md` matches current behavior

For startup/auth/proxy/cert changes:
- verify log messages remain clear and actionable
- verify `landing.html.tpl` instructions match actual commands

## Commit Scope

- Group related changes only.
- Do not include unrelated formatting churn.
- Do not edit generated/cache folders (`__pycache__`, temporary outputs).
