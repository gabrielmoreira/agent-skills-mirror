---
name: subagents
description: Use when the user asks to find, select, call, or delegate work to an Agent/智能体, digital employee/数字员工, or Crew; when the target is unknown or must be selected by capability; when independent tasks can run in parallel; or when isolated research or a specialized Agent would improve the result.
---

# Subagent Dispatch Skill

Use `call_subagent` to delegate tasks to other agents, and `wait_for_subagents` to collect results from background runs.
These tools are Code Mode tools: run the snippets below with `run_sdk_snippet`, where `sdk.tool.call(...)` is available.

Agent is the generic technical term. Crew is the product term for a marketplace custom Agent presented as a digital employee (数字员工). Users may say Agent, 智能体, digital employee, 数字员工, or Crew. Do not call built-in Agents Crew.

## When To Use

Delegate when at least one is true:

- The task is large enough to benefit from an isolated execution context
- Multiple independent tasks can run in parallel
- You need a specialized agent type (read-only explore, shell-heavy work)

Do not delegate when:

- The task is small and can be done directly
- The work requires constant access to the current conversation state
- Multiple sub-agents would write to the same file with no merge plan
- You cannot summarize the full context into a self-contained prompt

**Depth limit**: sub-agents cannot call `call_subagent`. Only the root agent may dispatch.

## Selecting The Target Agent

- If the user provides a built-in name, local `.agent` name, or `SMA-...` code, skip discovery and call that Agent directly.
- If the target is unknown or must be selected by capability, call `find_agents` to search marketplace custom Agents presented as Crew digital employees.
- Built-in Agents (`magic`, `explore`, `shell`, `search`) do not require discovery.

```python
from sdk.tool import tool

result = tool.call("find_agents", {
    "keywords": [
        "<core term in the user's language>",
        "<distinct variant in the user's language>",
        "<optional common term from another relevant language>",
    ],
    "query": "<the user's complete requirement in the user's language>",
    "limit": 5,
})
print(result.content)
```

- `keywords`: build the complete recall list before the first call and submit it once.
  - Infer the user's language from the request and use that language for the main terms.
  - Usually use two to four high-information words or phrases with distinct recall value.
  - Add a term from another language only when candidate names, common industry terminology, or the target search source is likely to use it. English is often useful for product names and technical acronyms, but it is not mandatory.
  - English requests normally use English terms only. Japanese requests should use Japanese terms first, Korean requests should use Korean terms first, and the same rule applies to every other language. Preserve relevant terms when the user mixes languages.
  - Prefer short terms that may appear directly in candidate names.
  - For short names or acronyms, include common case forms when search sources may treat them differently.
  - Do not enumerate case forms for ordinary phrases, add overlapping synonyms only to increase the count, put the complete requirement in an item, or call `find_agents` once per keyword.
- `query`: the user's complete requirement in the user's language, used to select more relevant candidates.
- `limit`: choose based on the task. The default is `5`; valid values are `1` through `20`.

Read `result.content`, choose by `code`, `name`, and `description`, then pass the selected `SMA-...` code directly as `call_subagent.agent_name`.
Do not automatically split or retry the same search intent when no candidates are returned.

### Browsing The Full Agent List

When the user asks which Agents are available rather than asking to get something done, browse instead of searching: pass `keywords=[]` and `query=None`. Results come back in a stable order with no relevance filtering, so the first entry is not necessarily the best fit.

```python
from sdk.tool import tool

result = tool.call("find_agents", {
    "keywords": [],
    "query": None,
    "limit": 20,
})
print(result.content)
```

Read `has_more` and `next_page` from `result.content`. To read the following page, keep every other argument unchanged and set `page` to `next_page`. Page order is stable and pages do not overlap.

Do not page through the whole directory to see everything — each page costs context. Read further pages only when the user asked for the complete list, or when the current page contains no suitable Agent.

Paging is not available for keyword search, because ranked order is not stable across pages. When a keyword search returns too few results, raise `limit` or change `keywords` instead.

## Tool: call_subagent

```python
from sdk.tool import tool

result = tool.call("call_subagent", {
    "agent_name": str,       # required; use "" when fork=True to inherit the current Agent
    "agent_id": str,         # required; base ID for new sessions, exact final ID when resuming
    "task_label": str,       # required; user-facing label in the user's language
    "prompt": str,           # required
    "model_id": str,         # optional, defaults to inheriting the caller's model
    "background": bool,      # optional, default False
    "fork": bool,            # optional, default False
    "resume": bool,          # optional, default False
})
```

### agent_name

Target agent to call. Accepted values:

- Built-in names or aliases: `magic`, `explore`, `shell`, `search`, `ppt`, `data_analysis`
- Marketplace custom Agent codes returned by `find_agents`, such as `SMA-...` (Crew digital employees)
- Local `.agent` filenames

For marketplace custom Agent codes, `call_subagent` prepares the Agent automatically before dispatch.

Built-in types:

- `magic`: general-purpose, full tool access (web, files, code). Use for complex multi-step tasks.
- `explore`: read-only. Searches files, reads code, answers structural questions. Cannot modify anything.
- `shell`: shell command specialist. Runs scripts, installs deps, performs system operations.
- `search`: web research specialist. Searches the web and reads pages to gather external information. Cannot modify local files.

Other `.agent` files (e.g. `data-analyst`) can also be used by name.

### agent_id

For a new session, provide a human-readable base ID such as `market-research`.

- With `resume=False`, the tool always creates a new session, appends a sequence number, and returns the final ID, such as `market-research-2`.
- The requested base ID is not the session address. Read the exact final ID from `result.data["agent_id"]` or `result.content`.
- With `resume=True`, pass the exact final ID returned by the earlier call. The session must already exist.
- Never infer that a repeated base ID should resume an old session.
- Name by responsibility, not by sequence: `ppt-outline`, `shell-install-ffmpeg` — not `task1`, `worker-a`

### Session lifecycle

- New blank session: `fork=False, resume=False`
- New session inheriting the current context: `fork=True, resume=False`
- Continue an existing session: `fork=False, resume=True`
- `fork=True, resume=True` is invalid

Completed sub-agent histories can be inspected later with the `chat-history` skill. Parent identity is stored explicitly in each new sub-agent's `.session.json`; do not infer parent-child relationships from directory nesting.

Fork creates a new independent session and never overwrites an existing one. Resume is always explicit because the caller may not know that an older session used the same name.

### task_label

User-facing label shown directly in the UI for this delegated task. It is not the agent's name and not `agent_id`.

- Must use the same language as the user's request so the label is understandable. Do not default to English.
- Make it concise and distinct in multi-agent runs.
- It may change between calls even when `agent_id` stays the same.

### prompt

With `fork=False, resume=False`, the sub-agent has no access to the parent's conversation history. The prompt must be fully self-contained. Include:

- The exact task
- Expected output format
- Relevant file paths or object identifiers
- Constraints (e.g. read-only, specific file to write)
- Success criteria

Bad:

```text
Find out what competitors are doing and summarize.
```

Good:

```text
Search the web for the top 3 competitors of [product category] that have launched or updated in the past 12 months.
For each, return: product name, target users, main differentiator, and source URL.
Focus on product launch articles, review sites, and tech media. Do not modify files.
```

### background

- `False` (default): run synchronously, block until the sub-agent finishes, return result immediately. The parent agent is completely blocked with no progress visibility — only suitable for quick tasks that finish in seconds.
- `True`: dispatch as a background task and return immediately. Must follow with `wait_for_subagents` to collect the result.

Use `background=True` in two scenarios:

1. **Parallel workloads**: sequential `call_subagent(..., background=True)` calls result in concurrent execution regardless of whether the model supports parallel tool calls.
2. **Long-running tasks**: even a single sub-agent should use `background=True` when the task may take more than a few seconds. This gives the parent progress visibility via `wait_for_subagents` (timeout snapshots, `pattern` matching for checkpoint-based interleaving), and keeps the sandbox alive during long waits.

### fork

- `False` (default): sub-agent starts with empty conversation history. The `prompt` must be fully self-contained.
- `True`: creates a new sub-agent that inherits the parent's full conversation history and uses the same Agent as the parent. Set `agent_name=""` and keep `resume=False`. The `prompt` is a directive, not a briefing, because the fork already has full context.

If `fork=true` receives a non-empty `agent_name` that does not identify the current Agent, the runtime ignores it, uses the current Agent, and includes a short warning in `result.content`.

Fork mode is useful when the sub-agent needs to reason over the same conversation context as the parent, e.g. generating a summary, extracting decisions, or continuing a task in isolation.

### resume

- `False` (default): create a new session. `agent_id` is a base name; use the final ID returned by the tool for all later references.
- `True`: continue the exact existing session named by the final `agent_id`. Keep `fork=False`.

After every `call_subagent`, treat the returned final `agent_id` as authoritative. Use it for `wait_for_subagents` and any later resume call.

## Tool: wait_for_subagents

```python
from sdk.tool import tool

result = tool.call("wait_for_subagents", {
    "agent_ids": ["id-a", "id-b"],  # required, list of agent_ids from background calls
    "timeout":   30,                # optional, seconds (POSIX: -1 = infinite wait), default 30
    "kill":      False,             # optional, if True: kill all listed agents immediately
    "pattern":   None,              # optional, Python regex to match against new assistant messages
})
```

### timeout (POSIX semantics)

| Value | Behavior |
|-------|----------|
| `> 0` | Wait up to N seconds. If agents are still running, returns current status with progress snapshot. You must either call again to keep waiting, or use kill=True. Unattended agents run indefinitely. |
| `= 0` | Return current status snapshot immediately without waiting. |
| `= -1` | Wait indefinitely until all agents finish (capped at 60 minutes). |

Default is 30 seconds. The tool is designed for repeated calls — timeout does NOT mean failure, it means "still running". Read the `Last message:` progress snapshot to decide whether to keep waiting or kill.

### kill

Set `kill=True` to immediately terminate all specified sub-agents and return their results. The `timeout` parameter is ignored when `kill=True`. Safe to call on already-finished agents.

### Handling `running` status

When `wait_for_subagents` returns agents with status `running`, those agents are still executing in the background. You must take one of these actions:

1. **Keep waiting**: call `wait_for_subagents` again with the same `agent_ids` (and optionally a longer timeout)
2. **Kill**: call `wait_for_subagents` with `kill=True` to terminate them immediately

Do not proceed without dealing with running agents — they run indefinitely and consume resources until explicitly waited on or killed. Read the `Last message:` progress snapshot in the result to decide: if the agent is making progress, wait longer; if it looks stuck or the task is no longer needed, kill it.

Awaits all listed agents together. `result.content` uses this format per agent:

```
[i/total] task_label: status
Sub-agent: agent_name/agent_id
To continue this exact session, call call_subagent with agent_id `agent_id`, resume=true, and fork=false.
Result:
```final output```
```

- `status` values: `done`, `error`, `interrupted`, `running`, `not_found`, `ambiguous`
- `Result:` appears only when status is `done` — contains the sub-agent's final output
- When status is `running` (timed out), `Result:` is replaced by `Last message:` — this is the last assistant message the sub-agent produced before the timeout, useful for gauging progress
- `wait_for_subagents` is idempotent — if status is still `running`, call it again or kill it. Do not ignore running agents — they consume resources indefinitely until explicitly waited on or killed.
- `result.data["results"]`: structured list for programmatic access, fields: `agent_id`, `agent_name`, `task_label`, `status`, `result`, `error`, `last_activity`, `matched_content`

## Output Target

Decide where results go before dispatching. If the output target is missing from the prompt, the sub-agent will guess — and will usually create a file or object it shouldn't.

Three patterns:

**Shared container** (canvas, slides): pass the same container identifier (e.g. project path) to every sub-agent; tell each one which section it owns. Do not let sub-agents create or choose their own container.

**Single file** (report, document): assign the full file to one agent, or have parallel agents draft their sections independently then designate one merge agent to write the final file.

**Independent outputs** (one file per topic, one canvas per theme): each agent gets its own target; no coordination needed.

Never let multiple sub-agents write to the same file concurrently.

## Reporting Results to the User

Sub-agents may include output file paths in their results. When reporting to the user, convert those paths to `[@file_path:path]` format — the frontend renders them as clickable links.

Example: Research report is ready: `[@file_path:reports/market-research.md]`

## Sync Example

```python
from sdk.tool import tool

result = tool.call("call_subagent", {
    "agent_name": "explore",
    "agent_id": "find-product-positioning-doc",
    "task_label": "positioning source lookup",
    "prompt": """Find the single workspace document that is most useful for answering: "What is this project, who is it for, and what does it provide?"
Check workspace folders that are likely to contain project briefs, product analysis, requirements, launch materials, or internal planning before searching elsewhere.
Return:
1. the file path
2. a 3-5 bullet summary
3. one related file worth reading next
Do not modify files.""",
    "background": False,
    "resume": False,
})

print(result.content)
final_agent_id = result.data["agent_id"]
```

## Parallel Example

Dispatch first (sequential calls, concurrent execution):

```python
from sdk.tool import tool

def dispatch(agent_id_base, task_label, prompt):
    result = tool.call("call_subagent", {
        "agent_name": "search",
        "agent_id": agent_id_base,
        "task_label": task_label,
        "prompt": prompt,
        "background": True,
        "resume": False,
    })
    print(result.content)
    return result.data["agent_id"]

competitors_id = dispatch("research-competitors", "competitor research", """Search the web for the top 3-5 competitors in this product space.
For each, return: product name, target users, main differentiator, and source URL.
Focus on product launches, review sites, and tech media from the past 12 months.""")
signals_id = dispatch("research-market-signals", "market signals", """Search the web for recent market signals in this product space.
Return:
1. notable user needs or pain points (with source URLs)
2. recurring themes across articles or community discussions
3. any emerging trends worth tracking""")
```

Then wait:

```python
result = tool.call("wait_for_subagents", {
    "agent_ids": [competitors_id, signals_id],
    "timeout": 60,
})

print(result.content)
# If result shows any agent with status "running":
# - Read "Last message:" to gauge progress
# - Call wait_for_subagents again to keep waiting, OR
# - Call wait_for_subagents with kill=True to terminate
# Do NOT ignore running agents — they consume resources indefinitely.
```

## Advanced: Checkpoint Pattern Matching

Use `pattern` to implement interleaved parent/sub-agent execution. The sub-agent outputs a checkpoint marker; the parent wakes up on match, processes intermediate results, then resumes waiting.

```python
from sdk.tool import tool

# Dispatch a sub-agent that outputs checkpoints and keep its final ID
dispatch_result = tool.call("call_subagent", {
    "agent_name": "explore",
    "agent_id": "long-research",
    "task_label": "long research",
    "prompt": """Research X thoroughly. After each major section, output exactly:
[CHECKPOINT: section_name]
followed by your findings so far. Continue until all sections are done.""",
    "background": True,
    "resume": False,
})
long_research_id = dispatch_result.data["agent_id"]

# Wait for the first checkpoint
result = tool.call("wait_for_subagents", {
    "agent_ids": [long_research_id],
    "timeout": 120,
    "pattern": r"\[CHECKPOINT:",
})

# result.data["results"][0]["matched_content"] contains the message with the checkpoint
# Process intermediate results, then wait for next checkpoint or completion
```

Rules:
- `pattern` is a Python regex matched against each new assistant message (after the wait call starts)
- `pattern` applies only when `timeout != 0` and `kill=False`
- Only messages produced AFTER the wait call are scanned — no false triggers from historical content
- When matched, `result.data["results"][i]["matched_content"]` contains the full message that triggered the match
- The sub-agent continues running after a pattern match — call `wait_for_subagents` again to keep collecting, or use `kill=True` to terminate if the task is done
- If the agent finishes before any match, returns normally with `status: done`
- Pattern errors (invalid regex) return an immediate error result

## Checklist

Before dispatching:

- Is delegation actually necessary?
- Does the prompt contain all required context (no reference to parent conversation)?
- For a new session, is `agent_id` a human-readable base name and `resume=False`?
- For waiting or resuming, are you using the exact final `agent_id` returned by `call_subagent`?
- For an existing session, is `resume=True` and `fork=False`?
- Is `task_label` concise, distinct, and written in the same language as the user's request?
- Is the output target explicit and conflict-free?
- If `background=True`, is there a matching `wait_for_subagents`?
- If an agent needs to be stopped, use `wait_for_subagents(agent_ids=[...], kill=True)` instead of re-dispatching
