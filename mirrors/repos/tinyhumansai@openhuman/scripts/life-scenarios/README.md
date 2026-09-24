# Life-scenario harness benchmark

Six everyday assistant tasks — calendar triage, receipt scanning, live web
research, planning, multi-source synthesis, and a fact-check-and-publish
pipeline — run against the real OpenHuman core and scored on what actually
landed on disk.

It answers one question: **how much of a realistic task does the shipping
harness finish, and what does that cost in tokens, cache, money and time?**

```bash
# everything, on the shipping desktop path
node scripts/life-scenarios/run.mjs

# one scenario, a stronger model
node scripts/life-scenarios/run.mjs --only calendar-buffer --model anthropic/claude-sonnet-5

# the comparison arm: a custom agent definition with file tools advertised
node scripts/life-scenarios/run.mjs --driver rpc --agent life_scenarios

# re-score an old run without spending anything
node scripts/life-scenarios/run.mjs --grade-only target/life-scenarios/<run-id>
```

Requires a built core (`cargo build --manifest-path Cargo.toml -p openhuman-cli
--bin openhuman-core`) and `OPENROUTER_API_KEY` in the environment.

## Headless, but shaped like the desktop app

The default `--driver desktop` drives the core the way the Tauri composer
does, with the UI removed and nothing else changed:

| desktop app | here |
| --- | --- |
| Tauri spawns the core as a tokio task | spawn `openhuman-core serve` |
| composer calls `openhuman.channel_web_chat` | same RPC, same params |
| reply streams over Socket.IO | same events over `GET /events` |
| orchestrator agent, every tool pack withheld | same — no custom definition |
| approval gate ON, a human clicks Approve | gate ON, a responder approves |
| BYOK set in Settings → Models | `config.update_model_settings` |
| signed-in session | offline local session |

Three things are deliberately *not* the app, and each buys reproducibility:

- **Its own `HOME`.** `default_root_openhuman_dir` resolves `<home>/.openhuman`,
  so config, keyring, auth profiles, workspace and session db all land in the
  run directory. A run cannot read or corrupt the operator's install — and
  installing a credential into a shared `~/.openhuman` would sign a running
  desktop app out.
- **BYOK inference, not the hosted backend.** A benchmark whose price and
  availability belong to someone else is not a benchmark. `--managed` opts
  back into the account's own configured route.
- **A mock Composio.** See below.
- **A mock search backend.** See below.

`--driver rpc` switches to `openhuman.inference_agent_chat`, the only path that
can scope a per-turn `cwd` and name an `agent_id`. That is the comparison arm,
not the product path.

## The corpus is fictional

Everything under `fixtures/` is invented: one persona (Alex Rivera
`<alex.rivera@example.com>`), eleven mail messages, a seven-event calendar day,
a generated PDF hotel booking, and a draft article. Every domain is
`*.example`. Nothing here came from a real mailbox, calendar or bank, so the
whole corpus is safe to commit and a run is repeatable.

The fixtures are anchored to **2026-09-22** as "today"; the scenario prompts
say so explicitly rather than relying on the clock.

Each scenario gets a fresh copy of the whole corpus in
`target/life-scenarios/<run-id>/sandbox/<scenario-id>/`, which is the agent's
action directory. Outputs are expected under `out/`.

### Mock Composio

Scenarios 1, 2 and 5 are *about* mail and calendar. Stubbing those out would
benchmark the wrong thing, and the real Composio needs live consumer accounts,
costs quota and is not reproducible. So `mock-composio.mjs` serves Composio's
wire shape over the same fixtures the file tools see: `GMAIL_FETCH_EMAILS`
returns the fixture mailbox in Gmail's message shape,
`GOOGLECALENDAR_EVENTS_LIST` returns the fixture calendar in Google's event
shape, and the write actions (`GMAIL_SEND_EMAIL`, `GOOGLECALENDAR_UPDATE_EVENT`)
record what the agent *tried* to do into `composio-outbox.json` instead of
doing it — so a grader can assert on the attempt.

Wiring it up needs three things together, and two of them are easy to miss:

1. `[composio] mode = "direct"` in `config.toml`. `create_composio_client`
   dispatches on that field alone; in the default `backend` mode the env
   override is never consulted.
2. **Both** `OPENHUMAN_COMPOSIO_DIRECT_BASE_V2` and `..._V3`. The match arm is
   `(Some, Some)` — setting only one silently falls through to the production
   Composio URLs.
3. A **debug** build. The env override in
   `integrations/composio/client/factory.rs` is `#[cfg(debug_assertions)]`-gated.

### Mock search

`web_search_tool` is not a local tool: it posts to
`/agent-integrations/parallel/search` on the hosted backend, which resolves the
query against a paid provider and bills the caller's team. This run has no
session to spend — inference is BYOK and the credential is an offline local
token — so every call came back `SESSION_EXPIRED … 401 Invalid token`.

The tool was advertised anyway, so the model spent calls discovering it was dead
and then routed around it by hand. In the 2026-09-23 run `baggage-policy` burned
two calls on the 401s, improvised a DuckDuckGo HTML scrape, guessed delta.com
paths and collected four 404s — then hit the 15-call cap with the answer
assembled and the requested file unwritten, scoring 0/1. Offering a capability
the run's own configuration cannot serve is a defect in the rig.

`mock-search.mjs` fixes it by **mocking discovery, not retrieval**. It ranks the
fixture corpus in `fixtures/search-index.json` and returns *real, live* URLs; the
agent still fetches every page over the network with `web_fetch` and still has to
read what the page says. So `baggage-policy`'s `cites_delta_com` and
`states_carryon_dimensions` checks stay honest — what is gone is the search
engine the run cannot pay for, not the comprehension being measured. Excerpts in
the fixture stop short of the numbers the graders assert on, so an agent that
answers from the excerpt alone still fails.

Ranking is deliberately crude (weighted term overlap over keywords, title, URL
and excerpt). A query the corpus does not cover returns **nothing** rather than
the least-bad rows: a confidently wrong result set is worse for the agent than an
empty one, because it spends fetches on it.

Three things were easy to get wrong, and all three cost a run:

1. **It has to take over the whole backend base.** `api_url` is the single base
   every backend caller resolves through (`api::config::effective_backend_api_url`).
   Loopback on an ephemeral port is what makes that work:
   `looks_like_local_ai_endpoint` treats loopback as an inference signal only
   when paired with an LLM-ish port or path, so a bare `http://127.0.0.1:<random>`
   passes through as a backend override.
2. **`api_url` in `config.toml` is not enough.** `auth.set_credential` activates
   a per-user config dir whose id the core derives at runtime; `prepareHome`
   writes `users/local/`, the core activates `users/local-dragonfly/`, finds no
   `api_url` there and falls back to the hosted backend. The override that
   actually holds is `BACKEND_URL`, which `api_base_from_env` reads whichever
   config wins.
3. **Every response needs the `{ success, data }` envelope.**
   `integrations/client/errors.rs::parse_envelope` unwraps it. A bare payload
   fails as `missing field 'success'` — and fails late enough to read as a
   broken tool rather than an empty result, so the agent abandons the task. It
   did exactly that, six times in a row.

The other backend calls the run cannot authenticate (`/teams/me/usage`, the
Composio toolkit list) get benign stubs, so the log shows the run's own
behaviour rather than one fixed auth failure repeated every turn. Composio is
untouched: it is redirected separately over `OPENHUMAN_COMPOSIO_DIRECT_BASE_V*`.

`--no-mock-search` opts out and dials the hosted backend.

Self-test: `scripts/__tests__/life-scenarios-mock-search.test.mjs`.

## Approvals are answered, not switched off

The gate is installed and an `ApprovalResponder` answers it — it polls
`approval.list_pending` and answers `approve_once`, exactly as the approval card
does, recording every decision to `approvals.json`. A headless harness that sets
`OPENHUMAN_APPROVAL_GATE=0` is measuring a product nobody runs; one that leaves
the gate unanswered is measuring the ten-minute deny timeout.

**How many approvals a task needed is itself a result.** A task that parks
fourteen times is not one a supervised user would enjoy, however good the final
artifact is. `--no-approvals` uninstalls the gate instead, for comparison.

Expect that number to be near zero on the default run, and read it as a
property of the product rather than of the harness: the shipped autonomy policy
is **off** (`[autonomy] enabled = false`), so `gate_decision` answers `Allow`
for every class and almost nothing parks. Flip `enabled = true` in
`prepareHome`'s config block to measure the supervised arm, where the responder
does the work the approval card would.

## Grading

"The turn completed" is not completion. A model that writes a plausible CSV
full of invented rows has to score zero on the rows it invented, so every
grader checks facts that are only derivable from the fixtures:

- `calendar-buffer` — exactly three gaps under 15 minutes exist (`ev-02` at 0
  min, `ev-05` at 0, `ev-06` at **10** — the one that catches a model matching
  on "back-to-back" rather than "under fifteen"), and `ev-07` is a solo focus
  block that must *not* be flagged.
- `subscription-scan` — four real subscriptions among a one-off order, a
  usage-based utility bill, a phishing mail and a bank alert that duplicates a
  receipt already counted. Only StreamFlix rose in price (13.99 → 15.99).
- `baggage-policy` — the only scenario that leaves the sandbox. Demands cited
  `delta.com` URLs, so a model answering from memory is detectable.
- `meal-plan` — five days, prep under 30 minutes, no duplicate grocery lines,
  and spinach/feta/olive oil each reused across at least two dinners.
- `trip-itinerary` — facts that exist *only* inside the binary PDF (hotel name,
  address, phone), plus the flight code from the mail, plus a live weather
  source. 14 October is spent in the air and must not be scheduled.
- `fact-check-publish` — one asset referenced by the draft is missing from
  disk and one hyperlink does not resolve; both must be named in the lint
  report and must not survive into either output.

Scores are `passed/total` checks. Failed check ids are printed with the detail
that explains them.

## Output

```
target/life-scenarios/<run-id>/
  results.json            per-scenario usage, grade, tool calls, files written
  approvals.json          every approval decision the responder made
  composio-outbox.json    writes the agent attempted through Composio
  composio-requests.json  every request the mock received
  search-requests.json    every query the mock search served, and what it matched
  core.log                the core's own log for the whole run
  home/                   the throwaway HOME (config, keyring, workspace)
  sandbox/<scenario>/     the corpus copy the agent worked in
```

## Known harness findings this suite surfaced

- [`FINDINGS.md`](FINDINGS.md) — the defect list, ranked, with the fix each wants.
- [`DIAGNOSIS.md`](DIAGNOSIS.md) — the causal trace behind the headline result
  (four of six scenarios wrote nothing), tool call by tool call, including the
  two claims from the first pass that did not survive checking.
