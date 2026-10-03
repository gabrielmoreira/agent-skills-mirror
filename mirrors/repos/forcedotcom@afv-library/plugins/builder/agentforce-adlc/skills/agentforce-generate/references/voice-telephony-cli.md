# Headless Telephony (PSTN) Channel Attach via SF CLI

**Scope: the last step only.** This covers attaching an **already-authored, published, and
active** voice agent to a real phone number (PSTN) — the step this skill previously deferred to
the Agent Builder UI. Authoring the agent (the `.agent` file, `modality voice:` block,
subagents/topics/actions, publish, activate) is handled by the normal `agentforce-generate`
flow — **do not re-do it here.** This doc starts *after* `sf agent publish` + `sf agent activate`.

The whole channel attach is headless — `sf` CLI, `sf project deploy`, and REST. **No Agent
Builder step.** This supersedes the older "channel wiring is UI-only" guidance.

> **Ask before wiring — this step is opt-in.** Channel attach creates real routing
> infrastructure (flows, a queue, an active `MessagingChannel`) and binds a provisioned phone
> number. **Never run it automatically** as part of publish/activate. Confirm both first:
> (1) the user has **explicitly asked** to wire telephony, and (2) a **provisioned phone number**
> exists (do not assume/invent one). If either is missing, stop and tell the user what's needed.

> The only thing that still needs the UI is picking a **non-default voice ID / tuning** (the
> voice picklist isn't enumerable via CLI — see [voice-modality-reference.md](voice-modality-reference.md)).
> Channel *attachment* is not UI-only.

Commands below are adapted from the Agentforce Contact Center `afv-pstn-setup-cli` skill.

---

## Prerequisites (produced by the normal authoring flow)

- A voice agent **already published + active** via `agentforce-generate` (authored with
  `modality voice:` and a voice-capable connection surface).
- Org authenticated via `sf` CLI; you are inside the SFDX project dir (`sf agent
  activate/deactivate` fail outside one with `InvalidProjectWorkspaceError`).
- A **provisioned phone number** supplied by the user (do not assume one).

---

## What "attach to telephony" adds on top of the published agent

```text
Inbound call on +1XXXXXXXXXX
        ↓  MessagingChannel (PstnVoice)  ← created here
  SessionHandlerId → FlowDefinition (300…)
        ↓  Voice Routing Flow (routingType=Copilot)  ← created here
  copilotId → BotDefinition (the published agent)
        ↓
  Published voice agent (planner needs a Telephony surface — see Step 1)
        ↓ (on escalation)
  Voice Escalation Flow (routingType=QueueBased) → voice queue  ← created here
```

Deploy order: **preflight number is Live (Step 0) → escalation flow → queue → (verify planner) → inbound routing flow → channel.**

---

## Step 0 — Preflight: the supplied number must already be provisioned + Live (do this FIRST)

**Before any deploy or create step**, confirm the exact phone number the user supplied is
already provisioned and `CodeStatus=Live`. Nothing below (planner patch, escalation flow, queue,
inbound flow, `MessagingChannel`) may run until this passes — otherwise a typo'd or unprovisioned
number leaves real routing infrastructure created for a number that can never route, which defeats
the opt-in gate.

```bash
sf data query --target-org <alias> \
  --query "SELECT Id, CodeStatus FROM PhoneNumber WHERE PhoneNumber='<phone_number>'"
```
Proceed **only** when the query returns exactly the supplied number with `CodeStatus=Live`. **Stop
and make zero changes** if any of these hold:
- no row is returned (number not provisioned on this org),
- `CodeStatus` is anything other than `Live` (still provisioning / failed),
- the query errors with `INVALID_TYPE` (Agentforce Voice numbers aren't provisioned on this org —
  verify in Setup → Service → Voice → Agentforce Voice Setup).

Tell the user exactly what's missing and do not attempt to create or invent a number.

## Step 1 — Verify the published planner carries a Telephony surface

Authoring produces the planner; you only need to **confirm** (and patch only if missing) that it
has a `Telephony` surface — the DSL commonly emits `Messaging` + `CustomerWebClient` (ECv2 for
Preview) but PSTN routing needs `SurfaceAction__Telephony`.

```bash
sf project retrieve start --metadata "GenAiPlannerBundle:<Agent_API_Name>" --target-org <alias>
```
Confirm: `plannerType=Atlas__VoiceAgent`, a `SurfaceAction__Telephony` `plannerSurface`
(with `outboundRouteConfigs` naming the escalation flow), and ≥1 `localTopics` (a topic-less
planner accepts then drops calls in ~10s). If the Telephony surface is absent, add it and
redeploy with the agent deactivated:
```bash
sf agent deactivate --api-name <Agent_API_Name> --target-org <alias>
sf project deploy start --source-dir <project-source-dir>/genAiPlannerBundles/<Agent_API_Name> --target-org <alias> --wait 10
sf agent activate --api-name <Agent_API_Name> --target-org <alias>
```
> `<project-source-dir>` is the source directory derived from `sfdx-project.json`: take the
> `packageDirectories[]` entry with `"default": true` (else the first) and append `/main/default`
> to its `path` → e.g. `force-app/main/default`. The `path` value alone (e.g. `force-app`) is the
> package root, not the source dir — don't append the metadata folder to it directly.
> Topics/actions themselves come from the authored `.agent` — don't hand-write them here; if
> they're missing, fix the source agent and re-publish via `agentforce-generate`.

## Step 2 — Voice queue (ExternalRouting)

Deploy `QueueRoutingConfig` with **`RoutingModel=ExternalRouting`** (`LeastActive` breaks PSTN —
calls arrive, agent never answers), a `Group` (Queue) linked to it, a `QueueSObject` for
`VoiceCall`, and add the running user as a member. Save the queue Id.

## Step 3 — Escalation flow (before Step 4/5)

Deploy a `RoutingFlow`: `routingType=QueueBased`, `serviceChannelDevName=sfdc_phone`, variable
`recordId` (capital I), `apiVersion=66.0`. The planner references `<Agent_API_Name>_Voice_Escalation`
by name — a missing flow silently breaks escalation.

## Step 4 — Inbound voice routing flow

Deploy a `RoutingFlow` that routes inbound calls to the agent. Critical fields (from a working org):
- `routingType` = **`Copilot`** (NOT `Bot` — silently fails)
- `copilotId.setupReferenceType` = **`BotDefinition`** (NOT `Bot`)
- `serviceChannelLabel` = **`Phone`** (NOT `"Voice Call"`); `serviceChannelDevName` = `sfdc_phone`
- Variable name = **`recordid`** (lowercase — differs from the escalation flow's `recordId`)
- Include **all** empty `<inputParameters>` Flow Builder generates; `apiVersion=66.0`,
  `CanvasMode=AUTO_LAYOUT_CANVAS`, `areMetricsLoggedToDataCloud=false`

## Step 5 — Create + wire the MessagingChannel (the former "UI-only" step)

This is the core of the last step — what Agent Builder → Connections → Voice used to own:

```bash
# 1. Create the channel
CHANNEL_ID=$(sf data create record --sobject MessagingChannel \
  --values "MasterLabel='<Label>' DeveloperName='<Dev_Name>' MessageType='PstnVoice' MessagingPlatformKey='<phone_number>' IsActive=true" \
  --json --target-org <alias> | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")

# 2. Get the inbound flow's FlowDefinition ID (300… prefix — NOT the 301… version ID)
FLOW_DEF_ID=$(sf api request rest \
  "/services/data/v62.0/tooling/query?q=SELECT+Id+FROM+FlowDefinition+WHERE+DeveloperName='<Agent_API_Name>_Voice_Omni_Flow'" \
  --target-org <alias> | python3 -c "import json,sys;r=json.load(sys.stdin)['records'];print(r[0]['Id'] if r else '')")

# 3. Wire SessionHandlerId + FallbackQueueId (both mandatory)
sf api request rest "/services/data/v62.0/sobjects/MessagingChannel/$CHANNEL_ID" \
  --method PATCH \
  --body "{\"SessionHandlerId\":\"$FLOW_DEF_ID\",\"FallbackQueueId\":\"<Queue_Id>\"}" \
  --target-org <alias>
```

Channel facts:
- `MessageType` = **`PstnVoice`** (NOT `Phone` — only one `Phone` channel allowed per org).
- `SessionHandlerId` must be a **FlowDefinition ID (`300…`)**, not a Flow *version* ID (`301…`).
- `FallbackQueueId` is **mandatory** — without it calls may drop.

## Step 6 — Smoke-test end-to-end

The number was already confirmed `Live` in Step 0, so this step just verifies the wiring holds
together: agent `Status=Active`, channel `IsActive=true` with `SessionHandlerId` set, phone still
`CodeStatus=Live`, queue has a `VoiceCall` SObject + ≥1 member.
```bash
sf data query --query "SELECT Id, CodeStatus FROM PhoneNumber WHERE PhoneNumber='<phone_number>'" --target-org <alias>
```
Then place a test call and confirm the agent answers.

---

## Troubleshooting — call not reaching the agent

```bash
sf data query --query "SELECT Id, DisconnectReason, ConversationId, CallSubtype, VendorType FROM VoiceCall ORDER BY CreatedDate DESC LIMIT 5" --target-org <alias>
sf data query --query "SELECT Id, BotId, Status, ActiveTime, HandleTime, RoutingModel FROM AgentWork ORDER BY CreatedDate DESC LIMIT 5" --target-org <alias>
```

| VoiceCall.ConversationId | AgentWork | ActiveTime | Root cause |
|---|---|---|---|
| null | — | — | PSTN / Amazon Connect not reaching Salesforce |
| set | none | — | Routing flow not running, or `SessionHandlerId` is a `301…` version ID |
| set | BotId null | — | Queue `RoutingModel=LeastActive` → change to `ExternalRouting` |
| set | BotId set | 0 | Planner has **no topics** — fix source agent, re-publish |
| set | BotId set | >0 | Bot ran — inspect `MessagingSession` + transcript / welcome message |

## Key gotchas (channel-attach only)

| Mistake | Symptom | Fix |
|---|---|---|
| `routingType=Bot` in inbound flow | Agent not invoked | `routingType=Copilot` |
| `setupReferenceType=Bot` | Deploy error / silent fail | `BotDefinition` |
| `serviceChannelLabel="Voice Call"` | Flow can't resolve channel | `"Phone"` |
| No `SurfaceAction__Telephony` surface on planner | Escalation never fires on voice | Add Telephony surface + redeploy (Step 1) |
| `SessionHandlerId` = `301…` (version) | Channel doesn't route | Use FlowDefinition `300…` |
| `MessageType=Phone` | "Only one Phone channel allowed" | `PstnVoice` |
| `RoutingModel=LeastActive` | Calls arrive, agent never answers | `ExternalRouting` |
| `sf agent activate/deactivate` outside project dir | `InvalidProjectWorkspaceError` | `cd` into the SFDX project first |

---

## Related References
- [voice-modality-reference.md](voice-modality-reference.md) — `modality voice:` block, connection surfaces, authoring guidance.
- [voice-latency-heuristics.md](voice-latency-heuristics.md) — live-call latency anti-patterns.
