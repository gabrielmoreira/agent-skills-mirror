# Skills

### Config sources and priority

Winner per skill name (highest first):

1. **project** — `<workspace>/{.reasonix,.agents,.agent,.claude}/skills/`
2. **custom** — `[skills].paths` (and plugin package skill roots)
3. **global** — `<Reasonix home>/skills` and home convention dirs
4. **builtin** — shipped skills (including this guide)

Same name: higher scope wins; lower scopes are **shadowed**. `[skills].disabled_skills` hides a name from List/Read entirely.

Discovery conventions: `.reasonix`, `.agents`, `.agent`, `.claude` (see `config.ConventionDirs`). Layouts: `<name>/SKILL.md` or flat `<name>.md` (Claude flat files need skill frontmatter).

### Checks

| Entry | How |
| --- | --- |
| CLI | `reasonix doctor capabilities` → Skills section |
| Desktop | Settings → Skills; Settings → Diagnostics |
| Chat / agent | `/skills` picker, `/reasonix-guide`, `run_skill` |

### Symptom → cause → fix

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skill missing from index | Disabled, shadowed, wrong root, or catalog preview limit | Search/list through `use_capability`; then check `skill.shadowed`, disabled names, and discovery roots |
| Builtin overridden | Project/global same name | Rename or remove user skill; disable if intentional |
| Flat Claude file ignored | No skill frontmatter under `.claude/skills` | Add `description:` / `runAs:` frontmatter or use `SKILL.md` folder |
| Body never loads | Expected: bodies are on-demand | Invoke via `/name` or `run_skill` |

### Ordered triage

1. `reasonix doctor capabilities --json` → Skills
2. Confirm name not in `disabled_skills`
3. Confirm winner Path/Scope; if shadowed, inspect lower-priority roots
4. Missing description: skill may load but index placeholder is weak — add `description:`
5. Reopen session / Refresh Skills after config changes
