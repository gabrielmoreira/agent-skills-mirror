# Quickstart: NetClaw Mobile Siri Reliability Fix + Two-Way Voice + Theme Toggle (Pass 1 of 3)

Prove the three root-cause fixes, the two-way-voice upgrade, and the theme toggle end-to-end on
a real device, then the automated checks.

## Manual walkthrough (🔌 DEVICE required — this bug class does not reproduce off-device)

1. **Fresh install, no foreground launch.** Install a release build (`flutter build ios --release`
   + `xcrun devicectl device install app`) without ever opening the app's UI.
2. **Border Health via Siri.** Say "Hey Siri, check NetClaw Border health." Confirm Siri speaks
   the real, currently-cached status (not a web search, not silence, not a generic error).
3. **Pending Approvals via Shortcuts.** Tap "Pending Approvals" directly in the Shortcuts app.
   Confirm it speaks/shows the real current count.
4. **Ask NetClaw — fast path.** Say "Hey Siri, ask NetClaw a question," answer with something the
   Border can resolve quickly (e.g. a status check backed by a fast API, not a slow CLI/SSH-backed
   one). If the Border finishes within the fast window, confirm Siri speaks the real answer aloud,
   free of `**`/`#`/`- ` markup artifacts.
5. **Ask NetClaw — fallback path.** Ask something slower. Confirm Siri speaks the existing "Sent
   to NetClaw, I'll let you know when it answers" acknowledgment, and that opening the app shortly
   after (or receiving a timely notification) shows the real answer with no duplicate/missing
   entry in the conversation history.
6. **No crash under realistic conditions.** Repeat steps 2-5 with the main app foregrounded,
   backgrounded, and fully force-quit beforehand. Confirm no crash in any state (`idevicecrashreport
   -e -k -u <udid> <dest>` shows no new `Runner-*.ips` after the run).
7. **Theme toggle.** In Settings, choose "Light" while the phone's system setting is Dark. Confirm
   the whole app switches immediately. Force-quit and reopen; confirm it's still Light. Choose
   "System"; confirm it now follows the phone's system setting again.
8. **Diagnostic cleanup confirmed.** Confirm `bh_diag.log`/`bh_diag_native.log` are no longer
   created in the app's Documents directory after any of the above
   (`xcrun devicectl device copy from --domain-type appDataContainer --domain-identifier
   ca.automateyournetwork.netclaw.mobile --source /Documents --destination <dest>` should show
   neither file).

## Automated checks

```bash
cd mobile/netclaw-mobile
flutter test test/ask_border_headless_test.dart \
              test/border_health_headless_test.dart \
              test/pending_approvals_headless_test.dart \
              test/theme_preference_test.dart -r expanded
```

Expected coverage:
- Fast-path two-way-voice return value matches the real answer verbatim, with markdown stripped.
- Fallback acknowledgment path is completely unchanged in behavior and timing semantics.
- A turn answered via the fast path is recorded exactly once, in the `completed` (or `failed`)
  state, indistinguishable in shape from one recorded via the existing slow/notify path.
- `ThemePreference` round-trips all three values and defaults to `system` when never set.

## Success signals (from spec)

- SC-001: all three actions succeed on first real attempt ≥9/10 tries, fresh install, no prior
  foreground launch.
- SC-002: fast-path spoken answers are markup-free ≥9/10 tries when the Border answers in time.
- SC-003: zero lost/duplicated/stuck Siri-originated turns.
- SC-004: theme choice honored immediately and remembered across a full app restart, 100%.
- SC-005: zero crashes attributable to a voice/Shortcuts action across a full verification pass.
