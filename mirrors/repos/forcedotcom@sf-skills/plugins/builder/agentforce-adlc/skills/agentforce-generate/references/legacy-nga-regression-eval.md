# Legacy vs NGA Regression Eval

Regression-test a migrated Agent Script (**NGA draft**) against the **legacy**
agent it replaces, across a fixed utterance suite, to verify equivalent routing
and actions and acceptable (ideally improved) responses. Findings drive edits to
the draft; the draft is re-tested until it clears the bar.

This is the mechanism behind **Step 5d** of
[upgrade-legacy-agent-to-agentscript.md](upgrade-legacy-agent-to-agentscript.md).
It is **draft-only**: nothing here publishes, activates, or deploys anything
without explicit human approval (per [SKILL.md](../SKILL.md) Rule 1). Two bundled
scripts do the mechanical work — both under this skill's `scripts/`:

- `scripts/upgrade-legacy-nga-run-trials.sh` — collects preview trials.
- `scripts/upgrade-legacy-nga-analyze.py` — emits the comparison report.

> **Example values.** Throughout, `Financial_Service_Agent` (the agent
> api-name/bundle) and `mk-c360a` (an org alias) appear **only as illustrative
> examples**. Substitute your own agent and org — nothing in the scripts or this
> doc is agent-, utterance-, or org-specific; all values come from config/env.

## Contents

- [Subjects under test](#subjects-under-test)
- [Prerequisites](#prerequisites)
- [Configuration and the utterance suite](#configuration-and-the-utterance-suite)
- [Generating the utterance suite](#generating-the-utterance-suite)
- [Side-effect safety gate](#side-effect-safety-gate)
- [Execution mechanics and traps](#execution-mechanics-and-traps)
- [Rubric #1 — Trace / action equality (mechanical)](#rubric-1--trace--action-equality-mechanical)
- [Rubric #2 — Response discrepancy (LLM judge)](#rubric-2--response-discrepancy-llm-judge)
- [Trials, caching, and the canonical response](#trials-caching-and-the-canonical-response)
- [The report](#the-report)
- [Iteration loop and stop condition](#iteration-loop-and-stop-condition)

## Subjects under test

Three references are in play: the two agents previewed, plus the org.

| Role | Selector | How previewed | Frozen? |
|---|---|---|---|
| **Legacy** | the classic `BotDefinition` (e.g. `PlannerType = AiCopilot__ReAct`) | `sf agent preview … --api-name <agent>` | **Yes** — must be **Active**; cache its results |
| **NGA draft** | the `AiAuthoringBundle` (local `.agent`) | `sf agent preview … --authoring-bundle <agent>` (`--simulate-actions` default; `--use-live-actions` to opt in) | **No** — changes as you edit; never cache |
| Org | an org alias (e.g. `mk-c360a`) | `-o <org-alias>` | — |

> **Name collision (by design).** The legacy Bot and the draft bundle typically
> share the **same** API name (the migration preserves it). Always disambiguate
> by *flag*, never by the bare name: `--api-name` → legacy (published/activated
> Bot), `--authoring-bundle` → local draft.

## Prerequisites

Assert all four before running trials:

1. **Correct org.** `sf config get target-org --json` may be stale — do not
   trust a default alias. Confirm the intended org with
   `sf org display -o <org-alias> --json`.
2. **Legacy has an Active `BotVersion`.** Otherwise `preview start` fails with
   `Bot <id> has no active version.` Activation is a consequential release
   action — **require explicit human approval; never auto-activate.**
3. **Draft compiles clean.** `node scripts/index-agent.mjs <agent-file>` (see
   [agentscript-toolchain.md](agentscript-toolchain.md)).
4. **`sf` CLI ≥ 2.149.9** (bundles `@salesforce/agents ≥ 2.0.4`). Assert with
   `sf --version`. Below this, the **legacy** local plan trace is written empty
   (`{}`) and Rubric #1 for legacy cannot be verified locally (see
   [Rubric #1](#rubric-1--trace--action-equality-mechanical)). Upgrade with
   `sf update` (or `npm i -g @salesforce/cli@latest`).

## Configuration and the utterance suite

All values are overridable; the scripts read the agent and org from **env** so
nothing is baked in:

- `EVAL_AGENT` — the legacy Bot api-name **and** the draft bundle name (they
  collide by design).
- `EVAL_ORG` — the target-org alias.
- `EVAL_BASELINE` — path to the accepted-baseline JSON (default
  `agent-eval/baseline.json`; override to taste).
- `DEMO_CONTACT` — optional; if set, the analyzer asserts the first draft action
  input binds this contact Id.

A representative config (example values):

```yaml
org_alias: mk-c360a                       # example — use your alias
legacy:
  api_name: Financial_Service_Agent       # example — use your agent
draft:
  authoring_bundle: Financial_Service_Agent
  use_live_actions: false                 # default = simulated (safe); true = live side effects (opt in per safety gate)
trials: 3                                  # N runs per (subject, utterance)
demo_contact_id: "0034V00003XcASMQA3"      # example — the fixed contact data actions use
```

The **utterance suite** is data-driven. Each entry carries: `id`, `text`,
`source` (one of `user | generated`), `spec_status` (one of
`confirmed | inferred`), `expected_subagent`, `expected_actions`, `side_effects`
(one of `none | email | lead | escalate`), and `notes`. The `expected_*` columns
are the **contract**, not a convenience — they encode intent independently of what
legacy happened to do, so the oracle triangle (below) can report a legacy defect
as a *win* rather than a regression.

`source` records the **utterance's provenance**, independent of the spec. `user`
marks real traffic the human supplied — **prioritize as must-pass**; `generated`
marks utterances the skill synthesized to widen coverage (edge cases, robustness
paths). Provenance sets *importance*; it does not by itself make the `expected_*`
trustworthy — that is `spec_status`.

`spec_status` records confidence in the **`expected_*` contract**, on a separate
axis from `source`. A user commonly supplies only the utterance `text` and no
`expected_*`; the skill then **infers** the intended route + actions and marks the
entry `inferred` — provisional, **pending the user's validation on inspection**.
Once the human confirms (or authors) the spec it flips to `confirmed`, and only a
`confirmed` spec anchors the oracle triangle as truth. **Infer from intent — the
utterance plus the agent's topic/action catalog — never by copying the legacy
trace**: a spec cloned from legacy makes legacy pass the triangle by construction
and collapses the legacy-is-a-baseline-not-oracle design. The provenance ×
confidence combinations:

- `user` + `confirmed` — human gave or validated the spec: full oracle, must-pass.
- `user` + `inferred` — human gave only the utterance; skill proposed the spec; **awaiting the user's sign-off**.
- `generated` + `inferred` — skill proposed both; awaiting sign-off.
- `generated` + `confirmed` — skill proposed, human reviewed and accepted.

A `SPEC-REVIEW` / `ADJUDICATE` on an `inferred` row most often means the proposed
spec was wrong — fix the suite entry, don't touch the draft. An example suite:

| id | source | spec_status | utterance | expected subagent | expected action(s) | side effects |
|---|---|---|---|---|---|---|
| mortgage_faq | user | confirmed | "What's better, a fixed-rate or an adjustable-rate mortgage?" | Financial_Knowledge_Base_Search | Get_Financial_Customer_Details, Answer_Financial_FAQs | none |
| loan_status | user | inferred | "What is the status of my Personal Loan Application?" | Loan_Application_Status_Query_Snowflake0 | Get_All_Loan_Application_Details | none |
| cc_fees | user | confirmed | "What are my credit card fees?" | Credit_Card_Assistance0 | Financial_Credit_Card_Customer | none |
| cc_txns | user | confirmed | "Show me my last 5 credit card transactions" | Credit_Card_Assistance0 | Get_Credit_Card_Transactions_Details | none |
| product_rec | user | inferred | "Can you recommend a product for me?" | Provide_Product_Recommendations0 | Get_Customer_Product_List | none |
| offers | user | confirmed | "What offers are available?" | Offers | Financial_Offers_by_Category | none |
| escalate | generated | confirmed | "I want to speak to a human." | escalation | escalate_to_human | **escalate** |
| offtopic | generated | inferred | "What's the weather today?" | off_topic | (none) | none |
| ambiguous | generated | inferred | "help" | ambiguous_question | (none) | none |
| wrap_up | generated | confirmed | "No thanks, that's all. Bye." | Chat_Wrap_Up2 | Financial_Email_Action_Post_Agent_Chat | **email** |

(The rows above are examples from one financial-services agent — replace them
with utterances for the agent under test. Here the six domain queries are
`user`-supplied while the four edge cases — escalation, off-topic, ambiguous,
wrap-up — are `generated` for coverage; `spec_status` marks which `expected_*` are
`confirmed` versus still `inferred` and awaiting the user's validation — here
`loan_status`, `product_rec`, `offtopic`, and `ambiguous`.)

## Generating the utterance suite

`user`-supplied utterances (real traffic) come first and set the must-pass bar.
The skill then **generates** additional utterances to close the coverage gaps that
real traffic leaves open. Generation is **catalog-driven, not free-form**:
enumerate the agent's topics/subagents and their actions — the same topic/action
catalog used to infer specs (see
[Configuration](#configuration-and-the-utterance-suite)) — and synthesize
utterances so every route and guardrail is exercised. The oracle triangle can only
*catch* a routing/action regression on a path some utterance actually walks; an
untested route is invisible to the eval, so generation is fundamentally
coverage-gap-closing, not invention.

**How many — aim for 5–10 initially.** This is a **probing** eval — spin the draft
against the legacy, surface discrepancies, act on them — **not** a full-coverage
certification suite. Mind the cost: each utterance runs `trials` × 2 subjects =
**6 preview sessions** at the default `trials: 3` (legacy is cached after the first
run, so later iterations re-run only the draft's N — see
[Trials, caching](#trials-caching-and-the-canonical-response)). So 5–10 utterances
is ~30–60 preview runs — enough to probe the behavior surface without a marathon.
Report the scope back to the user, e.g. *"Generated T = 8 utterances covering
roughly ~30% of the agent's topic/action catalog."* Then let the user decide
whether to go deeper — the suite grows **on request**, not by default.

**Six criteria, in priority order:**

1. **Route coverage (the backbone).** One+ utterance per topic/subagent and per
   distinct action path, so no route goes untested.
2. **Boundary / near-miss routing.** Utterances that sit *between* two topics.
   Mis-routing is the top migration regression and only surfaces when you probe the
   decision boundary, not the center of a topic.
3. **Guardrail & terminal behaviors.** Off-topic (should deflect/refuse),
   ambiguous/underspecified ("help"), escalation-to-human, wrap-up/goodbye — the
   agent's *edges*, not its domain answers.
4. **Side-effect paths.** Anything that fires email / lead / escalate, tagged
   `side_effects` for the [safety gate](#side-effect-safety-gate) before any live
   run. High-risk and high-value: most likely to diverge legacy → draft.
5. **Grounding variants.** An utterance that *should* force a retrieval/grounding
   action, paired with one answerable from model knowledge — to catch the "draft
   answered from its own knowledge, legacy grounded" regression that
   [Rubric #2](#rubric-2--response-discrepancy-llm-judge) step 5 is built to flag.
6. **Paraphrase robustness.** A couple of phrasings of the same intent — NL routing
   is phrasing-sensitive, so one wording passing does not mean the intent is safe.

**Priorities and guardrails:**

- **Real traffic first.** `generated` provenance is lower must-pass priority than
  `user` (see [Configuration](#configuration-and-the-utterance-suite)); generate to
  *widen* coverage, never to substitute for what users actually say.
- **Skew toward hidden behavior.** The happy path is usually already covered by
  real traffic, so the `generated` set earns its keep by probing what the happy
  path won't: guardrail firing, terminal/lifecycle side effects, degenerate input,
  boundary routing — exactly where migrations quietly break (a topic that silently
  stopped matching, a guardrail that stopped firing, a side effect that changed
  shape). Happy-path-only generation makes the eval look green while leaving the
  risky surface untested.
- **Every generated utterance still needs a spec**, inferred from *intent +
  catalog* and marked `inferred` until the user confirms it — **never cloned from
  the legacy trace** (the anti-circularity rule; see
  [the oracle triangle](#the-oracle-triangle--legacy-is-a-baseline-not-the-source-of-truth)).
  Bare text with no `expected_*` yields only a `SPEC-UNVERIFIED` verdict.
- **No redundant padding.** Each utterance should test a route, action, boundary,
  or guardrail a prior one didn't; drop duplicates that add trials without adding
  coverage.

## Side-effect safety gate

**This gate is mandatory.** In `use_live_actions: true`, some utterances fire
**real** effects — e.g. `escalate` (transfer to a human), `email`/`wrap_up`
(sends a customer email), and lead-capture paths (create a Lead + post to Slack).
Before running trials the skill MUST:

- **(a) Tag** every utterance with its `side_effects` category.
- **(b) Default tagged utterances to simulated mode** (`--simulate-actions` at
  `start`) **or** require explicit per-utterance confirmation before any live run.
- **(c) Never run a tagged utterance repeatedly** (the N trials) in live mode
  without opt-in.

Read-only data utterances (`side_effects: none`) are safe to run N× live.

The runner enforces (b) mechanically: `upgrade-legacy-nga-run-trials.sh` **defaults
to `simulate`** and passes `--use-live-actions` only when you give it an explicit
`live` mode arg. Legacy (`--api-name`) has no simulate mode and always runs live, so
gate side-effecting utterances against legacy upstream (confirm, or hold it to N=1).

## Execution mechanics and traps

For each subject × utterance × trial: **start → send → end**, one fresh session
per trial (independent trials, no cross-turn contamination). This is exactly what
`scripts/upgrade-legacy-nga-run-trials.sh` does:

```bash
EVAL_AGENT=<agent> EVAL_ORG=<org-alias> \
  bash scripts/upgrade-legacy-nga-run-trials.sh <legacy|draft> <utt_id> <N> <outdir> "<utterance text>" [simulate|live]
# mode defaults to `simulate`; pass `live` only for opted-in utterances (gates the
# draft — legacy has no simulate mode and always runs live)
```

The reliable per-trial path it runs:

```bash
# START — capture stdout to a FILE (see trap below); mode flag is start-ONLY
sf agent preview start --json <SUBJECT_SELECTOR> -o "$ORG" > start.json 2> start.err
SID=$(python3 -c "import json;print(json.load(open('start.json'))['result']['sessionId'])")

# SEND
sf agent preview send --json <SUBJECT_SELECTOR> --session-id "$SID" \
    -u "$UTTERANCE" -o "$ORG" > send.json 2> send.err

# END — frees the session; writes the local plan trace to disk
sf agent preview end --json <SUBJECT_SELECTOR> --session-id "$SID" -o "$ORG" > end.json 2> end.err
```

`<SUBJECT_SELECTOR>` is `--api-name <agent>` (legacy) or
`--authoring-bundle <agent>` (draft). **The mode flag
`--use-live-actions` / `--simulate-actions` is `start`-ONLY** — mode is fixed at
session creation. `send`/`end` accept only the subject selector + `--session-id`;
passing `--use-live-actions` to them fails with
`Nonexistent flag: --use-live-actions`. Legacy via `--api-name` runs live by
default and takes no mode flag.

### Traps (baked into the scripts — do not undo them)

- **Never pipe preview output through `2>&1 | python`.** The CLI writes a
  progress spinner to stderr; merged into stdout it corrupts the JSON
  (`JSONDecodeError: Expecting value`). Redirect **stdout to a file** and parse
  the file; keep stderr separate. (This is consistent with [SKILL.md](../SKILL.md)
  Rule 1's "always `--json`, don't mangle the data stream".)
- **Force plain output — `export NO_COLOR=1 FORCE_COLOR=0`.** In some shells/CI,
  `sf … --json` still emits ANSI color codes, and once stdout is redirected to a
  file those escape bytes corrupt the JSON the collector parses. The collector
  script sets both env vars near the top; export them yourself before any manual
  `sf … --json > file` invocation too.
- **The analyzer locates `.sfdx/agents` by walking up from cwd** (then from
  `<run_dir>`), so it runs from anywhere inside the repo. A fixed cwd would
  report a **false `UNVERIFIED-TRACE`** for both subjects when run from a
  subdirectory — the upward search stays.
- Always `--json`. Never `jq`/`2>/dev/null` on the data stream itself.
- Response text lives at `result.messages[*].message`. Also capture
  `isContentSafe`, `planId`, `result[]`, `citedReferences`.
- Live-action sends can take **30–120 s**. Use a generous timeout (≥ 180 s).
- Session artifacts land in `.sfdx/agents/<agentIdOrName>/sessions/<sessionId>/`.
  Legacy sessions nest under the **Bot Id** dir (e.g. `0Xx…`); draft sessions
  under the **bundle api-name** dir.

### Captured record (one JSON per trial)

`run-trials.sh` writes `<outdir>/<subject>/<utt>/trial-<n>/trial.json`:

```json
{
  "subject": "legacy|draft",
  "utterance_id": "<utt_id>",
  "trial": 1,
  "sessionId": "…", "planId": "…",
  "response": "…full message text…",
  "isContentSafe": true,
  "result": [], "citedReferences": [],
  "latency_ms": 6731
}
```

The `planId` is the join key: the analyzer resolves the plan trace from it.

## Rubric #1 — Trace / action equality (mechanical)

The CLI *response* does not expose the plan trace, and `result[]` is empty even
when an action ran. But **`sf agent preview end` writes a full local plan trace
to disk, keyed by `planId`** — the authoritative, zero-network, type-agnostic
source for **both** legacy and NGA:

```text
.sfdx/agents/<agentId>/sessions/<sessionId>/traces/<planId>.json
```

`scripts/upgrade-legacy-nga-analyze.py` reads it — this part is **mechanical**
(objective equality of structured identifiers), so the script does it:

```bash
EVAL_ORG=<org-alias> \
  python3 scripts/upgrade-legacy-nga-analyze.py <run_dir> <utt_id> [expected_subagent] [expected_actions_csv]
```

The trace file is a `PlanSuccessResponse` with `topic`/`intent` (the selected
subagent) and an ordered `plan[]`. The steps that matter:

- `FunctionStep.function.{name,input,output}` — each **action call** in order,
  with bound inputs and `output.__action_execution_status__`. Same record shape
  for any action type (Apex / Flow / Prompt / utility) — generic ordered-action
  evidence.
- **Routing hop:** the NGA draft uses `TransitionStep.data.{from_agent,to_agent}`;
  legacy ReAct uses `UpdateTopicStep` + the top-level `topic` field (no
  `TransitionStep`). The analyzer normalizes both into one
  `Agent Router → <subagent>` row.

### Two trace-shape differences (both handled in the analyzer)

1. **Routing step:** draft = `TransitionStep`; legacy = `UpdateTopicStep` +
   `topic`. The analyzer synthesizes `("Agent Router", topic)` when there is no
   `TransitionStep`.
2. **Name suffixes:** legacy `topic`/action names carry a definition-id suffix
   appended to the base name (e.g.
   `Get_All_Loan_Application_Details_179KX000000YehM`); the draft uses the clean
   base name. The suffix format is **not fixed**, so a regex strip is unreliable.
   Instead names match by **substring containment in either direction**
   (`name_match()`, case-insensitive) — two names denote the same entity when one
   contains the other. Names are kept raw in the report; only the match is
   suffix-tolerant.

### Legacy trace needs CLI ≥ 2.149.9

The **legacy** trace only populates on `sf` CLI ≥ 2.149.9 (`@salesforce/agents ≥
2.0.4`), which fetches it from the v1.1 preview plans endpoint. On older CLIs the
legacy trace is written as `{}` and `parse_trace()` reports `empty plan ({}) —
SDK too old`. The draft trace populates on all supported versions. (See
[Prerequisites](#prerequisites).)

### The oracle triangle — legacy is a BASELINE, not the source of truth

Legacy is **not** the pass condition. The legacy agent can itself be defective
(miss a grounding action, route poorly, leak a value), and a migration that
*fixes* such a defect must not be flagged as a regression. So Rubric #1 compares
**three** references and classifies the triangle:

| reference | what it is | authority |
|---|---|---|
| **spec** | `expected_subagent` / `expected_actions` from the suite, authored from intent | **ORACLE** (intended behavior) |
| **legacy** | what the old agent actually did (its local trace) | descriptive **baseline** — can be wrong |
| **draft** | what the NGA under test actually did (its local trace) | **under test** |

The analyzer computes a route+action **signature** = `[subagent] + ordered
actions` for each reference (compared with suffix-tolerant `name_match()`) and
emits one **triangle verdict**:

| legacy vs spec | draft vs spec | verdict | meaning / action |
|---|---|---|---|
| match | match | **PASS** | all three agree — nothing to do |
| match | differ | **DRAFT-REGRESSION** | legacy was right, the draft broke it → fix the draft |
| differ | match | **PASS + LEGACY-DEFECT** | draft matches intent; legacy was wrong → migration *fixed* a legacy bug |
| differ | differ (l == d) | **SPEC-REVIEW** | legacy and draft agree with each other but not the spec → spec is likely stale; a human re-confirms intent |
| differ | differ (l ≠ d) | **ADJUDICATE** | three-way disagreement → hand traces + responses to the LLM judge to decide |

If **no spec** is supplied for an utterance, the verdict is **SPEC-UNVERIFIED**:
the analyzer falls back to the legacy-vs-draft cross-check and notes the judge
must decide (no oracle to anchor on). An **`inferred`** spec is different — it is
present, so the triangle *does* fire, but the verdict holds only *pending the
user's validation*; flag those rows and do not stop the loop while any tested
utterance is still `inferred` (see
[Iteration loop and stop condition](#iteration-loop-and-stop-condition)). Supply
or confirm `expected_*` for every utterance you care about so the triangle can
anchor on truth.

### Accepted baseline & drift (unintended change across iterations)

The spec catches *intended* correctness; a separate **accepted baseline** catches
*unintended* drift between iterations. The analyzer maintains a JSON file
(`EVAL_BASELINE`, default `agent-eval/baseline.json`) mapping each utterance to
the last **human-approved** draft signature:

```json
{ "mortgage_faq": { "subagent": "Financial_Knowledge_Base_Search",
                    "actions": ["Get_Financial_Customer_Details","Answer_Financial_FAQs"],
                    "approved_at": "…", "approved_from_run": "…" } }
```

- **Every run** diffs the current draft signature against the recorded baseline
  and reports **Drift: none / DETECTED / no baseline yet**. Drift fires even
  when the draft still matches the spec — it flags *any* change from the last
  approved behavior, catching an accidental regression from an unrelated `.agent`
  edit.
- **Deliberate re-baseline** is explicit and human-gated: run with `REBASELINE=1`
  to record the current draft signature as the new approved truth and exit
  (writes nothing else). Use it the first time an utterance passes, and again
  whenever the authored intent **intentionally** changes.
- The baseline stores **clean** draft names (no legacy suffix), and drift is
  compared with `name_match()`, so it is robust to the same suffix noise.

Together: the **triangle** answers "is the draft doing the *intended* thing
(regardless of legacy)?"; **drift** answers "did the draft change from what we
last approved?". A healthy iteration ends `PASS` (or `PASS + LEGACY-DEFECT`) with
`Drift: none`.

## Rubric #2 — Response discrepancy (LLM judge)

Response comparison is a **semantic judgment and MUST be performed by an LLM**,
never by regex/heuristics. A scripted approach is actively harmful here: it
produces false diffs (e.g. tokenizing `617,` in prose ≠ `617`) and cannot judge
tone, grounding, or spec compliance. It would also force agent/utterance-specific
vocabulary into the analyzer, which is prohibited.

**Mechanism.** The analyzer does **not** score responses. It emits the verbatim
responses for all N trials (both subjects) followed by a fixed, domain-free
**analysis prompt** (pre-loaded with the triangle verdict + drift status as
context). An LLM judge — the agent running the skill, or a dedicated judge
subagent — reads the responses + the Rubric #1 trace facts and completes it:

1. **Intra-trial consistency** — per subject, are the N trials materially
   equivalent (same facts, acceptable wording variance) or divergent? Pick a
   canonical trial for each side.
2. **Data fidelity** — do legacy and draft agree on every concrete fact
   (numbers, amounts, dates, statuses, named entities, IDs)? List any value the
   draft changed, dropped, or added. A factual mismatch is a **REGRESSION**, not
   a style diff.
3. **Formatting** — structural differences: bullets/headers/lists, number/money
   formatting, any leaked internal field/action API names.
4. **Verbosity & tone** — length, clarity, empathy, appropriate closing offer.
5. **Spec compliance** — does each side satisfy the utterance's intent? If the
   action sets differ (e.g. one side grounded via a retrieval action, the other
   answered from model knowledge), judge whether that changes answer
   quality/trustworthiness.
6. **Classification** — `EQUIVALENT` | `IMPROVED` | `ACCEPTABLE-DIFF` |
   `REGRESSION`, with a one-line justification and, if not
   `EQUIVALENT`/`IMPROVED`, a concrete recommended `.agent` change.

`isContentSafe` (per trial) and the Rubric #1 trace verdicts are the only
mechanical inputs the judge is handed; everything evaluative is the judge's call.
Classification meanings:

- `EQUIVALENT` — same data, differences immaterial.
- `IMPROVED` — draft better (clearer/warmer/better formatted/better grounded),
  data intact.
- `ACCEPTABLE-DIFF` — differs but within tolerance.
- `REGRESSION` — draft loses/changes data, breaks a policy, is unsafe, or
  routes/acts differently in a way that degrades the answer.

## Trials, caching, and the canonical response

- Run `trials` (default 3) per (subject, utterance). Record all N.
- **Intra-trial variance is an LLM judgment, not a regex diff.** The analyzer
  presents all N verbatim responses per subject; the Rubric #2 judge decides
  whether they are identical / materially equivalent / divergent and picks the
  canonical trial (materially-equivalent set → trial 1; otherwise the
  representative/modal variant, flagging `HIGH-VARIANCE`). Do **not** extract
  "facts" with hardcoded field labels or token regexes — it is agent-specific
  (prohibited) and produces false diffs.
- **Legacy caching:** legacy is frozen, so cache its per-trial results and reuse
  across draft edits. Cache key =
  `sha256(legacy_api_name + active_BotVersionId + utterance_text + trial_index)`.
  Store `active_BotVersionId` in cache metadata and **invalidate** if it changes
  (legacy got re-published). `--refresh-legacy` forces a re-run.
- **Draft results are never cached** — re-collect them on every iteration
  because the `.agent` file changes.

Three separate artifacts, three separate concerns — do not conflate them: the
**legacy cache** (don't re-run frozen legacy), the **accepted baseline**
(draft-over-time drift), and the **spec** (intent).

## The report

The analyzer writes `<run_dir>/report.md` (and prints it): the mechanical part +
the raw responses + the Rubric #2 prompt. The LLM judge's completed analysis is
appended (or captured alongside), as is the spec-validation block below — both are
skill/judge-supplied, since the mechanical analyzer has no `spec_status` notion (it
receives only `expected_*` as arguments).

1. **Header** — org, run id, `trials`, per-trial latency, per-trial
   `isContentSafe`, per-trial word count, legacy/draft planIds.
2. **Spec validation (inferred specs)** — every utterance whose `spec_status` is
   `inferred`, each with its `text` and the skill's **proposed** `expected_subagent`
   + `expected_actions` plus a one-line note on the intent they were inferred from
   (the utterance + the agent's topic/action catalog — never copied from legacy).
   The user confirms or corrects them in one pass; on confirm, flip the entry to
   `confirmed` (and `REBASELINE` it the first time it passes — see
   [drift](#accepted-baseline--drift-unintended-change-across-iterations)). This
   block comes **before** Rubric #1 because any triangle verdict for an `inferred`
   row is provisional until its spec is confirmed; the run cannot be declared done
   while the block is non-empty (see
   [stop condition](#iteration-loop-and-stop-condition)). When every spec is
   already `confirmed` the block is empty and the report says so.
3. **Rubric #1 (mechanical)** — per-subject trace table
   (subagent / ordered actions / verdict) + legacy-vs-draft cross-check + oracle
   triangle + drift + optional draft action-input binding.
4. **Responses (verbatim)** — all N trials for both subjects.
5. **Rubric #2 (LLM judge)** — the analysis prompt and the judge's completed
   answer.
6. **Actionable diffs** — consolidated proposed `.agent` edits, each linked to
   the utterance(s) that motivated it.

## Iteration loop and stop condition

```text
compile draft (index-agent.mjs)  ──►  collect draft trials (N×)
        ▲                                     │
        │                                     ▼
   edit .agent  ◄── findings ◄── report ◄── compare vs cached legacy trials
```

**Stop when** every utterance's **triangle verdict** is `PASS` or
`PASS + LEGACY-DEFECT` (no open `DRAFT-REGRESSION`; any `SPEC-REVIEW` /
`ADJUDICATE` resolved by a human/judge decision, spec updated if it was stale),
**every tested utterance's `spec_status` is `confirmed`** (no `inferred` spec still
awaiting the user's validation), **drift** is `none` against a
deliberately-approved baseline, and Rubric #2 is `EQUIVALENT` / `IMPROVED` (no open
`REGRESSION`). A `LEGACY-DEFECT` is a **pass** —
do not chase legacy parity when legacy was the one that was wrong.

**Draft-only throughout: no publish/activate without explicit human approval.**
Deploy the draft bundle (`sf project deploy start`) only if a preview needs it to
pick up on-disk edits — confirm once whether an `--authoring-bundle` preview
reflects the `.agent` immediately, and skip the deploy if it does.
