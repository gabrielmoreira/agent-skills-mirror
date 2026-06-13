# Agent guide

This is a native macOS SwiftUI app that manages Pi coding-agent resources and runs Pi sessions through the installed `pi` CLI in JSONL RPC mode.

Use Xcode 26.4+ on macOS 26. Dependencies are resolved through the Xcode project’s Swift Package Manager setup. Local validation commands:
- `xcodebuild -project agent-deck.xcodeproj -scheme agent-deck -configuration Debug -destination 'platform=macOS' CODE_SIGNING_ALLOWED=NO build`
- `xcodebuild -project agent-deck.xcodeproj -scheme agent-deck -destination 'platform=macOS' test`

For release packaging, use the notarized DMG workflow in `scripts/package-dmg.sh` and `.github/workflows/release.yml`.

Critical constraints: never edit bundled built-in resources in place; user edits must go through the app's override/persistence paths. Keep write targets explicit in the UI. Report-only native subagents must write artifacts only, not project files.

For detailed guidance, read the relevant guide before editing that area:

- Invariants and contributor rules: `docs/agent-guidelines/INVARIANTS.md`
- Architecture and source map: `docs/agent-guidelines/ARCHITECTURE.md`
- SwiftUI and toolbar conventions: `docs/agent-guidelines/SWIFTUI.md`
- Build, tests, and validation: `docs/agent-guidelines/TESTING.md`
- Release packaging and signing: `docs/agent-guidelines/RELEASE.md`
