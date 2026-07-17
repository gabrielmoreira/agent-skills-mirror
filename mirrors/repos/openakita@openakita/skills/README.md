# External skills

`skills/catalog.json` is the source of truth for the default user-facing categories of
workspace and bundled external skills. A user's bindings in
`data/skills/skill_categories.json` take precedence over these defaults.

## Inclusion policy

An external skill belongs in the bundled wheel only when it has a distinct user task,
accurate prerequisites, an OpenAkita-compatible execution path, and a maintainable
upstream/license record. Keep optional or credentialed skills disabled by default.

Do not bundle:

- bulk skill collections that have not been reviewed individually;
- instructions tied to another agent runtime's private tools;
- wrappers that claim an integration but only contain illustrative snippets;
- archived or retired APIs without a maintained compatibility path;
- generic prompts that duplicate the base model without adding a workflow.

The curated wheel list is grouped by task in `pyproject.toml`. Repository-only skills may
remain available during development, but every top-level external skill must appear exactly
once in `catalog.json`.
