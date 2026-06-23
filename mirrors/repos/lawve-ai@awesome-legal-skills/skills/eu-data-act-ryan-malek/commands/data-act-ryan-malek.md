---
description: EU Data Act skill — classify, draft, lookup, analyze, or audit under Regulation (EU) 2023/2854. Produces lawyer-style Word output.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /data-act-ryan-malek — EU Data Act lawyer skill

Invoke the EU Data Act skill installed at `~/.claude/skills/data-act-ryan-malek/`.

User input: $ARGUMENTS

## What to do

1. Read `~/.claude/skills/data-act-ryan-malek/SKILL.md` and follow its workflow exactly. The orchestrator handles verbatim citation, gotchas, house style, template filling, and Word rendering.

2. If `$ARGUMENTS` is non-empty, treat it as the lawyer's request. Common patterns:
   - `/data-act-ryan-malek classify [description]` → classify mode
   - `/data-act-ryan-malek draft [what to draft]` → draft mode
   - `/data-act-ryan-malek lookup [provision]` → lookup mode
   - `/data-act-ryan-malek analyze [scenario]` → analyze mode
   - `/data-act-ryan-malek audit [offering]` → audit mode
   - `/data-act-ryan-malek save-here` → set `config.output_dir = cwd` (always save Word to current folder, don't ask)
   - `/data-act-ryan-malek save-to-desktop` → set `config.output_dir = desktop`
   - `/data-act-ryan-malek ask-where-to-save` → reset `config.output_dir = ""` (prompt next export)

3. If `$ARGUMENTS` is empty, ask which Data Act task the lawyer wants:

   ```
   **Which mode?**

     A) **classify** — is the offering a connected product / related service / DPS / overlap? *(Recommended when starting a new matter)*
     B) draft — pre-contract notice / Art. 25 clauses / refusal letter
     C) lookup — verbatim regulation / FAQ text by reference
     D) analyze — apply the regulation to specific facts

   (audit mode also available — say "audit" or describe.)

   Reply A / B / C / D, or describe.
   ```

4. Never reproduce regulation, recital, or FAQ text from training data. Always read verbatim from `~/.claude/skills/data-act-ryan-malek/assets/source/`.

5. Default output is the chat itself. After the chat answer, ask the lawyer whether to export to Word. If yes, render via `python3 ~/.claude/skills/data-act-ryan-malek/scripts/render_docx.py --template <md> --deliverable-type <type>`. The renderer:
   - Writes to the lawyer's current working directory under `Data Act outputs/{date}_{type}.docx` by default.
   - Falls back to `~/Desktop/Data Act outputs/` if cwd isn't writeable or resolves inside the skill folder.
   - Honours `config.output_dir` if set (`cwd`, `desktop`, or an absolute path).
   - Uses pandoc + `assets/styles/lawyer-reference.docx` for proper Calibri / navy headings / page numbers / table grid / blockquote styling.
   - Appends the short disclaimer with the FAQ version + verified-as-of date.
   - Prints the absolute path AND a `file://` URI so the lawyer can click through.
   - NEVER writes deliverables inside the skill folder.

## Quick reference paths (skill-internal)

- Knowledge layer: `~/.claude/skills/data-act-ryan-malek/references/`
- Verbatim sources: `~/.claude/skills/data-act-ryan-malek/assets/source/`
- Drafting templates: `~/.claude/skills/data-act-ryan-malek/assets/templates/`
- Scripts: `~/.claude/skills/data-act-ryan-malek/scripts/`

## Disclaimer

This command invokes a skill that produces starting-point drafts only. It is not legal advice. See `~/.claude/skills/data-act-ryan-malek/LICENSE` for the full disclaimer.
