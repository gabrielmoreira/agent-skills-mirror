---
name: obsidian-project-documentation
description: Document technical projects in Obsidian vault. Use when the User mentions "document this", "close out", "wrap up", "update notes", "track progress", "where are we at", or asks about project docs.
version: 3.2.1
allowed-tools: Read, Bash, AskUserQuestion, Task
---

# Obsidian Project Documentation Assistant

This skill helps maintain project documentation in an Obsidian vault while working with Claude Code. It
automatically captures project progress and insights into structured, consistent notes.

**Architecture:** This skill acts as a lightweight launcher that detects project context, asks clarifying
questions if needed, then launches an agent to handle the documentation work in the background.

## How This Works

Three situations trigger this skill, falling into two execution paths:

| Situation | Trigger | Path |
| --------- | ------- | ---- |
| **1** — New session start | User opens a project and says hello, or Claude Code starts | **Path A** — read-only context load |
| **2** — Mid-session documentation | "document this", "update notes", "track progress", etc. | **Path B** — full documentation run |
| **3** — Session end | "wrap up", "close out", "we're done for today", etc. | **Path B** — full documentation run |

**Path A is read-only.** It must never launch the documentation agent or write to the vault.

**Path B launches the agent.** It performs context detection and spawns the manager agent to write vault notes.

## Shared Step: Load Configuration

Before following either path, load the config:

### Step 1: Load Configuration

```bash
cat ~/.claude/obsidian-project-assistant-config.json 2>/dev/null
```

Expected format:

```json
{
  "vault_path": "/path/to/ObsidianVault",
  "areas": ["Hardware", "Software", "Woodworking", "Music Synthesis"],
  "auto_commit": false,
  "auto_push": false,
  "git_enabled": true
}
```

**If config doesn't exist (first-run setup):**

Use AskUserQuestion to ask the User for their Obsidian vault path:

```text
Question: "Where is your Obsidian vault? (e.g. ~/Documents/ObsidianVault)"
Options:
  - ~/Documents/ObsidianVault
  - ~/Documents/MyVault
  - Other (custom path)
```

Then write the config to `~/.claude/obsidian-project-assistant-config.json`:

```bash
cat > ~/.claude/obsidian-project-assistant-config.json <<EOF
{
  "vault_path": "<user-provided path with ~ expanded to $HOME>",
  "areas": ["Hardware", "Software", "Woodworking", "Music Synthesis"],
  "auto_commit": false,
  "auto_push": false,
  "git_enabled": true
}
EOF
```

Confirm the config was written, then follow the appropriate path below.

## Path A: Session Start (Situation 1)

Read-only. Do not launch the agent. Do not write to the vault.

### Step A1: Detect Project Name

Use the same detection logic as Step B2 (git repo name → directory name) to determine which vault note to load.

### Step A2: Read Project Context

```bash
cat "{vault_path}/Projects/{project_name}.md" 2>/dev/null
```

Also read `CLAUDE.md` from the current working directory if it exists.

### Step A3: Welcome the User

Greet the User by name, summarise:

- Current project phase and status from the vault note
- The next steps recorded at the end of the last session
- Any decisions or open questions worth flagging

Keep this brief — it is an orientation, not a report.

## Path B: Documentation Run (Situations 2 & 3)

### Step B1: Quick Context Detection

#### Detect Project Name

Try these methods in order:

1. **From the User's message** - If the User explicitly mentions project name in their request
2. **From git repository**:

   ```bash
   git rev-parse --is-inside-work-tree 2>/dev/null && basename $(git rev-parse --show-toplevel)
   ```

   Transform kebab-case → Title Case (e.g., "obsidian-project-assistant" → "Obsidian Project Assistant")

3. **From directory name**:

   ```bash
   basename $(pwd)
   ```

If none of these work or result is generic (like "src", "build", "test"), refer to Step B2 below.

#### Detect Project Area

Run all four area detections in parallel and count matches. This avoids the false positives of a sequential
if/elif chain where the first match wins regardless of signal strength.

```bash
HW=$(find . -maxdepth 2 -type f \( -name "*.ino" -o -name "*.pcb" -o -name "*.sch" -o -name "platformio.ini" -o -name "arduino_secrets.h" \) 2>/dev/null | wc -l)
SW=$(find . -maxdepth 2 -type f \( -name "package.json" -o -name "requirements.txt" -o -name "Cargo.toml" -o -name "go.mod" -o -name "*.py" -o -name "*.js" -o -name "*.ts" \) 2>/dev/null | wc -l)
WW=$(find . -maxdepth 2 -type f \( -name "*.stl" -o -name "*.blend" -o -name "*.f3d" -o -name "*.skp" -o -name "cut-list.md" \) 2>/dev/null | wc -l)
MS=$(find . -maxdepth 2 -type f \( -name "*.pd" -o -name "*.maxpat" -o -name "*.syx" -o -name "*.amxd" -o -name "patch-notes.md" \) 2>/dev/null | wc -l)
```

Select the area using this decision logic:

- If `HW > 0` AND `SW > 0`: area is ambiguous (embedded software) — refer to Step B2
- Else if exactly one count is greater than all others: use that area
- Else if all counts are zero, or no clear winner: refer to Step B2

If no clear match, refer to Step B2 below.

#### Extract Description

Try to extract a brief description:

1. Check if README.md exists and read first paragraph
2. Check package.json for description field
3. Parse the User's message for description
4. See Step B2 below if the previous steps fail.

### Step B2: Ask Clarifying Questions

If project_name is null OR area is null, use AskUserQuestion before launching agent:

**If project name is unclear:**

```text
Question: "What would you like to name this project?"
Options:
  - [Current directory name]
  - [Git repo name if available]
  - Other (custom input)
```

**If area is unclear:**

```text
Question: "What type of project is this?"
Options:
  - Hardware
  - Software
  - Woodworking
  - Music Synthesis
  - Other (custom input)
```

### Step B3: Launch Documentation Agent

Launch an `obsidian-project-documentation:manager` agent with a prompt that includes all of the following context
variables. Every variable must be populated from the sources listed — do not leave any as empty or undefined.

| Variable | Source |
| -------- | ------ |
| `{vault_path}` | `vault_path` from config |
| `{project_name}` | Detected or user-supplied in Step 2–3 |
| `{area}` | Detected or user-supplied in Step 2–3 |
| `{description}` | Extracted or user-supplied in Step 2–3 |
| `{cwd}` | Run `pwd` |
| `{current_date}` | Run `date +%Y-%m-%d` |
| `{auto_commit}` | `auto_commit` from config |
| `{auto_push}` | `auto_push` from config |
| `{git_enabled}` | `git_enabled` from config |
| `{user_original_message}` | The exact message the User sent that triggered this skill |

Use this prompt template, substituting each `{variable}` with its value:

```text
Vault Path: {vault_path}
Project Name: {project_name}
Project Area: {area}
Description: {description}
Working Directory: {cwd}
Current Date: {current_date}
auto_commit: {auto_commit}
auto_push: {auto_push}
git_enabled: {git_enabled}
User's original message: {user_original_message}
```

### Step B4: Report Results

When the agent completes, inform the User:

```text
✅ Project documented successfully!
📝 Updated: {path_to_note}
📋 Summary: {what_was_documented}
🔄 Git: {commit_status} {push_status}
```

## Error Handling

If errors occur:

- **Config missing**: Run first-run setup (ask for vault path, write config)
- **Vault not accessible**: Verify vault_path in config
- **Git operations fail**: Report error, but still create/update note
- **Template missing**: Use a basic template or ask the User to reinstall

## Important things to remember

- Use absolute paths for all file operations.
- Use the current date for all timestamp operations.
- Handle errors gracefully (missing templates, git failures, etc.).
- When refering to the User, use their name and not 'User'. If in any doubt of the User's pronouns, ask the
  User but always remember them.
