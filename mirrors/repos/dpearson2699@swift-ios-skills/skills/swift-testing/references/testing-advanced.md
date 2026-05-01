# Advanced Testing Patterns

Warning-severity issues, programmatic test cancellation, and image attachments for Swift Testing.

## Contents

- [Warning-Severity Issues](#warning-severity-issues)
- [Programmatic Test Cancellation](#programmatic-test-cancellation)
- [Exit Test Value Capturing](#exit-test-value-capturing)
- [Image Attachments](#image-attachments)
- [Proposal Reference](#proposal-reference)

## Warning-Severity Issues

ST-0013 adds a `severity` parameter to `Issue.record()`. Warnings are surfaced in test output but do not cause the test to fail.

```swift
@Test func dataIntegrity() {
    let result = loadData()

    // Hard failure — test fails
    #expect(result.isValid)

    // Warning — logged but test still passes
    if result.processingTime > 2.0 {
        Issue.record(
            "Processing took \(result.processingTime)s — exceeds 2s target",
            severity: .warning
        )
    }
}
```

Use warnings for:
- Performance regressions that aren't blocking
- Deprecated code paths that still work
- Non-critical data quality checks
- Flaky conditions you want to track without failing CI

## Programmatic Test Cancellation

ST-0016 adds `try Test.cancel()` to stop a test from within without marking it as passed or failed. The test is recorded as "cancelled."

```swift
@Test func requiresNetwork() throws {
    guard NetworkMonitor.shared.isConnected else {
        try Test.cancel("No network — skipping integration test")
    }

    let response = try await APIClient.shared.healthCheck()
    #expect(response.status == .ok)
}
```

Key differences from other mechanisms:
- Throwing an error — marks the test as failed
- `withKnownIssue` — marks a failure as expected (test still runs)
- `try Test.cancel()` — marks the test as cancelled (neutral outcome, test stops)

## Exit Test Value Capturing

ST-0012 allows exit tests to capture values from the enclosing scope. Previously, `#expect(exitsWith:)` closures could not reference local variables.

```swift
@Test func exitCodeValidation() async {
    let expectedCode: Int32 = 42
    await #expect(exitsWith: .failure) {
        exit(expectedCode)  // Can now capture `expectedCode`
    }
}
```

## Image Attachments

ST-0014 adds cross-import overlays for attaching images to test results. When you import both `Testing` and a UI framework, attachment initializers for platform image types become available.

```swift
import Testing
import UIKit

@Test func renderedOutput() async throws {
    let view = ChartView(data: sampleData)
    let renderer = UIGraphicsImageRenderer(size: CGSize(width: 400, height: 300))
    let image = renderer.image { ctx in
        view.drawHierarchy(in: view.bounds, afterScreenUpdates: true)
    }

    // Attach UIImage directly — available via cross-import overlay
    Attachment(image, named: "chart-output").record()
}
```

Supported types via overlays:
- `UIImage` (when importing UIKit)
- `CGImage` (when importing CoreGraphics)
- `NSImage` (when importing AppKit — macOS)

## Proposal Reference

| Proposal | Feature |
|---|---|
| ST-0009 | Attachments API (`Attachment` type, `.record()`) |
| ST-0012 | Exit test value capturing |
| ST-0013 | Warning-severity issues (`Issue.record` with `severity:`) |
| ST-0014 | Image attachments on Apple platforms (cross-import overlays) |
| ST-0016 | Programmatic test cancellation (`try Test.cancel()`) |
