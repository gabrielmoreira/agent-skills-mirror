---
name: hooks-creator
description: "**WORKFLOW SKILL — MANDATORY for ANY hook work.** Create, configure, edit, debug, fix, or review lifecycle hooks for VS Code Copilot (default) and Claude Code. USE FOR (always load this skill, never improvise): criar hook, configurar hook, editar hook, escrever hook, hook do Copilot, hook do GitHub Copilot, hook do Claude, hook do agente, agent hook, lifecycle hook, PreToolUse, PostToolUse, SessionStart, SubagentStop, Stop hook, UserPromptSubmit, PreCompact, bloquear comando, validar tool call, injetar contexto, guard, .agent.md frontmatter hooks, hooks.json, .github/hooks, .claude/settings.json, hook script Node.js, JS hook, cross-platform hook, hook não dispara, hook silencioso, hook ignorado, permissionDecision, hookSpecificOutput, additionalContext. **DEFAULT PLATFORM = VS Code GitHub Copilot.** Only target Claude Code when the user explicitly says \"Claude\" / \"Claude Code\" OR the workspace has a `.claude/` directory. NEVER assume Claude. DO NOT USE FOR: general coding, creating agents (use agent-creator), creating skills (use skill-creator)."
argument-hint: Describe what the hook should enforce or automate (target platform defaults to VS Code Copilot)
license: MIT
---

# Hooks Creator — Complete Guide to Agent Lifecycle Hooks

You are an expert at creating and configuring lifecycle hooks for AI agents. When the user asks you to create a hook, follow this guide to produce a complete, cross-platform, well-structured hook configuration. **All hooks should be written in JavaScript (Node.js)** — a single `.js` file that runs identically on Windows, macOS, and Linux.

## ⚠️ MANDATORY DEFAULT: VS Code GitHub Copilot

**Unless the user explicitly says otherwise, the target platform is ALWAYS VS Code GitHub Copilot.**

- ✅ Default target: **VS Code Copilot** — `.github/hooks/*.json` (workspace) or `.agent.md` frontmatter (agent-scoped)
- ✅ Switch to Claude Code ONLY if: user explicitly says "Claude" / "Claude Code", OR a `.claude/` directory exists in the workspace, OR the user is editing `~/.claude/settings.json`
- ❌ NEVER assume Claude Code by default
- ❌ NEVER write hooks to `.claude/settings.json` without explicit user request or evidence
- ❌ If unsure, **ASK** which platform — do not guess Claude

When generating examples, paths, configuration snippets, or installation steps, default to the Copilot equivalents (`.github/hooks/`, `~/.copilot/hooks/scripts/`, `chat.useCustomAgentHooks`, `tool_name === 'run_in_terminal'`). Mention Claude Code only as a secondary note when relevant.

## What are Hooks?

Hooks are **deterministic commands** executed at specific lifecycle events during an agent session. Unlike instructions (which are non-deterministic \u2014 the agent may or may not follow them), hooks **guarantee execution**. They run as real processes, receive structured JSON input via stdin, and return structured JSON output via stdout. Use hooks when you need certainty: enforcement, logging, validation, or context injection that must happen every time.

## Platform Detection

**Default = VS Code GitHub Copilot.** Only switch to Claude Code with explicit evidence (see decision table below).

| Signal | Platform | Hook Support |
|--------|----------|-------------|
| **Nothing said + no evidence** | **VS Code Copilot (DEFAULT)** | 8 events, `command` type only |
| User says "Copilot" / "GitHub Copilot" / "VS Code" | VS Code Copilot | 8 events, `command` type only |
| `.agent.md` in workspace | VS Code Copilot | 8 events, `command` type only |
| `.github/hooks/` exists | VS Code Copilot | Workspace hooks |
| User explicitly says "Claude" / "Claude Code" | Claude Code | 20 events, 4 hook types |
| `.claude/` directory exists | Claude Code | 20 events, 4 hook types |
| Both `.agent.md` and `.claude/` present | Ask the user which one | — |

**Detection strategy:**
1. Re-read the user's exact wording. Did they say "Copilot" or "Claude"? Trust their words.
2. Check for `.claude/` directory → if absent, target is Copilot.
3. Check for `.github/hooks/` or `.agent.md` → confirms Copilot.
4. If still unclear AND there's no signal at all → **default to Copilot**, do not ask.
5. Only ask when both ecosystems are clearly present and the user didn't pick one.

## Lifecycle Events

Complete event table across platforms:

| Event | VS Code | Claude Code | Trigger |
|-------|:-------:|:-----------:|---------|
| SessionStart | \u2705 | \u2705 | First prompt of session |
| UserPromptSubmit | \u2705 | \u2705 | User sends message |
| PreToolUse | \u2705 | \u2705 | Before any tool invocation |
| PostToolUse | \u2705 | \u2705 | After tool completes |
| PreCompact | \u2705 | \u2705 | Before context compaction |
| SubagentStart | \u2705 | \u2705 | Subagent created |
| SubagentStop | \u2705 | \u2705 | Subagent completes |
| Stop | \u2705 | \u2705 | Session ends |
| PermissionRequest | \u274c | \u2705 | Tool needs permission |
| PostToolUseFailure | \u274c | \u2705 | Tool fails |
| Notification | \u274c | \u2705 | Status notification |
| TaskCompleted | \u274c | \u2705 | Task finishes |
| Others (6 more) | \u274c | \u2705 | Various |

When targeting VS Code only, use the 8 shared events. When targeting Claude Code or hybrid, the full 20 events are available.

## Configuration Locations

| Location | Scope | Platform |
|----------|-------|----------|
| `.github/hooks/*.json` | Workspace (shared with team) | VS Code |
| `.agent.md` frontmatter `hooks:` | Agent-specific | VS Code (requires `chat.useCustomAgentHooks: true`) |
| `.claude/settings.json` | Workspace | Claude Code + VS Code |
| `~/.claude/settings.json` | User global | Claude Code + VS Code |

**Scope rules:**
- Hooks are **per-workspace** \u2014 they only apply inside the project where they are configured. Other workspaces are unaffected.
- VS Code has no global hooks path for **workspace hooks** (`.github/hooks/`). To reuse those across projects, copy the files or use a template repo.
- Claude Code supports `~/.claude/settings.json` as a **user-global** hook location \u2014 hooks defined there apply to all projects.

**Global vs workspace scripts for agent-scoped hooks:**
- Agent-scoped hooks (frontmatter) reference **scripts by path**. If the scripts live inside the workspace (e.g., `hooks/`), they only work in that workspace.
- **Recommended for portable agents**: store hook scripts in a **global user directory** (e.g., `~/.copilot/hooks/scripts/`) and reference them with `node` + the path. Since `node` is cross-platform, a single command works everywhere:
  - `node ~/.copilot/hooks/scripts/my-hook.js` \u2014 `~` expands on Unix; on Windows use `%USERPROFILE%` or an absolute path
- This way, agents synced to any workspace always find their hook scripts. No per-workspace setup needed.
- **Workspace hooks** (`.github/hooks/*.json`) should keep scripts inside the project \u2014 they are project-specific by nature (e.g., injecting git context).

**`chat.useCustomAgentHooks` setting:**
- This setting **only enables/disables** the agent-scoped hooks feature \u2014 it does NOT create or define any hooks.
- Hooks are defined in `.github/hooks/*.json` (workspace) and `.agent.md` frontmatter (agent-scoped). The setting just controls whether VS Code reads the frontmatter hooks.
- Recommended: set it **once in User Settings (global)** so it applies to all workspaces automatically \u2014 avoids repeating it in every `.vscode/settings.json`.

**Precedence**: Agent-scoped hooks (frontmatter) run in addition to workspace hooks (`.github/hooks/`). They do NOT replace each other \u2014 both execute.

## Multiple Hooks Behavior

When multiple hooks are defined for the same event (either multiple entries in the array, or workspace + agent-scoped):

- **All hooks execute** \u2014 no short-circuit. Even if hook 1 returns `deny`, hook 2 still runs.
- **Most restrictive wins**: `deny` > `ask` > `allow`. If any hook denies, the tool call is denied.
- **Independent evaluation**: each hook receives the original tool input. One hook\u2019s output does NOT affect another hook\u2019s input.
- **Synchronous execution** (VS Code): hooks run sequentially, not in parallel. The agent waits for each to complete.
- **Additive across scopes**: agent-scoped hooks run IN ADDITION TO workspace hooks \u2014 they don\u2019t replace each other.

| Hook A | Hook B | Result |
|--------|--------|--------|
| allow  | allow  | allow  |
| allow  | deny   | deny   |
| allow  | ask    | ask    |
| deny   | ask    | deny   |
| deny   | deny   | deny   |

**Implication**: A security hook that returns `deny` cannot be overridden by another hook returning `allow`. This makes `deny` hooks reliable safety nets.

## Hook Configuration Format

### VS Code JSON (workspace hooks in `.github/hooks/`)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "node hooks/format.js",
        "timeout": 15
      }
    ]
  }
}
```

### Agent Frontmatter (agent-scoped hooks)

```yaml
hooks:
  PostToolUse:
    - type: command
      command: "node hooks/format.js"
```

**Field reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Hook type. VS Code supports `command` only. |
| `command` | Yes | Command to run. Use `node hooks/my-hook.js` for cross-platform compatibility. |
| `timeout` | No | Max seconds before the hook is killed. Default varies by platform. |

> **Note:** With JavaScript hooks, the `windows` override field is **no longer needed** \u2014 `node` runs identically on all platforms with a single command.

## Input/Output Contract

Hooks receive JSON via **stdin** and return JSON via **stdout**.

### Exit Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| `0` | Success | stdout parsed as JSON |
| `2` | Blocking error | stderr content \u2192 agent feedback |
| Other | Warning | Non-blocking, hook output ignored |

### Key Input Fields

| Field | Type | Description |
|-------|------|-------------|
| `tool_name` | string | Name of the tool being invoked (PreToolUse/PostToolUse) |
| `tool_input` | object | Arguments passed to the tool |
| `hookEventName` | string | Which lifecycle event triggered this hook |
| `sessionId` | string | Current session identifier |
| `cwd` | string | Current working directory |

### Key Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `continue` | bool | Whether the agent should proceed |
| `stopReason` | string | Why the hook stopped execution |
| `systemMessage` | string | Message injected into agent context |
| `hookSpecificOutput` | object | Event-specific data (wrapped output) |

### What Reaches the Agent vs. UI-Only

Not all output mechanisms inject content into the agent\u2019s context. Some only display warnings in the VS Code UI that the user sees but the agent does not.

| Mechanism | Agent sees it? | Use case |
|-----------|:--------------:|----------|
| `hookSpecificOutput.additionalContext` | \u2705 Yes | Inject context (SessionStart, PreToolUse, PostToolUse, SubagentStart) |
| `hookSpecificOutput.decision: "block"` + `reason` | \u2705 Yes | Force agent to act before stopping (workspace Stop, PostToolUse) |
| Top-level `decision: "block"` + `reason` | \u2705 Yes | Force agent to act before stopping (SubagentStop, custom agent Stop) |
| `hookSpecificOutput.permissionDecision` + `additionalContext` | \u2705 Yes | Control tool approval with context (PreToolUse) |
| Exit code `2` + stderr | \u2705 Yes | Block operation, stderr shown to model (any event) |
| `systemMessage` (top-level) | \u274c No \u2014 UI only | Visual warning for the user |
| `continue: false` + `stopReason` | \u274c No \u2014 UI only | Stop session, reason shown to user |

**Critical implication**: If you want the agent to react to a Stop hook message (e.g., "run tests before finishing"), use `hookSpecificOutput.decision: "block"` with `reason` \u2014 NOT `systemMessage`. The `systemMessage` field only shows a warning banner in the VS Code chat UI; the agent never sees it.

### PreToolUse-Specific Output

| Field | Type | Description |
|-------|------|-------------|
| `permissionDecision` | string | See values below |
| `permissionDecisionReason` | string | Reason shown to user in the confirmation prompt (for "deny" or "ask") |
| `updatedInput` | object | Modified tool arguments |
| `additionalContext` | string | Extra context for the agent |

**`permissionDecision` values:**

| Value | Behavior |
|-------|----------|
| `"allow"` | Auto-approve the tool call \u2014 no user prompt |
| `"deny"` | Block the tool call. Agent receives `additionalContext` and must adapt. |
| `"ask"` | VS Code shows a confirmation prompt to the user. If user approves, tool executes. If user denies, tool is blocked. |

> **\u26a0\ufe0f PreToolUse fields (`permissionDecision`, `permissionDecisionReason`, `updatedInput`, `additionalContext`) MUST be inside `hookSpecificOutput`.** Placing them at the JSON top-level causes VS Code to silently ignore the output \u2014 the tool call proceeds as if no hook existed. This is the most common PreToolUse hook bug.
>
> ```json
> // \u274c WRONG \u2014 VS Code ignores these fields at top-level
> {
>   "permissionDecision": "deny",
>   "permissionDecisionReason": "reason for user",
>   "additionalContext": "reason"
> }
>
> // \u2705 CORRECT \u2014 fields inside hookSpecificOutput
> {
>   "hookSpecificOutput": {
>     "permissionDecision": "deny",
>     "permissionDecisionReason": "reason for user",
>     "additionalContext": "reason"
>   }
> }
> ```

### Stop-Specific Output

| Field | Type | Description |
|-------|------|-------------|
| `decision` | string | `"block"` \u2014 prevents the agent from stopping |
| `reason` | string | Required when decision is "block". Tells the agent why it should continue |

> **\u26a0\ufe0f Custom agent Stop hooks are treated as SubagentStop.** When a Stop hook is scoped to a custom agent (defined in `.agent.md` frontmatter), VS Code treats it as a `SubagentStop` event. The SubagentStop format expects `decision` and `reason` at the **JSON top-level**, not inside `hookSpecificOutput`. If you only put them inside `hookSpecificOutput`, the hook fires but the agent **ignores the output** \u2014 the block instruction never reaches the agent\u2019s context.
>
> **Best practice:** Always output `decision`/`reason` at **both** top-level AND inside `hookSpecificOutput`. This ensures the hook works whether VS Code routes it as Stop or SubagentStop:
>
> ```js
> const result = {
>   decision: 'block',
>   reason: 'Run tests before finishing.',
>   hookSpecificOutput: {
>     hookEventName: 'Stop',
>     decision: 'block',
>     reason: 'Run tests before finishing.'
>   }
> };
> process.stdout.write(JSON.stringify(result) + '\n');
> ```

> **\u26a0\ufe0f Agents with ONLY `Stop` hooks (no `PreToolUse`) crash as subagents.** When an agent defines `hooks:` with only `Stop` events and no `PreToolUse`, invoking it via `runSubagent` crashes with `Cannot read properties of undefined (reading 'length')`. **Workaround:** Always include at least one `PreToolUse` hook entry. For read-only agents, use a no-op guard (e.g., `pre-commit-guard` which only fires on destructive operations).

> **\u26a0\ufe0f `systemMessage` is UI-only \u2014 the agent never sees it.** It displays a warning banner in the chat for the user. If you need the agent to act on a Stop hook, use `decision: "block"` with `reason` \u2014 this IS injected into the agent\u2019s context. Putting `systemMessage` inside `hookSpecificOutput` is never valid \u2014 it\u2019s not a recognized field there and causes unintended blocking.

## Cross-Platform Scripts

**JavaScript (Node.js) is the primary format for all hook scripts.** A single `.js` file works on Windows, macOS, and Linux \u2014 no platform-specific overrides needed.

### Canonical JS Hook Structure

Every JS hook follows this pattern:

```js
#!/usr/bin/env node
// Brief description of what this hook does
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let inputJson;
  try { inputJson = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // ... hook logic here ...

  const result = { /* output JSON */ };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

**Key rules:**
- Shebang: `#!/usr/bin/env node`
- Always include `'use strict';`
- Read stdin as a stream (`on('data')` + `on('end')`) \u2014 never `fs.readFileSync('/dev/stdin')` (fails on Windows)
- Parse JSON with try/catch \u2014 exit 0 on parse failure (safe no-op)
- Only use Node.js built-ins: `fs`, `path`, `os`, `child_process` \u2014 **no external dependencies** (no `npm install`)
- Output via `process.stdout.write(JSON.stringify(result) + '\n')` \u2014 NOT `console.log` (which may add platform-specific line endings)
- For no-op / passthrough: call `process.exit(0)` \u2014 don\u2019t just `return` from the callback

### Configuration

```json
{
  "type": "command",
  "command": "node hooks/my-hook.js",
  "timeout": 10
}
```

No `windows:` override needed \u2014 `node` is cross-platform by default.

For agent frontmatter:
```yaml
hooks:
  Stop:
    - type: command
      command: "node hooks/my-hook.js"
```

### Using Node.js Built-ins

Hooks can use any Node.js built-in module without external dependencies:

| Module | Use case |
|--------|----------|
| `fs` | Read files (transcripts, configs, SKILL.md content) |
| `path` | Cross-platform path manipulation |
| `os` | Home directory (`os.homedir()`), platform detection |
| `child_process` | Run git commands, formatters, linters |

Example: reading a file in a hook:
```js
const fs = require('fs');
const path = require('path');
const os = require('os');

// Read a config file from the user's home directory
const configPath = path.join(os.homedir(), '.copilot', 'rules.json');
if (fs.existsSync(configPath)) {
  const rules = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  // ... use rules
}
```

### Legacy: PS1+SH Pairs

> For backward compatibility, hooks can still be written as paired `.ps1` (Windows) and `.sh` (Linux/macOS) scripts with the `windows:` override field. This pattern is **not recommended** for new hooks due to:
> - Double maintenance burden (two files per hook)
> - PowerShell 5.1 encoding issues (UTF-8 BOM, em-dash corruption)
> - Platform-specific quoting/escaping complexity
> - Harder to test and debug
>
> If you encounter existing PS1+SH hooks, consider migrating them to single JS files.

> **\u26a0\ufe0f YAML ESCAPE TRAP (still applies to any path)**: In YAML double-quoted strings, `\v` is a valid escape sequence (vertical tab). If a script name starts with `v` (e.g., `verify-claims`), the path `hooks\verify-claims.js` becomes `hooks` + vertical-tab + `erify-claims.js`. **Fix:** use forward slashes in YAML paths: `hooks/verify-claims.js`. Or double-escape: `hooks\\verify-claims.js`.

## VS Code Matcher Workaround

**CRITICAL**: VS Code currently ignores matchers in hook configuration. To filter by tool name, filter **inside the script**.

```js
#!/usr/bin/env node
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let inputJson;
  try { inputJson = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // Only run for file-editing tools
  const tool = inputJson.tool_name;
  if (tool !== 'replace_string_in_file' && tool !== 'create_file' && tool !== 'multi_replace_string_in_file') {
    process.exit(0);
  }

  // ... actual hook logic
});
```

This pattern is essential for any hook that should only trigger on specific tools.

## Common Patterns

Ready-to-use recipes (see `references/examples.md` for complete implementations):

| Pattern | Event | Purpose |
|---------|-------|---------|
| Auto-format after edit | PostToolUse | Run prettier/eslint after file changes |
| Project context injection | SessionStart | Feed project info to agent at start |
| Block dangerous commands | PreToolUse | Prevent rm -rf, DROP TABLE, etc. |
| Task completion reminder | Stop | Remind agent to produce task map |
| Subagent audit | SubagentStart | Log which subagent was invoked |
| Output format enforcement | Stop | Remind of required output template |
| Conditional git guard | PreToolUse | Different decisions per git action (commit/push/tag) |

## Conditional Hook Logic

When a hook needs different decisions for different scenarios, implement decision tree logic **inside the script** rather than using multiple hooks (since multiple hooks aggregate with "most restrictive wins", they can\u2019t implement priority/fallback logic).

Example: git guard with conventional commit validation (based on `hooks/pre-commit-guard.js`):
- `git commit` + conventional message \u2192 `allow`
- `git commit` + bad message \u2192 `deny`
- `git push` / `git tag` \u2192 `ask` (user confirmation)

### JavaScript pattern (abbreviated)

```js
#!/usr/bin/env node
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let inputJson;
  try { inputJson = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // Only intercept terminal commands
  if (inputJson.tool_name !== 'run_in_terminal' && inputJson.tool_name !== 'Bash') {
    process.exit(0);
  }

  const cmd = (inputJson.tool_input && inputJson.tool_input.command) || '';
  if (!cmd) process.exit(0);

  const gitMatch = cmd.match(/git\s+(-[^\s]+\s+)*(commit|push|tag)\b/);
  if (!gitMatch) process.exit(0);
  const action = gitMatch[2];

  let decision = 'allow';
  const contexts = [];

  if (action === 'push' || action === 'tag') {
    decision = 'ask';
    contexts.push('git ' + action + ' requires user confirmation');
  } else if (action === 'commit') {
    const msgMatch = cmd.match(/-a?m\s+["'](.+?)["']/) || cmd.match(/-a?m\s+(\S+)/);
    if (msgMatch) {
      const msg = msgMatch[1];
      if (/^(feat|fix|docs|chore|refactor|test|ci|build|perf|style|revert)(\(.+\))?(!)?\.?\:\s+.+/i.test(msg)) {
        decision = 'allow';
      } else {
        decision = 'deny';
        contexts.push('Commit must follow conventional commits (e.g. feat: add feature)');
      }
    } else {
      decision = 'deny';
      contexts.push('Commit must include -m with a conventional commit message');
    }
  }

  const result = { hookSpecificOutput: { permissionDecision: decision } };
  if (contexts.length > 0) {
    result.hookSpecificOutput.additionalContext = contexts.join('; ');
    result.hookSpecificOutput.permissionDecisionReason = contexts.join('; ');
  }
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

Key insight: a single script with branching logic is more expressive than multiple hooks, because multiple hooks can only **tighten** permissions (most restrictive wins), never **loosen** them.

## Security Best Practices

| \u274c Don\u2019t | \u2705 Do |
|----------|-------|
| Hardcode secrets in hook scripts | Use environment variables |
| Trust `tool_input` without validation | Sanitize and quote all inputs |
| Run hooks from untrusted repos without review | Audit hook scripts before use |
| Allow agent to edit hook scripts | Set `chat.tools.edits.autoApprove` to require manual approval |

Hook scripts run with **the user\u2019s permissions**. A malicious hook in a cloned repo could exfiltrate data, modify files, or run arbitrary commands. Always review hook scripts from external sources.

## Common Pitfalls

| \u274c Pitfall | \u2705 Fix |
|-----------|--------|
| Forgetting `process.exit(0)` for no-op cases | Every early-return path must call `process.exit(0)` \u2014 don\u2019t just `return` inside the `on('end')` callback |
| Not consuming all stdin data | Always use the stream pattern (`on('data')` + `on('end')`) \u2014 never `fs.readFileSync('/dev/stdin')` (fails on Windows) |
| Using `console.log` for JSON output | Use `process.stdout.write(JSON.stringify(result) + '\n')` \u2014 `console.log` may behave differently across platforms |
| Stop hook infinite loop (hook prevents stop \u2192 agent retries \u2192 hook prevents again) | Check `inputJson.stop_hook_active === true` and `process.exit(0)` if true |
| Hook returning non-JSON to stdout | Return valid JSON or nothing (exit 0) |
| Assuming matchers work in VS Code | Filter `tool_name` inside the script |
| Long-running hooks blocking the agent | Set appropriate `timeout` values |
| Agent-scoped hooks not working | Enable `chat.useCustomAgentHooks: true` in VS Code User Settings (global) |
| YAML `\v` escape in script paths | In double-quoted YAML, `\v` = vertical tab. Use forward slashes: `hooks/verify-claims.js` |
| Marker file for "retry guard" hooks | Marker auto-bypass lets agent pass on 2nd attempt without real verification \u2014 always block, let the agent demonstrate compliance |
| Claude Code terminal tool is `Bash`, not `run_in_terminal` | Check for both: `inputJson.tool_name !== 'Bash' && inputJson.tool_name !== 'run_in_terminal'` |
| PreToolUse fields at JSON top-level | Wrap in `hookSpecificOutput` \u2014 VS Code ignores top-level PreToolUse fields |
| Stop hook `decision`/`reason` only inside `hookSpecificOutput` for custom agents | VS Code treats custom agent Stop hooks as SubagentStop \u2014 needs `decision`/`reason` at **top-level**. Always output at both levels for safety |
| Claude hooks bleeding into VS Code Copilot sessions | `chat.useClaudeHooks: true` in VS Code imports ALL hooks from `~/.claude/settings.json` as global hooks \u2014 they fire for every agent. Set `chat.useClaudeHooks: false` if hooks are in agent frontmatter to avoid duplication |
| Using external npm packages in hooks | Hooks must use only Node.js built-ins (`fs`, `path`, `os`, `child_process`) \u2014 no `require('axios')` or similar. Hooks run without `npm install`. |
| Agents with ONLY Stop hooks (no PreToolUse) crash as subagents | Always include at least one PreToolUse hook entry. Use a no-op guard for read-only agents |

## Claude Code vs Copilot \u2014 Key Differences for Hook Scripts

When creating hooks that work on both platforms, be aware of these differences:

| Aspect | VS Code Copilot | Claude Code |
|--------|----------------|-------------|
| Primary script format | JavaScript (Node.js) | JavaScript (Node.js) |
| Terminal tool name | `run_in_terminal` | `Bash` (also accepts `run_in_terminal`) |
| Stop hook enforcement | For **workspace hooks** (`.github/hooks/`): `hookSpecificOutput.decision: "block"` + `reason`. For **custom agent hooks** (frontmatter): output `decision`/`reason` at **top-level** (SubagentStop format). **Best practice:** always include both top-level AND `hookSpecificOutput` for compatibility. Top-level `systemMessage` \u2014 rendered as warning in UI only (agent does NOT see it). | `decision: "block"` \u2014 blocks the agent from stopping |
| Windows config field | Not needed with JS hooks | Not needed with JS hooks |
| Global hooks location | `~/.copilot/hooks/scripts/` | `~/.claude/hooks-scripts/` |
| Matcher support | Ignored \u2014 filter inside script | Supported (regex on tool_name) |
| Hook import setting | `chat.useClaudeHooks` \u2014 when `true`, imports `~/.claude/settings.json` hooks as **global** (not agent-scoped). Default: `false` | N/A \u2014 Claude Code uses its own `~/.claude/settings.json` natively |

**Tool name check pattern** (handles both platforms):
```js
// JavaScript \u2014 works on both platforms
if (inputJson.tool_name !== 'Bash' && inputJson.tool_name !== 'run_in_terminal') {
  process.exit(0);
}
```

## Neural Link Integration

When the user\u2019s environment uses **Neural Link** as the hook dispatcher (configured via Skill Manager), newly created hooks should include a `.neural-link.json` companion file. This file lives alongside the `.js` scripts and is automatically processed during `Pull All`.

### When to Generate

Generate a `.neural-link.json` companion file when:
- The hook is being placed in a repo that uses Skill Manager distribution (has `hooks/` directory)
- The user mentions Neural Link, adaptive scoring, or learning
- Ask the user if unsure: "Should I generate Neural Link configuration for adaptive scoring?"

Do NOT generate when:
- The hook is workspace-only (`.github/hooks/`)
- The user explicitly says they don\u2019t use Neural Link

### Companion File Schema

The file MUST be named `.neural-link.json` and placed in the same `hooks/` directory as the scripts:

```
hooks/
  my-hook.js
  my-hook.neural-link.json    \u2190 companion file
```

**IMPORTANT**: The filename pattern is `{hook-name}.neural-link.json` \u2014 matching the hook script name (without extension).

```jsonc
{
  // Handler name \u2014 must match the script base name (without .js)
  "handler": "my-hook",

  // Which lifecycle events this hook handles
  "events": ["PreToolUse"],

  // Default weights per agent (agents not listed get learning.defaultWeight from config)
  "weights": {
    "implementor": 0.8,
    "researcher": 0.5,
    "orchestrator": 0.3
  },

  // Optional modifiers \u2014 contextual score adjustments
  "modifiers": [
    {
      "condition": { "field": "tool_name", "op": "in", "value": ["run_in_terminal"] },
      "adjust": "+0.2"
    }
  ],

  // Optional: training scenarios for pre-training the learner
  "trainingScenarios": [
    {
      "input": {
        "event": "PreToolUse",
        "agentSlug": "implementor",
        "tool": "run_in_terminal",
        "payload": { "command": "rm -rf /", "isBackground": false }
      },
      "mockResults": [
        { "handler": "my-hook", "action": "block", "reason": "Dangerous command" }
      ],
      "label": "should block destructive terminal commands"
    },
    {
      "input": {
        "event": "PreToolUse",
        "agentSlug": "implementor",
        "tool": "read_file",
        "payload": { "filePath": "src/index.ts" }
      },
      "mockResults": [
        { "handler": "my-hook", "action": "allow" }
      ],
      "label": "should allow safe read operations"
    }
  ]
}
```

### Weight Guidelines

| Agent Role | Typical Weight | Rationale |
|-----------|---------------|----------|
| implementor | 0.7\u20130.9 | Full tool access, most hooks are relevant |
| researcher | 0.3\u20130.6 | Read-only, fewer hooks apply |
| orchestrator | 0.2\u20130.4 | Coordination only, minimal hook relevance |
| validator | 0.3\u20130.5 | Analysis focus, some hooks apply |

### Training Scenario Guidelines

- Include at least 2 scenarios: one that triggers the hook (block/deny) and one that doesn\u2019t (allow)
- Use realistic tool names and payloads
- The `label` field is human-readable \u2014 describe the expected behavior
- The `mockResults` format matches Neural Link\u2019s `e2e-pretrain.mjs` pipeline
- More scenarios = faster learner convergence. 4-6 scenarios per hook is a good target.

## Distribution via Skill Manager

The **Skill Manager extension** can automatically distribute hook scripts alongside agents and skills. This is the recommended approach for teams and shared repos.

### How it works

1. Place hook scripts (`.js` files) in a `hooks/` directory at the repo root (alongside `agents/` and `skills/`)
2. When the extension runs `Pull All`, it syncs hooks to `~/.copilot/hooks/scripts/` \u2014 same global location referenced by agents
3. Hook scripts are always overwritten from the repo (repo is source of truth, no conflict resolution)

### Repo structure

```
my-repo/
  agents/         \u2190 agent .md files (synced to ~/.copilot/agents/)
  skills/         \u2190 skill directories (synced to ~/.copilot/skills/)
  hooks/          \u2190 hook scripts (synced to ~/.copilot/hooks/scripts/)
    pre-commit-guard.js
    stop-checklist.js
    output-format.js
    verify-claims.js
    hooks.json
```

### Configuration

The hooks directory path defaults to `hooks/` and can be overridden in `.skillmanager.json`:

```json
{
  "hooks": { "path": "hooks" }
}
```

The destination directory defaults to `~/.copilot/hooks/scripts/` and can be overridden via the `skillManager.hooksPath` VS Code setting.

### Why this matters

Without distribution, hook scripts must be manually copied to each machine. With the Skill Manager:
- **New team member** installs the extension \u2192 pulls \u2192 agents + hooks are ready
- **Hook update** pushed to repo \u2192 next pull automatically updates scripts everywhere
- **Cross-platform** \u2014 single JS file works on all operating systems, no platform-specific variants to sync

## Advanced Patterns

### Policy Engine (Declarative Rules)

Separate rules (WHAT to enforce) from the executor (HOW to enforce). The hook becomes a generic engine that reads rules from a file:

```
Hook script \u2192 reads rules.json \u2192 evaluates input \u2192 returns decision
```

Rules can be:
- Local file (`~/.copilot/rules.json`) \u2014 synced via Skill Manager
- Repo file (`.github/hooks/rules.json`) \u2014 per-project
- Both (with inheritance/merge)

This enables standardized policies across teams without editing hook scripts.

### Server-Side Validation (Tamper-Proof)

For scenarios where the LLM must not be able to bypass the validation logic, move all decision-making to an external HTTP server. The hook becomes a thin client:

```js
#!/usr/bin/env node
'use strict';
const http = require('http');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  const url = new URL(process.env.HOOK_API_URL + '/validate');
  const options = {
    hostname: url.hostname,
    port: url.port,
    path: url.pathname,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  };
  const req = http.request(options, (res) => {
    let body = '';
    res.on('data', (chunk) => { body += chunk; });
    res.on('end', () => {
      process.stdout.write(body + '\n');
    });
  });
  req.on('error', () => { process.exit(0); });
  req.write(rawInput);
  req.end();
});
```

Benefits:
- LLM cannot read server-side logic (blackbox)
- Rules update without redeploying hooks
- Centralized audit trail

Trade-offs:
- Requires network connectivity
- Adds latency (~100-200ms per hook call)
- Server must be maintained

### Compiled Blackbox Hooks

An alternative to server-side: compile the hook script to a binary (Go, Rust, C#). The LLM can see the binary exists but cannot read its logic. The binary reads secrets from environment variables at runtime, making the validation logic opaque.

Note: This is less practical than server-side for most teams but useful for offline/airgapped environments.

### Transcript-Aware Hooks (Smart Detection)

Instead of always blocking or always reminding, hooks can **analyze the session transcript** to make context-aware decisions. The VS Code Copilot transcript is a JSONL file where each line is a JSON event.

**Transcript location**: `%APPDATA%\Code\User\workspaceStorage\<id>\GitHub.copilot-chat\transcripts\*.jsonl`

The hook receives the transcript path via `transcript_path` in the stdin JSON.

**Event types in the transcript JSONL:**

| Event | Purpose |
|-------|--------|
| `session.start` | Session begins (1 per file) |
| `user.message` | User sends a message |
| `assistant.turn_start` | Agent turn begins |
| `assistant.message` | Agent response (contains `content` and `toolRequests`) |
| `tool.execution_start` | Tool invocation (contains `toolName` and `arguments`) |
| `tool.execution_complete` | Tool finished |
| `assistant.turn_end` | Agent turn ends |

Each interaction cycle: `user.message` \u2192 `assistant.turn_start` \u2192 `assistant.message` (with tool calls) \u2192 `assistant.turn_end`.

**Scoping to current interaction:**

A critical pattern \u2014 without scoping, hooks re-analyze the entire transcript and produce "sticky" false positives from old turns. Always find the **last `user.message`** and only process from there:

```js
// JavaScript \u2014 scope to current interaction
const lines = fs.readFileSync(transcriptPath, 'utf8').split('\n');
let startIdx = 0;
for (let i = lines.length - 1; i >= 0; i--) {
  if (lines[i].includes('"user.message"')) {
    startIdx = i;
    break;
  }
}
for (let i = startIdx; i < lines.length; i++) {
  const line = lines[i];
  if (!line || line.length < 20) continue;
  let evt;
  try { evt = JSON.parse(line); } catch (_) { continue; }
  // Process only events from this interaction
}
```

**Example: Smart skill-feedback (only block when feedback-protocol skills were used)**

Instead of always reminding about feedback, the hook checks if a SKILL.md with "Feedback Protocol" was actually read during the session (from `hooks/skill-feedback.js`):

```js
// Find SKILL.md reads in tool.execution_start events
for (let i = startIdx; i < lines.length; i++) {
  const line = lines[i];
  if (!line.includes('"tool.execution_start"')) continue;
  let evt;
  try { evt = JSON.parse(line); } catch (_) { continue; }
  if (evt.data && evt.data.toolName === 'read_file') {
    const fp = evt.data.arguments && evt.data.arguments.filePath;
    if (fp && /[\\/]skills[\\/]/.test(fp) && /SKILL\.md$/.test(fp)) {
      // Check actual file for "Feedback Protocol"
      if (fs.existsSync(fp)) {
        const content = fs.readFileSync(fp, 'utf8');
        if (/Feedback Protocol/.test(content)) {
          feedbackSkills.push(skillName);
        }
      }
    }
  }
}
```

**Example: File reference verification (only block for unverified paths)**

The hook collects paths accessed via tools (`read_file`, `grep_search`, `file_search`, etc.) and compares against paths mentioned in `assistant.message` content. Only unverified mentions trigger a block (from `hooks/verify-claims.js`):

```js
// Collect accessed paths from tool calls
if (evt.type === 'tool.execution_start' && fileTools.includes(evt.data.toolName)) {
  if (evt.data.arguments.filePath) accessedPaths.add(evt.data.arguments.filePath);
  if (evt.data.arguments.path) accessedPaths.add(evt.data.arguments.path);
}

// Extract mentioned paths from assistant content
const winPathRe = /([a-zA-Z]:\\(?:[\w\s._-]+\\)*[\w._-]+\.\w+)/gi;
const relPathRe = /((src|test|docs|hooks|skills)[\\\/][\w._\/-]+\.\w+)/gi;
// ... match against content, compare with accessedPaths
```

**Key design principles for transcript-aware hooks:**
- **Scope narrowly** \u2014 always use `user.message` boundary to avoid sticky false positives
- **Exit 0 when condition not met** \u2014 silent passthrough is the default; only block when there\u2019s a real finding
- **Read actual files when needed** \u2014 the transcript shows which tools were called, but checking file content (e.g., for "Feedback Protocol") requires reading the file from disk
- **Node.js built-ins only** \u2014 use `fs` for file reading, `path` for path manipulation, no external JSON parsers needed

## Companion Skills

- For creating the agents that use hooks: use **agent-creator**
- For creating skills (which cannot define hooks): use **skill-creator**

<!-- FEEDBACK:START -->
---
threshold: 5
---

## Feedback Protocol \u2014 hooks-creator

### When to Log a Review

Log a review whenever you help a user create hooks and:
- The instructions in SKILL.md were insufficient or unclear
- A hook event, configuration format, or platform behavior changed and the skill is outdated
- You had to improvise guidance not covered by the skill
- The user\u2019s resulting hook had issues traceable to missing instructions
- Cross-platform compatibility issues were encountered

### Review Format

Create a JSON file in `.vscode/skill-reviews/hooks-creator/`:

```json
{
  "date": "YYYY-MM-DD",
  "author": "dev-name",
  "type": "improvement | correction | addition",
  "section": "Section Name",
  "suggestion": "What should change",
  "context": "What prompted this feedback"
}
```

### Consolidation

When 5 reviews accumulate, summarize them into a single actionable
improvement for the skill maintainer.

<!-- FEEDBACK:END -->
