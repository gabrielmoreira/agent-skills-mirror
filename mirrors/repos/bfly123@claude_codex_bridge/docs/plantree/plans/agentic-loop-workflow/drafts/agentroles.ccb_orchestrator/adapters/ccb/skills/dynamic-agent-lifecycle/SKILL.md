---
name: dynamic-agent-lifecycle
description: Private CCB skill for resolving placement, inspecting, adding, parking, resuming, and safely releasing non-loop dynamic agents through `ccb layout resolve`, `ccb agent`, and read-only layout status commands.
---

# Dynamic Agent Lifecycle

Use this skill when a trusted workflow role needs a temporary or long-lived
non-loop CCB agent, or when dynamic agent ownership, visibility, dispatch, or
release state is unclear.

This skill is for generic dynamic agents such as planner helpers, extra
frontdesk/dialog agents, diagnostics, brokers, or specialist reviewers. For
loop execution capacity such as worker/checker nodes, use
`orchestrator-capacity` and `ccb loop capacity ...` instead.

## Boundary

Allowed command surface:

```bash
ccb agent status --json
ccb agent status --class <role-class> --json
ccb agent show <agent> --json
ccb layout resolve <agent> [--window <name>|--window-class <class>|--loop-id <id> --node-id <id>] --json
ccb agent add <name>:<provider> --role <role-id> [--window <name>|--window-class <class>] [--hidden|--visible|--parked] --json
ccb agent add <name>:<provider> --profile <profile> [--window <name>|--window-class <class>] [--hidden|--visible|--parked] --json
ccb agent hide <agent> --json
ccb agent park <agent> --json
ccb agent resume <agent> [--hidden|--visible] --json
ccb agent remove <agent> --policy auto --idle-only --json
ccb agent release <agent> --idle-only --json
ccb layout status --json
```

Never edit `.ccb/ccb.config`, write `.ccb/runtime` files, call raw `ccb reload`,
call raw `ccb kill`, run `tmux`, kill provider processes, or use
`remove --policy kill` unless the human operator explicitly asks for a forced
reset with a reason.

## Inspect First

Before mutating, inspect lifecycle state:

```bash
ccb agent status --json
ccb layout status --json
```

Use JSON fields as the authority:

- `agent_kind`: `static`, `dynamic`, or `loop`;
- `ownership_class`: `static_configured`, `dynamic_session`,
  `dynamic_manual`, or `loop_capacity`;
- `dispatch_state`: `enabled` or `disabled`;
- `lifecycle_state`: `visible`, `hidden`, `parked`, `configured`, or
  `unloaded`;
- `pane_identity_source`: `observed`, `runtime`, `record`, or `missing`;
- `apply_status`, `apply_plan_class`, `apply_stage`, `failed_apply`;
- `retained_busy`.

If `source=loop` or `ownership_class=loop_capacity`, stop and use
`orchestrator-capacity`.

## Add

Choose the smallest allowed placement:

- Use `--window <name>` only for a known exact logical window.
- Use `--window-class <class>` for a class such as `frontdesk-dialog` or
  `plan-orchestrate`; CCB chooses the concrete page/window and reflow.
- Omit both only when the entry window is acceptable.

Before `ccb agent add`, resolve placement with the same placement arguments:

```bash
ccb layout resolve planner_helper1 --window-class plan-orchestrate --json
```

Use the resolver output as preflight evidence:

- `layout_status` must be `ok`;
- `addable` must be `true`;
- `placement_mode` must match the intended placement class;
- `resolved_window_name` is CCB-owned evidence for where the add will land;
- `will_create_window` is allowed only when the requested class or exact
  window policy expects a new logical window.

If resolve reports an unexpected `target_surface`, existing agent, or target
window, stop and report a blocker instead of guessing a different placement.

Example:

```bash
ccb layout resolve planner_helper1 --window-class plan-orchestrate --json
ccb agent add planner_helper1:codex \
  --role agentroles.planner \
  --window-class plan-orchestrate \
  --hidden \
  --json
```

Require `agent_lifecycle_status="active"`. For live projects, require
`apply.apply_status="applied"` and record `apply.plan_class` as evidence. If
the command returns `failed_apply=true`, `retained_busy=true`, or any blocked
status, report a blocker instead of treating the agent as ready. Verify that
the final `resolved_window_name` matches the preflight resolver unless CCB
reports a newer conflicting runtime state.

## Hide, Park, Resume

Use hide for visual declutter. Use park when the agent should keep context but
reject new dispatch:

```bash
ccb agent park <agent> --json
ccb agent resume <agent> --hidden --json
```

After park/resume, verify with `ccb agent show <agent> --json` and check
`dispatch_state`.

## Remove Or Release

Default to safe release:

```bash
ccb agent release <agent> --idle-only --json
```

Use `remove --policy auto --idle-only` only when a specific policy path is
needed. If the result is `retained_busy=true`, keep the agent and report the
busy reason. Do not force unload long-lived interactive roles; park them and
return a handoff.

After unload, confirm with:

```bash
ccb layout status --json
ccb agent status --json
```

The removed agent should disappear from dynamic layout records, surviving panes
must keep their agent names, and `namespace_reflowed_windows` should name only
the affected logical window when reflow occurs.

## Failure Handling

On any failed, blocked, retained, missing-pane, or dispatch-disabled state:

1. stop lifecycle escalation;
2. report command, target agent, `apply_status`, `apply_plan_class`,
   `failed_apply`, `retained_busy`, and relevant window/pane evidence;
3. keep unrelated dynamic agents separate;
4. return `blocked` or `replan_required` instead of silently degrading.
