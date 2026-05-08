# Subagent

Recursive in-process delegation. The model fires the **`Task`** tool with a `prompt` (and optional `agent` name); the engine builds a fresh `Agent` instance, runs its own bounded loop to completion, and returns the final assistant text as the tool's result. Up to `DEFAULT_MAX_DEPTH = 3` levels of nesting. Distinct from the **agent team** subsystem (subprocess-per-teammate via `SpawnTeammate` + filesystem mailboxes) and from the **TaskCreate/Update/Get/List** tools (in-memory progress scratchpad with no LLM involvement).

Named agents — markdown frontmatter under `.thclaws/agents/*.md` — let the model pick a pre-configured persona (custom instructions, tool subset, model override, iteration cap). The active set is computed at worker start (legacy JSON + four standard dirs + plugin dirs); subagent spawns look it up by name and the factory composes a child agent from its frontmatter + the parent's runtime state.

This doc covers: the three-tier planning hierarchy (subagent vs team vs TaskCreate), wire format + on-disk AgentDef format, `ProductionAgentFactory` build pipeline (system prompt composition, tool registry composition, propagation invariants), recursion + depth tracking, registration sites in CLI vs GUI (and the SUB3 ordering rule), cancel propagation (M6.33 SUB4), the M6.33 audit fixes in detail, the testing surface, and known gaps.

**Source modules:**
- `crates/core/src/subagent.rs` — `TOOL_NAME = "Task"`, `DEFAULT_MAX_DEPTH = 3`, `AgentFactory` trait, `ProductionAgentFactory`, `SubAgentTool` (depth/max_depth/agent_defs/cancel state, `Tool` impl)
- `crates/core/src/agent_defs.rs` — `AgentDef` schema, `AgentDefsConfig::load_with_extra`, markdown frontmatter parser, four standard agent dirs + plugin no-clobber merging
- `crates/core/src/agent.rs` — `Agent::run_turn` (subagent's own loop is the same loop), `collect_agent_turn` + `collect_agent_turn_with_cancel` (cancel-aware stream consumer used by SubAgentTool), `Agent::with_cancel` / `with_approver` / `with_permission_mode` builders consumed by `ProductionAgentFactory::build`
- `crates/core/src/repl.rs` — CLI registration site (after `--allowed-tools` / `--disallowed-tools` filter)
- `crates/core/src/shared_session.rs::run_worker` — GUI registration site (before `Agent::new` so `tools.clone()` captures the Task tool)
- `crates/core/src/default_prompts/subagent.md` — embedded "you are a sub-agent" addendum appended to the child's system prompt when `child_depth > 0`
- `crates/core/src/cancel.rs` — `CancelToken` shared between parent + subagent (Arc-internally, so `cancel.cancel()` flips the bit for both)
- `crates/core/src/plugins.rs::plugin_agent_dirs` — plugin-contributed agent directories merged additively (no-clobber)

**Cross-references:**
- [`agentic-loop.md`](agentic-loop.md) — the subagent's loop *is* `Agent::run_turn`; same per-turn pipeline (compact → stream → assemble → dispatch → loop / stop)
- [`permissions.md`](permissions.md) — M6.20 BUG H1 propagation (parent's approver + `permission_mode` flow into the child); subagent spawn always requires approval (`requires_approval = true`)
- [`context-composer.md`](context-composer.md) — the parent's full system prompt (CLAUDE.md + memory + KMS + plan + todos) is copied into the child verbatim, then optionally extended with the agent_def `instructions` body and the embedded `subagent.md` addendum
- [`commands.md`](commands.md) — agent_defs share the markdown-with-frontmatter format with prompt commands; both live under `.claude/...` + `.thclaws/...` for cross-tool compatibility
- [`plugins.md`](plugins.md) — plugin-contributed agent dirs surface via `plugin_agent_dirs()` and merge no-clobber into `AgentDefsConfig`
- [`built-in-tools.md`](built-in-tools.md) §Task — Task tool surface (concise)

---

## 1. Concept

Subagent is the **mid-ceremony delegation tool** in thClaws's three-tier hierarchy:

```
mechanism      │  process model       │  state sharing       │  use when
───────────────┼──────────────────────┼──────────────────────┼─────────────────────
TaskCreate /   │  in-memory only      │  none (own store)    │  ephemeral progress
Update / Get / │  no LLM call         │                      │  tracking inside one
List           │                      │                      │  process
───────────────┼──────────────────────┼──────────────────────┼─────────────────────
Task           │  in-process recursive│  inherits parent's   │  bounded subtask
(this doc)     │  Agent::run_turn     │  tools / system /    │  needing a fresh
               │  call (same thread)  │  approver /          │  conversation
               │                      │  permission_mode /   │  history; up to 3
               │                      │  cancel              │  levels deep
───────────────┼──────────────────────┼──────────────────────┼─────────────────────
SpawnTeammate +│  subprocess per      │  filesystem mailboxes│  long-lived parallel
team mailboxes │  teammate (thclaws -p│  (.thclaws/team/...) │  agents with their
               │  per process)        │  no shared memory    │  own session each
```

The model picks based on what the work needs:
- **Internal counters (turn-level scratchpad), no LLM involvement** → `TaskCreate`. Lives in `Arc<Mutex<TaskStore>>`; gone on restart.
- **"Spawn an isolated researcher with a clean history but my tools/restrictions"** → `Task`. Same process, same approver, same sandbox. Returns a single text answer to the caller.
- **"Spawn five teammates in parallel that each take 30 minutes"** → `SpawnTeammate`. Subprocess each, JSON mailboxes for coordination, separate sessions visible in the Team tab.

If the model picks wrong, the user can correct mid-conversation. The system prompt's framing (see §10) and the tool descriptions both nudge toward the right choice.

### Why a separate tool from `SpawnTeammate`?

The two tools COULD be merged, but the cost models are very different:

| | Task (subagent) | SpawnTeammate (team) |
|---|---|---|
| Spawn cost | Microseconds (in-process Agent::new) | Hundreds of ms (fork + exec + provider handshake) |
| Memory | Shares parent's tool registry Arcs | New process; full WorkerState |
| Crash blast radius | Same process — child panic kills parent | Subprocess crash → parent observes via mailbox status |
| Visibility | Single chat surface; tool result text | Team tab pane per teammate, separate session JSONL |

Subagents are for "bounded helper" work (research, summarize, analyze a file). Teammates are for "long-running parallel worker" work (build N services in parallel, run a long migration). Mixing them up burns cost in the wrong direction.

---

## 2. Wire format

### Input schema

```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "Short label for the sub-task (shown in logs)."
    },
    "prompt": {
      "type": "string",
      "description": "The full instruction for the sub-agent."
    },
    "agent": {
      "type": "string",
      "description": "Optional named agent from agents.json. Available: <names>"
    }
  },
  "required": ["prompt"]
}
```

`prompt` is the only required field. `description` is shown in logs / approval modals so the user knows what the spawn is for. `agent` picks a named definition from `AgentDefsConfig` — the description string is rebuilt each call from the loaded names so the model sees the live list (e.g. *"Available: researcher, reviewer, coder"*).

### Output

The subagent's final assistant message becomes the tool's `Ok(String)` result. If the subagent produced no text (only tool calls, then stopped) the wrapper returns `Err(Error::Agent("sub-agent returned empty response"))` rather than `Ok("")` — empty results are a model-side bug we surface explicitly.

### Approval gate

`SubAgentTool::requires_approval` returns **true unconditionally**. Every Task spawn pops an approval modal in Ask mode (every spawn auto-approves in Auto mode). There's no per-call deny-list; the cost / blast-radius is high enough that "always confirm" is the conservative default. The approver is the parent's own `Arc<dyn ApprovalSink>` (see [`permissions.md`](permissions.md) — M6.20 BUG H1 wired this propagation).

---

## 3. AgentDef on-disk format

Markdown file with YAML frontmatter. Body becomes `instructions` (appended to the parent's system prompt as `# Agent instructions\n<body>`).

```markdown
---
name: researcher
description: Researches topics thoroughly
model: claude-sonnet-4-5
tools: Read, Grep, Glob, WebSearch
disallowedTools: Bash, Write, Edit
maxTurns: 20
color: blue
permissionMode: ask
---
You are a research agent. Search the codebase and the web for relevant
context, summarize findings with file path + line number citations, and
return a single self-contained answer.
```

| Field | Type | Notes |
|---|---|---|
| `name` | string | Identifier for `Task({"agent": "..."})`. Falls back to filename stem if absent. |
| `description` | string | Surface text (currently unused at runtime; reserved for catalog UIs). |
| `model` | string \| null | Override the parent's model. **Used verbatim** — no alias resolution (SUB5, deferred). |
| `tools` | comma-list | Allow-list. Empty = all of parent's `base_tools`. Non-empty = intersect with parent's. |
| `disallowedTools` / `disallowed_tools` | comma-list | Deny-list. Removed AFTER the allow-list filter (M6.33 SUB2 fix). |
| `maxTurns` / `max_iterations` | int | Per-turn budget for the subagent's own loop. Default 200. |
| `color` | string | Terminal color hint for team-tab rendering (subagents don't currently render here). |
| `isolation` | string | Reserved for the team subsystem; ignored by Task. |
| `permissionMode` / `permission_mode` | string | Reserved; subagents inherit parent's mode (M6.20 BUG H1) regardless of this field today. |

The body (everything after the closing `---`) is parsed by `crate::memory::parse_frontmatter` and stored as `instructions`. Empty body = no addendum (child uses parent's system prompt unchanged).

### Load order

`AgentDefsConfig::load_with_extra` walks five sources, **later entries override earlier ones on name collision**:

1. `~/.config/thclaws/agents.json` — legacy JSON (single file with `agents: [...]` array)
2. `~/.claude/agents/*.md` — user-global Claude Code dir (compatibility)
3. `~/.config/thclaws/agents/*.md` — user-global thClaws dir
4. `.claude/agents/*.md` — project Claude Code dir
5. `.thclaws/agents/*.md` — project thClaws dir (highest priority)

Plus any plugin-contributed dirs returned by `plugins::plugin_agent_dirs()`, merged via `load_md_dir_no_clobber` — plugins **never shadow** a user/project agent of the same name (the existing entry wins).

This matches the [`commands.md`](commands.md) + [`memory.md`](memory.md) precedence model: project beats user, user beats global, plugins are additive.

---

## 4. `ProductionAgentFactory`

The factory consumed by `SubAgentTool` to construct the child agent. One instance per worker (CLI or GUI), shared across recursive depths. Promoted from the CLI-only `ReplAgentFactory` in M6.33 (SUB1) so the GUI worker uses the same code path.

```rust
pub struct ProductionAgentFactory {
    pub provider: Arc<dyn Provider>,
    pub base_tools: ToolRegistry,        // snapshot of parent's filtered registry (SUB3)
    pub model: String,                   // parent's model (agent_def.model overrides)
    pub system: String,                  // parent's full system prompt
    pub max_iterations: usize,           // parent's iteration cap (agent_def.maxTurns overrides)
    pub max_depth: usize,                // recursion ceiling
    pub agent_defs: AgentDefsConfig,     // for nested Task lookups
    pub approver: Arc<dyn ApprovalSink>, // M6.20 BUG H1 — parent's gate
    pub permission_mode: PermissionMode, // M6.20 BUG H1 — parent's mode
    pub cancel: Option<CancelToken>,     // M6.33 SUB4 — parent's cancel signal
}
```

### `build(prompt, agent_def, child_depth)` pipeline

```
1. RESOLVE MODEL
   model = agent_def.model.unwrap_or(parent.model)

2. COMPOSE SYSTEM PROMPT
   system = parent.system
   if agent_def && !agent_def.instructions.is_empty():
       system += "\n\n# Agent instructions\n" + agent_def.instructions
   if child_depth > 0:
       system += embedded subagent.md ("you are a sub-agent...")

3. RESOLVE max_iterations
   max_iter = agent_def.max_iterations.unwrap_or(parent.max_iterations)

4. COMPOSE TOOL REGISTRY  (M6.33 SUB2 fix)
   tools = if agent_def.tools.is_empty():
              parent.base_tools.clone()
           else:
              ToolRegistry::new()
              for name in agent_def.tools:
                  if let Some(t) = parent.base_tools.get(name): tools.register(t)
   if agent_def:
       for name in agent_def.disallowed_tools:    ← pre-fix this loop didn't exist
           tools.remove(name)

5. ADD RECURSIVE Task TOOL  (M6.33 SUB4 cancel propagation)
   if child_depth < max_depth:
       child_factory = ProductionAgentFactory { …, cancel: self.cancel.clone() }
       child_tool = SubAgentTool::new(child_factory)
                       .with_depth(child_depth)
                       .with_max_depth(max_depth)
                       .with_agent_defs(self.agent_defs.clone())
       if let Some(c) = self.cancel:
           child_tool = child_tool.with_cancel(c)
       tools.register(child_tool)
   // else: leaf has no Task tool — chain terminates

6. BUILD AGENT  (M6.20 BUG H1 + M6.33 SUB4)
   agent = Agent::new(provider, tools, model, system)
              .with_max_iterations(max_iter)
              .with_approver(parent.approver)
              .with_permission_mode(parent.permission_mode)
   if let Some(c) = self.cancel:
       agent = agent.with_cancel(c)
   return agent
```

### Propagation invariants

The factory enforces six things flowing parent → child:

| Field | Source | Why |
|---|---|---|
| `provider` | parent | Same wire client (auth, base URL, headers). Avoids spinning up a duplicate. |
| `system` | parent verbatim + agent_def addendum | Child sees the same CLAUDE.md / memory / KMS / plan / todos context. |
| `tools` (filtered) | parent's filtered `base_tools` ∩ agent_def filters | SUB3: child can't access tools the parent was forbidden from using. |
| `approver` | parent's Arc | M6.20 BUG H1: child can't bypass Ask mode. Same Arc → yolo flag set on parent propagates instantly. |
| `permission_mode` | parent | M6.20 BUG H1: prevents the dispatch fallback at `agent.rs:1112` from promoting Ask back to Auto for the child. |
| `cancel` | parent (when present) | M6.33 SUB4: ctrl-C reaches a runaway subagent's retry-backoff sleeps + stream consumer. |

### What's NOT propagated

| Field | Behavior | Why |
|---|---|---|
| `history` | Child starts empty | Subagents have a fresh conversation by design — that's the point. |
| `budget_tokens` | Re-derived from child's effective model | Different model (via `agent_def.model`) gets its own context window. |
| `thinking_budget` | Default `None` | No agent_def field for it today (gap). |

---

## 5. `SubAgentTool::call` flow

```rust
async fn call(&self, input: Value) -> Result<String> {
    if self.depth >= self.max_depth {
        return Err(Error::Agent(format!(
            "sub-agent recursion limit reached (depth {}/{})",
            self.depth, self.max_depth
        )));
    }
    let prompt = req_str(&input, "prompt")?.to_string();
    let agent_name = input.get("agent").and_then(Value::as_str);
    let agent_def = agent_name.and_then(|name| self.agent_defs.get(name));
    if agent_name.is_some() && agent_def.is_none() {
        return Err(Error::Agent(format!("unknown agent '{}'. Available: {}", ...)));
    }
    let child_depth = self.depth + 1;
    let agent = self.factory.build(&prompt, agent_def, child_depth).await?;
    let stream = agent.run_turn(prompt);
    let outcome = collect_agent_turn_with_cancel(stream, self.cancel.clone()).await?;
    if outcome.text.is_empty() {
        Err(Error::Agent("sub-agent returned empty response".into()))
    } else {
        Ok(outcome.text)
    }
}
```

Five gates / steps:

1. **Depth check** — fires *before* parsing input. A leaf subagent (depth = max_depth) refuses cleanly without spending tokens.
2. **Input parse** — `prompt` required; `agent` optional. Unknown `agent` name → friendly error listing available names.
3. **Agent build** — delegates to the factory (§4).
4. **Run** — `agent.run_turn(prompt)` returns an `AgentEvent` stream; same per-turn pipeline as the top-level agent (see [`agentic-loop.md`](agentic-loop.md)). The subagent's own internal loop runs to its own stop condition (no more tool calls / max_iterations hit / cancel).
5. **Collect** — `collect_agent_turn_with_cancel` consumes the stream into an `AgentTurnOutcome`. With cancel = `Some(token)`, it `tokio::select!`s each iteration between the next stream event and `token.cancelled()` — ctrl-C aborts mid-stream rather than waiting for natural completion.

### Stop conditions for the subagent's loop

Same as any `Agent::run_turn`:

- No more `tool_use` blocks in the assistant's last message → natural turn-end
- `max_iterations` reached → forced stop (returns the last assistant text as the result)
- `CancelToken::cancel()` fires → aborts the stream consumer → propagates `Err(Error::Agent("cancelled by user"))` up to the parent's tool dispatch

There's no "subagent timeout" beyond `max_iterations`. Long-running tools inside the subagent (e.g. a 30 s bash command) block the whole subagent + parent until they complete or the cancel signal arrives.

---

## 6. Recursion semantics

`max_depth = 3` by default. A subagent at depth 1 can spawn one at depth 2, which can spawn one at depth 3 — but the depth-3 leaf has **no Task tool registered** (step 5 of `build` skips registration when `child_depth >= max_depth`), so the chain terminates structurally, not via a runtime error.

```
parent (depth 0)              ← run_repl / build_state
  └── Task → child (depth 1)  ← Task tool present
        └── Task → child (2)  ← Task tool present
              └── Task → child (3)  ← NO Task tool — leaf
```

If the depth-3 leaf tries to invoke Task anyway (e.g. via a tool-name typo it hallucinates), the dispatcher returns the standard "unknown tool" ToolResult — same surface as any other typo, no special "you've hit the recursion limit" affordance at that level.

The depth-check at `SubAgentTool::call` line 1 is a defense-in-depth backstop for the case where someone manually constructs a `SubAgentTool::new(factory).with_depth(3).with_max_depth(3)` and tries to call it directly. In production, structural omission (step 5) does the work first.

### Why 3?

Empirical: deeper than 3 is almost always the model losing track of what it's delegating. Exposed via `DEFAULT_MAX_DEPTH` constant for future tuning, but no config knob today.

---

## 7. Registration sites

Two consumers wire `ProductionAgentFactory` + `SubAgentTool` into a `tool_registry`:

### CLI — `repl.rs::run_repl`

```rust
// 1. Build base registry with built-ins + tasks + MCP tools
// 2. Apply --allowed-tools / --disallowed-tools filter to tool_registry
// 3. Snapshot the FILTERED registry as base_tools
// 4. Register Task with the filtered base_tools
{
    let plugin_agent_dirs = plugins::plugin_agent_dirs();
    let agent_defs = AgentDefsConfig::load_with_extra(&plugin_agent_dirs);
    let base_tools = tool_registry.clone();    // ← captures FILTERED registry
    let factory = Arc::new(ProductionAgentFactory {
        provider: provider.clone(),
        base_tools,
        model: config.model.clone(),
        system: system.clone(),
        max_iterations: config.max_iterations,
        max_depth: subagent::DEFAULT_MAX_DEPTH,
        agent_defs: agent_defs.clone(),
        approver: approver.clone(),
        permission_mode: perm_mode,
        cancel: None,                          // ← CLI: no cancel plumbing
    });
    tool_registry.register(Arc::new(
        SubAgentTool::new(factory)
            .with_depth(0)
            .with_agent_defs(agent_defs),
    ));
}
```

The **ordering** is the M6.33 SUB3 fix — pre-fix the registration ran *before* the tool-filter, so `base_tools` snapshotted the unfiltered set: `thclaws --disallowed-tools Bash` removed Bash from the parent's surface but the subagent's `base_tools` still had it (privilege-escalation primitive).

CLI `cancel: None` because the CLI loop doesn't wire a `CancelToken` anywhere — ctrl-C in the CLI is signal-handled at the rustyline layer, not bridged into a token. Bridging would require touching the REPL signal handler; deferred (SUB9).

### GUI — `shared_session.rs::run_worker`

```rust
let perm_mode = if config.permissions == "auto" {
    PermissionMode::Auto
} else {
    PermissionMode::Ask
};
{
    let agent_defs = AgentDefsConfig::load_with_extra(&plugins::plugin_agent_dirs());
    let factory = Arc::new(ProductionAgentFactory {
        provider: provider.clone(),
        base_tools: tools.clone(),
        model: config.model.clone(),
        system: system.clone(),
        max_iterations: config.max_iterations,
        max_depth: subagent::DEFAULT_MAX_DEPTH,
        agent_defs: agent_defs.clone(),
        approver: approver.clone(),
        permission_mode: perm_mode,
        cancel: Some(cancel.clone()),          // ← GUI: full cancel propagation
    });
    tools.register(Arc::new(
        SubAgentTool::new(factory)
            .with_depth(0)
            .with_agent_defs(agent_defs),
    ));
}
let mut agent = Agent::new(provider, tools.clone(), &config.model, &system)
    .with_approver(approver.clone())
    .with_cancel(cancel.clone());
agent.permission_mode = perm_mode;
```

Two GUI-specific differences from CLI:

- **Registration runs BEFORE `Agent::new`** so `tools.clone()` snapshots a registry that already contains Task. Pre-M6.33 (SUB1) the GUI never called register at all — every `Task(...)` from the chat tab returned "unknown tool" silently to the user.
- **`cancel: Some(cancel.clone())`** so a worker-level cancel (fired from the sidebar Cancel button or the per-line `/cancel` slash) reaches the subagent's stream consumer. CancelToken is `Arc<AtomicBool>` internally — same atomic, same Arc count grows, `cancel.cancel()` flips the bit observed by every clone.

The GUI doesn't expose `--allowed-tools` / `--disallowed-tools` flags, so SUB3 ordering doesn't apply here today. **If/when** Settings exposes a tool-filter, the same "register Task AFTER filter" rule must be honored.

---

## 8. Cancel propagation (M6.33 SUB4)

Pre-fix: parent's `CancelToken` reached its own retry-backoff sleeps (M6.17 H1 + M3) but the subagent had no cancel — `collect_agent_turn(stream)` consumed the entire stream regardless of ctrl-C. Worst-case: subagent in iteration 50 of 200 with a 30 s tool timeout → user waits ~25 minutes for the subagent to finish before the next prompt is responsive.

Post-fix flow:

```
GUI worker             parent Agent           SubAgentTool         child Agent
─────────              ────────────           ────────────         ───────────
cancel_tk ──with_cancel──> agent
   │
   │ build_state registers Task with cancel: Some(cancel_tk)
   │       │
   │       └────────────────────────────> SubAgentTool { cancel: Some(cancel_tk) }
   │                                          │
   │                                          │ on call:
   │                                          │   factory.build(...) returns:
   │                                          └─────────────────────────────────> child agent
   │                                              .with_cancel(cancel_tk)         (same Arc)
   │
   │ user clicks Cancel → cancel_tk.cancel() → AtomicBool flips
   │                                          │
   │                                          ├── parent's retry sleep observes → Err
   │                                          ├── child's retry sleep observes → Err
   │                                          └── collect_agent_turn_with_cancel
   │                                              (subagent's stream consumer):
   │                                                tokio::select! {
   │                                                  ev = stream.next() => …,
   │                                                  _ = cancel_tk.cancelled() =>
   │                                                      return Err("cancelled by user")
   │                                                }
```

`collect_agent_turn` (the cancel-less variant) is now a thin wrapper: `collect_agent_turn_with_cancel(stream, None)`. The select branch only arms when `cancel.is_some()`, so the no-cancel path has no overhead.

**CLI gap**: `cancel: None` means the CLI subagent flow is uninterruptible. ctrl-C / `/cancel` in the CLI doesn't reach the subagent. Deferred (SUB9) — fix would bridge CLI signal handling into a CancelToken.

---

## 9. M6.33 audit fixes (recap)

Four MED-severity bugs shipped in M6.33 (`dev-log/148-subagent-m6-33-audit-fixes.md`):

| Bug | Severity | Symptom | Fix site |
|---|---|---|---|
| SUB1 | MED | GUI subagent calls returned "unknown tool: Task" silently | `shared_session.rs::run_worker` registration block |
| SUB2 | MED | `agent_def.disallowed_tools` parsed but never applied | `subagent.rs::ProductionAgentFactory::build` step 4 deny-list loop |
| SUB3 | MED | Subagent's `base_tools` held tools the parent was forbidden from (privilege escalation) | `repl.rs::run_repl` reordering: register Task AFTER tool filter |
| SUB4 | MED | ctrl-C reached parent but subagent ran to completion (10+ min worst case) | `subagent.rs` cancel field + `agent.rs::collect_agent_turn_with_cancel` + GUI registration passes `Some(cancel)` |

Pre-M6.33 the CLI had its own `ReplAgentFactory` and the GUI had no factory at all. Consolidating into `ProductionAgentFactory` (one struct, two consumers) made the SUB1 + SUB4 fixes possible without parallel implementations.

---

## 10. System-prompt framing

The embedded `subagent.md` prompt is appended to the child's system prompt **only when `child_depth > 0`** — i.e. the depth-0 top-level agent never sees it. The addendum:

```
# Sub-agent mode

You were launched via the Task tool as an autonomous sub-agent. You run with
your own conversation history and return a single final answer to your caller.

- Do NOT ask the caller follow-up questions — make reasonable assumptions and proceed.
- Do NOT loop or poll. When your bounded subtask is complete, produce your final answer and stop.
- Your final assistant message IS the response delivered back to the caller, so make it
  self-contained: summarize what you did, key findings, and any file paths the caller should read.
- Tool calls are allowed; recursion is allowed up to the configured depth limit.
```

The four bullets pin behaviors that subagents otherwise drift on:
- "make assumptions, don't ask" — there's no UI for the subagent to ask the user; questions would deadlock
- "produce your final answer and stop" — the model's natural inclination is to keep iterating
- "self-contained" — the parent only sees the final assistant text, no tool-result stream
- "recursion is allowed" — surfaces that nested Task is a valid primitive (some models won't try without explicit permission)

The parent's system prompt (CLAUDE.md / memory / KMS / plan / todos) is preserved verbatim because the subagent often needs the same project context to do its job.

The agent_def `instructions` body is appended between the parent system and the addendum, framed as `# Agent instructions\n<body>`. Order: parent system → agent instructions → "you are a sub-agent" addendum.

---

## 11. Testing surface

`subagent::tests` (subagent.rs:313) has 6 unit tests:

| Test | What it pins |
|---|---|
| `sub_agent_returns_text` | Happy path — single-turn subagent returns its assistant text as the tool's `Ok` result |
| `depth_limit_enforced` | A `with_depth(3).with_max_depth(3)` tool refuses with "recursion limit" before parsing input |
| `unknown_agent_errors` | `{"agent": "nonexistent"}` returns a friendly error listing available names |
| `named_agent_passed_to_factory` | `agent_def` reaches `factory.build`'s `agent_def: Option<&AgentDef>` argument when looked up by name |
| `production_factory_applies_agent_def_disallowed_tools` (M6.33 SUB2) | A child built with `agent_def.disallowed_tools = [Bash]` has no Bash in its tool registry |
| `production_factory_propagates_cancel_token` (M6.33 SUB4) | `factory.cancel.cancel()` flips the child agent's cancel atom (Arc-shared, same instance) |

Plus `subagent_factory_propagates_approver_and_permission_mode` in `repl::tests` (the M6.20 BUG H1 regression test) — pins that `ProductionAgentFactory.build` propagates the parent's approver Arc and `permission_mode`. Asserts via `Arc::strong_count` growth (proves the factory cloned rather than dropped the Arc).

SUB1 + SUB3 don't have unit tests because they're integration-level (CLI startup ordering / GUI worker startup). Verified by code inspection.

`Agent.tools` and `Agent.cancel` are `pub(crate)` so the SUB2 + SUB4 regression tests can inspect them. The `pub(crate)` is deliberate — they're not part of the public API, just visible to in-crate tests.

---

## 12. Known gaps (deferred to future sprints)

LOW-severity items surfaced in the M6.33 audit but not fixed:

- **SUB5** — `agent_def.model` used verbatim. No alias resolution. An agent def saying `claude-sonnet-4-6` runs on Sonnet even if the parent was using a routed alias like `openrouter/anthropic/claude-sonnet-4`. Defer until model-alias normalization is centralized.
- **SUB6** — `agent_def.max_iterations` used verbatim. An agent def claiming `max_iterations: 1000` runs 1000 iterations even if the parent is configured for 50. No "cap at parent" policy today.
- **SUB7** — No per-subagent token budget. Child uses parent's compaction threshold; subagents with very different context profiles get the same trigger.
- **SUB8** — Recursive `child_factory` shares parent's `system` — only the immediate child gets the agent_def addendum. A grandchild spawned via Task reverts to the parent's system. Probably correct (grandchild isn't running the named agent), but worth documenting.
- **SUB9** — CLI cancel plumbing missing (covered in §8). Subagents in the CLI are uninterruptible.
- **SUB10** — `requires_approval` always true — every spawn pops an approval modal. No way to "yolo" a chain of agent_defs in one decision.
- **SUB11** — No per-agent metrics. Subagent token usage rolls into parent's counters; operators can't see "how much did the researcher agent cost this week."

---

## 13. What lives where (source-line index)

| Concern | File | Symbol / line |
|---|---|---|
| Tool name + max depth constants | `subagent.rs` | `TOOL_NAME`, `DEFAULT_MAX_DEPTH` |
| Factory trait | `subagent.rs` | `AgentFactory` |
| Production factory struct | `subagent.rs` | `ProductionAgentFactory` |
| Factory build pipeline | `subagent.rs` | `impl AgentFactory for ProductionAgentFactory::build` |
| Tool struct + state | `subagent.rs` | `SubAgentTool` |
| Builder methods | `subagent.rs` | `with_depth`, `with_max_depth`, `with_agent_defs`, `with_cancel` |
| Tool::call dispatch | `subagent.rs` | `impl Tool for SubAgentTool::call` |
| Cancel-aware stream consumer | `agent.rs` | `collect_agent_turn_with_cancel` |
| Backwards-compat wrapper | `agent.rs` | `collect_agent_turn` (delegates with `None`) |
| AgentDef schema | `agent_defs.rs` | `AgentDef` |
| Load + merge | `agent_defs.rs` | `AgentDefsConfig::load_with_extra` |
| Frontmatter parser | `agent_defs.rs` | `parse_agent_md` |
| Standard agent dirs | `agent_defs.rs` | `agent_dirs` (5 entries) |
| Plugin no-clobber merge | `agent_defs.rs` | `load_md_dir_no_clobber` |
| Embedded "you are a sub-agent" prompt | `default_prompts/subagent.md` | (whole file) |
| CLI registration site | `repl.rs::run_repl` | block after `--disallowed-tools` filter |
| GUI registration site | `shared_session.rs::run_worker` | block before `Agent::new(provider, tools.clone(), …)` |
| Plugin agent dirs accessor | `plugins.rs` | `plugin_agent_dirs` |
| CancelToken | `cancel.rs` | `CancelToken::new`, `cancel`, `is_cancelled`, `reset`, `cancelled()` future |
