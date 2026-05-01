---
name: accessibility
description: Comprehensive SwiftUI accessibility audit against Apple HIG. Checks VoiceOver labels, Reduce Motion, Dynamic Type, color contrast, and accessible controls. Use before App Store submission or when adding new UI.
---

# SwiftUI Accessibility Audit

Audit the codebase for Apple HIG accessibility compliance. Covers VoiceOver, motion, vision, and interaction accessibility.

## When to use this skill

- Before App Store submission (required for Accessibility Nutrition Labels)
- After adding new Views, custom controls, or animations
- When reviewing PRs with UI changes
- When the user asks to check accessibility

## Quick Reference: HIG Requirements

| Category | Requirement |
|----------|-------------|
| **VoiceOver** | All interactive elements must have descriptive labels; images need alt text |
| **Reduce Motion** | Animations must respect `accessibilityReduceMotion`; provide static alternatives |
| **Dynamic Type** | Text must scale with system font size; use relative sizing |
| **Color/Contrast** | Don't rely solely on color; maintain 4.5:1 contrast ratio |
| **Touch Targets** | Minimum 44×44pt for all interactive elements |

---

## Step 1: VoiceOver Labels Audit

### 1.1 Missing Labels on Interactive Elements

```bash
# Buttons without accessibility labels
rg --type swift -g '!*Tests*' 'Button\s*\{' YourApp/Views/ | head -20

# Images without accessibility labels (decorative should use accessibilityHidden)
rg --type swift -g '!*Tests*' 'Image\(' YourApp/Views/ | head -20

# Custom controls that may need labels
rg --type swift -g '!*Tests*' '\.onTapGesture|\.gesture\(' YourApp/Views/ | head -20
```

### 1.2 accessibilityHidden on Non-Decorative Images

```bash
# Find hidden images - verify they are truly decorative
rg --type swift -g '!*Tests*' -B2 -A2 '\.accessibilityHidden\(true\)' YourApp/Views/ | head -30
```

**HIG Requirement:** Only hide truly decorative images. Meaningful images (icons indicating state, informational graphics) must NOT be hidden.

### 1.3 Accessibility Element Grouping

```bash
# Check for intentional grouping - ensure labels are preserved
rg --type swift -g '!*Tests*' '\.accessibilityElement\(children:' YourApp/Views/
```

**Verify:** When using `.accessibilityElement(children: .ignore)` or `.combine`, ensure the parent has a proper `.accessibilityLabel()` that describes the grouped content.

### 1.4 Labels Using Technical/Internal Values

```bash
# rawValue in accessibility contexts (should use localizedName)
rg --type swift -g '!*Tests*' '\.accessibilityLabel.*\.rawValue|\.accessibilityValue.*\.rawValue' YourApp/Views/
```

### 1.5 Unlocalized Strings in Views (Affects VoiceOver)

```bash
# Text(verbatim:) and Text(.init()) bypass localization
rg --type swift -g '!*Tests*' 'Text\(verbatim:|Text\(\.init\(' YourApp/Views/
```

**Fix:** Use `Text("string", comment:)` for user-facing text so VoiceOver reads localized content.

---

## Step 2: Reduce Motion & Transparency Audit

### 2.1 Animations Not Respecting Reduce Motion

```bash
# Animations that may need @Environment(\.accessibilityReduceMotion)
rg --type swift -g '!*Tests*' '\.animation\(|withAnimation|\.transition\(' YourApp/Views/ | head -30

# Check if Reduce Motion is being read
rg --type swift -g '!*Tests*' 'accessibilityReduceMotion' YourApp/
```

**Fix Pattern:**
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
.animation(reduceMotion ? nil : .easeInOut, value: state)
```

### 2.2 Auto-Playing or Looping Animations

```bash
# Repeating animations
rg --type swift -g '!*Tests*' '\.repeatForever|\.repeat\(' YourApp/Views/

# Timer-driven animations
rg --type swift -g '!*Tests*' 'Timer\.publish|onReceive.*timer' YourApp/Views/
```

### 2.3 Reduce Transparency (Blurred/Transparent UI)

```bash
# Blur effects and materials that need solid alternatives
rg --type swift -g '!*Tests*' '\.blur\(|\.background\(\.ultraThinMaterial|\.background\(\.thinMaterial' YourApp/Views/

# Check if Reduce Transparency is being respected
rg --type swift -g '!*Tests*' 'accessibilityReduceTransparency' YourApp/
```

**HIG Requirement:** When `accessibilityReduceTransparency` is enabled, replace blur/transparency effects with solid backgrounds.

---

## Step 3: Color & Contrast Audit

### 3.1 Color-Only Indicators

```bash
# Color-only status indicators (need shape/icon alternatives)
rg --type swift -g '!*Tests*' '\.foregroundColor\(.*\.red|\.green|\.yellow' YourApp/Views/

# Check for differentiate without color
rg --type swift -g '!*Tests*' 'accessibilityDifferentiateWithoutColor' YourApp/
```

**HIG Requirement:** When `accessibilityDifferentiateWithoutColor` is enabled, add icons, patterns, or text labels alongside color indicators.

**Fix Pattern:**
```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

HStack {
    Circle().fill(isActive ? .green : .red)
    if differentiateWithoutColor {
        Image(systemName: isActive ? "checkmark" : "xmark")
    }
}
```

### 3.2 Contrast Verification

Manual check:
- Run Accessibility Inspector in Xcode
- Check 4.5:1 ratio for normal text, 3:1 for large text
- Test in Light and Dark modes

---

## Step 4: Dynamic Type Audit

### 4.1 Fixed Font Sizes

```bash
# Hardcoded font sizes (should use relative sizing)
rg --type swift -g '!*Tests*' '\.font\(\.system\(size:' YourApp/Views/ | head -20

# Custom fonts that may not scale
rg --type swift -g '!*Tests*' 'Font\.custom\(' YourApp/Views/
```

**Fix:** Use semantic fonts: `.font(.body)`, `.font(.headline)`

### 4.2 dynamicTypeSize Restrictions

```bash
# Check for dynamicTypeSize limits (may prevent scaling)
rg --type swift -g '!*Tests*' '\.dynamicTypeSize\(' YourApp/Views/
```

**Verify:** If limiting Dynamic Type range, ensure it's for layout constraints only, not to prevent accessibility scaling.

### 4.3 minimumScaleFactor on Labels

```bash
# Labels that shrink text instead of wrapping
rg --type swift -g '!*Tests*' '\.minimumScaleFactor\(' YourApp/Views/
```

**Verify:** Acceptable for single-line constraints (e.g., tab bar labels), but prefer `.lineLimit(nil)` for body text.

### 4.4 Fixed Frame Heights (Clips Large Text)

```bash
# Fixed heights that may clip scaled text
rg --type swift -g '!*Tests*' '\.frame\(height:|\.frame\(.*height:' YourApp/Views/ | head -20
```

**Fix:** Use `.frame(minHeight:)` for text containers.

---

## Step 5: Touch Target Audit

```bash
# Small touch targets
rg --type swift -g '!*Tests*' '\.frame\(width:\s*[0-3][0-9],' YourApp/Views/

# ContentShape for gesture areas
rg --type swift -g '!*Tests*' '\.contentShape\(' YourApp/Views/
```

**HIG Requirement:** All touch targets minimum 44×44pt. Use `.contentShape()` to expand hit areas.

---

## Step 6: Watch App Audit

```bash
WATCH_DIR="YourApp Watch App"

# VoiceOver labels
rg --type swift '\.accessibilityLabel\(|\.accessibilityValue\(' "$WATCH_DIR/Views/"

# Reduce Motion
rg --type swift 'accessibilityReduceMotion|WKAccessibilityIsReduceMotionEnabled' "$WATCH_DIR/"

# Always On Display (AOD) - pause animations when dimmed
rg --type swift 'isLuminanceReduced' "$WATCH_DIR/"
```

**watchOS Requirement:** When `isLuminanceReduced` is true (Always On Display), pause animations and reduce visual complexity:
```swift
@Environment(\.isLuminanceReduced) var isLuminanceReduced

.animation(isLuminanceReduced ? nil : .default, value: state)
```

---

## Step 7: Accessibility Inspector Verification

1. **Xcode > Open Developer Tool > Accessibility Inspector**
2. Run app in Simulator
3. Audit each screen for missing labels, incorrect traits, contrast issues

---

## Skip Patterns

- `#Preview { }` blocks
- `*Tests*/`, `*UITests*/` folders
- Decorative images (should have `.accessibilityHidden(true)`)

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| VoiceOver labels | X | ✅/❌ |
| accessibilityHidden audit | X | ✅/❌ |
| Element grouping | X | ✅/❌ |
| Reduce Motion | X | ✅/❌ |
| Reduce Transparency | X | ✅/❌ |
| Differentiate Without Color | X | ✅/❌ |
| Dynamic Type | X | ✅/❌ |
| Touch targets | X | ✅/❌ |
| Watch app (incl. AOD) | X | ✅/❌ |
