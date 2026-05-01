# Platform Reference — VS Code Copilot vs Claude Code

Complete comparison of hook capabilities between platforms. **JavaScript (Node.js) is the recommended script format for both platforms.**

---

## Lifecycle Events

| # | Event | VS Code Copilot | Claude Code | Description |
|---|-------|:---------------:|:-----------:|-------------|
| 1 | SessionStart | ✅ | ✅ | First prompt of a new session |
| 2 | UserPromptSubmit | ✅ | ✅ | User sends a message |
| 3 | PreToolUse | ✅ | ✅ | Before any tool invocation |
| 4 | PostToolUse | ✅ | ✅ | After tool completes successfully |
| 5 | PreCompact | ✅ | ✅ | Before context compaction |
| 6 | SubagentStart | ✅ | ✅ | Subagent spawned |
| 7 | SubagentStop | ✅ | ✅ | Subagent completes |
| 8 | Stop | ✅ | ✅ | Session ends |
| 9 | PermissionRequest | ❌ | ✅ | Tool needs user permission |
| 10 | PostToolUseFailure | ❌ | ✅ | Tool execution failed |
| 11 | Notification | ❌ | ✅ | Status notification sent |
| 12 | TaskCompleted | ❌ | ✅ | Task finishes |
| 13 | PreCompact | ❌ | ✅ | Before memory compaction |
| 14 | PostCompact | ❌ | ✅ | After memory compaction |
| 15 | ToolError | ❌ | ✅ | Tool throws an error |
| 16 | PreRetry | ❌ | ✅ | Before retrying failed operation |
| 17 | ContextWindowOverflow | ❌ | ✅ | Context exceeds limit |
| 18 | RateLimitHit | ❌ | ✅ | API rate limit reached |
| 19 | CacheHit | ❌ | ✅ | Prompt cache hit |
| 20 | CacheMiss | ❌ | ✅ | Prompt cache miss |

---

## Hook Types

| Type | VS Code Copilot | Claude Code | Description |
|------|:---------------:|:-----------:|-------------|
| `command` | ✅ | ✅ | Shell command execution |
| `http` | ❌ | ✅ | HTTP webhook call |
| `prompt` | ❌ | ✅ | Template-based prompt injection |
| `agent` | ❌ | ✅ | Delegate to another agent |

**VS Code limitation**: Only `command` type hooks are supported. For HTTP webhooks, wrap the HTTP call in a JS script (using Node.js built-in `http`/`https` modules).

---

## Script Format Recommendation

| Format | Recommendation | Pros | Cons |
|--------|---------------|------|------|
| **JavaScript (.js)** | ✅ **Primary — use this** | Single file, cross-platform, no encoding issues, native JSON support | Requires Node.js installed |
| PowerShell + Bash pairs | ⚠️ Legacy | Native to each OS | Double maintenance, PS 5.1 encoding bugs, quoting complexity |

**Configuration comparison:**

```json
// ✅ JavaScript — single command, no windows override needed
{
  "type": "command",
  "command": "node hooks/my-hook.js",
  "timeout": 10
}

// ⚠️ Legacy PS1+SH — requires windows override
{
  "type": "command",
  "command": "bash hooks/my-hook.sh",
  "windows": "powershell -ExecutionPolicy Bypass -File hooks\\my-hook.ps1",
  "timeout": 10
}
```

---

## Input Format Differences

| Aspect | VS Code Copilot | Claude Code |
|--------|----------------|-------------|
| Casing | camelCase | snake_case |
| Tool name field | `tool_name` | `tool_name` |
| Tool input field | `tool_input` | `tool_input` |
| Session ID | `sessionId` | `session_id` |
| Event name | `hookEventName` | `hook_event_name` |
| Working directory | `cwd` | `cwd` |

**Recommendation**: When writing cross-platform scripts, check for both casing patterns:

```js
// JavaScript — check for both platform field names
const session = inputJson.sessionId || inputJson.session_id || '';
const eventName = inputJson.hookEventName || inputJson.hook_event_name || '';
```

---

## Tool Name Differences

Some tools have different names across platforms:

| Purpose | VS Code Copilot | Claude Code |
|---------|----------------|-------------|
| Edit file | `replace_string_in_file` | `edit_file` |
| Create file | `create_file` | `write_file` |
| Run command | `run_in_terminal` | `bash` / `execute` |
| Read file | `read_file` | `read_file` |
| Search | `grep_search` | `grep` |

**Recommendation**: When filtering by tool name, include both platform variants:

```js
// JavaScript — handle both platforms
const tool = inputJson.tool_name;
if (tool === 'replace_string_in_file' || tool === 'edit_file') {
  // Handle file edit
}

// Terminal commands — check both names
if (tool !== 'run_in_terminal' && tool !== 'Bash') {
  process.exit(0); // Not a terminal command
}
```

---

## Matcher Support

| Feature | VS Code Copilot | Claude Code |
|---------|:---------------:|:-----------:|
| Tool name matcher | ❌ (ignored) | ✅ |
| File pattern matcher | ❌ (ignored) | ✅ |
| Event matcher | ✅ (by config key) | ✅ |

**VS Code workaround**: Since matchers are ignored, filter `tool_name` inside the hook script. See the "VS Code Matcher Workaround" section in SKILL.md.

---

## Async Hooks

| Feature | VS Code Copilot | Claude Code |
|---------|:---------------:|:-----------:|
| Async execution | ❌ | ✅ |
| Parallel hooks | ❌ | ✅ |
| Fire-and-forget | ❌ | ✅ |
| Timeout configurable | ✅ | ✅ |

VS Code hooks are **synchronous** — the agent waits for the hook to complete before proceeding. Keep hooks fast (under 10-15 seconds). Claude Code supports async hooks that run in parallel without blocking the agent.

---

## Configuration Locations

| Location | Platform | Scope | Precedence |
|----------|----------|-------|------------|
| `.github/hooks/*.json` | VS Code | Workspace (team-shared) | Base |
| `.agent.md` frontmatter `hooks:` | VS Code | Agent-specific | Additive |
| `.claude/settings.json` | Claude Code + VS Code | Workspace | Base |
| `~/.claude/settings.json` | Claude Code + VS Code | User global | Fallback |
| `.vscode/settings.json` `chat.useCustomAgentHooks` | VS Code | Enable agent hooks | Required for frontmatter hooks |

**Note**: The VS Code setting `chat.useCustomAgentHooks: true` must be enabled for agent frontmatter hooks to work. Workspace hooks (`.github/hooks/`) work by default.

---

## Output Format

Both platforms expect the same JSON output structure from hooks:

```json
{
  "continue": true,
  "hookSpecificOutput": {
    "systemMessage": "Message injected into context",
    "additionalContext": "Extra context for the agent",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Reason shown to user in confirmation prompt"
  }
}
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `continue` | No | `true` | Whether the agent should proceed |
| `stopReason` | No | — | Reason for stopping (if `continue: false`) |
| `systemMessage` | No | — | Message injected into agent context |
| `hookSpecificOutput` | No | — | Event-specific structured output |

---

## Quick Decision Guide

| Scenario | Recommendation |
|----------|---------------|
| VS Code only | Use `.github/hooks/*.json` + agent frontmatter with `node hooks/my-hook.js` |
| Claude Code only | Use `.claude/settings.json` with full event/type support |
| Both platforms | Use `.claude/settings.json` (read by both) with `command` type, JS scripts |
| Team hooks | `.github/hooks/` (checked into git) with JS scripts |
| Personal hooks | `~/.claude/settings.json` (user global) |
| Agent-specific behavior | Agent frontmatter `hooks:` field |
| New hooks | Always use JavaScript (.js) — single file, cross-platform |
| Migrating old hooks | Convert PS1+SH pairs to single JS files |
