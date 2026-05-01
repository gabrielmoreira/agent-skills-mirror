---
name: crash-safety
description: Audit for crash risks - force unwraps, missing guards, unhandled errors, and unsafe optionals. Ensures safe fallbacks and user-friendly error states. Use before releases or when reviewing error-prone code.
---

# Crash & Error Resilience Audit

Find risky unwraps, missing guards, and unhandled errors. Add safe fallbacks and user-friendly error states.

## When to use this skill

- Before App Store submission
- After adding new async/error-prone code
- When reviewing PRs with optional handling
- After crash reports from TestFlight

## Quick Reference: Risk Levels

| Pattern | Risk | Fix |
|---------|------|-----|
| `fatalError()` | 🔴 Critical | Remove or guard with `#if DEBUG` |
| `!` force unwrap | 🔴 High | Use `guard let`, `if let`, or `??` |
| `try!` | 🔴 High | Use `do/catch` or `try?` with fallback |
| `preconditionFailure()` | 🔴 High | Remove from production paths |
| Implicit unwrap (`Type!`) | 🟡 Medium | Convert to optional with safe access |
| Missing `@MainActor` | 🟡 Medium | Add for UI-updating code |

---

## Step 1: Fatal Crash Patterns

### 1.1 fatalError / preconditionFailure / assertionFailure

```bash
# These crash in production!
rg --type swift -g '!*Tests*' -g '!*UITests*' 'fatalError\(|preconditionFailure\(|assertionFailure\(' YourApp/
```

**Fix:** Remove or wrap in `#if DEBUG`:
```swift
#if DEBUG
fatalError("Unimplemented")
#else
return defaultValue
#endif
```

### 1.2 Force Unwraps (`!`)

```bash
# Force unwraps - tighter pattern to reduce false positives
rg --type swift -g '!*Tests*' -g '!*UITests*' '[a-zA-Z_][a-zA-Z0-9_]*\s*!' YourApp/ | grep -v '!=' | grep -v '//' | head -40
```

**Exceptions (OK to skip):**
- `@IBOutlet` (UIKit pattern)
- `NSImage(named:)!` with known system images
- `URL(string: "https://...")!` with hardcoded valid URLs
- Code inside `#Preview { }` blocks
- Code inside `*Tests*/` directories

### 1.3 Force Try (`try!`)

```bash
rg --type swift -g '!*Tests*' -g '!*UITests*' 'try!' YourApp/
```

> **Note:** `try!` is acceptable in tests and previews where failure should crash during development.

**Fix:** Replace with `do/catch` or `try?` with default:
```swift
// ❌ Crashes on failure
let data = try! encoder.encode(object)

// ✅ Safe with error handling
let data = try? encoder.encode(object) ?? Data()
```

### 1.4 Implicitly Unwrapped Optionals (`Type!`)

```bash
rg --type swift -g '!*Tests*' ': [A-Z][a-zA-Z0-9_]*!' YourApp/ | grep -v '@IBOutlet' | head -20
```

---

## Step 2: Optional Safety Audit

### 2.1 Chained Optional Access Without Guards

```bash
# Deep optional chains that may be fragile
rg --type swift -g '!*Tests*' '\?\.\w+\?\.\w+' YourApp/ | head -20
```

### 2.2 Array/Dictionary Subscript Without Bounds Check

```bash
# Direct array indexing (may crash on out-of-bounds)
rg --type swift -g '!*Tests*' '\[\d+\]|\[index\]|\[i\]' YourApp/ | head -20
```

**Fix:** Use safe subscript or bounds check:
```swift
let item = array.indices.contains(index) ? array[index] : nil
```

---

## Step 3: Error Handling Audit

### 3.1 Empty Catch Blocks

```bash
# Swallowed errors (should at least log)
rg --type swift -g '!*Tests*' -A2 'catch\s*\{' YourApp/ | grep -B1 '^\s*\}' | head -20
```

### 3.2 Result Types Without Failure Handling

```bash
rg --type swift -g '!*Tests*' 'Result<' YourApp/ | head -15
rg --type swift -g '!*Tests*' '\.failure\(' YourApp/ | head -15
```

---

## Step 4: Async/Concurrency Safety

### 4.1 Missing @MainActor for UI Updates

```bash
# Task blocks that may update UI
rg --type swift -g '!*Tests*' 'Task\s*\{' YourApp/Views/ | head -20

# Check for MainActor annotations
rg --type swift -g '!*Tests*' '@MainActor' YourApp/
```

**Fix:** UI-updating async code needs `@MainActor`:
```swift
Task { @MainActor in
    self.isLoading = false
}
```

### 4.2 Task.detached & Continuation Misuse

```bash
# Task.detached (often misused, can cause actor isolation issues)
rg --type swift -g '!*Tests*' 'Task\.detached' YourApp/

# Continuations (must resume exactly once - missing resume = deadlock)
rg --type swift -g '!*Tests*' 'withCheckedContinuation|withUnsafeContinuation|withCheckedThrowingContinuation' YourApp/
```

**Verify continuations:**
- Every code path must call `continuation.resume()` exactly once
- Missing resume = deadlock
- Double resume = crash

### 4.3 Unstructured Task Cancellation

```bash
# Tasks that should be cancelled when view disappears
rg --type swift -g '!*Tests*' '\.task\s*\{|Task\s*\{' YourApp/Views/ | head -20
```

**Verify:** Long-running tasks should use `.task { }` modifier (auto-cancels) or manual cancellation.

---

## Step 5: User-Facing Error States

### 5.1 ContentUnavailableView for Empty/Error States

```bash
rg --type swift -g '!*Tests*' 'ContentUnavailableView' YourApp/Views/
```

### 5.2 Alert for User-Facing Errors

```bash
rg --type swift -g '!*Tests*' '\.alert\(' YourApp/Views/ | head -15
```

---

## Step 6: Watch App Audit

```bash
WATCH_DIR="YourApp Watch App"

# Fatal patterns in Watch app
rg --type swift 'fatalError\(|preconditionFailure\(' "$WATCH_DIR/"

# Force unwraps in Watch app
rg --type swift '[a-zA-Z_][a-zA-Z0-9_]*!' "$WATCH_DIR/" | grep -v '!=' | grep -v '//' | head -20
```

---

## Skip Patterns

- `*Tests*/`, `*UITests*/` — expected to crash on failure
- `#Preview { }` blocks — development only
- `@IBOutlet` force unwraps — UIKit pattern
- Hardcoded valid URLs: `URL(string: "https://...")!`

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| fatalError/precondition | X | ✅/❌ |
| Force unwraps (`!`) | X | ✅/❌ |
| Force try (`try!`) | X | ✅/❌ |
| Empty catch blocks | X | ✅/❌ |
| Task.detached/continuations | X | ✅/❌ |
| Missing @MainActor | X | ✅/❌ |
| User error states | X | ✅/❌ |
| Watch app | X | ✅/❌ |
