# Quickstart: Verifying Pass 3 (Siri Voice Window Tuning and Origin Marker)

## Automated checks (no phone required)

1. **Border-side origin threading** (`tests/n2n/test_edge_ask.py`):
   ```bash
   cd /Users/john.capobianco/netclaw
   python3 -m pytest tests/n2n/test_edge_ask.py -v
   ```
   Confirms `n2n/edge/ask` with an `"origin": "voice"` field reaches `run_agent_turn(origin="voice")`
   unchanged, and a request with no `origin` field still reaches it as `origin=None` (byte-identical
   to today).

2. **Mobile window/marker changes** (`mobile/netclaw-mobile/test/ask_border_headless_test.dart`,
   `edge_ask_client_test.dart` if present):
   ```bash
   cd mobile/netclaw-mobile
   flutter test test/ask_border_headless_test.dart
   ```
   Confirms `askBorderFastWindow` is now 12s (not 18s) and every `runAskBorder()` call sends
   `origin: 'voice'` on the underlying `EdgeAskClient.ask()` call.

## Live verification (needs the phone — User Story 3, do not skip)

Requires: a real iPhone, enrolled with NetClaw, unlocked, connected to the same network as the
Border (or reachable per its normal enrollment path), and the Border running the updated
`service.py`.

1. **Cold case**: restart the Border (or wait for the phone's session to go idle), then ask a
   trivial question by Siri ("Hey Siri, ask NetClaw what two plus two is"). Listen for a real
   spoken answer, not "Sent to NetClaw, I'll let you know when it answers."
2. **Warm case**: immediately ask a second, different trivial question by Siri in the same
   session. Confirm it also lands inside the window.
3. **Voice-shaped answer**: ask a question with a naturally longer honest answer (e.g. "ask NetClaw
   for the Border's health status") by Siri, and the same question through the app's Chat screen.
   Confirm the Siri answer is shorter/plainer and the Chat-screen answer is unchanged from before
   this feature.
4. **Re-run the Border's own measurement tool** (on the Border host) to confirm live numbers still
   match the ~9s/~3.9s this feature's window value was chosen against:
   ```bash
   python3 scripts/measure-turn-latency.py
   ```
   If live numbers disagree meaningfully with Pass 2's recorded baseline, treat the 12s constant as
   provisional and revisit before closing this feature out.
