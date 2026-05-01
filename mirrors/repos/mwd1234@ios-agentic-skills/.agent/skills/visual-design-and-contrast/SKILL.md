---
name: visual-design-and-contrast
description: HIG-first visual design audit for SwiftUI. Covers color systems, contrast, typography, spacing, icons, and accessibility visuals.
---

# Visual Design & Contrast (HIG-First)

Audit visual consistency and accessibility against Apple’s Human Interface Guidelines (HIG).

## When to use this skill

- Before App Store submission
- After large UI updates or new themes
- When introducing new colors or typography
- When users report readability issues

---

## Required Guidance

Always use Apple’s **Human Interface Guidelines (HIG)** as the source of truth for design decisions.
For documentation lookup, use the **sosumi.ai MCP server**.
The sosumi.ai site has an **“MCP Usage”** section that explains how to connect the MCP server in your IDE/Claude Code/etc.

---

## Step 1: Color System Audit

- Use semantic colors (not hard-coded RGB)
- Ensure Dark Mode parity
- Avoid color-only status indicators

Checks:
- All custom colors defined in asset catalogs
- No hard-coded `Color(.sRGB, …)` in views

---

## Step 2: Contrast & Readability

Manual checks:
- Accessibility Inspector contrast checks
- 4.5:1 contrast for body text, 3:1 for large text

Avoid:
- Light text on bright backgrounds
- Thin fonts at small sizes

---

## Step 3: Typography Consistency

- Prefer semantic fonts: `.body`, `.headline`, `.title2`
- Respect Dynamic Type
- Avoid fixed font sizes unless absolutely necessary

---

## Step 4: Spacing & Layout Rhythm

- Use consistent spacing tokens (8/12/16/24)
- Avoid arbitrary per-view padding
- Use alignment guides consistently

---

## Step 5: Iconography & SF Symbols

- Use SF Symbols where possible
- Avoid mixing styles (outline vs filled) in same context
- Ensure icon meaning is obvious without color

---

## Step 6: Visual States

- Distinct states for normal/selected/disabled
- Clear focus ring / selection treatment
- Hover / pressed feedback where applicable

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| Color system | X | ✅/❌ |
| Contrast | X | ✅/❌ |
| Typography | X | ✅/❌ |
| Spacing | X | ✅/❌ |
| Iconography | X | ✅/❌ |
| Visual states | X | ✅/❌ |
