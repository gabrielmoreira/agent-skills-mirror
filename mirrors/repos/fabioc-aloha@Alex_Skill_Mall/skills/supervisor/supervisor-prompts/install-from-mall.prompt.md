---
description: "Supervisor: Guided install of a skill, trifecta, pattern, or MCP config from Alex_Skill_Mall into the heir's local/ subdirs"
mode: agent
lastReviewed: 2026-04-30
---

# Install from Mall

Walk the user through installing a Mall asset into the right `local/` subdir so Edition upgrades don't overwrite it.

## Steps

1. **Ask what to install** — the user should provide either:
   - A skill name (e.g., `md-to-pdf`, `shell-injection-prevention`)
   - A pattern name (e.g., `champion-challenger-cache`)
   - An MCP config name (when Mall ships those)
   - "browse" — open <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.md> and pick

2. **Locate the Mall locally** — try in priority order:
   - `~/Alex_Skill_Mall` (or `%USERPROFILE%\Alex_Skill_Mall` on Windows)
   - Any sibling directory: check `..\Alex_Skill_Mall` from heir root
   - If absent, instruct: `git clone https://github.com/fabioc-aloha/Alex_Skill_Mall.git ~/Alex_Skill_Mall`

3. **Identify the asset type** by its path in the Mall:

   | Path matches | Type | Destination |
   |--------------|------|-------------|
   | `skills/<cat>/<name>/SKILL.md` only | skill alone | `.github/skills/local/<name>/` |
   | `skills/<cat>/<name>/SKILL.md` + `<name>.cjs` | skill + muscle | skill → `.github/skills/local/<name>/`, muscle → `.github/muscles/local/<name>.cjs` |
   | `skills/<cat>/<name>/` with SKILL.md + `.instructions.md` + `.cjs` | trifecta | each part → its `local/` home |
   | `patterns/<name>.md` | pattern | `.github/instructions/local/<name>.instructions.md` (add frontmatter) |
   | `mcp/<name>.json` | MCP server | merge into heir's `.mcp.json` (root, not `.github/`) |
   | `scaffolds/<name>/` | scaffold | refuse — scaffolds bootstrap *new* repos, not existing heirs |

4. **Copy** the files using `cp -r` (or `Copy-Item -Recurse` on Windows).
5. **Update path references** if any moved (e.g., `.cjs` from skill folder to muscles).
6. **Add frontmatter** if installing a pattern — derive `description` from the file's first paragraph and ask the user for a sensible `applyTo` glob.
7. **Read External Dependencies** — open the SKILL.md, surface any `Pandoc`, `npm install foo`, environment variables required.
8. **Verify** with a dry-run upgrade:

   ```bash
   node .github/scripts/upgrade-self.cjs
   ```

   Confirm none of the just-installed files appear under "would write" / "would delete". If they do, the install went to an edition-owned path — move them.

9. **Stage but do NOT commit** — show `git status` and let the user decide the commit message and timing.

## Refuse if

- Mall not found locally and user declines to clone it
- Asset is a scaffold (wrong tool — use `bootstrap-heir.cjs` instead)
- Heir's `.github/scripts/upgrade-self.cjs` doesn't exist (heir not bootstrapped — guide them through bootstrap first)
- Target file already exists under `local/` — ask the user whether to overwrite or rename

## Quick Reference

```bash
# Skill alone
cp -r ~/Alex_Skill_Mall/skills/<cat>/<name> .github/skills/local/<name>

# Skill with muscle companion
cp -r ~/Alex_Skill_Mall/skills/<cat>/<name> .github/skills/local/<name>
mv .github/skills/local/<name>/<name>.cjs .github/muscles/local/<name>.cjs
```
