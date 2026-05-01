---
name: testing-strategy
description: Testing strategy for SwiftUI + watchOS. Defines unit/UI coverage, ViewModel tests, haptics verification, localization checks, and CI-safe expectations.
---

# Testing Strategy

Build confidence across core flows with a layered test approach. Focus on deterministic logic, stable UI flows, and regression coverage.

## When to use this skill

- Before App Store submission
- When adding a new feature or ViewModel
- After refactors touching haptics, timers, or syncing
- When flaky UI tests appear

---

## Test Layers

### 1) Unit Tests (Fast, deterministic)

**Targets:** ViewModels, Managers, Models, Utilities

Checklist:
- Pure logic in Models/Utilities has unit tests
- ViewModels tested for state transitions
- Async flows tested with `XCTestExpectation`
- Watch sync logic tested with mock `WCSession`

Suggested patterns:
- Dependency injection via protocols
- Use fakes/stubs for haptics, timers, clock

### 2) UI Tests (Critical flows only)

**Targets:** Core journeys and regressions

Recommended flows:
- Start/stop timer
- Edit haptic pattern
- Save/restore presets
- Watch ↔ Phone sync path (smoke test)

### 3) Snapshot / Visual Regression (Optional)

Use snapshots for stable screens (settings, templates, empty states). Avoid animation-heavy views.

---

## Coverage Map (Suggested)

| Area | Minimum Coverage | Notes |
|------|------------------|-------|
| ViewModels | 80%+ | Highest ROI tests |
| Managers | 70%+ | Haptics, timers, storage |
| Views | Key flows | UI test smoke coverage |
| Watch sync | Basic | Validate payload and fallback |
| Localization | Automated | Ensure no missing keys |

---

## Test Hygiene

- Avoid hardcoded dates; inject clocks
- Avoid timers in tests; inject schedulers
- Use `@MainActor` for UI-bound tests
- Keep UI tests under 3–5 critical paths

---

## Localization Regression

Run localization scripts as part of CI or before release:

```bash
python3 scripts/check_localization_status.py YourApp/Localizable.xcstrings
python3 scripts/check_localization_status.py YourApp/AppIntents/AppShortcuts.xcstrings
python3 scripts/check_localization_status.py "YourApp Watch App/Localizable.xcstrings"
```

---

## Output Format

| Category | Status | Notes |
|----------|--------|-------|
| Unit test coverage | ✅/❌ | Gaps listed |
| ViewModel tests | ✅/❌ | Missing cases |
| UI smoke flows | ✅/❌ | Flaky steps |
| Watch sync tests | ✅/❌ | Missing coverage |
| Localization checks | ✅/❌ | Missing keys |
