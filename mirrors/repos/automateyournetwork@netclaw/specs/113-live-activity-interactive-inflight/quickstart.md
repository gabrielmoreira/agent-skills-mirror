# Quickstart: NetClaw Mobile Interactive and In-Flight Live Activity (B3)

Both items' core claims — a real interactive Lock Screen button, a real ticking timer, real Dynamic
Island rendering — are 🔌 **DEVICE**-only per spec.md's Context and each User Story's Independent Test.
Run the automated checks first, then the manual steps below on a real, enrolled iPhone.

```bash
cd mobile/netclaw-mobile
flutter analyze
flutter test
xcodebuild -workspace ios/Runner.xcworkspace -scheme Runner -sdk iphoneos -configuration Debug build CODE_SIGNING_ALLOWED=NO
```

The `Runner` scheme build embeds and compiles the `LiveActivityWidget` extension target as part of the
same build (matching how spec 112 verified `WatchComplication` via the `WatchApp` scheme rather than a
standalone extension-scheme invocation).

## Verifying User Story 1 (Approve/Deny from the Lock Screen)

On a real, enrolled iOS 17+ device with the phone locked:

1. Trigger a real pending approval on the Border (same method spec 110's US3 quickstart uses) so its Live
   Activity appears on the Lock Screen.
2. Without unlocking manually, tap "Approve" on the activity.
3. Confirm the device unlocks/foregrounds directly into the Approvals tab, and the existing fresh
   biometric/passcode confirmation prompt for that approval appears or is immediately available — NOT
   already resolved.
4. Complete the confirmation and confirm the approval resolves normally, and the Live Activity updates to
   a resolved state and dismisses (User Story 2).
5. Repeat with "Deny" and confirm the same foreground-not-resolve behavior.
6. On an iOS 16.2 device (below 17) if available, confirm the activity shows no buttons at all and behaves
   exactly as it did before this spec.

🔌 **DEVICE** entirely — a locked-screen interactive Live Activity button cannot be meaningfully exercised
in the Simulator.

## Verifying User Story 2 (activity reflects resolution from any surface)

With a pending-approval Live Activity showing, resolve that same approval from a different surface each
time: the in-app Approvals screen, a notification's Approve/Deny action, and (if a paired watch is
available) the watch app. Confirm the Live Activity updates to a resolved state and dismisses each time,
without the operator having touched the activity itself.

🔌 **DEVICE** entirely.

## Verifying User Story 3 (in-flight query activity)

With the app backgrounded or the phone locked:

1. Submit a real question through Chat expected to take at least a minute (a real multi-member question,
   per the README's own documented examples).
2. Confirm a Live Activity appears within about a second, showing the question text and a timer starting
   at zero and ticking continuously.
3. If the Border sends a `task_progress` update (a stall-checkpoint message), confirm the activity's status
   text updates to show it verbatim — and confirm no member count of any kind ever appears anywhere in the
   activity.
4. Wait for the answer (or force a failure/cancellation) and confirm the activity reflects that outcome
   and then ends — it does not keep ticking afterward.
5. Submit a second question while the first is still in flight and confirm two independent activities
   appear, each tracking its own state.
6. Tap the in-flight activity and confirm the app opens to Chat, showing that specific turn.

🔌 **DEVICE** entirely — Dynamic Island/Lock Screen live-timer behavior has no meaningful Simulator
equivalent.

## What "done" looks like for this spec

- `flutter analyze` clean, full `flutter test` suite passing, zero regressions, including new coverage for
  `live_activity.dart`'s start/update/end sequencing per task id and the two new `netclaw://` deep-link
  shapes (SC-006).
- `xcodebuild` for the `Runner` scheme compiles successfully with the three new Swift files correctly
  added to their required target(s) (dual membership for `AskActivityAttributes.swift`, research.md R5).
- Every 🔌 **DEVICE** scenario above exercised on real hardware, or explicitly listed as unverified in
  README's platform-notes section — unchanged honesty standard from specs 072/073/110/111/112.
- No approval is ever resolved from a Live Activity tap without the operator completing the existing fresh
  biometric/passcode confirmation (SC-002) — the one non-negotiable safety property this spec must not
  regress.
- Nothing shown by the in-flight activity is ever fabricated (SC-005) — no member count anywhere.
