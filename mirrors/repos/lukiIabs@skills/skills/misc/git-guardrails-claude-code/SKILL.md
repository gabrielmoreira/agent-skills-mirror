---
name: git-guardrails-claude-code
description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
---

# Setup Git Guardrails

Sets up a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them.

## What Gets Blocked

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, Claude sees a message telling it that it does not have authority to access these commands.

## Steps

### 1. Ask scope

Ask the user: install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?

### 2. Build and copy the hook

The bundled **TypeScript** source is committed at [scripts/block-dangerous-git.ts](scripts/block-dangerous-git.ts). From the **`skills`** repository root (repo root containing `package.json` for tooling):

```bash
npm install
npm run build
```

Copy the compiled file to your hooks directory (`dist/` mirrors paths under the repo):

- **Project**: copy `dist/skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.js` → `.claude/hooks/block-dangerous-git.js`
- **Global**: same file → `~/.claude/hooks/block-dangerous-git.js`

The hook runs with **Node**: use `node` in the Claude settings snippets below.

### 3. Add hook to settings

Add to the appropriate settings file:

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.js"
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`):

Use one `"command"` string that invokes **Node** on the copied `.js`. Example (POSIX):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node $HOME/.claude/hooks/block-dangerous-git.js"
          }
        ]
      }
    ]
  }
}
```

On **Windows**, use the absolute path to `%USERPROFILE%\.claude\hooks\block-dangerous-git.js`, or whatever path your hook runner resolves.

If the settings file already exists, merge the hook into existing `hooks.PreToolUse` array — don't overwrite other settings.

### 4. Ask about customization

Ask if user wants to add or remove any patterns from the blocked list. Edit [scripts/block-dangerous-git.ts](scripts/block-dangerous-git.ts) and rerun `npm run build`, then recopy `.js`.

### 5. Verify

From this repository root, after **`npm run build`**:

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | node dist/skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.js
```

Should exit with code **2** and print a `BLOCKED` message to stderr.
