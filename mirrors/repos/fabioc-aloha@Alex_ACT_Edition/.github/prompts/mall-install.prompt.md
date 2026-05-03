---
description: "Install a plugin from the Alex ACT Plugin Mall into local/ paths"
mode: agent
lastReviewed: 2026-05-02
---

# /mall install

Install a plugin from the Plugin Mall into this project's `local/` paths.

## Steps

1. **Identify the plugin** from the user's request. If no specific plugin named, run the selection protocol from `mall-installation.instructions.md` (assess project needs, recommend candidates, ask for confirmation).

2. **Fetch plugin.json** to understand what the plugin ships:

   ```bash
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/plugin.json \
     --jq .content | base64 -d
   ```

3. **Check prerequisites**:
   - `requires_edition`: is the heir's Edition version sufficient? Check `.github/VERSION`.
   - `requires_plugins`: are dependency plugins already installed in `local/`?
   - Already installed? Check `.github/skills/local/<name>/`.

4. **Show the user what will be installed**:

   ```text
   Plugin: <name> (<shape>, <tier>)
   Token cost: ~<token_cost> tokens
   Artifacts:
     - skill -> .github/skills/local/<name>/SKILL.md
     - muscle -> .github/muscles/local/<name>.cjs (if applicable)
     - instruction -> .github/instructions/local/<file> (if applicable)
   ```

   Ask for confirmation before proceeding.

5. **Download and install** each artifact per `install_paths` in plugin.json:

   ```bash
   # Create directories
   mkdir -p .github/skills/local/<name>

   # Download each artifact
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/SKILL.md \
     --jq .content | base64 -d > .github/skills/local/<name>/SKILL.md
   ```

   Repeat for each artifact listed in plugin.json.

6. **Copy plugin.json and README.md** into the local skill folder for reference:

   ```bash
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/plugin.json \
     --jq .content | base64 -d > .github/skills/local/<name>/plugin.json
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/README.md \
     --jq .content | base64 -d > .github/skills/local/<name>/README.md
   ```

7. **Commit**:

   ```bash
   git add .github/skills/local .github/instructions/local .github/muscles/local .github/prompts/local
   git commit -m "Install plugin: <name> from ACT Plugin Mall"
   ```

8. **Report**: confirm what was installed, the token cost, and any next steps from the plugin's README.

## Refuse if

- Plugin not found in CATALOG.json
- Already installed (ask to overwrite or skip)
- `requires_edition` not met (suggest upgrading Edition first)
- Plugin overlaps with Edition baseline (explain which artifact already covers it)
