# Operational Protocols (Common Definition)

Standard operational protocols shared by all agents. Each agent's Operational section need only specify **journal-specific topics** (1-2 lines) and reference this file for everything else.

---

## Journal

Each agent maintains a personal journal at `.agents/{agent-name}.md`.

**Format:**
```markdown
## YYYY-MM-DD - [Title]
**[Topic-specific field]:** [Content]
**Insight:** [What was learned]
**Apply when:** [Future scenario where this applies]
```

**Rules:**
- Create the file if missing on first use
- Record only genuinely reusable insights — not task logs
- Each agent defines its own topic focus (e.g., Scout: investigation patterns, Bolt: bottleneck learnings)
- Also read `.agents/PROJECT.md` for cross-agent context before starting work

---

## Activity Log

All agents log activity to `.agents/PROJECT.md` (shared cross-agent log).

**Format:**
```
| YYYY-MM-DD | AgentName | Action | Scope (files/area) | Outcome |
```

**Rules:**
- Add one row per task completion
- Before starting work: check PROJECT.md exists and read recent entries for context
- When orchestrating: ensure downstream agents also log their activity

---

## AUTORUN Protocol

When executing in AUTORUN mode, emit step completion markers.

**Format:**
```
_STEP_COMPLETE:
  Agent: [AgentName]
  Status: SUCCESS | PARTIAL | BLOCKED | FAILED
  Output: [Brief summary of results]
  Next: [NextAgent] | VERIFY | DONE
```

**Rules:**
- Emit after completing your assigned work
- PARTIAL: some deliverables produced but not all
- BLOCKED: cannot proceed without external input
- FAILED: attempted but could not produce deliverables
- Full protocol details → `_common/AUTORUN.md`

---

## Nexus Hub Protocol

All agents operate in hub-and-spoke mode through Nexus.

**Input marker:** `## NEXUS_ROUTING` — Nexus is routing a task to you
**Output marker:** `## NEXUS_HANDOFF` — Return results to Nexus

**Handoff format:** → `_common/HANDOFF.md`

**Rules:**
- Never hand off directly to another agent — always return to Nexus
- Include all fields required by the handoff format
- Attach relevant artifacts and findings

---

## Output Language

- Explanations, reports, questions: follow the CLI global config (`settings.json` `language` field, `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`)
- Code, identifiers, APIs, commit messages: **Repository conventions** (typically English)

---

## Git

Follow `_common/GIT_GUIDELINES.md`:
- Conventional Commits: `type(scope): description`
- No agent names in commits or PRs
- Subject < 50 characters, imperative mood
- Body explains "why", not "what"

---

## Shell Commands

When agents emit, document, or execute shell commands (in SKILL.md examples, references, generated scripts, or Bash tool calls), assume the user runs **macOS (Darwin)** with **zsh** unless the repository or user states otherwise.

**Rules:**
- Default to BSD-compatible syntax. macOS ships BSD coreutils, not GNU. Commands written for Linux often fail silently or with cryptic errors on macOS.
- When BSD/GNU divergence matters, prefer portable POSIX syntax. If GNU-only flags are required, document the dependency (`brew install coreutils gnu-sed`) and use `g`-prefixed binaries (`gsed`, `gdate`, `gfind`, `gstat`).
- Do not assume `/bin/bash` — macOS default shell is zsh. Use `#!/usr/bin/env bash` in scripts that require bash.

**Common BSD/GNU divergences to watch:**

| Command | macOS (BSD) | Linux (GNU) | Portable form |
|---------|-------------|-------------|---------------|
| `sed -i` | `sed -i '' 's/a/b/' f` | `sed -i 's/a/b/' f` | Use `sed -i.bak ... && rm f.bak` or write to a temp file |
| `date -d` | unsupported | `date -d '1 day ago'` | Use `date -v-1d` (BSD) or branch on `uname` |
| `readlink -f` | unsupported pre-12.3 | supported | Use `python3 -c "import os; print(os.path.realpath('$f'))"` |
| `stat -c` | `stat -f` | `stat -c` | Branch on `uname` or use `gstat` |
| `mktemp` | requires template arg variant | tolerant | Always pass an explicit template |
| `xargs -r` | unsupported | supported | Pipe through `[ -s ] && xargs` instead |
| `tar --xattrs` | different defaults | GNU defaults | Specify flags explicitly |

**When generating shell commands for the user:**
- If the command is macOS-incompatible, either rewrite portably or call out the limitation explicitly.
- For one-shot interactive Bash tool calls, prefer the BSD form directly (the user is on macOS).
- For SKILL.md examples and reference scripts intended for reuse, prefer portable POSIX or branch on `uname` so Linux CI environments still work.

---

## Subagent Parallel

When a task has 2-3 independent subtasks, agents may spawn sub-agents via the Agent tool for parallel execution.

**Decision & patterns:** → `_common/SUBAGENT.md`

---

## Self-Evolution

All agents load prior context before starting work (Tier 1). Agents with learning loops run post-task calibration (Tier 2).

**Protocol:** → `_common/SELF_EVOLUTION.md`
**Outward signals:** → `_common/EVOLUTION.md`
