# Output Templates — service-itsm-agentic-setup-agentforce-coordinate

Emit one of these text blocks at the corresponding step in the workflow. Setup is presented as
**two sequential setup stages** — Stage 1 (enable platform features) must finish before Stage 2
(install & activate agent templates). Optional Employee Agent escalation follows Stage 2 and runs
only after the Employee agent is active. Only items with a working child skill appear — hide
placeholder rows.

## Naming features in prose (never use bare item numbers)

The `#1`–`#5` labels and the menu's `#` column are internal shorthand for the ordering/delegation
rules and a **selection handle** in the menu (the user replies `1, 2`). They are **not** feature
names. In every message the user reads — opt-out/skip, prerequisite/blocked, progress, next-step, and
the completion summary — refer to each feature by its full menu name, never by a bare number or range.

This matters most when a user skips a Stage 1 platform toggle and you explain the downstream impact:

```text
Wrong (internal positional labels leak to the user):
   You skipped the Specialized Agent Templates toggle — that's the prerequisite for feature #4
   (Specialized Agents for Employee). Features #1–#3 (Studio, Fulfiller agent, Employee agent) can
   all proceed, but #4 will be blocked.

Right (features named in full):
   You skipped the Specialized Agent Templates toggle. That toggle is the prerequisite for building
   Specialized Agents for Employee, so Agentforce Studio, the IT Service Fulfiller agent, and the IT
   Service Employee agent can all still be set up — but Specialized Agents for Employee can't be built
   until that toggle is enabled.
```

A digit is fine only as a menu selection handle (`reply 1, 2`); it must never stand in for a feature
name in prose, progress, or the completion summary.

## Feature menu (Behavior step 3)

```text
Agentforce for ITSM Setup (via service-itsm-agentic-setup-agentforce-coordinate)

Here are the features available for Agentforce ITSM. Stage 1 (enable) must finish before
Stage 2 (install & activate). Employee Agent escalation is available after the Employee agent is active:

┌───┬─────────┬──────────────────────────────┬────────────────────────────────────────────────────────┬────────────────────┬──────────┐
│ # │ Stage   │ Item                         │ Description                                            │ Action             │ Status   │
├───┼─────────┼──────────────────────────────┼────────────────────────────────────────────────────────┼────────────────────┼──────────┤
│ 1 │ Stage 1 │ Agentforce Studio enablement │ Turn on org-level Agentforce, Einstein GenAI, and IT   │ Enable features    │ Not done │
│   │         │ (Foundation for all agents)  │ Service agent features                                 │                    │          │
│ 2 │ Stage 2 │ IT Service Fulfiller Agent   │ Automate actions and simplify critical asks for IT     │ Install + activate │ Not done │
│   │         │                              │ service fulfillers who work with incidents, problems,  │                    │          │
│   │         │                              │ change requests and more to resolve issues and         │                    │          │
│   │         │                              │ requests.                                              │                    │          │
│   │         │                              │ Setup: creates the agent from this template and        │                    │          │
│   │         │                              │ activates a version.                                   │                    │          │
│ 3 │ Stage 2 │ IT Service Employee Agent    │ Help employees quickly troubleshoot IT issues, raise   │ Install + activate │ Not done │
│   │         │                              │ service requests, and track their incidents with ease. │                    │          │
│   │         │                              │ Setup: creates the agent from this template and        │                    │          │
│   │         │                              │ activates a version.                                   │                    │          │
│ 4 │ Stage 2 │ Specialized Agents           │ Use the specialized templates and build agents that    │ Install + activate │ Not done │
│   │         │ for Employee                 │ power your employee agent. Refine the agent logic, as  │                    │          │
│   │         │                              │ necessary, and then activate them.                     │                    │          │
│   │         │                              │ Setup: pick one specialized template (e.g. Password    │                    │          │
│   │         │                              │ Manager, Onboarding), then create and activate that    │                    │          │
│   │         │                              │ standalone agent. Re-run this item to add more.        │                    │          │
│ 5 │ Post    │ Employee Agent escalation    │ Configure human handoff to the General IT queue with   │ Configure handoff  │ Not done │
│   │ setup   │                              │ failure-threshold directives.                          │                    │          │
└───┴─────────┴──────────────────────────────┴────────────────────────────────────────────────────────┴────────────────────┴──────────┘

Reply with the numbers of the features you want to set up (one or more, e.g. `1` or `1, 2`).
If you pick a Stage 2 template without Stage 1, I'll enable the Stage 1 foundation first.
After any Stage 2 agent is created and activated, I'll automatically set up its runtime access
(Stage 3) so it works when opened — that's not a numbered choice.
```

Stage 1 (Agentforce Studio enablement) is the **foundation** — it enables the org-level platform
features every agent is built on. Stage 2 items (the Fulfiller agent, the Employee agent, and
Specialized Agents for Employee) are **installed from a template and activated**; they can be set up
in any order once Stage 1 is done. The post-setup Employee Agent escalation item requires the
Employee agent to be active.

**Specialized Agents for Employee** is a third Stage 2 item, shown right after the IT Service
Employee Agent to keep the two employee options together. Both use the same child skill
(`service-itsm-agentic-setup-employee-agent-configure`): the IT Service Employee Agent installs the
broad, ready-to-go employee agent, while Specialized Agents for Employee starts from one of the
specialized employee templates (for example Password Manager, Certificate Management, Onboarding, or
Hardware Request). Ask which specialized template the user wants **before** delegating this item —
the child skill defaults to the broad agent when handed no name (which would just re-create the IT
Service Employee Agent), and once given a name it disambiguates a partial or ambiguous match. The
chosen template names the agent it creates. The specialized templates themselves are turned on in
Stage 1; this item is where you build and activate an agent from them.

**Employee Agent escalation** is a post-setup item, shown after the Stage 2 agents. It delegates to
`service-agentforce-human-escalation-configure` and configures the Employee agent's hand-off to a
human — `canEscalate`, outbound routing, a staffed General IT queue, and failure-threshold
directives. It requires the IT Service Employee Agent to be Active first, so run it only after item 3
has succeeded.

## Post-feature progress (Behavior step 5)

Example after Stage 1 (Agentforce Studio enablement) completes:

```text
Agentforce Studio — enabled successfully
(via service-itsm-agentic-setup-agentforce-studio-configure)

┌───┬─────────┬───────────────────────────────┬─────────────┐
│ # │ Stage   │ Item                          │ Status      │
├───┼─────────┼───────────────────────────────┼─────────────┤
│ 1 │ Stage 1 │ Agentforce Studio enablement  │ Done        │
│   │         │ (Foundation for all agents)   │             │
│ 2 │ Stage 2 │ IT Service Fulfiller Agent    │ Not done    │
│ 3 │ Stage 2 │ IT Service Employee Agent     │ Not done    │
│ 4 │ Stage 2 │ Specialized Agents            │ Not done    │
│   │         │ for Employee                  │             │
│ R │ Stage 3 │ Runtime access for the        │ Not started │
│   │ (auto)  │ agent(s)                      │             │
│ 5 │ Post    │ Employee Agent escalation     │ Not done    │
│   │ setup   │                               │             │
└───┴─────────┴───────────────────────────────┴─────────────┘

Stage 1 (foundation) is enabled. On to Stage 2 — install and activate the IT
Service Fulfiller agent, the IT Service Employee agent, and/or a specialized
employee agent from their templates. The Fulfiller agent gives IT technicians an
assistant for triage, case summaries, and record automations; the Employee agent
gives requesters self-service help with their own requests; and Specialized
Agents for Employee builds a focused employee agent (such as Password Manager or
Onboarding) from a specialized template you pick. Once an agent is live, I'll set
up its runtime access (Stage 3) automatically — no need to pick it.
```

## Runtime access hand-off (Behavior step 5 — automatic Stage 3)

The `R` (Stage 3) row is not a menu choice. As soon as the Stage 2 queue is drained and at least one
agent went live this session (`Done`), delegate **once** to
`service-itsm-agentic-setup-agent-runtime-access-assign`, covering every newly-live agent. That skill
runs its own target-user selection and confirm-to-write gate — this orchestrator only guarantees the
hand-off happens, never a silent grant. Narrate it like this before delegating:

```text
Your agent(s) are live. One required follow-up before anyone can use them: an activated agent's
actions call platform features the user can't run yet, so it fails the moment it's opened. I'll set
up runtime access now (Stage 3) — granting the runtime feature permissions the agent's actions use,
plus an Agent Access permission set, to the user(s) you choose.

Handing off to service-itsm-agentic-setup-agent-runtime-access-assign …
```

Then mark the `R` row from its Phase-7 verdict: `ASSIGNED`/`ALREADY-ASSIGNED` → `Done`; `NONE-PROVISIONED`
→ `No-op — nothing to assign`; the user declined the runtime skill's own gate → `Skipped by user`;
`PARTIAL`/`FAILED` → stop and surface the failure in plain language (do not mark `Done`).

## Completion summary (Behavior step 6)

The completion summary fires either (a) after every item completes, or (b) when the user says they
are finished — even if some items are still `Not done`. When rendering:

- Substitute each row's actual tracked status: `Done`, `In progress`, or `Not done`. Do NOT
  hard-code `Done`. The Stage 3 (Runtime access) row is special — its status is one of `Done`
  (runtime access set up), `No-op — nothing to assign` (the runtime skill found nothing provisioned
  to grant), `Skipped by user` (the user declined the runtime skill's own gate), or `Not started`
  (no Stage 2 agent went live, so Stage 3 never triggered).
- A row is **settled** when it is `Done`, or — for Stage 3 only — `No-op — nothing to assign`, or a
  `Not started` that is correct because no agent went live. `Skipped by user` on Stage 3 (an agent
  went live but runtime access was declined) is **not** settled.
- Choose the header line based on whether every item is settled:
  - All items settled → `Agentforce for ITSM Setup — Complete`
  - Any selected item still `Not done`/`In progress`, or Stage 3 left `Skipped by user` after an
    agent went live → `Agentforce for ITSM Setup — Finished`
- Choose the closing line based on state:
  - Complete → `Your Agentforce for ITSM setup is complete.`
  - Otherwise → `You have finished the items you selected. The remaining items can be resumed later by re-invoking this orchestrator.`

Example — user finished after only enabling Agentforce Studio (the Stage 2 agents stayed `Not done`):

```text
Agentforce for ITSM Setup — Finished
(via service-itsm-agentic-setup-agentforce-coordinate)

┌───┬─────────┬───────────────────────────────┬─────────────┐
│ # │ Stage   │ Item                          │ Status      │
├───┼─────────┼───────────────────────────────┼─────────────┤
│ 1 │ Stage 1 │ Agentforce Studio enablement  │ Done        │
│   │         │ (Foundation for all agents)   │             │
│ 2 │ Stage 2 │ IT Service Fulfiller Agent    │ Not done    │
│ 3 │ Stage 2 │ IT Service Employee Agent     │ Not done    │
│ 4 │ Stage 2 │ Specialized Agents            │ Not done    │
│   │         │ for Employee                  │             │
│ R │ Stage 3 │ Runtime access for the        │ Not started │
│   │ (auto)  │ agent(s)                      │             │
│ 5 │ Post    │ Employee Agent escalation     │ Not done    │
│   │ setup   │                               │             │
└───┴─────────┴───────────────────────────────┴─────────────┘

You have finished the items you selected. The remaining items can be
resumed later by re-invoking this orchestrator.
```

Here Stage 3 is `Not started` because only Studio was enabled — no agent went live, so the
runtime-access step correctly never triggered, and its unfinished status does not by itself force
`Finished` (the unselected Stage 2 items already do). Had a Stage 2 agent gone live, Stage 3 would
show `Done`, `No-op — nothing to assign`, or `Skipped by user` instead.
