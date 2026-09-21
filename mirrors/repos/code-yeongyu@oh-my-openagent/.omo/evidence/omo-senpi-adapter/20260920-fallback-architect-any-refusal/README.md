# Live QA - fallback-architect arms on any refusal-driven fallback (omo#8513)

Branch `fix/fallback-architect-any-refusal`, worktree off `origin/dev` @ `e614da3ce`.

## What was tested

`packages/omo-senpi/scripts/qa/fallback-architect-e2e.mjs` drives the REAL `senpi` binary once per
scenario against an isolated sandbox (own `SENPI_CODING_AGENT_DIR`, `HOME`, `XDG_CONFIG_HOME`,
session dir) and the two-model mock provider in the same directory, then reads the persisted session
JSONL for `omo-fallback-architect:directive` and `omo-fallback-architect:notice` entries.

Six scenarios: A classifier refusal, B Anthropic usage-policy rejection, C transient failure (must
inject nothing), D architect category disabled (must inject nothing), E architect undeclared so the
builtin runtime gate decides, F a refusal on `omo-mock/claude-opus-5` - a primary OUTSIDE the fable
family, which is the behaviour this change adds.

Two driver fixtures moved with it: the mock provider now serves a second primary (`claude-opus-5`)
so F can refuse off a non-fable model, and it registers `claude-fable-5-1` in the registry because
the builtin architect category is gated on `requiresModel: "claude-fable-5-1"`.

## What was observed

`baseline-committed-bundle.json` - the committed (pre-change) extension bundle, this branch's driver:

    result FAIL
    A PASS  B PASS  C PASS  D PASS
    E-builtin-default   FAIL  directives=0
    F-non-fable-refusal FAIL  directives=0

`fallback-architect-e2e.json` - the rebuilt bundle carrying the source change plus the fixture repair:

    result PASS, isolatedRealAgentDir true, liveSessionActivity []
    A PASS  B PASS  C PASS  D PASS  E PASS  F PASS   (directives 1/1/0/0/1/1, notices 1/1/0/0/1/1, exit 0)

F is the RED -> GREEN pair for the defect: a refusal on a non-fable primary injected nothing before
the change and injects exactly one directive and one notice after it.

E failed on the pre-change bundle too, so it is not a regression from this change. Its cause is
fixture drift: the builtin architect gate moved to `claude-fable-5-1` in `2d03a69b3`, while the mock
registry still served only `claude-fable-5`, so the undeclared-category scenario could never reach an
active architect. Adding the gate model to the registry restores what E was written to prove.

## Why it is enough

The unit suite proves the seam (71 tests over the component, including the new non-fable and dotted
fable cases and the copy-conditionality assertions); this driver proves the shipped extension bundle
inside a real senpi session, which is where the gate actually runs. The negative scenarios C and D
still inject nothing, so widening the arming condition did not turn the nudge into noise, and the
notice details (`from` / `to`) are asserted per scenario rather than against a fixed pair.

## What was omitted

No secrets, tokens, credentials or environment dumps are captured: the two JSON files hold only
scenario names, counts, exit statuses and booleans. The sandbox paths are temporary and already gone.
`isolatedRealAgentDir: true` plus an empty `liveSessionActivity` record that the real agent directory
was not written.
