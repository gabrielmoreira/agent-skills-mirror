# Quickstart: Verifying the Border Turn Latency Fix

**Feature**: [spec.md](./spec.md) | **Contracts**: [gateway-ws-rpc.md](./contracts/gateway-ws-rpc.md), [run-agent-turn.md](./contracts/run-agent-turn.md)

## Run the measurement script (FR-016a, SC-009)

```bash
cd /home/johncapobianco/netclaw
python3 scripts/measure-turn-latency.py
```

Reports, in one invocation:

1. **Fixed preparation time** — reads the gateway's own `[trace:embedded-run]` log line for a
   freshly-fired trivial turn and extracts the `bundle-tools:NNms` component (the same field this
   feature's research.md used to find the root cause).
2. **Trivial-turn end-to-end time** — wall-clock from request to reply for a controlled two-
   character-answer question, same measurement method as the spec's 37.9s baseline.
3. **Recent real phone-question durations** — pulls the last N (default 20, matching the spec's
   original sample) recorded Siri/phone-originated turn durations from the session store, reporting
   min/median/max, same method as the spec's 36s–452s baseline.

Compare its output against this spec's recorded baseline table (spec.md, "Context: what was
measured") and the targets in Success Criteria (SC-001, SC-002, SC-004).

## Manual before/after check

```bash
# Before the fix is applied (or on main, for comparison):
time openclaw agent --agent main --session-key manual-check-1 --json -m "Reply with exactly: OK"
time openclaw agent --agent main --session-key manual-check-1 --json -m "Reply with exactly: OK"
# Expect: both calls pay ~27-37s (today's behavior — no reuse even within one session key).

# After the fix (once gateway.py dispatches via WS RPC without cleanupBundleMcpOnRunEnd):
# Fire two turns in the same session_key through the Border's normal entry point (Slack, chat,
# or a direct call into run_agent_turn) and confirm the SECOND is not slower than the first —
# ideally near-instant relative to the ~27s first-turn cost (SC-003).
```

## Verify capability retention (FR-004, SC-005)

Exercise each of the 8 configured MCP servers' tools once each through a real turn (not just
`openclaw mcp doctor`), confirming every one still answers correctly post-fix. If any capability is
deliberately made ready on first use (FR-004a), exercise it twice in the same session and confirm
the readiness cost is paid only on the first of the two (SC-005).

## Verify voice-aware composition (US2, SC-007)

```bash
# Simulate a voice-marked request directly (the phone doesn't send this yet — Assumptions):
python3 -c "
import asyncio
from bgp.federation.gateway import run_agent_turn
print(asyncio.run(run_agent_turn('What is the Border health status?', origin='voice')))
"
```

Confirm: one or two plain sentences, no headers/bullets/emphasis markup, a complete honest
statement (not truncated). Then confirm an identical call **without** `origin` still returns
today's full-formatting answer (SC-006 — no observable change for unmarked requests).

## Verify backward compatibility (FR-008, SC-006)

Run the existing `chat.py`/`invocation.py`/`service.py` call sites exactly as they are today (no
code change needed) and confirm output is indistinguishable from pre-fix behavior for requests that
carry no origin marker.
