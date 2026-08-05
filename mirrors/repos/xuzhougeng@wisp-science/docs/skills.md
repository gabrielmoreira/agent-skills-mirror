# Skills

Wisp discovers `SKILL.md` packages from several scopes. The Skills settings
page shows the scope and absolute source path for every discovered skill, and
the Agent's `search_skills` result includes the same `scope` and `path` fields.
For inventory questions, `list_skill_catalog` pages through the complete
discovered or effective view and reports separate discovered, effective,
shadowed, parse-error, and currently searchable enabled counts. Search result
counts must not be interpreted as the configured Skill inventory. The
`current_configured_enabled_count` field is the authoritative count for the
current Agent snapshot. If a user-provided or remembered UI count differs, the
Agent reports the discrepancy instead of inventing an installed/enabled
distinction.

Skills may declare an optional `wisp` YAML mapping with `schema_version: 1`
and controlled `domains`, `research_stages`, `roles`, `evidence_types`,
`outputs`, and `side_effects`. Legacy frontmatter remains valid. Invalid Wisp
semantics are retained as catalog parse-error records instead of silently
entering the effective catalog.

Discovery uses this precedence when two packages declare the same public name:

1. `bundled` — the read-only catalog shipped with Wisp.
2. `project` — `<project>/.wisp/skills` for workflows owned by one project.
3. `global` — `~/.wisp/skills` for workflows shared by all projects.
4. `extra` — directories configured through `WISP_SKILLS_PATH`, in configured
   order.
5. `plugin` — Skills from enabled feature plugins. A plugin never replaces a
   host Skill with the same name.

**Settings → Skills → Reload skills** rescans all of these locations without
restarting Wisp. Newly discovered Skills are enabled by default. Existing
Skills that the user explicitly disabled remain disabled. Idle conversation
Agents are rebuilt on their next turn, so the new index is used without losing
conversation history or restarting the persistent Python/R runtime.

The **Add skill** action installs or updates a global Skill from a `SKILL.md`
file, a Skill folder, or a ZIP archive. A ZIP may contain `SKILL.md` directly or
wrap one Skill in a single top-level folder. A project Skill can be managed with
the project files under `.wisp/skills` and then loaded with **Reload skills**.
Only global Skills can be deleted from the Skills settings page; project and
extra-path files remain owned by their project or source directory. Plugin
Skills are managed from their plugin card.

Tags declared in `SKILL.md` appear automatically. Tags edited in Settings are a
user override and are also applied to Agent `search_skills` queries after the
next idle-Agent rebuild.

The **Capabilities** summary uses the same current enabled Skill inventory and
splits it into bundled and project-added counts. Project-added includes project,
global, extra-path, and project-enabled plugin Skills. MCP counts are split into
bundled packages and enabled custom/plugin services available to the project.
