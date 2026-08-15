---
name: swiftui-wcag-accessibility-auditor
description: "Audits native iOS SwiftUI source against WCAG 2.2 A/AA with VoiceOver labels, 44x44 targets, contrast, and patch-ready snippets. Use when auditing SwiftUI accessibility with WCAG traceability. Not for UIKit-first audits (mobile-accessibility-audit), heuristic-only SwiftUI review (swiftui-accessibility-auditor), or running the app."
version: 1.0.1
domain: SwiftUI Accessibility & WCAG Compliance
risk: safe
last_verified: 2026-05-30
self_updating: true
---

# SwiftUI WCAG Accessibility Auditor

## Overview

Audit native iOS SwiftUI features in a dual mode:

- **WCAG-driven coverage and evidence** — what fails, what is uncertain, and why, mapped to WCAG 2.2 Success Criteria.
- **SwiftUI patch-ready remediation** — what to change with minimal code edits.

Treat this as a **code audit**. Do not run the app. If a result cannot be proven from source, mark it `Needs user verification` and add a concrete user follow-up check.

### Scope Rules

- Audit **native iOS SwiftUI code only**.
- Audit `UIViewRepresentable` / `UIViewControllerRepresentable` bridges only to the extent they affect the SwiftUI feature.
- If the feature delegates core behavior to UIKit, say so and either narrow the audit or recommend `mobile-accessibility-audit`.
- Do **not** broaden scope to macOS, watchOS, web, or non-SwiftUI implementations.

### Compatibility Target

- **Standards:** WCAG 2.2 Level A and AA.
- **Devices:** iOS, iPadOS, tvOS.

## When to Use

Use this skill when you need **both**:

- WCAG 2.2 mapping / traceability, **and**
- SwiftUI-specific fixes/snippets.

Trigger keywords: `accessibility audit`, `WCAG`, `VoiceOver`, `SwiftUI a11y`, `contrast`, `focus state`, `tap target`, `Dynamic Type`, `accessible authentication`.

**Route elsewhere when:**

- `mobile-accessibility-audit` — feature includes `UIKit` or you only need standards-first audit coverage.
- `swiftui-accessibility-auditor` — you want a fast SwiftUI-only heuristic review without WCAG traceability.

## Prerequisites

- SwiftUI source files available in the workspace (`.swift`).
- `ripgrep` (`rg`) available on the host for search guidance.
- WCAG 2.2 and Apple SwiftUI accessibility docs reachable (see Source Anchors).

### Audit load order

Follow this order using **this SKILL.md** plus the Source Anchors — this folder does not ship extra reference files:

1. **Workflow** — Overview (Scope Rules, Compatibility Target) and Procedure. Code-only audit; statuses `Pass` / `Fail` / `Needs user verification`; evidence from source.
2. **Checklist** — Procedure step 3 plus Decision Rules (labels, combine children, 44×44 targets, Dynamic Type, focus, custom representations).
3. **Ambiguous SC** — [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) when a criterion's mobile applicability is unclear.
4. **API patterns** — Decision Rules and Pitfalls in this file (SwiftUI first; UIKit only if bridges are in scope).
5. **Remediation** — Procedure step 4 and the finding template (minimal snippets, P0/P1/P2).
6. **Manual follow-up** — only when generating `# User Follow-Up Checks` or a final manual validation list.

## Procedure

### 1. Define Scope

1. Identify the scoped feature flow and in-scope screens/states.
2. Identify the SwiftUI entry views and related subviews for the feature.
3. Note any `UIViewRepresentable` / `UIViewControllerRepresentable` bridges and whether they materially affect accessibility.

### 2. Search the Code (SwiftUI-first)

Run these searches from the project root (PowerShell on Windows host):

```powershell
rg --files | rg '\.swift$'
rg -n "struct .*View: View|body: some View|NavigationStack|sheet\(|fullScreenCover\(" .
rg -n "accessibility(Label|Hint|Value|Hidden)|accessibility(AddTraits|RemoveTraits)|accessibilityElement\(|accessibilityFocused\(" .
rg -n "@AccessibilityFocusState|onTapGesture|DragGesture|lineLimit\(|minimumScaleFactor|dynamicTypeSize" .
```

Then use Decision Rules and Pitfalls in this file for pattern interpretation (`.accessibilityRepresentation`, combined children).

### 3. Run the WCAG Checklist

1. Walk through Decision Rules and Procedure step 3 against the in-scope code.
2. Record evidence with statuses: `Pass`, `Fail`, `Needs user verification`.
3. Use the SwiftUI API examples to avoid false positives and identify missing semantics.

### 4. Generate Patch-Ready Fixes

1. Use Procedure step 4, Decision Rules, and the finding template for fix patterns and priority.
2. Produce minimal, directly applicable snippets for each finding.
3. If no code snippet is appropriate, state why in `*Fix suggestion*` (rare).

### 5. Produce the Report

Generate a Markdown report with:

- Prioritized findings (`P0`, `P1`, `P2`)
- WCAG SC mapping for each finding
- Patch-ready snippet embedded in each finding
- User follow-up checks (only for code-indeterminate items)

### Decision Rules

1. **Label vs. Hint:** Use `.accessibilityLabel` to describe *what* an element is. Use `.accessibilityHint` to describe *what happens* when activated. Do not repeat the label in the hint.
2. **Combine Children:** Use `.accessibilityElement(children: .combine)` on card components to read group details as a single element.
3. **Minimum Tap Targets:** Controls must maintain a minimum interactive hit target of 44×44 points. `.contentShape(Rectangle())` can help expand transparent targets.
4. **Dynamic Type:** Text sizes must scale automatically to accommodate user preferences. Check `lineLimit`, `minimumScaleFactor`, `dynamicTypeSize`.
5. **Focus Management:** Use `@AccessibilityFocusState` to track and programmatically transfer focus between elements (iOS 18/19).
6. **Custom Representations:** Use `.accessibilityRepresentation` to overlay standard accessible controls on top of highly custom graphical interfaces.

## Output Format (Strict, Concise)

Be concise. Use the following structure exactly.

**Rules:**

- Group findings by priority using top-level headings: `# Findings - P0`, `# Findings - P1`, `# Findings - P2`
- Omit empty priority groups.
- Put the code snippet in the same finding section (not in a separate snippets section).
- Omit the WCAG coverage matrix unless the user explicitly asks for it.
- Add `# Scope / Assumptions` only if ambiguity materially affects the audit.
- Add `# User Follow-Up Checks` only if there are `Needs user verification` items.

**Template for each finding:**

````md
# Findings - P1

## 1. <Problem name>
- **What**: <problem description with code evidence; include Confidence when useful, e.g. "Likely issue (confidence: medium)">
- **Where**: <file path + line(s)>
- **Fix suggestion**: <suggested fix in words>
- **WCAG**: <SC # - Title (Level)>

```swift
// patch-ready snippet
```
````

**Notes:**

- Keep snippets minimal and directly applicable to the cited code path.
- If no code snippet is appropriate, state why in `*Fix suggestion*`.

## Examples

- `Use $swiftui-wcag-accessibility-auditor to audit this SwiftUI checkout feature against WCAG 2.2 and return prioritized findings with patch-ready fixes in the strict finding format.`
- `Use $swiftui-wcag-accessibility-auditor to review this SwiftUI login + OTP flow for accessible authentication (3.3.8) and suggest minimal code changes.`
- `Use $swiftui-wcag-accessibility-auditor to audit this settings screen and produce user follow-up checks only for contrast, target size, and VoiceOver announcement timing.`

## Pitfalls

- **Focus Loop Trap:** If VoiceOver gets trapped in custom lists, programmatically manage the active accessibility focus element using `@AccessibilityFocusState`.
- **Contrast with Materials:** If backdrop transparency (materials) compromises text contrast, apply `.accessibilityReduceTransparency()` logic to fall back to high-contrast opaque styles.
- **Color-only indicators:** Never rely on color alone to convey state. Pair color with text, icon, or trait.
- **False positives on custom modifiers:** Always check Decision Rules and Pitfalls in this file before flagging a missing label — the element may use `.accessibilityRepresentation` or combined children.
- **UIKit bridges:** If the feature delegates core behavior to UIKit, do not fabricate SwiftUI fixes. Narrow the audit or route to `mobile-accessibility-audit`.
- **Unverifiable claims:** If a result cannot be proven from source (e.g., runtime contrast ratio, VoiceOver announcement timing), mark `Needs user verification` — do not assert a pass or fail.

## Verification

After producing the report, self-check:

1. **Every finding has all four fields**: What, Where, Fix suggestion, WCAG SC mapping.
2. **Every finding has an embedded snippet** or an explicit reason why none applies.
3. **No empty priority groups** appear in the output.
4. **No WCAG coverage matrix** is included unless the user explicitly requested it.
5. **`Needs user verification` items** appear under `# User Follow-Up Checks` with a concrete manual check.
6. **Scope is SwiftUI-native** — no macOS, watchOS, web, or non-SwiftUI findings unless explicitly bridged.

Quick self-audit command (PowerShell):

```powershell
rg -n "accessibilityLabel|accessibilityHint|accessibilityElement|accessibilityRepresentation|@AccessibilityFocusState|contentShape" .
```

Confirm that findings align with what is present vs. absent in the code.

## Resources

This folder ships only `SKILL.md`. Use Overview, Procedure, Decision Rules, Output Format, and Pitfalls above.

### Source Anchors

- [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [Apple SwiftUI Accessibility Guidelines](https://developer.apple.com/documentation/swiftui/accessibility)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

## Related Skills

- `mobile-accessibility-audit` — broader mobile audit including UIKit.
- `swiftui-accessibility-auditor` — fast SwiftUI-only heuristic review without WCAG traceability.

## Changelog

- **2026-05-30:** Updated to WCAG 2.2 Level A/AA standards, adding dynamic focus states and custom accessibility representations.
- **2026-05-31:** Re-checked W3C WCAG 2.2, Apple HIG, and Material Design sources.
