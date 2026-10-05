# Agentic Loop

## Canonical loop

The provider-neutral loop is:

```text
while not done:
  build context
  call model with visible tools
  receive final answer or tool requests
  validate every tool request
  check permission and approval policy
  execute or deny each tool request
  append structured tool results
  compact or retrieve context if needed
  stop on completion or budget
```

The model never executes a tool directly. It emits a structured request. The harness executes or rejects it.

## Loop invariants

Enforce these invariants in code:

1. Every tool call receives exactly one corresponding result.
2. Tool arguments are parsed and validated before execution.
3. A permission decision happens before every side effect.
4. Tool results are bounded, structured, and traceable.
5. The loop has hard step, time, token, cost, and tool-call budgets.
6. The final answer is based on observations, not assumed tool success.
7. Errors, denials, cancellations, and timeouts become structured observations.

## Simple pseudocode

```python
def run_agent(task, session):
    session.add_user_message(task)

    for step in range(session.max_steps):
        context = context_builder.build(session)

        if budget.exceeded(session):
            return stop("budget_exceeded", session)

        if compactor.should_compact(context, session):
            session = compactor.compact(session)
            context = context_builder.build(session)

        output = model.generate(
            context=context,
            tools=tool_registry.visible_tools(session),
        )
        session.record_model_output(output)

        if output.final_answer:
            return finalize(output.final_answer, session)

        if not output.tool_calls:
            return stop("no_final_answer_or_tool_call", session)

        for call in scheduler.order(output.tool_calls):
            result = handle_tool_call(call, session)
            session.add_tool_result(call.id, result)

    return stop("step_limit_reached", session)
```

Tool-call handler:

```python
def handle_tool_call(call, session):
    tool = tool_registry.get(call.name)
    if tool is None:
        return error_result("unknown_tool", call.name)

    try:
        args = tool.validate(call.arguments)
    except ValidationError as exc:
        return error_result("invalid_arguments", str(exc))

    decision = permission_engine.evaluate(tool, args, session)

    if decision.type == "deny":
        return denied_result(decision.reason)

    if decision.type == "approval_required":
        return pause_for_approval(call, decision, session)

    if decision.type == "sandbox":
        return sandbox.execute(tool, args)

    return tool.execute(args)
```

## Manual loop versus hosted loop

Some APIs require the application to run the entire loop manually. Others can perform parts of the loop server-side for hosted tools. The architecture should stay the same conceptually:

```text
manual client loop
- application sends tools
- model requests tool call
- application executes tool
- application sends tool result
- repeat

hosted or provider-assisted loop
- provider may execute hosted tools
- application still controls business tools, permissions, approvals, state, and traces
```

Even when the provider supports hosted tools, keep business-critical authorization and audit in the harness.

## Per-request model routing

After measuring a fixed-model loop, an advanced harness may expose a selected logical model that resolves to a physical model for each request. This is a post-MVP dispatch policy, not a new model or authority level. Keep the selected model and requested reasoning setting distinct from the physical provider/model and effective reasoning setting recorded for each attempt.

Route at a complete request boundary, before starting its stream. Give the router the request reason, selected configuration, current branch state, latest successful physical response, and any failed attempt being retried. Make continuation and retry behavior explicit:

| Request reason | Required policy decision |
|---|---|
| New user turn | Choose a destination from approved candidates using the current task and versioned routing state. |
| Tool-result or other continuation | Declare whether the run stays with the previous physical model or may reroute; preserve pending call/result relationships. |
| Retry | Identify the failed physical request separately from the last successful response; declare sticky retry, escalation, and permitted fallback conditions. |
| Direct utility call, such as a compaction summary | Declare its route and budget independently; default to no mutation of the conversation branch's routing state. |

Before dispatch, the host must verify:

1. **Destination access.** Resolve credentials for the physical destination and check tenant, data-disclosure, and deployment policy there. A logical catalogue entry or another provider's credentials do not establish usable destination access.
2. **Action compatibility.** Check required input modalities, tool calling, structured output, reasoning settings, and any programmatic action interface against the physical model and adapter. Do not silently replace required inputs or capabilities with placeholders; reject the route or record an explicitly permitted lossy conversion.
3. **History compatibility.** Project typed conversation history while preserving substantive observations and call/result identities. Provider-native reasoning signatures, continuation tokens, and stored-response references may be valid only for their originating model or provider. Use a tested conversion or full-context restart when allowed; never forge compatibility or silently discard task-critical evidence. See [provider adapters and state strategies](provider-api-patterns.md#api-adapter-layer).
4. **Actual request limits.** Recount the projected input against the destination's verified context/output limits with observation and output headroom. Logical selection metadata, a previous route's limits, and unknown model defaults cannot substitute for this check; use [context reduction](context-memory-compaction.md#staged-reduction-under-context-pressure) when needed.

Keep routing state outside the prompt under branch identity, router/configuration version, and state version. Validate updates against the expected version; record the accepted destination, reason, prior state, and resulting state together at a documented dispatch commit boundary after the checks above. A rejected or failed routing decision does not commit its candidate state. An admitted request that later fails or aborts retains an explicit attempt record and the committed state; record the latest successful route separately. Recovery must reconcile these records before another transition, and branch replay must not import a later sibling branch's routing state. Version or schema incompatibility requires an explicit migration, reset, or stopped outcome.

Routing is not a side-effect retry policy. Preserve the existing [retry rules](#retry-policy), [tool permissions](tools-and-permissions.md), and [configuration events](architecture.md#runtime-instruction-and-tool-configuration-events). Bound router latency, retries, escalations, and physical attempts under aggregate task budgets; record actual usage for every attempted destination. If the router fails, credentials are missing, or no compatible model fits, return a structured failure or use an already configured and equally validated fallback. Do not recurse through logical routes or silently substitute a destination.

Evaluate the routed policy against fixed-model baselines at the same task quality and authority floor using [model/configuration comparisons](evals.md#model-and-configuration-sweeps). Include router overhead, cold caches, failed attempts, and configuration transitions in completion cost and latency; cheaper individual calls do not establish a cheaper completed task.

## Step budgets

Use explicit budgets:

```text
max_model_turns
max_tool_calls
max_parallel_tool_calls
max_wall_time_seconds
max_input_tokens
max_output_tokens
max_total_cost
max_tool_result_chars
max_retries_per_model_call
max_retries_per_tool_call
```

When a budget is reached, stop with a clear status:

```json
{
  "status": "stopped",
  "reason": "step_limit_reached",
  "completed": false,
  "next_safe_action": "Ask the user whether to continue with a larger budget."
}
```

## Retry policy

Retry only safe failures.

Usually safe to retry:

- transient model API errors;
- network timeouts for read-only calls;
- idempotent retrieval;
- validation after the model fixes malformed arguments.

Do not automatically retry:

- payments;
- external sends;
- destructive actions;
- permission changes;
- operations with unclear idempotency.

For high-risk operations, use idempotency keys and approval records.

## Parallelization

Parallelize only independent, read-only, concurrency-safe tool calls.

Safe candidates:

- search;
- read;
- retrieve metadata;
- classify independent records;
- summarize independent documents.

Serialize:

- writes;
- sends;
- deletes;
- financial actions;
- permission changes;
- shell/process execution;
- multi-step external workflow commits.

This is committed parallelism: the complete calls and their independence are already known. An advanced code-mode harness may instead predict and prelaunch eligible calls while a program is still being generated. That requires exact claim-or-run identity, isolated disposable state, separate waste budgets, and cancellation accounting; use [speculative tool execution](speculative-tool-execution.md) rather than weakening the rules above.

## Human-in-the-loop loop

Sensitive actions should pause the loop:

```text
model requests action
  -> harness validates
  -> harness detects approval requirement
  -> harness emits approval request
  -> user or policy approves/rejects
  -> harness resumes with approval_result
```

Approval must be scoped to the exact action. Do not treat vague consent as blanket authorization.

## Goal-like loop

A goal loop is a long-running version of the standard loop. It needs additional state:

```text
objective
done condition
budget
checkpoints
current plan
progress log
validation method
stop rules
```

The loop should periodically ask:

1. Is the objective still valid?
2. What evidence proves progress?
3. Are we within budget?
4. Is the done condition met?
5. Is human approval needed before the next step?
6. Should compaction or handoff happen now?

Goal loops should not be used for vague backlogs or unrelated tasks.

## Termination rules

Stop when any of these are true:

- final answer produced;
- done condition satisfied;
- user approval is required;
- blocker requires user input;
- budget reached;
- repeated failure threshold reached;
- safety policy denies the task;
- tool or connector unavailable and no safe fallback exists.

## Provider-neutral implementation notes

- With OpenAI Responses-style APIs, represent model outputs as typed items and use previous response or conversation state if appropriate.
- With Chat Completions-style or OpenAI-compatible APIs, maintain message history manually and append tool result messages with matching call IDs.
- With Anthropic APIs, handle structured tool-use blocks and return corresponding tool-result blocks.
- With any provider, keep application-side validation, permissioning, and audit logs outside the model.
