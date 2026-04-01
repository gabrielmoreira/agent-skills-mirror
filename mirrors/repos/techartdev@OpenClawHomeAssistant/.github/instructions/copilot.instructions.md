# OpenClaw Home Assistant Add-on Patterns

Always reuse existing logic in `run.sh`, `oc_config_helper.py`, and `render_nginx.py`.
Avoid duplicate implementations for config parsing, gateway patching, or template rendering.
Respect guidelines in AGENTS.md

## Stack

- Home Assistant add-on (Debian Bookworm base)
- Bash runtime orchestrator (`run.sh`)
- Python helper scripts for config/template work
- nginx template rendering
- YAML config schema + 6 locale translation files

## Source of Truth

- Add-on options/schema: `openclaw_assistant_dev/config.yaml`
- Runtime boot logic: `openclaw_assistant_dev/run.sh`
- Safe OpenClaw config edits: `openclaw_assistant_dev/oc_config_helper.py`
- nginx + landing rendering: `openclaw_assistant_dev/render_nginx.py`
- UI text in Home Assistant: `openclaw_assistant_dev/translations/*.yaml`
- User-facing docs: `DOCS.md`

## Required Sync Rules

When changing add-on options, update in the same PR:

1. `config.yaml` option default + schema
2. All translation files (`en`, `bg`, `de`, `es`, `pl`, `pt-BR`)
3. `DOCS.md` config/troubleshooting sections
4. `CHANGELOG.md`

When changing landing/nginx placeholders:
- Keep template keys and `render_nginx.py` replacements in sync.

## Security Rules

- Do not log secrets/tokens.
- For gateway token docs/UI guidance, do not use `openclaw config get gateway.auth.token` (redacted in v2026.2.22+).
- Prefer `jq -r '.gateway.auth.token' /config/.openclaw/openclaw.json`.

## Editing Rules

- Keep fixes minimal and root-cause focused.
- Preserve backward compatibility for existing add-on options unless migration is explicit.
- Do not change unrelated behavior while fixing one issue.

## Validation Commands

```sh
bash -n openclaw_assistant_dev/run.sh
python3 -m py_compile openclaw_assistant_dev/oc_config_helper.py
python3 -m py_compile openclaw_assistant_dev/render_nginx.py
```

If behavior changes are user-visible, update `openclaw_assistant_dev/CHANGELOG.md`.
