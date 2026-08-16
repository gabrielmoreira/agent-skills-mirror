# Quickstart: NetClaw Mobile Watch Double Tap and Corner Complication (B4+B5)

Both items' core claim — a real Double Tap gesture, and real complication placement on an Infograph
watch face — are 🔌 **DEVICE**-only per spec.md's Context and each User Story's Independent Test. Run the
automated checks first, then the manual steps below on a real, paired Series 9/Ultra 2-or-later Apple
Watch.

```bash
cd mobile/netclaw-mobile
flutter analyze
flutter test
xcodebuild -workspace ios/Runner.xcworkspace -scheme WatchApp -sdk watchsimulator -configuration Debug build CODE_SIGNING_ALLOWED=NO
```

The first two commands are a pure regression guard — this spec touches no Dart code, so both must show
zero change in outcome versus the pre-existing baseline. The `WatchApp` scheme embeds and builds
`WatchComplication.appex` as part of the same build, so it verifies both targets — a standalone
`-scheme WatchComplication -sdk watchsimulator` invocation is deliberately not used here: it fails on
completely unmodified code too (confirmed via `git stash`), hitting the pre-existing "cross-SDK build
trap" README's spec 072 entry already documents (`-sdk` as a blunt flag forces every workspace target,
including phone-only plugins with no watchOS platform support at all, onto the watch SDK).

## Verifying User Story 1 (Double Tap on the topmost approval)

With a real, paired Series 9/Ultra 2-or-later Apple Watch running watchOS 11+:

1. Trigger a real pending approval on the Border (same method spec 110's US3 quickstart uses) so at least
   one shows in the watch app's Approvals tab.
2. Perform a Double Tap (pinch thumb and index finger together twice) while the Approvals view is open.
3. Confirm the same passcode-confirmation prompt a manual "Approve" tap would show appears, referencing
   that approval's target name.
4. Complete the prompt and confirm the approval resolves and disappears from the list, identical to a
   manual "Approve" tap succeeding.
5. Trigger a second pending approval, so two are showing. Double Tap again and confirm only the topmost
   approval's prompt appears — the second approval is untouched.
6. Cancel or fail the prompt (wrong passcode, or dismiss) and confirm nothing was resolved — the list is
   unchanged.
7. Clear all pending approvals so the list is empty, or force a connection-error state, and confirm Double
   Tap does nothing observable.

🔌 **DEVICE** entirely — Double Tap is a hardware-gated system gesture unavailable in the Simulator.

## Verifying User Story 2 (Double Tap to read an answer aloud)

On the same watch, submit a question via the Ask tab and wait for an answer. With the answer showing and
the "Read aloud" button visible, perform a Double Tap and confirm the answer is spoken aloud, identical to
tapping the button manually. Then return to the idle/waiting/failed states and confirm Double Tap does
nothing in those states.

🔌 **DEVICE** entirely.

## Verifying User Story 3 (corner complications)

On the same watch, set the active watch face to Infograph (or Infograph Modular). Open the face editor and
attempt to place both "NetClaw Status" and "Pending Approvals" into a corner slot. Confirm both are
selectable and render legibly. Trigger a real heartbeat push and a real approval, and confirm both corner
complications update the same way their existing circular/rectangular/inline placements already do.
Separately, on a fresh enrollment with no heartbeat ever received, confirm the heartbeat corner
complication shows the distinct "no data" state, not a false "all clear."

🔌 **DEVICE** entirely — accurate corner-slot rendering on a real Infograph face cannot be meaningfully
judged in the Simulator.

## Verifying backwards compatibility (FR-004/FR-006)

If a pre-Series-9 watch or a Series 9/Ultra 2 watch running watchOS below 11 is available, open the
Approvals and Ask views and confirm manual Approve/Deny/Read-aloud taps work exactly as before this spec —
no crash, no missing button, no behavior change. This is the direct verification of FR-004's "nothing
changes and nothing breaks" bar. If no such device is available, this step is explicitly listed as
unverified in README's platform-notes section rather than assumed.

## What "done" looks like for this spec

- `flutter analyze` clean, full `flutter test` suite passing, zero regressions (SC-005) — expected to be
  identical to the pre-existing baseline since no Dart code changes.
- Both `xcodebuild` commands above succeed for `WatchApp` and `WatchComplication` (SC-005).
- Every 🔌 **DEVICE** item above exercised on real hardware, or explicitly listed as unverified in
  README's platform-notes section — the honesty standard specs 072/073/110/111 established, unchanged
  here.
- No Double Tap gesture, under any Approvals-view state, ever resolves an approval without a passcode
  confirmation having succeeded first (SC-002) — the one safety property this spec must not regress.
