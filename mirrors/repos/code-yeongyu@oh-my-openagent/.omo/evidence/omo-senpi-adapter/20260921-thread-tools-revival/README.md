# Session-control QA - thread_rename / thread_set_model / thread_set_reasoning

Scenario: `packages/omo-senpi/scripts/qa/thread-tools/session-control-qa.mjs` (registered in `run-all.mjs` as `session-control`).
Run: `THREAD_QA_SENPI_ROOT=<senpi source checkout> bun packages/omo-senpi/scripts/qa/thread-tools/session-control-qa.mjs --out run.log --json report.json`
(The env var is what the shared `lib/harness.mjs` needs for its scratch/fake-model/cleanup helpers; the HOST under test is the engine THIS repo pins, `node_modules/@code-yeongyu/senpi` 1789991284089.)

## WHAT WAS TESTED

Every assertion drives the SHIPPED tool handlers - `createThreadTools` over `createLiveThreadSurface` - so the JSONL frames, the host's model catalog and its thinking-level policy are the real ones, not fixtures.

- Part A, read-only: `thread_list` (and nothing else) against the caller's DEFAULT socket, proving default socket resolution end to end without mutating any real session.
- Part B, isolated: a real `senpi --mode rpc --multi-session` host started by the scenario with its own scratch HOME/agent dir, mock provider and no network. Steps: list, create, rename + fresh-list readback, name_conflict, model_ambiguous, model_not_found, exact provider/id switch, turn-scoped reasoning, unsupported reasoning level, the literal `"self"` address, read, teardown.

## WHAT WAS OBSERVED

Final run: **failures=0 skipped=0**, 13 assertions PASS, `CLEANUP OK`.

- `live-default-socket-readonly` PASS - socket `~/.omo/agent/rpc/rpc.sock`, threads=0 (the user's host had no open sessions at that moment); zero mutations issued.
- `rename-visible-in-fresh-list` PASS - the label a fresh `thread_list` reports equals the one `thread_rename` set, and `thread_id` is unchanged.
- `rename-name-conflict` PASS - `name_conflict`.
- `set-model-ambiguous` PASS - the fragment `mock-mod` returns `model_ambiguous` with candidates `["mock/mock-model","mock/mock-model-fast","mock/mock-model-deep"]` rather than silently taking the first. (A bare `mock-model` would resolve on the exact-id rung, so the probe deliberately uses a fragment that is not an id.)
- `set-model-not-found` PASS - `model_not_found` carrying the available list.
- `set-model-exact` PASS - `mock/mock-model-fast` applied and echoed as `{provider:"mock", id:"mock-model-fast"}`.
- `set-reasoning-turn` PASS - a level the active model supports (`off`), echoed with `scope:"turn"`.
- `set-reasoning-unsupported` PASS - `minimal` on a model whose supported set is `["off"]` returns `thinking_level_unsupported` with `details.supported` deep-equal to the host's own list, and the thread is left unchanged.
- `rename-self` PASS - the literal `"self"` resolved to exactly the caller's own durable id.
- `read` PASS - `source:"live_host"`.
- `cleanup-no-leftovers` PASS - `survivor_pids=[] socket_holders=[] scratch_present=false`.

### Three pre-existing defects this scenario surfaced, all fixed RED-first in this branch

1. **Response correlation** - the one-shot JSONL client settled on the FIRST line the host wrote, so the `open_session` admission notice `{type:"queued", for_request}` (deliberately tagged with the request id, not the response id) or any broadcast failed the pending call. Fixed to correlate by response id (commit `b25f6d2ef`).
2. **Unaddressable create** - `open_session` answers with the ROUTING id and no name, while the address book keys entries by the DURABLE id, so `thread_create` handed back an id that resolved to `not_found` on the very next call, and its `name` parameter was never applied. The adapter now applies the name through `set_session_name` and merges the listed entry, returning an addressable thread.
3. **Session closed on disconnect** - `open_session.retain_on_disconnect` defaults to false, so a session created over this one-shot client went straight to `closing` and every later call answered `session_closing`. The adapter now sends `retain_on_disconnect: true`.

Defect 3 is also why the host must be the engine this repo PINS: `retain_on_disconnect` landed in senpi 2026.9.20, and the harness's default `THREAD_QA_SENPI_ROOT` source checkout on this machine is 2026.9.16, which ignores the flag silently.

## WHY IT IS ENOUGH

The three new tools are exercised on a real multi-session host through the shipped handlers, including all four of their failure codes, and the two addressing rules the family guarantees (`"self"` resolves only to the caller; the id `thread_create` returns is the id every later call accepts). The happy and failure reasoning paths are chosen from the host's own `get_available_thinking_levels`, so the assertion cannot pass by coincidence on a model with a different capability set.

## WHAT WAS OMITTED

- No prompt is ever sent, so no model generation happens; the fake model server exists only to give the catalog a base URL.
- The caller's real host is touched read-only (one `thread_list`), never mutated, and no `ulw-qa-sc-*` session is created on it.
- `thread_send`, `thread_interrupt` and `thread_handoff` delivery are covered by the pre-existing `cli-surface` scenario and the unit suite, not re-proven here.
- Session-scoped (non-turn) reasoning is not asserted against an unsupported level: the wire validates only the turn scope, and recording the remembered preference is the engine's contract, not this family's.
