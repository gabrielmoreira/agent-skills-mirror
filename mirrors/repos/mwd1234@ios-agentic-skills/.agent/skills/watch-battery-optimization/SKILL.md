---
name: watch-battery-optimization
description: watchOS battery and AOD optimization audit. Covers TimelineView usage, Always On Display behavior, energy log checks, and haptic behavior while dimmed.
---

# watchOS Battery Optimization

Audit watchOS code for battery impact, with special focus on Always On Display (AOD) and TimelineView usage.

## When to use this skill

- Before App Store submission
- After adding animations, timers, or sync logic
- When users report battery drain
- After changes to AOD behavior

---

## Step 1: AOD (Always On Display)

**Requirement:** When AOD is active (`isLuminanceReduced == true`), the UI should simplify **but haptic feedback must still fire** for segment changes. Do not disable haptics in AOD mode.

Check for:
- `@Environment(\.isLuminanceReduced)` usage
- Any conditional logic that disables haptics when dimmed

Suggested pattern:
```swift
@Environment(\.isLuminanceReduced) var isLuminanceReduced

// UI simplification
.animation(isLuminanceReduced ? nil : .default, value: state)

// Haptics should still run regardless of AOD
if shouldFireHaptic {
    haptics.play(pattern)
}
```

---

## Step 2: TimelineView & Timers

```bash
WATCH_DIR="YourApp Watch App"

# TimelineView usage
rg --type swift 'TimelineView' "$WATCH_DIR/"

# Periodic timeline (battery heavy)
rg --type swift 'TimelineView.*\.periodic' "$WATCH_DIR/"

# Timers
rg --type swift 'Timer\.' "$WATCH_DIR/"
```

Guidance:
- Prefer `.animation` schedules over `.periodic`
- Avoid tight timers (< 0.1s)
- Use `.task { }` to auto-cancel on view disappearance

---

## Step 3: Animation & GPU Cost

```bash
# Heavy animations
rg --type swift '\.animation\(|withAnimation|Canvas\s*\{|\.drawingGroup\(|\.blur\(' "$WATCH_DIR/Views/"
```

Guidance:
- Pause or simplify animations in AOD
- Avoid `Canvas` and heavy blur on watch

---

## Step 4: Background & Extended Runtime

```bash
rg --type swift 'WKExtendedRuntimeSession' "$WATCH_DIR/"
```

Guidance:
- Use only when necessary
- End sessions promptly

---

## Step 5: Energy Log Verification

Use Instruments → Energy Log to validate:
- No sustained high energy usage
- No excessive wakeups
- No continuous GPU usage

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| AOD behavior & haptics | X | ✅/❌ |
| TimelineView usage | X | ✅/❌ |
| Timer frequency | X | ✅/❌ |
| Animation cost | X | ✅/❌ |
| Extended runtime | X | ✅/❌ |
| Energy Log results | X | ✅/❌ |
