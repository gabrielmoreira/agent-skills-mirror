# Session Sources

How to locate sessions and skill usage per host. Follow the recipe for your host; fall back
to the next tier if the preferred source is unavailable.

---

## Host recipes

### Copilot CLI (Tier A — session store)

The Copilot CLI maintains a **session store** (SQLite-backed, local) that is queryable from
inside the agent. Skill invocations are recorded as rows in the `tool_requests` table:

```
tool_requests.name = 'skill'
tool_requests.arguments_json  contains  {"skill": "<name>"}
```

Each row is linked to a `session_id`, enabling per-session skill attribution.

**What to collect:**
- Distinct skill names used in the target session (`skill` value from `arguments_json`).
- Invocation count per skill (number of matching rows).
- Approximate time window (first and last `timestamp` of matching rows for each skill).

**Friction correlation:**
Friction signals sit near (in time and `session_id`) the skill's active window. Look for:
- `tool_requests` rows whose tool completion carried a failure/error status.
- `events` rows of type `tool.execution_complete` with `tool_complete_success = false`
  within the skill's window.
- Clusters of repeated calls to the same tool name within a short span.

**What NOT to collect:** Do not read `tool_complete_result_content`, `user_content`, or
`assistant_content` columns into the artifact. Record only tool names, success/failure
booleans, and counts. Never read credential values, file contents, or any runtime values.

---

### Claude Code (Tier A — transcript JSONL)

Claude Code writes a transcript JSONL to a path typically available as `transcript_path` in
the session context (check the agent's environment or session metadata).

**Parsing for skill usage:**
- Lines where the tool name is `skill` (or the equivalent Skill tool call) with an argument
  indicating the skill name — e.g. `{"skill": "<name>"}`.
- Lines where a file matching `**/SKILL.md` is loaded or read (an `InstructionsLoaded`
  event or equivalent file-read tool call) — this is secondary evidence that a skill was
  active.

**Friction correlation:**
- Tool-call lines with `success: false` or an error field within ±N turns of a skill
  invocation.
- Repeated tool calls of the same name in a short span.
- Explicit user messages expressing frustration or requesting a workaround (paraphrase the
  intent, do not quote the message).

**What NOT to collect:** Do not copy raw transcript lines. Parse for tool names, error
types/names, and invocation counts. All evidence in a `FrictionFinding` must be paraphrased.

---

### Gemini CLI (Tier A — transcript JSONL)

Same approach as Claude Code above. Gemini CLI also exposes a `transcript_path`. The
JSONL schema may differ in field names but the structure is analogous:

- Find Skill tool calls or equivalent invocations that reference a skill name.
- Find `SKILL.md` file-load events as secondary confirmation.
- Correlate nearby failures using the same proximity heuristic.

---

### opencode (Tier B — `session.idle` hook)

opencode exposes a `session.idle` event (not a true `SessionEnd`). Skill usage signals come
from the same transcript/tool-call stream, parsed on turn end. Staging is throttled and
deduplicated by the adapter. Core skill uses the staged marker (see CONTRACT §8) as its
primary source; fall back to visible-conversation analysis.

---

### Amp (Tier B — `agent.end` hook)

Same pattern as opencode. Use the staged marker if present; otherwise visible conversation.

---

### Cursor, Windsurf, Codex CLI, Copilot cloud agents (Tier C — no hooks)

No session store or transcript is accessible from the agent context. Use **visible
conversation only** (see below). Findings may be fewer; confidence is typically `Possible`
unless the user confirms a finding.

---

## Fallback: current conversation only

When no store or transcript is reachable, reflect purely on what is visible in the current
conversation window.

**What to look for in the visible conversation:**
- Skill tool invocations (`skill` tool calls with a `skill` argument).
- `SKILL.md`-style instruction blocks loaded at conversation start.
- Error or failure messages attributed to a skill's actions (by name, not value).
- User follow-ups that describe a problem with what a skill produced.
- Repeated attempts at the same action sequence.

**Limitations to acknowledge in the artifact:**
- Only the current conversation is covered — prior sessions are not reflected.
- No timestamps, so ordering is positional only.
- Attribution confidence is often `Possible` without store corroboration.

---

## Generic skill-usage signals

Regardless of host, these signals confirm a skill was active:

| Signal | Strength |
|---|---|
| `skill` tool call with explicit skill name argument | Strong |
| `SKILL.md` file loaded / `InstructionsLoaded` event for the skill | Strong |
| Calling skill injects its own identity into the nudge context | Strong (raises confidence) |
| Tool call to a tool name advertised in a skill's SKILL.md | Moderate |
| User message referencing a skill by name | Moderate |
| Agent response citing guidance traceable to a skill | Weak |

---

## Scope injection by a calling skill

A calling skill (one that invokes `skill-reflect` programmatically) **may inject scope** by
providing one or more of:

- **`skills`** — an explicit list of skill names to review (e.g. `["my-ci-helper"]`).
- **`sessionId`** — a specific session id to scope to.
- **`context`** — `"this_conversation"` to restrict to the visible conversation only.
- **`selfIdentity`** — the calling skill's own name, confirming attribution.

When scope is injected, honor it instead of the defaults. Attribution confidence is higher
when `selfIdentity` is provided — the caller is a first-party signal that it was active.

When no scope is injected, default to: all distributed skills visible in the most recent
session (or in the current conversation for Tier C hosts), excluding `skill-reflect` and
`skill-reflect-auto`.

---

## Privacy rule (non-negotiable)

**Never read secrets, credential values, file contents, user data, or verbatim conversation
text into the report.** Collect only:
- Tool names and argument keys (not values).
- Success / failure boolean and error type names (not error messages verbatim).
- Counts and timestamps.
- Skill names.

Everything in a `FrictionFinding` must be paraphrased from these signals.
