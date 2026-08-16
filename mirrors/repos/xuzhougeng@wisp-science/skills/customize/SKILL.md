---
name: customize
description: Create a Wisp specialist or author a project-local skill using the tools Wisp actually exposes. Use when the user wants a custom Agent persona, a restricted specialist loadout, a new skill, or changes to an existing project-local skill.
---

# Customize Wisp

Wisp exposes customization through explicit tools and Settings UI. Python has
no control-plane SDK. Never invent profile, connector, or skill CRUD methods.

## Create a specialist

Use `save_specialist` only when it is advertised in the current session.

1. Ask what single job the specialist owns and what it must not do.
2. Draft a display name, one-line description, and concise instructions that
   extend Wisp's base prompt.
3. Decide whether to inherit project skills/connectors or use explicit
   whitelists. Use exact installed skill names returned by `search_skills`.
   Include connector names only when the user supplied or confirmed them.
4. Show the complete proposal and obtain confirmation before creating or
   updating it.
5. To edit an existing specialist, call `configure` with `action=get` and
   key `specialists`, then `save_specialist` with that `id`. Omit `id` to
   create. Builtin instruction text cannot be replaced.
6. Call `save_specialist` with `name` and `instructions`; add `description`,
   `model_id`, `skills`, or `connectors` only when intentionally chosen.
7. Report the returned specialist id. Deletion, icons, and color still live
   under **Settings → Specialists**.

Omit `skills` and `connectors` to inherit project settings. An empty list is an
explicit zero-access whitelist and is not equivalent to omission.

## Author or update a skill

Load `skill-creator`. For a project-local skill, edit files under:

```text
.wisp/skills/<skill-name>/SKILL.md
```

Use `read`, `write`, and `edit`. `search_skills` and `use_skill` are discovery
and loading tools, not mutation tools. If a newly created project skill is not
visible immediately, refresh or reopen the project so Wisp rebuilds its skill
index.

For a user-wide skill, create the folder in the project first, validate it, then
ask the user to install that folder through **Settings → Skills**. Wisp copies
installed skills to its user skill directory; there is no Agent-side publish or
delete interface.

## Custom appearance

For a user stylesheet (hide the lead bar, restyle chat, override tokens), load
`custom-theme`. Write CSS that uses documented tokens, then apply it with
`configure` `set custom_css` or ask the user to import the file under
**Settings → Appearance**.

## Boundaries

- Do not modify Wisp's SQLite store directly.
- Do not use `python`, `shell`, or `run_in_context` to bypass Settings or tool
  authorization.
- Do not promise conversation identity switching; the user selects specialists
  through Wisp's UI.
- Do not claim connector enumeration when no connector-management tool is
  advertised.
