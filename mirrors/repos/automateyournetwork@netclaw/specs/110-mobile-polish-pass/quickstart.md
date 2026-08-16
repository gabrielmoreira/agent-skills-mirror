# Quickstart: NetClaw Mobile 1.0.1 Polish Pass (Phase A + C1)

All seven stories are provable by `flutter analyze` + `flutter test` except
where noted 🔌 **DEVICE** (per Clarifications, 2026-08-14, and spec.md's
Context). Run the automated checks first, then the manual steps below for
anything that needs a real device/simulator.

```bash
cd mobile/netclaw-mobile
flutter analyze
flutter test
```

## Verifying User Story 1 (dark mode)

```bash
flutter run -d <UDID>
```

On the device/simulator: Settings app → Display & Brightness → Dark, then
return to NetClaw without force-quitting it. Confirm the theme updates live
(no restart needed). Force-quit and relaunch under Dark to confirm cold
start also renders dark. Walk every tab (Dashboard, Chat, Feed, Approvals,
Settings) and visually confirm no light-background flash, no illegible
gray-on-dark text, and the launch splash itself is dark before the app UI
appears.

## Verifying User Story 2 (copy/share/select/markdown)

Seed or generate a long chat answer (the README's own ~1583-byte example, or
any real multi-line CLI output/table). Confirm:

- The answer text can be selected (tap-and-drag a selection).
- The overflow menu (always visible on the turn) offers Copy, "Copy question
  + answer," and Share; long-pressing the answer opens the identical menu.
- An answer containing a fenced code block or a `|`-table renders as
  formatted Markdown, with a monospaced code block and its own copy button.
- An answer containing bare `#`/`*`/`_`/`|` with no fence or table row
  renders as plain monospaced preformatted text, unmangled.
- The identical treatment applies to a Feed message body.

🔌 **DEVICE** (manual, per Clarifications 2026-08-14): scroll rapidly past a
~5000-character seeded answer and confirm no visibly janky/dropped-frame
scrolling. This is a qualitative check, not an automated assertion — record
the outcome in README's platform-notes section either way.

## Verifying User Story 3 (Time Sensitive approvals)

On a physical device (Focus modes are not meaningfully testable in the
simulator): Settings app → Focus → create/enable a Focus mode, configure it
to allow only Time Sensitive notifications. Trigger a real approval push
(e.g. `scripts/edge-heartbeat.py` or an actual pending-change flow) and
confirm it is shown. With the same Focus mode still active, trigger an
ordinary feed/chat-answer push and confirm it is NOT shown. 🔌 **DEVICE**.

## Verifying User Story 4 (Face ID app lock)

Settings → enable "Require Face ID to open NetClaw" → select a grace-period
duration. Force-quit and relaunch: confirm the lock screen appears with no
app content visible until Face ID (or passcode fallback) succeeds. Background
the app briefly (less than the selected duration) and resume: confirm no
re-prompt. Background it longer than the selected duration and resume:
confirm the lock screen reappears. Cancel/fail authentication once and
confirm content is never exposed. Change the grace-period duration and
repeat the background/resume check with the new value. 🔌 **DEVICE** for the
actual biometric prompt; the grace-period arithmetic itself is unit-tested.

## Verifying User Story 5 (haptics)

Phone: trigger each of the six events (receive a mock approval push, resolve
it, complete a chat answer, enroll a fresh device, force a Border
disconnect) on a physical device with haptics enabled and confirm a distinct
buzz per event, with no repeated buzzing while the reconnect loop retries.
🔌 **DEVICE** for feeling the actual haptic; the event-to-haptic-call mapping
and the retry-loop debounce are both unit-tested against a recording fake.

Watch: repeat on the paired Apple Watch app and confirm the watch-native
equivalents fire. 🔌 **DEVICE** entirely (no Dart test surface — Swift-only
change, research.md R6).

## Verifying User Story 6 (search across Chat and Feed)

With a chat history and feed containing several entries: type a query into
each screen's new search field and confirm the list narrows live with
matches highlighted; clear it and confirm the full list returns. Select a
state filter chip (e.g. "failed") and an origin filter chip (e.g. "watch")
together with an active query and confirm all three compose (AND, not OR).
Acknowledge/delete a turn while a filter is active and confirm the correct
underlying turn is affected. Force-close and relaunch the app and confirm
the search/filter state has reset.

## Verifying User Story 7 (Dashboard unread/pending tap-through)

With at least one unread Feed message: open Dashboard, tap "Unread," confirm
the app switches to Feed and the badge/highlight clears exactly as tapping
the Feed tab directly does. Clear that, generate an unread Chat turn instead
(zero unread Feed), tap "Unread" again, confirm it goes to Chat this time.
With both Feed and Chat unread simultaneously, confirm Feed wins. With zero
unread anywhere, confirm tapping "Unread" does nothing. Separately, tap
"Pending approvals" (with any count, including zero) and confirm it always
switches to Approvals.

## What "done" looks like for this spec

- `flutter analyze` clean, full `flutter test` suite passing, zero
  regressions, zero skipped tests (SC-007).
- `pubspec.yaml` at `1.0.1+2` (FR-016).
- Every 🔌 **DEVICE** item above exercised on real hardware, or explicitly
  listed as unverified in README's platform-notes section — the honesty
  standard specs 072/073 established, unchanged here.
- No dead taps remain on the Dashboard's "Unread"/"Pending approvals" rows
  (SC-008).
