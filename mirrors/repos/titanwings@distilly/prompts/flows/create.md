# Create a Person Skill

The flow for `colleague`, `relationship` and `celebrity`. Resolve every `prompts/...` and `tools/...` path against `{distilly_skill_root}` (see `SKILL.md`).

## Family matrix

Every step below reads its prompt from this table.

| character | intake | persona analyzer | persona builder | merger | storage root |
|-----------|--------|------------------|-----------------|--------|--------------|
| `colleague` | `prompts/colleague/intake.md` | `prompts/colleague/persona_analyzer.md` | `prompts/colleague/persona_builder.md` | `prompts/colleague/merger.md` | `./skills/colleague/{slug}` |
| `relationship` | `prompts/relationship/intake.md` | `prompts/relationship/persona_analyzer.md` | `prompts/relationship/persona_builder.md` | `prompts/relationship/merger.md` | `./skills/relationship/{slug}` |
| `celebrity` | `prompts/celebrity/intake.md` | `prompts/celebrity/persona_analyzer.md` | `prompts/celebrity/persona_builder.md` | `prompts/celebrity/merger.md` | `./skills/celebrity/{slug}` |

Shared across all families:
- Work analyzer: `prompts/shared/work_analyzer.md`
- Work builder: `prompts/shared/work_builder.md`
- Correction handler: `prompts/shared/correction_handler.md`

## Step 0: Confirm the character family

If the user entered `/distilly`, first confirm which family should be distilled:

1. `owner`: the user themself (the default on a personal agent's first run)
2. `colleague`
3. `relationship`
4. `celebrity`

For `owner` (including "distill myself"), stop here and follow `prompts/flows/owner.md` instead.

If the host already passed an explicit family, lock the character family immediately.

If the current family is `celebrity`, also confirm the research profile:

1. `budget-friendly`
2. `budget-unfriendly`

Default to `budget-friendly`. Only switch to `budget-unfriendly` when the user explicitly wants deeper research, higher confidence, or accepts a slower and more expensive distillation pass.

## Step 1: Basic Info Collection

Follow the family's intake prompt from the matrix above. It owns the questions, their order and the confirmation summary; for `celebrity` it also settles the collection strategy and `research_profile`. Everything except the alias can be skipped. Summarize and confirm before moving on.

## Step 2: Source Material Import

Follow `prompts/flows/sources.md` to offer the import options and read what the user provides.

If the user says "no files" or "skip", generate the Skill from the Step 1 answers only.

## Step 3: Analyze Source Material

If the family is `celebrity`, first run `prompts/flows/celebrity_research.md` for the chosen research profile.

Then analyze along two tracks:

**Track A (Work Skill)**:
- Refer to `prompts/shared/work_analyzer.md`
- Extract: responsible systems, technical standards, workflow, output preferences, experience
- For `celebrity`, interpret `work` as methods, judgment frameworks, and decision patterns rather than literal job scope

**Track B (Persona)**:
- Use the family-specific persona analyzer
- If `celebrity` with `research_profile=budget-unfriendly`, use:
  - `prompts/celebrity/budget_unfriendly/persona_analyzer.md`
- Translate user-provided tags into concrete behavior rules
- Extract from materials: communication style, decision patterns, interpersonal behavior
- For `celebrity`, retain:
  - mental models
  - decision heuristics
  - expression DNA
  - contradictions
  - honest boundaries

## Step 4: Generate and Preview

Use `prompts/shared/work_builder.md` to generate Work content.
Use the family's persona builder from the matrix to generate Persona content; `celebrity` + `budget-unfriendly` uses `prompts/celebrity/budget_unfriendly/persona_builder.md`.

Show the user a summary (5-8 lines each), ask:
```
Work Skill Summary:
  - Responsible for: {xxx}
  - Tech stack: {xxx}
  - CR focus: {xxx}
  ...

Persona Summary:
  - Core personality: {xxx}
  - Communication style: {xxx}
  - Decision pattern: {xxx}
  ...

Confirm generation? Or need adjustments?
```

## Step 5: Write Files

After user confirmation, do not hand-build a `skills/colleague/{slug}`-style tree. Always go through the writer:

1. Resolve the current storage root:
   - `colleague` → `./skills/colleague`
   - `relationship` → `./skills/relationship`
   - `celebrity` → `./skills/celebrity`
2. Use the `Write` tool to create three temporary files:
   - `/tmp/distilly_{slug}_meta.json`
   - `/tmp/distilly_{slug}_work.md`
   - `/tmp/distilly_{slug}_persona.md`
3. The temporary meta file must include at least:
   - `name`
   - `display_name`
   - `character`
   - `research_profile` (required when `character=celebrity`)
   - `classification.language` (must match the user's language, for example `zh-CN` or `en`)
   - `profile`
   - `tags`
   - `knowledge_sources`
4. Then call:
   ```bash
   python3 "{distilly_skill_root}/tools/skill_writer.py" \
     --action create \
     --character {character} \
     --research-profile {research_profile} \
     --slug {slug} \
     --name "{name}" \
     --meta /tmp/distilly_{slug}_meta.json \
     --work /tmp/distilly_{slug}_work.md \
     --persona /tmp/distilly_{slug}_persona.md \
     --base-dir {resolved_base_dir}
   ```
5. This command will generate:
   - `SKILL.md`
   - `work.md`
   - `persona.md`
   - `work_skill.md`
   - `persona_skill.md`
   - `manifest.json`
   - `meta.json`
   - To install the generated role skill into a host, append the relevant flag:
     - Claude Code: `--install-claude-skill`
     - OpenClaw: `--install-openclaw-skill`
     - Codex: `--install-codex-skill`
     - Hermes: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host hermes --force`; for a trusted project, append `--skills-dir .hermes/skills`, run `hermes skills trust`, then start a new session or run `/reload-skills`. Use `~/.agents/skills` only when it is explicitly configured in Hermes `skills.external_dirs`
     - DeepSeek Harness: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host deepseek-harness --force`; append `--skills-dir .dsh/skills` for a project install
     - Pi: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host pi --force`; append `--skills-dir .pi/skills` for a project install, then invoke it with `/skill:{character}-{slug}`
     - Grok Build: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host grok-build --force`; append `--skills-dir .grok/skills` for a project install
     - OpenCode: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host opencode --force`; append `--skills-dir .opencode/skills` for a project install
     - The shared installer writes only the self-contained `SKILL.md` and install metadata and normalizes legacy frontmatter in the installed copy. Do not manually copy the whole generated directory; it may contain private source material
     - Claude Code on Windows: optionally add `--install-claude-command-shim`
6. If the current family is `celebrity`, run a quality check after creation:
   ```bash
   python3 "{distilly_skill_root}/tools/research/quality_check.py" "{resolved_base_dir}/{slug}/SKILL.md" --profile {research_profile}
   ```
7. If `source_grounding` still fails for a `celebrity` skill:
   - you may add honest limitation notes and a grounded source summary
   - only add URLs when they are real, specific, and traceable sources
   - **never** use site roots, topic pages, search pages, or other generic links as fake grounding
   - if no verified external sources exist, keep the FAIL state and explain what source material is still missing

When reporting success, return the correct family-specific location instead of assuming colleague storage.
