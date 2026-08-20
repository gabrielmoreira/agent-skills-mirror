---
name: ulw-loop
description: [omh] Hermes Loop workflow: agentic interviewer -> planner -> researcher -> builder -> reviewer cycles until a real gate. Use when the user says: loop, goal loop, long horizon goal, never stop, research plan ultragoal feedback, token exhaustion resume, permission profile, star 10k.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, goal-loop]
    category: goal-loop
    phase: continuous-goal-loop
    role: planner
    quality_tier: loop-gated
---

# Loop

This is a Hermes-native `loop` workflow skill.

## Why This Exists

`loop` exists for goals whose correct implementation cannot be known upfront but can be discovered through bounded cycles of definition, action, verification, and revision without confusing planned cycles with observed progress.

## Do Not Use When

- The user asks for one bounded delivery cycle; use `ultrawork`'s delivery-boundary capability instead.
- Scope and milestones are already known and only durable checkpoint/resume tracking is needed; use `ultrawork`'s durable-checkpoint capability.
- The user gives only a north-star outcome such as revenue, stars, or adoption and has not accepted a bounded first loop goal.
- The goal is too vague to name an observable problem, next artifact, verification signal, or stop condition.
- The goal depends mainly on external waiting, adoption, revenue, or community response without observable local next actions.
- The permission profile does not allow repeated research, handoff, queue, or feedback cycles.

## Examples

Good example:

- Prompt: ./loop make OMH a credible Hermes workflow pack with install, docs, QA, and feedback cycles.
- Expected behavior: Start a permission-scoped loop, maintain loop_cycle/v1 state, choose the next concrete task, and keep external outcomes as waiting states.
- Why: The request is long-horizon and needs repeated discovery, verification, feedback, and resume decisions.

Bad example:

- Prompt: ./loop merge this already reviewed one-line README fix.
- Expected behavior: Use a direct delivery or PR workflow instead of starting a persistent loop.
- Why: The task is bounded and should stop after merge evidence rather than create ongoing cycles.

## Completion Checklist

- The request is classified as task, project, north-star ambition, external-wait, or unclear before a loop starts.
- The current loop_status_card/v1 names the queue item, tick status, verification_plan, and next action.
- failure_mode_summary checks verification_gap, comprehension_debt, and cognitive_surrender before progress advances.
- Completion is backed by linked goal/runtime evidence; queued loop ticks alone are not observed work.

## Recovery Notes

- If a queued tick is pending, show it as prepared queue state and use loop status/run-once before claiming progress.
- If feedback is unclear, ask one gate question or route back to research/plan rather than advancing the loop.
- If the goal turns into external waiting, record the waiting state and next observable signal instead of continuing locally.
- If context or budget is exhausted, checkpoint the loop artifact and continue from the latest loop_cycle/v1 state.

## Workflow Lane

- Current lane: **Intent -> plan** (`oh-my-hermes`, `meta-router`, `deep-interview`, `context`, `plan`, `ralplan`, `codebase-onboarding`, `codegraph-refresh`, `+4 more`) - clarify, plan, ship, or loop goals.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user starts a high-level goal or invokes loop. Direct loop invocation means start/continue through interviewer, planner, researcher, builder, reviewer, and loop-controller lanes until a real gate stops it.

    Strong routing signals: `loop`, `./loop`, `$loop`, `goal loop`, `long horizon goal`, `never stop`, `research plan ultragoal feedback`, `token exhaustion resume`, `permission profile`, `star 10k`, `10k star`, `loop engineering`, `루프`, `목표 루프`, `장기 목표`, `끝까지`, `토큰 고갈`, `피드백 루프`, `끝날 때까지 계속`, `계속 돌려줘`, `keep running until done`

## Catalog Metadata

Category: `goal-loop`
Phase: `continuous-goal-loop`
Hermes role: `planner`
Quality tier: `loop-gated`
Reasoning demand: `heavy`

Quality bar:

- Treat direct `loop`, `./loop`, `$loop`, and OMH loop invocations as a start/continue signal rather than a picker or passive clarification path.
- Classify the goal as task, project, ambition, external-wait, or unclear inside the loop, then keep progressing until a real permission, evidence, verification, context, budget, or external-wait gate appears.
- A mid-run user message is an interjection, not a stop: answer it briefly and, in the same reply, continue the run — re-read the phase todo when one is active and dispatch or advance the next pending step, or state exactly what the run is waiting on (for example, lanes still in flight that resume when their results return). Only the user's explicit stop or cancel, or the engine's own completion gate, ends the run; when the interjection changes scope, say so and update the declared plan or todo instead of silently abandoning it.
- Expose core OMH roles: interviewer, planner, researcher, builder, reviewer, and loop controller.
- Route tiny direct tasks to one-cycle delivery surfaces instead of forcing loop overhead.
- Reframe a north-star ambition into a bounded arena, observable problem, next loop goal, and next verification without shrinking its ambition.
- Separate task discovery, distribution, execution, verification, next-task decision, runtime tick queueing, durable-checkpoint/handoff, feedback, waiting, and resume decisions.
- Expose a permission profile before executor/runtime dispatch, repository mutation, PR, merge, or external publishing.
- Expose the automation, worktree, skill, connector, and subagent building-block states without treating planned blocks as observed work.
- Choose workflow patterns such as single-step, fan-out-and-synthesize, adversarial verification, tournament, or triage batch as orchestration metadata only.
- Keep repeated scaffold shape stable, summarize within bounded budgets, and add verifier lanes only when risk or evidence warrants them.
- Keep prepared worktree/subagent/connector plans, observed executor work, linked goal completion, and external waiting as distinct evidence states.
- Use cheap inner-loop checks frequently and expensive outer-loop checks sparingly.
- Keep the practical small-loop recipe visible: test as stop signal, plan -> execute -> verify, one task at a time.
- Surface verification_gap, comprehension_debt, and cognitive_surrender as warnings before a loop starts looking self-steering.

Handoff policy:

Keep loop orchestration, role sequencing, verification-tier selection, deterministic runtime ticks, loop_engineering/v1 status, feedback evaluation, and permission narration in Hermes; prepare executor/runtime/worktree/connector/verifier handoffs only for concrete work and record completion only from linked evidence.

Required inputs:

- loopability assessment
- north-star goal summary when present
- bounded arena
- observable problem
- next verification
- goal reframe
- success criteria
- permission profile
- feedback or wait signal

Expected outputs:

- loopability_assessment/v1 task/project/ambition classification
- loop_start_card/v1 setup prompt
- loop_cycle/v1 state
- loop_engineering/v1 pipeline/building-block snapshot
- loop verification_policy for inner/outer checks
- loop failure_mode_summary over verification gap, comprehension debt, and cognitive surrender
- small-loop guidance: test as stop signal, plan -> execute -> verify, one task at a time
- loop_status_card/v1 next action
- loop_runtime/v1 queued tick with verification_plan refs
- loop_queue_handoff/v1 only when permitted
- executor-neutral handoff only when permitted
- external-wait or checkpoint boundary

Artifact expectations:

- metadata-only .omh/loops loop_cycle/v1 artifact with loopability_assessment/v1
- loop_engineering/v1 status over automation, worktree, skill, connector, subagent, verification policy, and failure modes
- loop_runtime/v1 queue entries with context_policy_ref, cost_policy_ref, and verification_plan
- loop_subagent_result_contract/v1 for prepared subagent handoffs
- loop_status_card/v1 wrapper payload with loopability_assessment, failure_mode_summary, and small_loop_guidance
- loop_start_card/v1 wrapper setup card
- linked goal_ledger/v1 only when completion evidence is required

Safety rules:

- Do not treat loop persistence as permission to bypass the selected permission profile.
- Do not treat a runtime tick as worktree creation, subagent dispatch, connector I/O, implementation, review, CI, merge, publication, or completion evidence.
- Do not claim goal completion from loop state; require linked goal_ledger/v1 completion evidence.
- When context or token budget runs out, checkpoint or rely on resumable state instead of pretending the loop is complete.
- External results such as market response, stars, or adoption are waiting states unless observed evidence is supplied.
- Do not let unattended loop progress bypass verification; missing or failed verification returns to plan/research or waits for evidence.
- Do not let comprehension debt or cognitive surrender hide behind green-looking loop status.

## Runtime Evidence

Preferred harness for this skill: `goal-loop`.

```sh
omh runtime record --skill loop --harness goal-loop --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMH-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
