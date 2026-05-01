---
name: haptics-design
description: Design and audit haptic patterns for clarity, comfort, and battery. Covers Core Haptics, watchOS constraints, and user expectations.
---

# Haptics Design

Create haptic patterns that are distinct, readable, and respectful of user context.

## When to use this skill

- When adding or editing haptic patterns
- Before App Store submission
- After feedback about confusing or overwhelming haptics
- When expanding watchOS support

---

## Core Principles

- Distinctiveness: each pattern must feel meaningfully different
- Clarity: short sequences over long, complex patterns
- Comfort: avoid intense or rapid sequences
- Respect context: don’t interrupt focus unnecessarily

---

## Step 1: Pattern Taxonomy

Define and document a small set of “pattern types”:
- Gentle reminder
- Segment transition
- Final completion
- Warning/overrun

Each pattern should be:
- Short (under ~2.5s)
- Unique in rhythm (not just stronger intensity)

---

## Step 2: Intensity & Sharpness Bounds

Guidelines:
- Avoid max intensity by default
- Avoid frequent sharp taps for long sessions
- Provide a “soft” mode if needed

---

## Step 3: Watch vs iPhone Haptics

- watchOS haptics are more noticeable—use lower frequency
- Avoid rapid multi-tap patterns on Watch
- Ensure Always On Display (AOD) respects reduced activity

---

## Step 4: User Control

- Offer a quick preview of patterns
- Allow per-pattern intensity scaling
- Respect silent mode / system haptic settings

---

## Step 5: Battery Impact

- Avoid haptic loops or frequent timers
- Prefer event-driven haptics
- Pause haptics when app is not active

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| Pattern distinctiveness | X | ✅/❌ |
| Intensity comfort | X | ✅/❌ |
| Watch constraints | X | ✅/❌ |
| User control | X | ✅/❌ |
| Battery impact | X | ✅/❌ |
