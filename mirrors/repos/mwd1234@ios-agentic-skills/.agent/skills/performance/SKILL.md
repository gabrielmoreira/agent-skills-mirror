---
name: performance
description: Audit for performance and battery - layout thrash, heavy animations, timers, background tasks. Identifies hotspots affecting smoothness and power consumption. Use before releases or when users report lag/battery drain.
---

# Performance & Battery Audit

Scan for layout thrash, heavy animations, timers, and background tasks. Flag hotspots and suggest fixes.

## When to use this skill

- Before App Store submission
- After adding complex animations or layouts
- When users report lag, jank, or battery drain
- When reviewing Views with frequent state changes

## Quick Reference: Common Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| GeometryReader in ScrollView | Layout thrash | Use `containerRelativeFrame` or cache sizes |
| Timer in View body | Battery drain | Use `.onReceive` with shared timer |
| Large images in List | Memory spike | Use `LazyVStack`, async image loading |
| Animation without `value:` | CPU/GPU | Scope animations with `value:` parameter |
| `.drawingGroup()` everywhere | GPU memory | Use only for complex overlapping content |

---

## Step 1: Layout Performance Audit

### 1.1 GeometryReader Misuse

```bash
# GeometryReader (expensive layout pass)
rg --type swift -g '!*Tests*' 'GeometryReader' YourApp/Views/ | head -15
```

**Issues:** GeometryReader inside ScrollView/List causes relayout on scroll.

**Fix (iOS 17+):**
```swift
// ❌ Expensive
GeometryReader { geo in content.frame(width: geo.size.width * 0.8) }

// ✅ Modern alternative
content.containerRelativeFrame(.horizontal) { width, _ in width * 0.8 }
```

### 1.2 Layout Invalidation in Body

```bash
# Inline expensive object creation
rg --type swift -g '!*Tests*' 'DateFormatter\(\)|NumberFormatter\(\)|JSONDecoder\(\)' YourApp/Views/
```

**Fix:** Move to static/cached properties.

---

## Step 2: Animation Performance

### 2.1 Animation Scope

```bash
# Animations without value parameter (animate everything)
rg --type swift -g '!*Tests*' '\.animation\([^,)]+\)' YourApp/Views/ | grep -v 'value:' | head -15
```

**Fix:** Always scope animations:
```swift
.animation(.easeInOut, value: isExpanded)  // ✅ Only animates this change
```

### 2.2 Heavy/Repeating Animations

```bash
# Repeating animations (battery impact)
rg --type swift -g '!*Tests*' '\.repeatForever|\.repeat\(' YourApp/Views/

# Canvas/TimelineView (GPU intensive)
rg --type swift -g '!*Tests*' 'Canvas\s*\{|TimelineView' YourApp/Views/
```

> **watchOS:** `TimelineView(.periodic)` is extremely battery-heavy. Prefer `.animation` schedule or pause when not visible.

### 2.3 Expensive Rendering Modifiers

```bash
# GPU-heavy modifiers
rg --type swift -g '!*Tests*' '\.drawingGroup\(|\.shadow\(radius:|\.blur\(|\.mask\s*\{|\.compositingGroup\(' YourApp/Views/ | head -20
```

**Guidance:**
- `.drawingGroup()` — Use only for complex overlapping content, not everywhere
- `.shadow(radius:)` — Expensive with large radii; cache or use images
- `.blur()` — Very expensive; consider pre-blurred assets
- `.mask { }` — Recalculates every frame; avoid in animations
- `.compositingGroup()` — Use sparingly for correct blending

---

## Step 3: ForEach & List Efficiency

### 3.1 Unstable ForEach IDs

```bash
# ForEach with \.self on non-Hashable-stable data (causes full diff)
rg --type swift -g '!*Tests*' 'ForEach.*\\\.self' YourApp/Views/ | head -15

# ForEach without explicit id:
rg --type swift -g '!*Tests*' 'ForEach\([^)]+\)\s*\{' YourApp/Views/ | grep -v 'id:' | head -15
```

**Issues:**
- `\.self` on arrays that get reordered/modified causes full re-render
- Missing stable IDs cause diffing cost

**Fix:** Use stable, unique identifiers:
```swift
ForEach(items, id: \.stableID) { item in ... }
```

### 3.2 LazyVStack/LazyHStack Usage

```bash
# Check for lazy stacks in lists
rg --type swift -g '!*Tests*' 'LazyVStack|LazyHStack|LazyVGrid|LazyHGrid' YourApp/Views/

# Non-lazy stacks in ScrollView (loads all content)
rg --type swift -g '!*Tests*' -B2 'ScrollView' YourApp/Views/ | grep -A2 'VStack\|HStack' | head -20
```

---

## Step 4: State Management

### 4.1 @State Arrays/Dictionaries

```bash
# Large state objects in Views
rg --type swift -g '!*Tests*' '@State\s+(private\s+)?var\s+\w+:\s*\[' YourApp/Views/ | head -15
```

**Fix:** Large collections should be in ViewModel/ObservableObject, not View @State.

### 4.2 @StateObject Initialization

```bash
# @StateObject in body (wrong - should be in init or property)
rg --type swift -g '!*Tests*' -B3 '@StateObject' YourApp/Views/ | head -20
```

**Fix:** Initialize `@StateObject` in property declaration or `init`, never in `body`:
```swift
// ✅ Correct
@StateObject private var viewModel = MyViewModel()

// ❌ Wrong - recreates on every render
var body: some View {
    let vm = MyViewModel() // BAD
}
```

---

## Step 5: Timer & Background Task Audit

### 5.1 Timer Usage

```bash
# Timer instances
rg --type swift -g '!*Tests*' 'Timer\.|Timer\.publish|Timer\.scheduledTimer' YourApp/
```

**Issues:**
- Timers not invalidated when view disappears
- High-frequency timers (< 0.1s) for non-critical updates

### 5.2 Background Tasks

```bash
rg --type swift -g '!*Tests*' 'BGTaskScheduler|BGAppRefreshTask|BGProcessingTask' YourApp/

# Extended runtime sessions (Watch)
rg --type swift 'WKExtendedRuntimeSession' "YourApp Watch App/"
```

---

## Step 6: Network Efficiency

```bash
# URLSession configuration
rg --type swift -g '!*Tests*' 'URLSession|URLSessionConfiguration' YourApp/
```

**Best practices:**
- Use `isDiscretionary = true` for non-urgent downloads
- Cache responses where appropriate

---

## Step 7: Watch App Performance

```bash
WATCH_DIR="YourApp Watch App"

# Timers on Watch (battery critical)
rg --type swift 'Timer\.' "$WATCH_DIR/"

# TimelineView on Watch (use .animation not .periodic)
rg --type swift 'TimelineView.*\.periodic' "$WATCH_DIR/"

# Heavy animations on Watch
rg --type swift '\.animation\(|withAnimation' "$WATCH_DIR/Views/"
```

> **watchOS priority:** Battery > Smoothness. `TimelineView(.periodic)` drains battery fast—use `.animation` schedule instead.

---

## Step 8: Instruments Verification

For issues found, verify with Instruments:
1. **Time Profiler** — CPU hotspots
2. **Core Animation** — Frame drops, offscreen renders
3. **Allocations** — Memory leaks, spikes
4. **Energy Log** — Battery impact

---

## Skip Patterns

- `*Tests*/`, `*UITests*/`
- `#Preview { }` blocks

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| GeometryReader usage | X | ✅/❌ |
| Animation scope | X | ✅/❌ |
| Expensive modifiers | X | ✅/❌ |
| ForEach IDs | X | ✅/❌ |
| @StateObject init | X | ✅/❌ |
| Timer management | X | ✅/❌ |
| Watch app battery | X | ✅/❌ |
