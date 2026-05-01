---
description: "Guided install of skills from Alex_Skill_Mall — assess project needs, filter candidates, install into local/"
mode: agent
lastReviewed: 2026-05-01
---

# Install from Mall

Assess what this project needs from the Mall, then install the right skills into `local/` subdirs.

## Steps

1. **Assess project needs** — follow the Skill Selection Protocol in `mall-installation.instructions.md`:
   - Read project identity (`copilot-instructions.local.md`, `README.md`, `package.json`, directory structure)
   - List what's already in `.github/skills/local/` and `.github/skills/` (Edition baseline)
   - Match project signals to Mall categories
   - Apply the selection filter (actually needed, not already covered, would be used soon)

2. **If the user named specific skills**, validate them against the filter. Install if they pass, explain why not if they don't.

3. **If no specific request** ("browse" or just `/install-from-mall`), recommend 3-5 skills based on the project assessment. Present as a table:

   | Skill | Category | Why this project needs it |
   | --- | --- | --- |
   | `<name>` | `<cat>` | `<one-line rationale>` |

   Ask the user to confirm before installing.

4. **Fetch from GitHub** (preferred) or local clone (fallback):
   - **GitHub API**: List skill files with `gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/skills/<cat>/<name> --jq '.[].path'`, then download each file with `gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/<path> --jq .content | base64 -d > <dest>`
   - **Local clone** (fallback): `~/Alex_Skill_Mall` or `C:\Development\Alex_Skill_Mall`

5. **Install** each confirmed skill:
   - Create `.github/skills/local/<name>/`
   - Copy contents (not folder) from Mall: `skills/<cat>/<name>/*` → `.github/skills/local/<name>/`
   - If `.cjs` companion exists, move to `.github/muscles/local/<name>.cjs`
   - Check External Dependencies in SKILL.md

6. **Verify** — run `node .github/scripts/upgrade-self.cjs` (dry-run). Confirm installed files don't appear in "would write/delete".

7. **Stage and commit** — `git add .github/skills/local .github/muscles/local && git commit -m "Install <N> Mall skills: <names>"`

## Refuse if

- Mall not found locally and user declines to clone
- Skill already exists in `.github/skills/local/` (ask to overwrite or skip)
- Skill overlaps with Edition baseline (explain which instruction/skill already covers it)
- Target is a scaffold (wrong tool)
