# Context compaction

How thClaws keeps a growing conversation under the model's context window. Every turn the agent loop estimates the message-history token count, deducts the system-prompt + tool-def overhead from the model's effective window, and — if over budget — drops the oldest messages while preserving `ToolUse` ↔ `ToolResult` pairs. If a single surviving message still exceeds the budget, an in-place truncation rescue cuts each Text / ToolResult block at a char boundary and appends a `[...truncated by thClaws]` notice. A separate LLM-summarized variant (`compact_with_summary`, invoked by `/compact`) keeps the last 4 messages verbatim and asks the provider to summarize the older ones into a synthetic user message. Plan mode adds two step-boundary variants (`compact_for_step_boundary` / `clear_for_step_boundary`) that fire at step transitions. All compaction events are persisted as `CompactionEvent` checkpoints in the session JSONL so `/load` reconstructs the trimmed view.

This doc consolidates the compaction story that is otherwise spread across [`agentic-loop.md`](agentic-loop.md) §5, [`context-composer.md`](context-composer.md) §5, [`plan-mode.md`](plan-mode.md) §9.3, [`sessions.md`](sessions.md) §8, [`prompt-cache.md`](prompt-cache.md) §8, and [`hooks.md`](hooks.md). Each of those still contains the canonical detail for its own subsystem; this file is the single-jump entry point for "how does compaction work?"

**Source modules:**
- `crates/core/src/compaction.rs` — `compact`, `estimate_messages_tokens`, `truncate_oversized_message`, `compact_with_summary`, `compact_for_step_boundary`, `clear_for_step_boundary`
- `crates/core/src/agent.rs` — `Agent::run_turn` / `run_turn_multipart` per-turn deduction + compact call site, `pre_compact` / `post_compact` hook fires
- `crates/core/src/tokens.rs` — `estimate_tokens` (chars/4 heuristic, conservative round-up)
- `crates/core/src/shared_session.rs::drive_turn_stream` — Ralph driver step-boundary compaction site
- `crates/core/src/session.rs` — `Session::append_compaction_to`, `CompactionEvent`, replay logic in `load_from`
- `crates/core/src/default_prompts/compaction.md` — the user-message prompt sent to the summarizer
- `crates/core/src/default_prompts/compaction_system.md` — the system prompt for the summarizer
- `crates/core/src/hooks.rs` — `fire_compact`, `HookEvent::PreCompact`, `HookEvent::PostCompact`

**Cross-references:**
- [`agentic-loop.md`](agentic-loop.md) §5 — per-turn pipeline owner; this doc duplicates its compaction section
- [`context-composer.md`](context-composer.md) §5 — budget arithmetic (system-prompt deduction + 1 KiB tool-def reserve)
- [`plan-mode.md`](plan-mode.md) §9.3 — step-boundary compaction inside the Ralph driver
- [`sessions.md`](sessions.md) §8 — JSONL `CompactionEvent` persistence + replay
- [`prompt-cache.md`](prompt-cache.md) §8 — why `compact_with_summary` invalidates the cache breakpoint
- [`hooks.md`](hooks.md) — `pre_compact` / `post_compact` lifecycle hooks

---

## 1. The five entry points

| Function | Trigger | Strategy | Persists checkpoint? |
|---|---|---|---|
| `compact` | Every turn in `run_turn_multipart` (no-op if under budget) | Drop-oldest, preserve tool pairs, min-1 truncation rescue | No — every-turn no-op fast path doesn't deserve a checkpoint |
| `compact_with_summary` | User invokes `/compact` | LLM summarizes older msgs, prepends as synthetic user message; keeps last 4 verbatim | Yes — `Session::append_compaction_to` |
| `compact_for_step_boundary` | Plan-mode step transition (M6.2 default) | Structural shrink: preserve plan-tool tool_results, replace others with placeholders | Yes |
| `clear_for_step_boundary` | Plan-mode step transition with `plan_context_strategy = "clear"` (M6.4) | Wipe history except first user message | Yes |
| `truncate_oversized_message` | Internal rescue inside `compact` (M6.17 BUG M1) | Char-boundary in-place truncation of each Text / ToolResult block + notice | N/A (called by `compact`) |

---

## 2. Per-turn `compact` — drop-oldest with two invariants

`compaction.rs::compact(messages, budget_tokens)` — synchronous drop-oldest. Two invariants:

1. **Tool-pair preservation.** Never splits a `ToolUse` from its `ToolResult`. If dropping the oldest message would orphan a result, the result is dropped too in the same step.
2. **At-least-one-message guarantee + truncation rescue (M6.17 BUG M1).** The drop loop stops with at least the last message. If that single message still exceeds budget, `truncate_oversized_message` truncates each Text / ToolResult block in-place (char-boundary safe via `is_char_boundary` walk-back) and appends:

   ```
   [...truncated by thClaws: original content exceeded the N token context budget]
   ```

   Pre-M6.17 the loop returned the single oversize message intact and the provider responded with HTTP 400 "context length exceeded." Post-fix the provider always sees a request that fits.

`estimate_messages_tokens` walks the list summing `tokens.rs::estimate_tokens` results — chars/4, always rounds up. Conservative for English, less safe for CJK / Thai. The 1 KiB tool-def reserve (§3) provides safety margin; the truncation rescue handles the catastrophic case.

---

## 3. Per-turn budget deduction (M6.18 BUG H1)

`Agent::new` reads the model's effective context window:

```
override (project / user settings.json modelOverrides)
  → catalogue lookup_exact(model)
    → catalogue provider_default(provider)
      → GLOBAL_FALLBACK = 128_000
```

Stored as `Agent::budget_tokens`.

The agent loop subtracts the system-prompt size and a 1 KiB tool-def reserve from that budget BEFORE compacting:

```rust
let system_tokens = crate::tokens::estimate_tokens(&system);
let tools_reserve_tokens = 1024;
let messages_budget = budget_tokens
    .saturating_sub(system_tokens)
    .saturating_sub(tools_reserve_tokens);
compact(&h, messages_budget)
```

**Why this exists.** Pre-fix, `compact()` got the full `budget_tokens`. A 50K system prompt + 128K "fitted" messages = 178K request → HTTP 400 from the provider. Post-fix the messages get squeezed harder so the total request fits.

**Why 1 KiB reserve.** Tool definitions are part of the request payload and count against the provider's context window. The reserve is a coarse pad — exact tool-def token cost varies by registry size, but 1 KiB covers the typical case without forcing a per-turn re-estimate.

---

## 4. `compact_with_summary` — the `/compact` slash

`compaction.rs:111`. Invoked by the `/compact` slash command in REPL or GUI. Strategy:

1. Split history at `len - 4`. The last 4 messages stay verbatim.
2. Render the older messages into a transcript blob.
3. Call the current provider with:
   - System prompt: `default_prompts/compaction_system.md` (the summarizer's role)
   - User message: `default_prompts/compaction.md` (the actual "summarize the following" instruction) + the transcript blob
4. The summary text is wrapped in a synthetic `Message { role: User, content: [Text(summary)] }` and prepended to the kept-verbatim tail.
5. Returns a new `Vec<Message>` (summary + recent 4).

**Failure mode.** If the summarizer call errors or returns empty, falls back to `compact(messages, budget_tokens)` — drop-oldest. The user gets a "compaction failed, dropped oldest instead" notice.

**Why keep 4 verbatim?** The most recent turn typically contains tool_use / tool_result pairs the model will reference next turn. Summarizing them loses the structured ids the model needs.

---

## 5. The compact min-1 rescue (M6.17 BUG M1)

Detail of `compact` step 2 above, called out separately because it's the historically-most-painful failure mode.

`truncate_oversized_message(msg, budget)` walks the message's content blocks:
- `Text(s)` — truncate `s` to roughly `budget * 4` chars (chars/4 inverse of `estimate_tokens`), walking back to the nearest `is_char_boundary` to avoid splitting UTF-8.
- `ToolResult { content }` — same treatment per block inside the result.
- `ToolUse` — left intact (the input JSON is small relative to outputs; truncating it would corrupt the JSON).
- Other variants — pass through.

After truncation, appends a single Text block with the `[...truncated by thClaws: original content exceeded the N token context budget]` notice so the model can read what happened and adjust strategy (e.g. re-issue a narrower tool call).

---

## 6. Plan-mode step-boundary compaction (M6.2 / M6.4)

Fires inside the Ralph driver in `shared_session.rs::drive_turn_stream` at the top of each per-step iteration:

```rust
if attempt == 1 && any_done {
    // Crossing a step boundary (different step id from last time)
    // AND there's actual completed work in history worth compacting.
    let mut history = state.agent.history_snapshot();
    let (changed, notice) = match config.plan_context_strategy.as_str() {
        "clear"   => clear_for_step_boundary(&mut history),       // wipes history except first user msg
        _         => compact_for_step_boundary(&mut history),    // structural shrink (default)
    };
    if changed {
        state.agent.set_history(history.clone());
        // Persist as a CompactionEvent in the session JSONL so /load restores trimmed history
        session.append_compaction_to(&path, &history);
    }
}
```

**Gate.** Fires only when:
1. `attempt == 1` (we just crossed a step boundary — different step id from last iteration)
2. At least one step is `Done` (there's actual completed work in history worth compacting)

### 6.1 Default strategy `"compact"` (M6.2)

`compact_for_step_boundary` — structural shrink that:
- **Preserves** plan-tool tool_results (`SubmitPlan` / `UpdatePlanStep` calls — the breadcrumbs the model uses to know what's already done)
- **Replaces** non-plan tool_results with short placeholders (e.g. `[ToolResult elided by step-boundary compaction]`)
- Keeps the message structure intact so tool_use / tool_result pairing isn't broken

The model continues to see "I called UpdatePlanStep with status=Done at step 3" but no longer sees the 50KB Read result it consumed during step 3.

### 6.2 Alternative strategy `"clear"` (M6.4)

`clear_for_step_boundary` — wipes history outright keeping only the first user message for project-level grounding. Set via `config.plan_context_strategy = "clear"` in `.thclaws/settings.json`.

Useful when steps are independent and prior context is pure noise (e.g. a fanout of unrelated migrations). Loses inter-step context so it's not the default.

### 6.3 Cross-step `output` channel (M6.3)

Because chat history is compacted at every step boundary, a `Read` tool result from step 1 isn't reliably present in step 5's context. Plan mode adds an explicit `output` field on `UpdatePlanStep` calls so steps can pass ids / hashes / paths / port numbers forward independent of history. See [`plan-mode.md`](plan-mode.md) §6 for the full schema.

---

## 7. Session JSONL persistence

Compaction is persisted as a checkpoint event in the session JSONL so `/load` reconstructs the trimmed view, not the original pre-compaction history.

### 7.1 Event format

```json
{"type":"compaction","messages":[{"role":"user","content":[...]},...],"replaces_count":42,"timestamp":1777752000}
```

- `messages` — the new (trimmed) message list
- `replaces_count` — informational only; the load logic walks sequentially and resets on each checkpoint, so the field isn't strictly required
- `timestamp` — write time in seconds

### 7.2 Write path

`Session::append_compaction_to(&path, &compacted)` is called from three sites:

| Call site | Trigger |
|---|---|
| `/compact` slash worker | After `compact_with_summary` returns |
| Ralph driver in `drive_turn_stream` | After step-boundary `compact_for_step_boundary` / `clear_for_step_boundary` returns |
| (per-turn `compact()` does NOT write a checkpoint) | The every-turn no-op fast path is too noisy to checkpoint |

Side effects:
- Writes a `compaction` event line to the JSONL
- Sets `state.session.messages = compacted.to_vec()`
- Resets `last_saved_count = compacted.len()` so subsequent `append_to` calls only emit new turns

### 7.3 Replay path

`load_from` walks the JSONL line-by-line. When it hits a `compaction` event:

```
kind == "compaction"     → messages.clear(); fill from checkpoint; bump last_timestamp
```

The original message events that preceded the compaction stay on disk forever (audit trail) — they're just overridden by the checkpoint on load. Subsequent message events in the file append after the checkpoint.

This gives both **forward correctness** (next load shows the compacted view) and **audit trail** (the original events are inspectable on disk via `cat session.jsonl`).

### 7.4 Recency contribution

Compaction events DO bump `updated_at` for sidebar sort recency — they represent real activity. Contrast with `plan_snapshot` events which are filtered out of the recency calc (M6.16.1) because `restore_from_session` writes a fresh-timestamped snapshot on every `/load` and would otherwise jump the just-clicked session to the top.

---

## 8. Prompt-cache interaction

From [`prompt-cache.md`](prompt-cache.md) §8: cached prefixes break when ANY byte in the cached prefix changes. Compaction is one of the invalidation triggers:

> **History compaction** — `compact_with_summary` rewrites the message list, breaking the second-to-last-msg breakpoint

Practical implication: `/compact` is expensive twice — once for the summarization call itself, once for the next turn re-paying the cache write premium. Use it deliberately, not reflexively.

The every-turn `compact()` no-op fast path does NOT rewrite the message list when under budget, so it doesn't invalidate the cache. Only actual trimming (i.e. `pre_tokens > messages_budget`) breaks the prefix.

Step-boundary compaction inside plan mode also breaks the cache at every step transition by design — the structural shrink rewrites tool_result content. This is the price of plan mode's "fresh context per step" guarantee.

---

## 9. Hook integration (M6.35)

From [`hooks.md`](hooks.md): two lifecycle events fire around the per-turn `compact()` call.

```rust
let pre_tokens = compaction::estimate_messages_tokens(&h);
let pre_count = h.len();
let will_compact = pre_tokens > messages_budget;
if will_compact {
    if let Some(hk) = &self.hooks {
        fire_compact(hk, HookEvent::PreCompact, pre_count, pre_tokens);
    }
}
let compacted = compact(&h, messages_budget);
if will_compact {
    if let Some(hk) = &self.hooks {
        let post_tokens = compaction::estimate_messages_tokens(&compacted);
        fire_compact(hk, HookEvent::PostCompact, compacted.len(), post_tokens);
    }
}
```

| Event | Fires when | Env vars |
|---|---|---|
| `pre_compact` | Before `compact()` runs AND `pre_tokens > messages_budget` | `THCLAWS_COMPACT_MESSAGES`, `THCLAWS_COMPACT_TOKENS` |
| `post_compact` | After `compact()` returns (same gate as pre_compact) | `THCLAWS_COMPACT_MESSAGES`, `THCLAWS_COMPACT_TOKENS` (post-compact values) |

**Gated on `pre_tokens > messages_budget`** so hooks fire only when compaction actually trims. `compact()` is called every turn to re-fit the window, but no-ops when within budget — without the gate, audit hooks would fire empty events on every turn (HOOK4 audit fix).

Configure in `.thclaws/settings.json`:

```json
{
  "hooks": {
    "pre_compact":  "echo \"compacting $THCLAWS_COMPACT_MESSAGES msgs ($THCLAWS_COMPACT_TOKENS tok)\" >> ~/.thclaws-audit.log",
    "post_compact": "echo \"after compact: $THCLAWS_COMPACT_MESSAGES msgs ($THCLAWS_COMPACT_TOKENS tok)\" >> ~/.thclaws-audit.log"
  }
}
```

**Deferred enhancement.** `THCLAWS_COMPACT_STRATEGY` env var (would expose `"compact"` vs `"clear"` for plan-mode step boundaries vs the per-turn / `/compact` paths). Cheap addition, not yet shipped.

---

## 10. Subagent / team interactions

**Subagents** (recursive in-process via `Task` tool) inherit the parent's `budget_tokens` and run the same `Agent::run_turn` loop, so they get the same `compact()` per-turn behavior. Known gap **SUB7**: no per-subagent token budget — children with very different context profiles get the same trigger as the parent.

**Team agents** (multi-process via filesystem mailboxes) have their own session + compaction lifecycle per teammate. The lead's compaction does not affect teammates' message histories. Inbox storage (separate from the agent's message history) is a JSON array per agent with no compaction — known gap **TEAM-M5 deferred** in [`agent-team.md`](agent-team.md). Don't conflate inbox compaction (not implemented) with message-history compaction (this doc).

---

## 11. Code organization

```
crates/core/src/
├── compaction.rs
│   ├── compact                        — drop-oldest with min-1 rescue (M6.17 M1)
│   ├── estimate_messages_tokens       — used by compact's loop check + hook env vars
│   ├── truncate_oversized_message     — char-boundary in-place rescue
│   ├── compact_with_summary           — LLM-summarized variant for /compact
│   ├── compact_for_step_boundary      — M6.2 plan-mode structural shrink
│   └── clear_for_step_boundary        — M6.4 plan-mode wipe-except-first
├── tokens.rs
│   └── estimate_tokens                — chars/4 conservative heuristic
├── agent.rs
│   └── run_turn_multipart             — per-turn compact call site + system-token deduction (M6.18 H1) + pre/post_compact hook fires
├── shared_session.rs
│   └── drive_turn_stream              — Ralph driver step-boundary compaction site
├── session.rs
│   ├── CompactionEvent                — JSONL event type
│   ├── append_compaction_to           — write path
│   └── load_from                      — replay path (clears messages on compaction event)
├── default_prompts/
│   ├── compaction.md                  — user-msg prompt to summarizer
│   └── compaction_system.md           — summarizer's system prompt
└── hooks.rs
    └── fire_compact                   — pre/post_compact convenience helper
```

---

## 12. Testing surface

`compaction` layer (~10 tests in `compaction.rs`):
- `compact_under_budget_returns_unchanged`
- `compact_drops_oldest_until_under_budget`
- `compact_preserves_tool_pair`
- `compact_truncates_oversized_single_message_with_notice` (M6.17 M1)
- `compact_subtracts_system_prompt_tokens_from_budget` (M6.18 H1 regression — lives in `agent.rs` tests)
- `summary_compaction_inserts_synthetic_user_message`
- `summary_compaction_falls_back_to_drop_oldest_on_provider_error`
- `step_boundary_compact_preserves_plan_tool_results`
- `step_boundary_clear_keeps_first_user_message_only`

`session` layer (`session.rs` tests):
- `compaction_event_replays_on_load_from`
- `messages_after_compaction_event_append_to_checkpoint`

---

## 13. Known gaps + dev-log chronology

| ID | Severity | Issue / Fix |
|---|---|---|
| M6.17 M1 | MED | `compact()` could return a single message > budget. New `truncate_oversized_message` rescues with char-boundary truncation + notice. |
| M6.18 H1 | HIGH | Compaction ignored system-prompt size; total request could exceed model context window. Fix in `agent.rs::run_turn_multipart` subtracts `estimate_tokens(system) + 1024 reserve` from budget before calling `compact`. |
| HOOK4 (M6.35) | MED | `pre_compact` / `post_compact` previously fired on every turn (even when no-op). Now gated on `pre_tokens > messages_budget`. |
| SUB7 | MED | No per-subagent token budget — children inherit parent's `budget_tokens`. |
| TEAM-M5 | LOW | Team-agent inbox compaction not implemented (separate subsystem from message-history compaction). |
| Hook strategy env | LOW | `THCLAWS_COMPACT_STRATEGY` not yet exposed; would let hooks distinguish per-turn vs `/compact` vs step-boundary trims. |

| Sprint | dev-log | What landed |
|---|---|---|
| M6.x | `120-130` | Step-boundary compaction strategies (M6.2 compact / M6.4 clear), per-step driver, plan-quality reinforcements, stalled-turn detector |
| M6.17 | `135` | `compact()` truncation rescue for over-budget single message |
| M6.18 | `~125` | System-prompt deduction + 1 KiB tool-def reserve before compact |
| M6.35 | (audit) | `pre_compact` / `post_compact` gating + wire-up |
