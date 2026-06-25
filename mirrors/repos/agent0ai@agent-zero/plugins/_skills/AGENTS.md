# Skills Plugin DOX

## Purpose

- Own active and hidden skill configuration injected into prompt protocol on each turn.

## Ownership

- `hooks.py` owns skill prompt injection and plugin lifecycle behavior.
- `api/skills_catalog.py` owns skill catalog access.
- `prompts/agent.system.active_skills.md` owns injected active-skill prompt content.
- `webui/` owns skill settings UI and store.
- `default_config.yaml`, `plugin.yaml`, `README.md`, and `LICENSE` own defaults, metadata, docs, and license.

## Local Contracts

- Keep active skill lists bounded by configured caps.
- Store configured skills in normalized portable paths.
- Hidden skills affect catalog/search/load visibility but must not be injected as active prompt content.

## Work Guidance

- Coordinate active-skill resolution changes with core skill loading and settings UI.

## Verification

- Run skill runtime/catalog tests or smoke-test active, hidden, global, project, and chat-scope behavior after changes.

## Child DOX Index

No child DOX files.
