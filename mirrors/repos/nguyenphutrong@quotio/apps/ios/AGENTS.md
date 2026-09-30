# Quotio iOS

Native iPhone companion, iOS 26+, Swift 6. The app and WidgetKit extension share
`QuotioMobile` and `QuotioHostClient`; do not import desktop `QuotioCore` modules.

- Keep credentials in the shared Keychain access group, never JSON/defaults/logs.
- Keep API identity, quota semantics and freshness authoritative on the Rust host.
- Remote connections require HTTPS and delegated read credentials. Never bypass TLS.
- `project.yml` is the XcodeGen source; check in the generated Xcode project so builds
  do not require XcodeGen. Run `xcodegen generate --spec apps/ios/project.yml` after
  changing target membership or adding resources.
- Shared pure models/tests live in `Sources/QuotioMobile` and `Tests/QuotioMobileTests`.
  Run `swift test --package-path apps/ios` from the repository root.
- Build/test scheme `QuotioIOS` with a discovered iOS 26+ Simulator destination.
  Tests use Swift Testing for models and XCTest for UI.
- UI copy is in `Shared/Localizable.xcstrings`, aligned for en, vi, fr, zh-Hans.
- Preserve privacy in accessibility output, charts, widgets and app-switcher snapshots.
- Do not claim background freshness, physical-device acceptance, signing or remote CI
  success from simulator builds or cross-compilation.

- Team IDs belong only in ignored `Config/Local.xcconfig`. Debug includes it;
  local Release signing passes it explicitly with `-xcconfig`. Never copy signing
  team values into the generator spec, generated project, examples or reports.
