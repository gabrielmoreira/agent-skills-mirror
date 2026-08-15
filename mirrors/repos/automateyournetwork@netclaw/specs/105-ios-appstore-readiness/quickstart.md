# Quickstart: iOS App Store Submission Readiness, Phase 1

## Verifying User Story 1 (onboarding explainer)

```bash
cd mobile/netclaw-mobile
# Uninstall first so local state (including any prior enrollment) is gone --
# NOTE: this also wipes the paired watch's transfer state, per lessons from
# spec 103; expect to redo Developer Mode / re-pair steps if testing on the
# same hardware used for that spec.
xcrun devicectl device uninstall app --device <UDID> ca.automateyournetwork.netclaw.mobile
flutter run -d <UDID> --debug
```

Confirm the explainer screen appears before the camera/QR scanner. Then
complete enrollment (scan a fresh QR from `./scripts/netclaw risk token
--edge <label>` on the Border) and relaunch — confirm the explainer does
NOT reappear.

For **SC-001**: show the explainer screen (not the whole app) to one person
who has never heard of NetClaw, and confirm they can correctly state, in
their own words, that a separate server they don't yet have is required.

## Verifying User Story 2 (device removal)

With an enrolled device: Settings → the new "Remove this device" control →
complete Face ID/Touch ID → confirm the app returns to the enrollment gate
(and, since no enrollment now exists, US1's explainer reappears on the very
next launch). Confirm cancelling the biometric prompt leaves the device
enrolled and unchanged. Time this flow — **SC-002** requires it to complete
in under 30 seconds.

Then repeat with the Border unreachable (turn off Wi-Fi/disconnect the
Border host) and confirm removal still succeeds — this is **FR-006**, and is
the whole point of the control existing (escaping a bad enrollment must not
require that enrollment's own server to cooperate).

## Executing User Story 3 (distribution build + TestFlight)

```bash
cd mobile/netclaw-mobile

# 1. Produce a distribution-signed archive + .ipa (research.md R3) --
#    same command-line path that has worked all session, pointed at
#    Release/distribution config instead of Debug.
flutter build ipa --export-options-plist=ios/ExportOptions.plist
# Output: build/ios/ipa/netclaw_mobile.ipa (exact name may vary --
# check flutter's own output for the actual path)

# 2. Upload to App Store Connect (research.md R4) using an API key
#    generated once in App Store Connect -> Users and Access -> Integrations.
#    `altool` does NOT take the key material on the command line -- it looks
#    for a file named AuthKey_<KEY_ID>.p8 in one of a few fixed local
#    directories. Place the downloaded key at one of these BEFORE running
#    the upload command, or it fails with a "key not found" error that gives
#    no hint what's missing:
#      ~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8
#      ~/.private_keys/AuthKey_<KEY_ID>.p8
mkdir -p ~/.appstoreconnect/private_keys
# (move/copy the downloaded AuthKey_<KEY_ID>.p8 into that directory now)

xcrun altool --upload-app \
  -f build/ios/ipa/netclaw_mobile.ipa \
  -t ios \
  --apiKey <KEY_ID> \
  --apiIssuer <ISSUER_ID>
```

If `ios/ExportOptions.plist` does not yet exist, Xcode's Organizer can
generate one interactively the first time (Product → Archive → Distribute
App → App Store Connect → stop before actually uploading, just export the
plist) — a one-time GUI step to produce a reusable, checked-in config file,
not a repeated dependency on the GUI for every future build.

3. In App Store Connect, once the build finishes processing: **TestFlight**
   tab → **External Testing** → create a group → add the build → invite at
   least one tester. Submitting here is what satisfies SC-004 per the
   Clarifications session — Apple's Beta App Review clearing is tracked
   separately, not required for this spec to be considered done.

## What "done" looks like for this spec

- A stranger installing fresh sees the explainer before the scanner (US1).
- An enrolled operator can remove their device via Settings + Face ID, with
  no Border-side action required (US2).
- One archive has been produced under distribution signing and submitted to
  an External Testing group in TestFlight (US3) — waiting on Apple's review
  to actually clear is explicitly not part of this spec's completion.
