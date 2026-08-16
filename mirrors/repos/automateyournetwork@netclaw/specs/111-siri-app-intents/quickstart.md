# Quickstart: NetClaw Mobile Siri / App Intents Integration (B1a)

Every intent's core claim — "Siri actually works while the app never opens" — is 🔌 **DEVICE**-only per
spec.md's Context and each User Story's Independent Test; it cannot be simulated meaningfully. Run the
automated checks first, then the manual steps below on a real, enrolled iPhone.

```bash
cd mobile/netclaw-mobile
flutter analyze
flutter test
xcodebuild -workspace ios/Runner.xcworkspace -scheme Runner -sdk iphoneos -configuration Debug build CODE_SIGNING_ALLOWED=NO
```

The Border-side addition has its own quick check (run from repo root — `tests/n2n/conftest.py` adds `mcp-servers/protocol-mcp` to `sys.path` itself):

```bash
python3 -m pytest tests/n2n/test_edge_approvals_list.py
```

## Verifying User Story 1 (AskBorderIntent)

With the app force-quit (not just backgrounded — the strongest test that Siri never opens it) on a real,
enrolled device with the Border reachable:

1. "Hey Siri, ask NetClaw [a real question, e.g. 'is BGP up on the core switch']."
2. Confirm Siri speaks a brief acknowledgment within a few seconds, and the app never appears on screen.
3. Wait for the Border to actually answer (may be seconds to minutes — the README's own 2m13s example is
   realistic). Confirm a local notification arrives with the real answer.
4. Open the app afterward, go to Chat, and confirm the turn is present with the question/answer, and that
   its `origin` reflects a Siri-originated ask (no UI surfaces this directly per this spec's scope — check
   via the persisted JSON file or a debug print if needed).

Repeat with the Border deliberately unreachable (Wi-Fi off, VPN down, whatever makes the Border
unreachable in your environment) and confirm a distinct spoken failure message within a bounded time, not a
hang. Repeat once more on a device with no enrollment at all and confirm a distinct "not set up yet"
message. Try the same phrase via the iPhone 15 Pro+ Action Button (if available) and via a Shortcuts
automation, and confirm both invoke the identical behavior — no separate implementation to verify.

🔌 **DEVICE** entirely — this cannot be exercised in the simulator (Siri phrase invocation, Action Button,
and real background execution all require physical hardware).

## Verifying User Story 2 (PendingApprovalsIntent)

With at least one real pending approval on the Border (trigger one the same way spec 110's US3 quickstart
does) and the app force-quit:

1. "Hey Siri, ask NetClaw how many approvals are pending."
2. Confirm the spoken count matches exactly what the in-app Approvals tab shows when opened immediately
   after.
3. Resolve or let the approval expire, ask again, and confirm the count is genuinely live (decreases),
   not a stale cached number from the first invocation.
4. With zero approvals pending, confirm Siri says so explicitly (e.g., "No approvals are pending"), not a
   bare "0."

Repeat the unreachable-Border and not-enrolled cases exactly as in User Story 1. 🔌 **DEVICE** entirely.

## Verifying User Story 3 (BorderHealthIntent)

With the app force-quit:

1. "Hey Siri, ask NetClaw for Border health."
2. Confirm the spoken summary matches the Dashboard's own connection-status display at that moment,
   including its implied recency (the spoken phrase should acknowledge the heartbeat's age, e.g. "As of 4
   minutes ago...").
3. Trigger a real heartbeat push (e.g. `scripts/edge-heartbeat.py`) while the app is backgrounded, wait for
   it to be delivered, then invoke the phrase again and confirm the spoken summary reflects the new
   heartbeat, not the previous one.
4. On a device that has never received a heartbeat at all (fresh enrollment, before any heartbeat push),
   confirm a distinct "no health data yet" message — not a false "Border unreachable."

Repeat the unreachable-Border and not-enrolled cases exactly as in User Story 1. 🔌 **DEVICE** entirely.

## What "done" looks like for this spec

- `flutter analyze` clean, full `flutter test` suite passing, zero regressions (SC-005).
- `xcodebuild` for the `Runner` scheme compiles successfully with the three new intents and the
  `AppShortcutsProvider` (SC-005).
- The new `n2n/edge/approvals_list` handler has a passing test asserting it returns a live count from
  `Authorizer.pending_approvals()`, not a cached/derived value.
- Every 🔌 **DEVICE** scenario above exercised on real hardware with the operator directly, or explicitly
  listed as unverified in README's platform-notes section — unchanged honesty standard from specs 072/073/
  110.
- No invocation of any of the three intents — success, failure, offline, or unenrolled — ever leaves the
  operator with silence (SC-004).
