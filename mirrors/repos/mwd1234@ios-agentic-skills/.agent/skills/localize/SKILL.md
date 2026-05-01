---
name: localize
description: Comprehensive SwiftUI localization audit - finds and fixes hardcoded strings, missing translations, and rawValue usages. Use when auditing code for localization issues, checking for untranslated strings, or preparing for App Store international launch.
---

# SwiftUI Localization Audit

Perform a thorough localization audit of the SwiftUI codebase to identify and fix hardcoded strings that need to be localized.

## When to use this skill

- Before submitting to the App Store for international markets
- After adding new UI features with user-facing text
- When reviewing PRs that touch Views, ViewModels, or Models
- When the user asks to check localization or translations

## How to use it

### Step 1: Pre-Flight Checks (All xcstrings Files)

Run localization status checks on **all** `.xcstrings` files upfront:

```bash
# iOS App
python3 scripts/check_localization_status.py YourApp/Localizable.xcstrings

# AppIntents (catches missing Siri shortcut translations early)
python3 scripts/check_localization_status.py YourApp/AppIntents/AppShortcuts.xcstrings

# Watch App
python3 scripts/check_localization_status.py "YourApp Watch App/Localizable.xcstrings"
```

> **Why AppIntents early?** Missing shortcut keys cause Siri regressions that are hard to catch later.

### Step 2: Scan Scope & Exclusions

**Directories to scan:**

| Target | Directories |
|--------|-------------|
| iOS App | `YourApp/Views/`, `YourApp/ViewModels/`, `YourApp/Models/`, `YourApp/Managers/` |
| Watch App | `YourApp Watch App/Views/`, `YourApp Watch App/ViewModels/`, `YourApp Watch App/Managers/` |
| AppIntents | `YourApp/AppIntents/` |

**Exclusions (always ignore):**

```bash
# Use rg (ripgrep) with exclusions for all searches:
rg --type swift -g '!*Tests*' -g '!*UITests*' "PATTERN" <directory>
```

- `*Tests*/`, `*UITests*/` — Test code is not user-facing
- Content inside `#Preview { }` blocks — Developer-only, stripped from production builds

### Step 3: High Priority Pattern Audit

Search for these patterns using `rg` (faster than grep on macOS):

```bash
# Button labels
rg --type swift -g '!*Tests*' 'Button\("' YourApp/Views/ YourApp/ViewModels/ YourApp/Models/

# Label text
rg --type swift -g '!*Tests*' 'Label\("' YourApp/Views/ YourApp/ViewModels/ YourApp/Models/

# Navigation titles
rg --type swift -g '!*Tests*' '\.navigationTitle\("' YourApp/Views/

# Alert titles
rg --type swift -g '!*Tests*' '\.alert\("' YourApp/Views/

# TextField placeholders
rg --type swift -g '!*Tests*' 'TextField\("' YourApp/Views/

# Picker labels
rg --type swift -g '!*Tests*' 'Picker\("' YourApp/Views/
```

| Pattern | Search | Fix |
|---------|--------|-----|
| Button labels | `Button("` | `Button(String(localized: "text", comment: "context"))` |
| Label text | `Label("` | `Label(String(localized: "text", comment: "context"), ...)` |
| Navigation titles | `.navigationTitle("` | `.navigationTitle(Text("text", comment: "title"))` |
| Alert titles | `.alert("` | Use `String(localized:)` for title and buttons |
| TextField placeholders | `TextField("` | Use localized prompt or `String(localized:)` |
| Picker labels | `Picker("` | `Picker(String(localized: "label", comment: "context"), ...)` |

### Step 4: Additional Localization Patterns

Check for these often-missed patterns:

```bash
# Text(verbatim:) - intentionally skipped from localization (verify it's correct)
rg --type swift -g '!*Tests*' 'Text\(verbatim:' YourApp/Views/ YourApp/ViewModels/

# Text(.init("...")) - bypasses automatic localization
rg --type swift -g '!*Tests*' 'Text\(\.init\(' YourApp/Views/ YourApp/ViewModels/

# NSLocalizedString - legacy pattern (convert to String(localized:))
rg --type swift -g '!*Tests*' 'NSLocalizedString\(' YourApp/Views/ YourApp/ViewModels/ YourApp/Models/

# AttributedString("...") - needs localization for user-facing text
rg --type swift -g '!*Tests*' 'AttributedString\("' YourApp/Views/ YourApp/ViewModels/
```

| Pattern | Issue | Fix |
|---------|-------|-----|
| `Text(verbatim:)` | Intentionally skipped — verify it's correct (e.g., user-generated content) | Leave if correct, otherwise use `Text("", comment:)` |
| `Text(.init("..."))` | Bypasses auto-localization | Use `Text("text", comment: "context")` |
| `NSLocalizedString(...)` | Legacy pattern | Convert to `String(localized: "key", comment: "context")` |
| `AttributedString("...")` | String not localized | Use `AttributedString(localized:)` or localized source string |

### Step 5: Medium Priority Pattern Audit

```bash
# rawValue in user-facing contexts
rg --type swift -g '!*Tests*' '\.rawValue' YourApp/Views/ YourApp/ViewModels/ YourApp/Models/
```

| Pattern | Issue | Fix |
|---------|-------|-----|
| `.rawValue` in Text/Label | User sees English enum value | Use `.localizedName` property |
| `.rawValue` in accessibility | VoiceOver reads English | Use `.localizedName` property |
| Menu item labels | Hardcoded text | Use `String(localized:)` |

### Step 6: Watch App Source Scan

Scan Watch app sources explicitly (not just its xcstrings):

```bash
WATCH_DIR="YourApp Watch App"

# Views
rg --type swift 'Button\("|Label\("|Text\("' "$WATCH_DIR/Views/"

# ViewModels
rg --type swift 'String\(' "$WATCH_DIR/ViewModels/" 2>/dev/null

# Managers (user-facing errors, notifications)
rg --type swift 'Text\("|\.alert\(' "$WATCH_DIR/Managers/" 2>/dev/null
```

### Step 7: Enum Localization Check

Ensure all user-facing enums have `localizedName` properties:

```swift
var localizedName: String {
    switch self {
    case .value: return String(localized: "Value", comment: "Enum description")
    }
}
```

### Step 8: Add Missing Translations

If missing translations are found, add them to `scripts/add_translations.py` and run:

```bash
python3 scripts/add_translations.py YourApp/Localizable.xcstrings
```

### Step 9: Remove Stale Strings

```bash
python3 scripts/remove_stale_strings.py YourApp/Localizable.xcstrings
```

### Step 10: Final Verification

Re-run pre-flight checks on **all** xcstrings files. Target: 0 stale, 0 missing for all files.

```bash
python3 scripts/check_localization_status.py YourApp/Localizable.xcstrings
python3 scripts/check_localization_status.py YourApp/AppIntents/AppShortcuts.xcstrings
python3 scripts/check_localization_status.py "YourApp Watch App/Localizable.xcstrings"
```

## Skip Patterns (Don't need localization)

- `#Preview { }` blocks — developer-only, stripped from production
- `*Tests*/`, `*UITests*/` folders — test code is not user-facing
- `Notification.Name` values
- File paths, identifiers, debug logging
- SF Symbol names
- `Text(verbatim:)` with user-generated or dynamic content

## Common Pitfalls (Lessons Learned)

### 1. Interpolating `localizedName` into `String(localized:)`

**Problem:** When interpolating a `localizedName` property into `String(localized:)`, you get a deprecation warning:

```swift
// ❌ Causes deprecation warning
.accessibilityLabel(String(localized: "Filter: \(category.localizedName)", comment: "Label"))
```

**Why?** `String(localized:)` expects types that conform to `CustomLocalizedStringResourceConvertible`. Custom `localizedName` strings don't.

**Fix:** Use plain string interpolation since `localizedName` is already localized:

```swift
// ✅ Correct - localizedName is already localized
.accessibilityLabel("Filter: \(category.localizedName)")
```

---

### 2. Text() Expects LocalizedStringKey, Not String Concatenation

**Problem:** `Text()` with string concatenation causes compile errors:

```swift
// ❌ Compile error: '+' requires RangeReplaceableCollection
Text("No " + filter.localizedName + " items")
```

**Why?** SwiftUI's `Text()` initializer expects a `LocalizedStringKey`, not a `String` with `+` operators.

**Fix:** Use `Text(verbatim:)` for pre-built strings with localized content:

```swift
// ✅ Option 1: Use Text(verbatim:) since content is already localized
Text(verbatim: "No \(filter.localizedName) items")

// ✅ Option 2: Build string separately
let label = "No \(filter.localizedName) items"
Text(verbatim: label)
```

---

### 3. Complex Views Cause Type-Check Timeout

**Problem:** Large view bodies with many nested elements cause compiler errors:

```
The compiler is unable to type-check this expression in reasonable time
```

**Why?** Swift's type inference struggles with deeply nested View expressions.

**Fix:** Extract sub-views into computed properties:

```swift
// ❌ Monolithic body causes type-check timeout
var body: some View {
    Group {
        if condition {
            // 50+ lines of nested views
        } else {
            // 50+ lines of nested views
        }
    }
}

// ✅ Extract into computed properties
private var accessibilityLayoutView: some View {
    // Accessibility layout
}

private var standardLayoutView: some View {
    // Standard layout
}

var body: some View {
    Group {
        if useAccessibilityLayout {
            accessibilityLayoutView
        } else {
            standardLayoutView
        }
    }
}
```

---

### 4. When to Use Each Pattern

| Scenario | Pattern |
|----------|---------|
| Static user-facing string | `String(localized: "text", comment: "context")` |
| Static Text with localization | `Text("text", comment: "context")` |
| Interpolated with already-localized values | `"Prefix: \(localizedName)"` (plain string) |
| Pre-built string in Text | `Text(verbatim: preBuiltString)` |
| Accessibility labels with dynamic content | `.accessibilityLabel("Filter: \(category.localizedName)")` |

## Output Format

Provide a summary table:

| Category | Found | Status |
|----------|-------|--------|
| Button labels | X | ✅/❌ |
| Navigation titles | X | ✅/❌ |
| rawValue usages | X | ✅/❌ |
| Text(verbatim:) audited | X | ✅/❌ |
| NSLocalizedString legacy | X | ✅/❌ |
| Watch App sources | X | ✅/❌ |
| Missing translations | X | ✅/❌ |

