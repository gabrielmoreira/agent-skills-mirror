# Quickstart: NetClaw Mobile Home Screen, Lock Screen, and Control Center Widgets (B1b+B2)

Real widget/control placement, rendering, and refresh timing are 🔌 **DEVICE**-only per spec.md's Context
and each User Story's Independent Test. Run the automated checks first, then the manual steps below on a
real, enrolled iPhone running iOS 18+ (the `NetClawWidgetExtension` target's own floor).

```bash
cd mobile/netclaw-mobile
flutter analyze
flutter test
xcodebuild -workspace ios/Runner.xcworkspace -scheme Runner -sdk iphoneos -configuration Debug build CODE_SIGNING_ALLOWED=NO
```

The `Runner` scheme build embeds and compiles `NetClawWidgetExtension` as part of the same build.

## Verifying User Story 1 (home-screen widget)

1. Long-press the home screen, tap `+`, find "NetClaw," add both the small and medium sizes.
2. Confirm both show Border health, pending-approval count, and a timestamped last-heartbeat reading (e.g.
   "as of 4 minutes ago").
3. Trigger a real heartbeat push and a real pending approval; confirm the widget reflects both the next
   time iOS grants it a refresh (not necessarily instantly — this is expected per FR-004).
4. On a fresh enrollment with no heartbeat ever received, confirm the widget shows a distinct "no data yet"
   state, not a false "all clear."

🔌 **DEVICE** entirely — widget rendering and refresh timing have no meaningful Simulator equivalent for
real iOS refresh-budget behavior.

## Verifying User Story 2 (Lock Screen widget)

1. On the Lock Screen, tap "Customize," add all three NetClaw accessory widgets
   (`.accessoryCircular`/`.accessoryRectangular`/`.accessoryInline`).
2. Confirm each renders legibly and shows no approval target name, requesting agent, or any other
   per-approval detail — a bare count or health summary only.
3. Tap a pending-count widget and confirm the app opens to Approvals; tap a health widget and confirm the
   app opens to Dashboard.

🔌 **DEVICE** entirely.

## Verifying User Story 3 (Control Center control)

1. Open Control Center settings, add the NetClaw control.
2. Confirm it shows the current pending-approval count.
3. Tap it and confirm the app foregrounds directly to Chat with the compose field ready to type — not a
   spoken/silent background ask (Control Center has no text-entry surface, research.md R2).

🔌 **DEVICE** entirely.

## What "done" looks like for this spec

- `flutter analyze` clean, full `flutter test` suite passing, zero regressions, including new coverage for
  `widget_data.dart`'s mirror-call wiring and the two new `netclaw://dashboard`/`netclaw://chat` deep-link
  parsers (SC-005).
- `xcodebuild` for the `Runner` scheme compiles successfully with `NetClawWidgetExtension`'s real content
  (no more Xcode placeholder "favorite emoji"/"timer" template code anywhere).
- Every 🔌 **DEVICE** scenario above exercised on real hardware, or explicitly listed as unverified in
  README's platform-notes section — unchanged honesty standard from specs 072/073/110/111/112/113.
- No widget or control ever shows per-approval detail (SC-002) or implies a heartbeat-derived value is live
  without showing its age (SC-004).
