# Agent Harness Architecture

## Definition

An agent harness is the provider-neutral runtime that lets a model act safely and repeatably. It is not the model and it is not only a prompt. It is the control plane that owns model calls, tool routing, permissions, memory, context compaction, approvals, tracing, and recovery.

The model should propose. The harness should dispose.

```text
Model responsibilities
- interpret user intent
- choose the next reasoning/action step
- request tools using structured calls
- synthesize observations
- produce final answers or plans

Harness responsibilities
- assemble instructions and context
- decide which tools are visible
- validate tool arguments
- enforce permissions and approvals
- execute tools or call external systems
- store state, artifacts, and traces
- compact and rehydrate context
- enforce budgets and stop conditions
```

## Component model

A robust harness contains these components:

```text
1. Instruction manager
2. Context builder
3. Model adapter
4. Tool registry
5. Permission engine
6. Execution engine
7. State store
8. Memory and retrieval layer
9. Compactor
10. Planner and goal controller
11. Workflow scheduler
12. Skill registry
13. MCP/external connector manager
14. Approval manager
15. Trace and evaluation system
16. Sandbox or execution boundary
```

## Boundary principle

Keep the trusted control plane outside model-directed compute.

The harness should own:

- user identity and tenant boundaries;
- credential management;
- approval records;
- audit logs;
- billing and rate limits;
- tool authorization;
- final commit to external systems.

Sandboxed or external execution can own:

- temporary files;
- generated artifacts;
- script execution;
- isolated browser or shell work;
- connector-specific data processing.

Do not put secrets, approval logic, or authorization decisions inside the model prompt or a sandbox the model can modify.

## Authority hierarchy

Maintain an explicit hierarchy:

```text
provider/system policy
  -> organization policy
  -> product/developer policy
  -> workspace/project policy
  -> domain or directory policy
  -> user task
  -> model-visible runtime reminders
  -> tool observations
  -> untrusted retrieved content
```

The harness should label content by authority level. Retrieved content may contain instructions, but those instructions are data, not policy.

## Event model

Store agent state as typed events rather than only chat messages.

Useful event types:

```text
user_message
assistant_message
tool_call
tool_result
approval_request
approval_result
plan_update
goal_update
skill_invocation
memory_load
context_compaction
instruction_configuration_changed
tool_configuration_changed
connector_call
workflow_plan
workflow_packet_started
workflow_packet_result
workflow_verification_result
workflow_integration_result
error
final_answer
```

Typed events improve replay, audit, compaction, evals, and debugging.

### Runtime instruction and tool configuration events

An advanced harness may change scoped instructions or visible tool declarations during a conversation without rewriting its earlier history. Keep this post-MVP: begin with a fixed instruction/tool bundle, then add ordered configuration events when changing task scope or loadouts makes them useful. This section owns their state and replay contract; the [instruction hierarchy](system-prompts-instructions.md#instruction-hierarchy) and [tool policy](tools-and-permissions.md) still determine authority.

Use typed operations against identified instruction sections and tool declarations rather than treating arbitrary conversation text as configuration. A transaction should identify the branch, event/request identity, originating authority, expected configuration version, ordered operations, effective boundary, and resulting version. Instruction operations may add or replace a named section, remove it, or change its order; tool operations may add, update, or remove a declaration by stable identity and schema/version. State the semantics of absent sections, conflicting versions, duplicate identities, and repeated requests. Preserve section authority labels and explicit ordering; a new user or tool message cannot become a higher-priority instruction because of its position.

The host validates authority, operations, identities, and dependencies before committing the transaction. Commit the event and effective configuration version atomically at a request boundary, so each model call uses one complete instruction/tool snapshot. Reject malformed, stale, unauthorized, or incompatible updates with a structured outcome; an idempotent repeat returns the original outcome, while the same identity with a different payload conflicts. An update arriving during generation is queued for a declared later boundary or triggers an explicit cancel-and-restart policy. Do not alter a request already in flight or expose half a transaction.

#### Declarations and executable loadouts

A visible schema describes a capability; it does not install an implementation, bind credentials, or authorize execution. Keep the host's executable loadout and permission state separate from model-visible declarations. Before exposing a tool, resolve its stable identity to an installed, compatible implementation and approved scope through the existing [tool contracts](tools-and-permissions.md#tool-schema-rules) or [environment-adaptive binding lifecycle](environment-adaptive-tools.md). Every physical call still uses current host policy.

Removing a declaration removes it from the effective tool set for later requests. Define whether the same transaction also revokes its binding or execution eligibility. A proposal made under an older snapshot must be checked against current policy before execution; an already executing call follows the declared cancellation/reconciliation policy and receives its terminal result. Removal does not erase earlier calls, results, receipts, or audit evidence. Configuration cleanup and content deletion are distinct operations governed by their existing retention policies.

#### Branch replay and provider projection

Build effective configuration by replaying authorized events in branch order from a trusted initial snapshot. Preserve event identities, versions, section order, and implementation references in checkpoints. A fork inherits configuration only through its selected ancestor; sibling events and later changes do not leak into it. Replay reconstructs declarations and intended state, not live credentials, executable bindings, or approvals: revalidate those through their canonical owners before using them.

Compaction must carry the current effective configuration and its provenance/version independently of conversational summary, together with any configuration delta needed for retained history. A checkpoint records the exact event boundary it covers; reject missing or inconsistent predecessor versions instead of silently falling back to a stale bundle. Follow [context preservation and rehydration](context-memory-compaction.md#rehydration-after-compaction) for the rest of active state.

The adapter may project configuration events into a provider's native ordered-update representation when that API supports and preserves their semantics. Otherwise checkpoint the effective configuration and start a request with the required complete system/tool bundle and compatible selected history, or stop if the provider cannot represent it safely. Record this projection boundary and any provider state-chain reset; appending a lower-authority text message is not an equivalent substitute for a trusted instruction update. Use [provider adapters and state strategies](provider-api-patterns.md#api-adapter-layer) for format and continuation handling, and [per-request routing](agentic-loop.md#per-request-model-routing) before changing destinations.

Active removal does not guarantee that former instruction text or tool definitions are absent from future provider payloads: native updates may retain them in historical messages. When payload exclusion is required, rebuild a compatible checkpoint and selected history, verify the actual serialized payload, and account for lost prefix reuse. Keep required audit history under its separate retention policy.

Record the configuration version actually used by each physical request. Compare native updates and checkpoint fallback for semantic parity and failure recovery using [evals](evals.md); prefix continuity and cache hit rate are separate measurements owned by [prompt caching](prompt-caching-and-cost.md). An append-only event log alone does not prove a provider preserves the earlier request prefix.

## Durable state outside the prompt

The prompt is not a database. Persist these outside model context:

- active plan;
- active goal;
- todo list;
- approval records;
- workflow plans, packet status, verifier outputs, and integration notes;
- tool traces;
- artifacts;
- retrieved resource references;
- skill invocations;
- loaded instruction scopes;
- compaction summaries;
- eval outcomes;
- connector credentials and scopes.

Then reattach only the relevant parts into the next model call.

## Harness maturity levels

### Level 0: Answer-only assistant

No tool execution. Useful for short Q&A, drafting, and summarization over provided content.

### Level 1: Retrieval agent

Can search and read trusted resources. No side effects.

### Level 2: Drafting agent

Can propose actions, draft messages, or produce plans. Cannot commit changes.

### Level 3: Approval-gated actor

Can prepare actions and execute them after explicit user or policy approval.

### Level 4: Policy-bounded autonomous actor

Can execute low-risk actions autonomously within strict scopes, budgets, and audit controls.

### Level 5: Long-running goal worker

Can continue across multiple turns or sessions toward a measurable objective. Requires durable state, compaction, budget enforcement, checkpoints, and evaluation.

Move up levels only when evals show the simpler level is insufficient.

## Always-on agents and durable runtime

Always-on describes a service that remains available to accept events and resume bounded work, even while inference is idle. Durability describes which accepted inputs, state changes, and outcomes survive specified failures. Neither determines an autonomy level, requires continuously running inference, or implies recursion, self-refinement, or high availability. Use [Always-on Agents and Durable Runtime](always-on-agents.md#taxonomy-and-boundaries) for the post-MVP acceptance, local-commit, task-ownership, application-state, observation, and resident-recovery contracts; keep the simpler request-scoped or resumable baseline first.

## Minimal viable harness

Start with:

1. one model adapter;
2. one context builder;
3. a narrow tool registry;
4. local schema validation;
5. runtime permission checks;
6. structured tool results;
7. step and cost budgets;
8. trace logging;
9. compaction only when needed;
10. a small eval set.

Add subagents, MCP, skill packages, goal loops, and automation only after the base loop is reliable.

## Workflow orchestration layer

Workflow orchestration is an optional layer for large decomposable tasks. It lets the model propose a workflow plan, while the harness validates, approves, schedules, observes, verifies, and integrates the work.

```text
objective
  -> workflow plan
  -> permission and budget check
  -> work packets
  -> worker contexts
  -> verifier contexts
  -> integration
  -> final result with evidence
```

Use this only when the single-worker loop is measurably insufficient because the task requires broad coverage, independent packet work, parallel read-only inspection, or separate verification. The workflow plan is not trusted policy. It is an artifact that must pass the same validation, permission, budget, and approval gates as any other model-proposed action.

When work requires persistent teams that own distinct research approaches and change allocation as evidence develops, use [adaptive agent teams](adaptive-agent-teams.md). This optional post-MVP composition adds portfolio contracts to the existing workflow and child-session mechanisms; it does not add a maturity level or grant authority.

## Design rule

Most agent failures are not caused by insufficient autonomy. They are caused by weak harness boundaries: broad tools, vague instructions, missing approval gates, unstructured tool results, poor context hygiene, and no evals.

## Harness engineering loop

Treat harness building as a feedback loop, not as a one-time prompt-writing exercise.

```text
agent fails or slows down
  -> identify missing capability, context, validator, or permission rule
  -> encode the fix into docs, tools, policies, schemas, or evals
  -> rerun and measure
  -> keep the improvement as part of the harness
```

The mature operating model is: humans steer, agents execute, and the harness turns human judgment into reusable constraints and feedback loops.

## Agent-legible environment

A harness should expose the right operating environment through approved tools. The agent needs access to source-of-truth documents, workflow state, validation signals, and audit evidence.

Examples:

```text
support: ticket history, policies, customer state, escalation rules
finance: ledger data, approval policy, reconciliations, audit events
operations: runbooks, logs, metrics, traces, incident timeline
legal: contract corpus, clause library, review rubric, redline history
research: source corpus, extraction tables, citation checks, reviewer notes
sales: account plan, CRM state, product constraints, approval rules
```

If a fact is not retrievable, inspectable, or encoded in durable state, the agent cannot reliably use it.

## Knowledge base as map and source of truth

Use the top-level instruction file as a concise map. Store deeper truth in structured references.

```text
short instruction map
  -> policies
  -> runbooks
  -> domain models
  -> active plans
  -> completed plans and decisions
  -> generated schemas and inventories
  -> quality scorecards
  -> eval fixtures
```

The instruction map should tell the agent where to look next. It should not be a giant manual that competes with task context.

## Mechanical invariants

Prompts should describe behavior. Harness checks should enforce behavior.

Encode recurring expectations as:

```text
schema validators
policy gates
structural checks
workflow validators
source-citation checks
PII or secret scanners
quality gates
cost and latency budgets
regression evals
```

Give validators remediation messages that can be returned to the model as structured observations.

## Entropy management

Agentic systems accumulate entropy: stale docs, duplicated rules, weak examples, obsolete tools, and low-quality patterns that future runs imitate.

Add recurring cleanup workflows:

```text
doc freshness scans
tool inventory cleanup
quality score updates
technical debt tracker updates
stale plan archival
repeated-failure analysis
prompt/tool bundle review
regression eval additions
```

Continuous cleanup is cheaper than waiting until drift becomes systemic.

## MVP harness default

When building a new domain agent, start with an MVP harness rather than a full autonomy platform. The MVP should include one primary job-to-be-done, a minimal typed tool registry, approval-gated risky actions, explicit budgets, a deterministic context builder, planning mode, auto-compaction, tracing, and a small eval set. Add goal-like loops, more connectors, skills, or subagents only after the single-agent MVP has measured gaps.

The recommended MVP sequence is:

```text
manual loop -> tools -> permissions -> structured observations -> budgets -> tracing -> planning -> context/memory -> compaction -> skills/connectors -> goal loop -> subagents
```

This sequence applies across domains. A coding agent may use file and shell tools; a support agent may use ticket and email tools; a finance agent may use ledger and approval tools. The harness pattern is the same.
