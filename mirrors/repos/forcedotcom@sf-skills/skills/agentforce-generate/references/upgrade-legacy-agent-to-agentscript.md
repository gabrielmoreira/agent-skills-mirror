# Upgrade a Legacy Agent to Agent Script (NGA)

Workflow for migrating a legacy Salesforce `GenAiPlannerBundle` agent into a
Next Gen Authoring (NGA) `AiAuthoringBundle` (Agent Script) bundle.

> Steps run in order: **Step 1** project setup → **Step 2** pick the legacy
> agent version → **Step 3** migrate via the Connect API → **Step 4** retrieve
> the NGA bundle → **Step 5** analyze, optimize, and iterate.

> **Narration:** keep progress lines to one short phrase — _"Gathering
> migratable versions…"_, _"Running the migration call inside a subagent…"_.
> Don't explain the rationale (why a subagent, what a screen is) inline; the
> user wants terse status, not a play-by-play.

## Contents

- [Kickoff — set expectations, then track progress](#kickoff--set-expectations-then-track-progress)
- [Step 1 — Project setup and requirements](#step-1--project-setup-and-requirements)
- [Step 2 — Identify the legacy agent version to upgrade](#step-2--identify-the-legacy-agent-version-to-upgrade)
- [Step 3 — Migrate the legacy agent with the `migrateAgentToNga` Connect API](#step-3--migrate-the-legacy-agent-with-the-migrateagenttonga-connect-api)
- [Step 4 — Retrieve the new NGA bundle into the project](#step-4--retrieve-the-new-nga-bundle-into-the-project)
- [Step 5 — Analyze, optimize, and iterate on the migrated Agent Script](#step-5--analyze-optimize-and-iterate-on-the-migrated-agent-script)
  - [5d — Regression-test the draft against the legacy agent](#5d--regression-test-the-draft-against-the-legacy-agent)

## Kickoff — set expectations, then track progress

Before touching anything, do two things so the user always knows what's coming
and where they are. Keep both **brief** — no rationale, no sub-steps.

**1. Show a high-level overview once, up front:**

> Migrating your legacy agent to Agent Script (NGA). The plan:
> 1. **Set up** — pick the target org and a local project
> 2. **Choose** — the legacy agent and the version to migrate
> 3. **Migrate** — one API call; creates a new NGA bundle in your org
> 4. **Retrieve** — pull the new agent down locally
> 5. **Optimize** — review and improve the result together
>
> The migration produces a **new NGA version** of your agent. Your original
> agent versions stay available in the legacy builder — nothing is overwritten
> or removed, so you can always fall back to them.
>
> The migration itself is quick — step 5 is where we make it good.

**2. Render this checklist now, and re-render it (compact) after each step** so
the user can see progress at a glance. Mark completed `[x]`, the active step
`[>]`, and the rest `[ ]`:

```text
- [ ] Step 1 — Project & org setup
- [ ] Step 2 — Pick legacy agent + version
- [ ] Step 3 — Migrate (Connect API)
- [ ] Step 4 — Retrieve NGA bundle
- [ ] Step 5 — Analyze & optimize
```

Re-render only the checklist between steps — don't re-explain finished work. At
the end of each step below you'll find a **Checklist** cue: advance the marker
and show the updated list before starting the next step.

## Step 1 — Project setup and requirements

The workflow needs a local **Salesforce DX project** to hold retrieved
metadata — the legacy `botVersion-meta.xml` files read in Step 2 and the
migrated `AiAuthoringBundle` pulled down in Step 4 all land here. Establish this
once, up front.

### Gather requirements

Collect two things. **Never assume a default for either — always confirm.**

1. **Target org** — the org that holds the legacy agent and will receive the
   migrated bundle (used as `<org-alias>` throughout). **Never silently use the
   default org.** Show the user the current default and the alternatives, then
   **require an explicit confirmation or choice** before proceeding — Step 3 is a
   mutating call, so the wrong org creates a bundle in the wrong place.

   ```bash
   sf config get target-org --json   # the current default, if any
   sf org list --json                # all authenticated orgs to choose from
   ```

   **Present the authenticated orgs as a selectable menu** (e.g. an
   `AskUserQuestion` pick-list) — the user should **choose**, never type an
   alias by hand. Mark the current default so it's obvious (e.g.
   `mk-sandbox (default)`) but still require an explicit pick. Use the chosen
   alias as `<org-alias>` everywhere below.
2. **DX project** — the path to the DX project to work in. If they don't have
   one, offer to create it and ask for a name/location.

Once the org is chosen, resolve **its** API version rather than pinning a
literal (versions bump every release, so a hardcoded number goes stale). Use it
as `<apiVersion>` in the endpoint paths below:

```bash
sf org display --target-org <org-alias> --json 2>/dev/null \
  | sed -E 's/\x1b\[[0-9;]*m//g' | jq -r '.result.apiVersion'   # e.g. 67.0
```

> **Minimum:** `migrateAgentToNga` (Step 3) requires **API v67.0+**. If the org
> reports lower, it predates the endpoint — stop and surface that.

### Use an existing project, or create one

A DX project is any directory containing an `sfdx-project.json`. Verify:

```bash
test -f <project-path>/sfdx-project.json && echo "DX project OK" || echo "no project here"
```

If none exists, create one and set `sourceApiVersion` to the org's
`<apiVersion>` resolved above (must be `67.0`+ for the Step 3 endpoint):

```bash
sf project generate --name <project-name> --output-dir <parent-dir>
# then, in sfdx-project.json, set  "sourceApiVersion": "<apiVersion>"
```

### Resolve the package directory — never assume `force-app`

Retrieved metadata lands under the project's **default package directory**. That
directory is declared in `sfdx-project.json` and is **not always `force-app`** —
`sf project generate` defaults to it, but existing projects often rename it or
declare several. Resolve it once from the project and use the result as
`<package-dir>` in every path below (the `default: true` entry, falling back to
the first `packageDirectories` entry):

```bash
jq -r '(.packageDirectories[] | select(.default == true) | .path) // .packageDirectories[0].path' \
  <project-path>/sfdx-project.json    # e.g. force-app
```

**All subsequent `sf project retrieve start` commands must be run from inside
this project directory** (`cd <project-path>`), so retrieved metadata is written
under its `<package-dir>/main/default/` tree — including
`aiAuthoringBundles/` (the migrated NGA bundle) and `bots/` (the legacy
`botVersion-meta.xml` files).

> **Checklist:** mark Step 1 done, Step 2 `[>]`, and re-render before continuing.

## Step 2 — Identify the legacy agent version to upgrade

The `migrateAgentToNga` call in Step 3 takes a single input: a classic
**`BotVersion`** Id (key prefix `0X9`). This step presents a **two-screen
selection** — first pick the agent, then pick one of its **non-NGA** versions —
and resolves the choice to that Id.

### Concepts

An Agentforce agent is backed by classic Bot SObjects, but as an **Agentforce
copilot**, not an old Einstein Bot:

- **`BotDefinition`** (key prefix `0Xx`) — the agent. For Agentforce agents
  `Type` is **`ExternalCopilot`** or **`InternalCopilot`**. **Do not** pick
  `Type = 'Bot'` records — those are old Einstein Bots, not Agentforce agents.
- **`BotVersion`** (key prefix `0X9`) — one version of that agent, with a
  `VersionNumber` and a `Status` (`Active` / `Inactive`). This is what you
  migrate.
- Each version is authored by a **planner**, identified in the version's
  `botVersion-meta.xml` as `<genAiPlannerName>`. That planner's
  **`PlannerType`** (queryable on the `GenAiPlannerDefinition` SObject) is the
  authoritative NGA-vs-legacy discriminator (see below).

### Distinguishing NGA from legacy (migratable) versions

Only **non-NGA** versions can be migrated — an NGA version is already Agent
Script. Once an NGA agent is published it *also* gets `Bot`/`BotVersion` records,
so the presence of a `BotVersion` does **not** mean a version is legacy. The
reliable signal is the planner's `PlannerType`:

| `PlannerType`                              | Meaning                    |
|--------------------------------------------|----------------------------|
| `Atlas__ConcurrentMultiAgentOrchestration` | **NGA** — already Agent Script; exclude |
| `AiCopilot__ReAct`                         | Legacy Agentforce (copilot) — migratable |
| `SentOS__SearchAgent`                      | Legacy search agent — migratable |
| _(anything other than `Atlas__…`)_         | Legacy — migratable        |

> **Do not** rely on `Bot.agentDSLEnabled` (in `bot-meta.xml`). It exists but is
> **definition-level and stale** — it can read `false` for an agent whose latest
> version is already NGA. Classify **per version** via `PlannerType`.

### Screen 1 — pick the agent

List the Agentforce agents (copilot-typed `BotDefinition`) and let the user pick
one:

```bash
sf data query \
  --query "SELECT DeveloperName, MasterLabel, Type FROM BotDefinition WHERE Type IN ('ExternalCopilot','InternalCopilot') ORDER BY MasterLabel" \
  --target-org <org-alias> \
  --json
```

#### Silent gate — reject developer names ending in `_<digits>`

**As soon as the agent is chosen, silently check its `DeveloperName` against the
pattern `_\d+$`** (an underscore followed by one or more digits at the end —
e.g. `Agent_01`, `Order_Agent_007`). Do **not** narrate this check when it
passes; just continue.

If it **matches**, the migration produces a bundle that can't be worked on from
the terminal (broken version handling) — see
[known-issues.md](known-issues.md) **Issue 21**. **Stop the migration here.** Do
not proceed to Screen 2 or the Step 3 call. Tell the user, concisely:

- The agent's developer name ends in `_<digits>`, which hits a known migration
  bug (link Issue 21).
- The fix is to rename the developer name to break up the trailing digits
  (e.g. `Agent_01` → `Agent_v01`), **then** restart this workflow.
- Renaming has ripple effects — Email Configurations, `package.xml` /
  `AiAuthoringBundle` deploy configs, and any Agent API integrations reference
  the agent by name and must be updated to match. (Point them at Issue 21 for
  the full list.)

```bash
# silent detection — no output unless it matches
printf '%s\n' "<agent-name>" | grep -Eq '_[0-9]+$' && echo "BLOCKED: see Issue 21"
```

### Screen 2 — pick a non-NGA version

For the chosen agent, gather its versions and each version's planner type, then
present **only the non-NGA versions**, ordered by `VersionNumber` **ascending**.

1. **Versions + Ids** (ascending) — the `0X9…` Id per version:

   ```bash
   sf data query \
     --query "SELECT Id, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '<agent-name>' AND BotDefinition.Type IN ('ExternalCopilot','InternalCopilot') ORDER BY VersionNumber ASC" \
     --target-org <org-alias> \
     --json
   ```

2. **Per-version planner link** — retrieve all versions' metadata at once and
   read `<genAiPlannerName>` from each `vN.botVersion-meta.xml`:

   ```bash
   sf project retrieve start --metadata "BotVersion:<agent-name>.*" --target-org <org-alias> --json
   # each: <package-dir>/main/default/bots/<agent-name>/vN.botVersion-meta.xml
   #   → <conversationDefinitionPlanners><genAiPlannerName>…</genAiPlannerName>
   ```

3. **Planner types** — resolve every planner's `PlannerType`:

   ```bash
   sf data query \
     --query "SELECT DeveloperName, PlannerType FROM GenAiPlannerDefinition" \
     --target-org <org-alias> \
     --json
   ```

Join version → `genAiPlannerName` → `PlannerType`, drop any version whose
`PlannerType` is `Atlas__ConcurrentMultiAgentOrchestration` (NGA), and present
the rest ascending, e.g.:

```text
Agent: Search_Agent
  v1  Inactive  (legacy: SentOS__SearchAgent)
  v6  Inactive  (legacy: SentOS__SearchAgent)
  # v2–v5, v7 hidden — already NGA (Atlas)
```

The `Id` (`0X9…`) of the version the user picks is the `botVersionId` you pass to
`migrateAgentToNga` in Step 3.

> **Checklist:** mark Step 2 done, Step 3 `[>]`, and re-render before continuing.

## Step 3 — Migrate the legacy agent with the `migrateAgentToNga` Connect API

Salesforce Core exposes a Connect REST endpoint that converts a classic
`BotVersion` into an NGA Agent Script bundle:

```text
POST /services/data/v<apiVersion>/connect/migrateAgentToNga   # <apiVersion> from Step 1, v67.0+
```

**Warning: This is a mutating call.** It does not validate/preview — a successful call
*creates* a new NGA bundle in the org (a real `AiAuthoringBundle`, key prefix
`1bY`, with a bundle version, key prefix `1bZ`). Confirm the target org and the
`botVersionId` before running it.

### Preferred: call it through the `sf` CLI

Invoke the Connect endpoint with `sf api request rest` — no manual token
handling. **`sf api request rest` has no `--json` flag** (passing it errors with
`Nonexistent flag: --json`). It streams the raw response *body* to stdout — for
this endpoint that body is already JSON — and prints a beta-command warning to
stderr. The body is ANSI-colorized even when piped, so strip the color codes
before reading or feeding it to `jq`:

```bash
sf api request rest "/services/data/v<apiVersion>/connect/migrateAgentToNga" \
  --method POST \
  --body '{"botVersionId":"<botVersionId>"}' \
  --target-org <org-alias> \
  2>/dev/null | sed -E 's/\x1b\[[0-9;]*m//g'
```

- `botVersionId` — the classic `BotVersion` Id (`0X9…`) selected in Step 2.
- The stripped stdout is the full JSON response. Pipe it to `jq` after the `sed`
  strip to pull individual fields.

#### Warning: Do the call in a subagent — the response can be huge

A newer version of this endpoint returns an **`agentScript`** field containing
the *entire* generated Agent Script inline. Reading the raw response into the
main context would bloat it badly. **Make the `migrateAgentToNga` call inside a
subagent** and have the subagent return only the small fields you need:
`bundleVersionApiName`, `bundleId`, `bundleVersionId`, `agentVersionFromNumber`,
`bundleVersionToNumber`, `conversionWarnings`, and `agentResponse`. Never return
`agentScript` up to the caller; the full script comes down through the Step 4
retrieve instead.

#### Response fields

The response shape is expanding. Handle the new fields **if present**, and fall
back to the older shape when they are absent:

| Field | Use |
|-------|-----|
| `bundleVersionApiName` | **Preferred.** The metadata `fullName` of the new bundle version — pass **directly** to the Step 4 retrieve, skipping the `bundleVersionId → fullName` lookup. |
| `bundleVersionId` (`1bZ…`) | Fallback join key when `bundleVersionApiName` is absent (see Step 4). |
| `bundleId` (`1bY…`) | The bundle (not version) Id. |
| `conversionWarnings` | List of warnings; review in Step 5. Often non-empty. |
| `agentResponse` | Notes/fixes from an agent that reviewed the generated script — useful input for Step 5 optimization. |
| `agentScript` | The full generated script inline — **do not** surface it; retrieve the bundle in Step 4 instead. |
| `agentVersionFromNumber` (Integer) | The legacy agent version that was migrated **from**. Use in the success message below. |
| `bundleVersionToNumber` (Integer) | The NGA bundle version that was created **to**. Use in the success message below. |

#### Report the result — always present the builder link

**On any successful migration, present the builder deep link so the user can
open the new agent immediately.** The link needs only `bundleId` and
`bundleVersionId`, which are present in **both** the old and new response shapes
— so the link is unconditional, never gated on the newer fields.

Confirm in one line, then hand over the link:

```text
Migrated <agent> to a new NGA agent. Open it in the builder: <builderUrl>
```

When the newer fields (`agentVersionFromNumber`, `bundleVersionToNumber`) are
present, use the more specific wording; otherwise fall back to the generic line
above:

```text
Legacy <agent> version <agentVersionFromNumber> has been migrated to NGA version <bundleVersionToNumber>.
Open in the builder: <builderUrl>
```

The builder URL is the org's Lightning host + the agent-authoring app, with the
**bundle** as the `project` and the **bundle version** as the `projectVersion`
(`project == bundle`):

```text
https://<lightning-host>/AgentAuthoring/agentAuthoringBuilder.app#/project?projectId=<bundleId>&projectVersionId=<bundleVersionId>
```

- `projectId` = `bundleId` (`1bY…`); `projectVersionId` = `bundleVersionId` (`1bZ…`) — both from the Step 3 response.
- Derive `<lightning-host>` from the chosen org, don't hardcode it:

  ```bash
  sf org display --target-org <org-alias> --json 2>/dev/null \
    | sed -E 's/\x1b\[[0-9;]*m//g' | jq -r '.result.instanceUrl'
  ```

  Use that host as-is; if it's a `*.my.salesforce.com` domain it redirects to the
  matching `*.lightning.force.com` builder.

> **Always call through `sf api request rest`.** It keeps authentication
> internal to the CLI. **Do not** hand-roll a `curl` call that extracts the org
> access token (e.g. `jq -r '.result.accessToken'`) — pulling a session token
> into a shell variable is prohibited in agent-executed workflows because it can
> surface in the transcript, context, or traces, even when it is never echoed.

#### Response shapes

A successful migration returns **HTTP 201**. The **current** shape (older
endpoint) looks like:

```json
{
  "bundleId": "1bYak000000LoRdEAK",
  "bundleVersionId": "1bZak000000dXCDEA2",
  "conversionWarnings": [
    "WARNING: Subagent TestSubAgent007 could not be resolved from standard subagents or has no actions. Is this expected?"
  ]
}
```

The **newer** shape adds `bundleVersionApiName`, `agentScript`, `agentResponse`,
and version-number fields:

```json
{
  "bundleId": "1bYak000000LoRdEAK",
  "bundleVersionId": "1bZak000000dXCDEA2",
  "bundleVersionApiName": "Agentforce_Service_Agent_4",
  "conversionWarnings": ["WARNING: …"],
  "agentScript": "system:\n    instructions:| …   (full script — do not surface)",
  "agentResponse": "Reviewed the generated script; adjusted …",
  "bundleVersionToNumber": 4,
  "agentVersionFromNumber": 1
}
```

`conversionWarnings` is often non-empty. Common entries flag subagents that
resolved to no actions during conversion (e.g. `Escalation`, custom test
subagents) — review them in Step 5 when refining the migrated script; they do
**not** fail the migration.

> **Checklist:** mark Step 3 done, Step 4 `[>]`, and re-render before continuing.

## Step 4 — Retrieve the new NGA bundle into the project

Pull the freshly-created `AiAuthoringBundle` into the DX project from Step 1 so
it can be reviewed and refined locally. Retrieval is by metadata **fullName**.

### Get the retrievable fullName

**Preferred (newer endpoint):** Step 3's response already includes
**`bundleVersionApiName`** — that *is* the metadata `fullName`. Use it directly
and **skip the lookup below**.

**Fallback (older endpoint, no `bundleVersionApiName`):** map the
`bundleVersionId` to a `fullName`. `sf org list metadata` reports each
`AiAuthoringBundle`'s `id`, and that `id` equals the **`bundleVersionId`**
(`1bZ…`) from Step 3 — **not** the `bundleId` (`1bY…`). Match on it:

```bash
sf org list metadata --metadata-type AiAuthoringBundle --target-org <org-alias> --json \
  2>/dev/null | sed -E 's/\x1b\[[0-9;]*m//g' \
  | jq -r --arg id "<bundleVersionId>" '.result[] | select(.id == $id) | .fullName'
```

Either path yields a versioned name like `Agentforce_Service_Agent_4`.

### Retrieve into the project

Run from **inside the Step 1 project directory** so the bundle lands under
`<package-dir>/main/default/aiAuthoringBundles/` (the `<package-dir>` resolved in
Step 1):

```bash
cd <project-path>
sf project retrieve start --metadata "AiAuthoringBundle:<fullName>" --target-org <org-alias>
```

> **Note on the on-disk name.** You pass the *versioned* `fullName` (e.g.
> `Agentforce_Service_Agent_4`), but the retrieve normalizes the local folder to
> the bundle's **`developer_name`** (its base name, e.g.
> `Agentforce_Service_Agent`). The result is:
>
> ```text
> <package-dir>/main/default/aiAuthoringBundles/<developer_name>/
>   <developer_name>.agent            # the Agent Script (YAML)
>   <developer_name>.bundle-meta.xml  # <bundleType>AGENT</bundleType>
> ```

The `.agent` file is the migrated Agent Script — `system:` instructions,
`config:`, `variables:`, subagents, and actions — ready for review in Step 5.

> **Checklist:** mark Step 4 done, Step 5 `[>]`, and re-render before continuing.

## Step 5 — Analyze, optimize, and iterate on the migrated Agent Script

`migrateAgentToNga` produces a **basic, mechanical transformation** of the
legacy agent metadata into Agent Script. It maps the old subagents/actions across
but does **not** leverage any of the primitives that make Agent Script powerful —
deterministic flow control, wired data flow, proper reference syntax, structured
escalation, etc. The migrated `.agent` is a *starting point*, not a finished
agent. This step hands off to the existing capabilities of the
**`agentforce-generate`** skill to understand it, then improve it.

Work against the retrieved bundle from Step 4
(`<package-dir>/main/default/aiAuthoringBundles/<developer_name>/<developer_name>.agent`).
Available inputs to inform the work:

- The retrieved `.agent` file (Step 4) — the migrated script itself.
- Step 3 `conversionWarnings` — unresolved subagents / actions to address.
- Step 3 `agentResponse` (newer endpoint only) — fixes/comments from an agent
  that already reviewed the generated script; a useful starting checklist.

### 5a — Understand what was produced

Route into the skill's **"Comprehend an Existing Agent"** task domain (see
[SKILL.md](../SKILL.md)). It reverse-engineers an Agent Spec, produces a Subagent
Map diagram, and flags anti-patterns — establishing what the mechanical
conversion actually built before you change it. Core references:
[Core Language](agent-script-core-language.md),
[Subagent Map Diagrams](agent-subagent-map-diagrams.md).

### 5b — Optimize to leverage Agent Script primitives

Route into the skill's **"Optimize an Agent"** task domain (see
[SKILL.md](../SKILL.md)) — this is the heart of turning a mechanical conversion
into a real Agent Script agent. It scans every subagent and applies:

- **Pattern 1 — Wire action outputs to deterministic consumers**
  ([Data Flow](optimization-pattern-1-data-flow.md)).
- **Pattern 2 — Extract requirement-backed deterministic logic**
  ([Deterministic Logic](optimization-pattern-2-deterministic-logic.md)) — the
  biggest lever on migrated agents, which encode all logic as model judgment.
  In particular, **any consequential or state-changing action** (order/status
  updates, writes, refunds, cancellations) must be **structurally gated** with
  `available when @variables.<trusted_state>` over verified state — do not leave
  the guard as a prose instruction like "only update for a verified customer,"
  which the model can ignore. For example, gate an `UpdateOrderStatus` alias with
  `available when @variables.verified` rather than trusting reasoning text.
- **Pattern 3 — Fix variable/action reference syntax**
  ([Reference Syntax](optimization-pattern-3-reference-syntax.md)) —
  `{!@variables.X}` / `{!@actions.X}` instead of bare references.
- **Pattern 4 — Repair promised human handoff**
  ([Escalation](optimization-pattern-4-escalation.md)) — resolves the
  unresolved-`Escalation`-subagent warnings commonly seen in `conversionWarnings`.
- **Pattern 5 — Voice-readiness** ([Voice Modality](voice-modality-reference.md))
  if the agent has a `modality voice:` block.

The domain presents an `## Optimization Report`, **stops for explicit approval**,
then applies approved edits. For deeper judgment on what "good" looks like, see
[Zen of AgentScript](zen-of-agentscript.md),
[Posture & Determinism](posture-and-determinism.md), and the
[Scoring Rubric](scoring-rubric.md).

### 5c — Validate, preview, and iterate

After edits, validate and confirm behavior — then loop 5b/5c until satisfied:

```bash
sf agent validate authoring-bundle --json --api-name <developer_name>
sf agent preview start --json --use-live-actions --authoring-bundle <developer_name>
```

See [Validation & Debugging](agent-validation-and-debugging.md) for the
preview/trace loop and [Safety Review](safety-review-reference.md) for the
7-category safety pass. When the agent is ready to release, continue into the
skill's **"Deploy, Publish, and Activate"** task domain.

### 5d — Regression-test the draft against the legacy agent

For higher assurance — especially before release, or when 5b changed routing or
actions — run a **side-by-side regression eval** that previews the migrated NGA
draft and the legacy agent against a fixed utterance suite and compares them.
This confirms the draft routes to the same subagents, calls the same actions, and
returns equivalent (ideally improved) responses. Full mechanism, scripts, and the
utterance-suite format are in
[legacy-nga-regression-eval.md](legacy-nga-regression-eval.md).

**When to run:** after the draft compiles and previews cleanly (5c), when you want
objective evidence that the migration preserved behavior — not on every tiny edit.
It requires the legacy agent to still have an **Active** `BotVersion` and `sf` CLI
**≥ 2.149.9**.

Two bundled scripts do the mechanical work:

- `scripts/upgrade-legacy-nga-run-trials.sh` — collects fresh-session preview
  trials for a subject (`legacy` | `draft`) × utterance (agent/org from
  `EVAL_AGENT` / `EVAL_ORG`).
- `scripts/upgrade-legacy-nga-analyze.py` — reads the local plan traces and emits
  the comparison report (mechanical Rubric #1 + verbatim responses + an LLM-judge
  prompt for Rubric #2).

> **Safety.** Live utterances that fire real side effects (escalation, customer
> email, lead capture) must be tagged and default to **simulated** mode or
> explicit per-utterance confirmation — never run repeatedly in live mode without
> opt-in. Draft-only otherwise: **no publish/activate/deploy** without explicit
> human approval.

**Stop condition:** every utterance's oracle-triangle verdict is `PASS` or
`PASS + LEGACY-DEFECT` (no open `DRAFT-REGRESSION`; any `SPEC-REVIEW` /
`ADJUDICATE` resolved), drift is `none` against a deliberately-approved baseline,
and the Rubric #2 judgment is `EQUIVALENT` / `IMPROVED` (no open `REGRESSION`). A
`LEGACY-DEFECT` is a **pass** — don't chase legacy parity when legacy was wrong.

> **Checklist:** mark Step 5 done — all five steps complete. Confirm the
> migration is finished and point the user at the optimized bundle.
