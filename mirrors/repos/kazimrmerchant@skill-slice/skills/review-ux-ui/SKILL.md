---
name: review-ux-ui
description: "Audits interfaces with Nielsen's 10 heuristics, WCAG 2.2 AA or AAA, keyboard and screen-reader flow, and cognitive-load maps, then returns a severity-ranked report. Trigger on UX review, UI audit, heuristic evaluation, or accessibility. Do not use for implementing CSS/HTML (frontend-design). Not a form-CRO conversion chair."
version: 1.0.1
domain: UI-UX
risk: safe
last_verified: 2026-05-30
self_updating: true
---

# UX/UI Auditing and Usability Review

## Overview

Evaluate user interfaces and interactive flows for usability, visual clarity, accessibility compliance, and cognitive overhead. This skill applies three core methodologies — heuristic evaluation, accessibility audit, and task flow analysis — and produces a structured, prioritized report with severity-scored recommendations.

## Sources Checked (2026-05-31)

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Material Design: https://m3.material.io/
- Nielsen Norman Group 10 Usability Heuristics: https://www.nngroup.com/articles/ten-usability-heuristics/

> Re-check official/current docs before relying on provider-specific APIs, policy, pricing, security behavior, or platform rules.

## When to Use

- **Use when**: Reviewing layouts, interactive prototypes, page mockups, or finished web views for usability flow bottlenecks, UX consistency, and accessibility standards.
- **Trigger keywords**: UX review, UI audit, accessibility audit, WCAG compliance, heuristic evaluation, usability testing, keyboard flow, screen reader, cognitive load, contrast check, focus order.
- **Route elsewhere**: Use `frontend-design` for writing implementation CSS/HTML scripts. Use `form-cro` specifically when optimizing conversion forms that are not signups or account creations.

## Prerequisites

- **Inputs required**: UI source code, screenshots, or URL of the active site/prototype. Target user persona context.
- **If source files are unavailable**: Request high-resolution screenshots or video recordings of interactive flows. Evaluate based on visual layout, text contrast, and logical steps.
- **Recommended tooling for programmatic passes** (run before manual review):
  - Axe-core 4.x — browser extension or CLI for automated WCAG checks.
  - Lighthouse 11+ — Chrome DevTools or CLI for accessibility scoring.
- **Windows host (primary)**: Use PowerShell for any CLI tooling. Example:

```powershell
# Run Lighthouse CLI against a URL (Node.js required)
npx lighthouse https://example.com --only-categories=accessibility --output=html --output-path=.\lighthouse-report.html

# Run axe-core CLI against a URL
npx @axe-core/cli https://example.com --save=.\axe-report.json
```

## Procedure

### Step 1: Heuristic Evaluation (Nielsen's 10)

Rate the interface against each usability heuristic. For every violation, record the heuristic ID, a severity score, the observation, and the location.

| ID | Heuristic | Key Verification Question |
| :--- | :--- | :--- |
| **1** | **Visibility of system status** | Does the system always inform users about active processes? |
| **2** | **Match between system and real world** | Does the system use familiar language and conceptual models? |
| **3** | **User control and freedom** | Can users easily undo actions, exit states, or rollback changes? |
| **4** | **Consistency and standards** | Do visual patterns and terms behave identically across pages? |
| **5** | **Error prevention** | Does the interface actively prevent incorrect actions before they occur? |
| **6** | **Recognition rather than recall** | Are navigation options and properties visible or easily accessible? |
| **7** | **Flexibility and efficiency of use** | Are accelerators (shortcuts) present for advanced users? |
| **8** | **Aesthetic and minimalist design** | Does every element serve a purpose without visual clutter? |
| **9** | **Error recovery** | Are error messages written in clear, helpful language that guides a fix? |
| **10** | **Help and documentation** | Is helper documentation contextual, searchable, and concise? |

#### Violation Severity Ratings

- **0**: No usability issue detected.
- **1** (Cosmetic): Fixed only if time permits.
- **2** (Minor): Low priority; causes slight user friction.
- **3** (Major): High priority; causes notable confusion or path blockages.
- **4** (Catastrophic): Must fix before release; blocks task completion.

#### Heuristic Evaluation Log Template

```markdown
| # | Heuristic Violation | Severity | Observation | Location |
|---|---|---|---|---|
| 1 | System Status | 3 | No loader displayed during credit card validation. | Payment Screen |
| 3 | User Control | 3 | Deleting a workspace project cannot be undone. | Settings Panel |
| 5 | Error Prevention | 2 | Date fields allow inputting impossible dates (e.g. June 31). | Booking Page |
```

### Step 2: Accessibility Audit (WCAG 2.2 Level AA)

Verify interfaces against modern accessibility requirements. Run Axe-core or Lighthouse first for automated detection, then manually verify each item below.

#### Perceivable (Category 1)

- [ ] **1.1.1 Non-text Content**: Informative images possess descriptive `alt` tags; decorative images utilize `alt=""`.
- [ ] **1.3.1 Info and Relationships**: Semantic markup (headings `<h1>`-`<h6>`, list elements, navigation landmarks) maps to visual structures.
- [ ] **1.4.1 Use of Color**: Color is not used as the sole conveyor of information (e.g. error states use icon + red text).
- [ ] **1.4.3 Contrast (Minimum)**: Text contrast measures at least 4.5:1 for standard text and 3:1 for large text.
- [ ] **1.4.11 Non-Text Contrast**: Visual buttons, border lines, and form boundaries measure at least 3:1 contrast against backdrops.

#### Operable (Category 2)

- [ ] **2.1.1 Keyboard**: All clickable elements, inputs, and actions can be triggered using keyboard keys (Tab, Space, Enter).
- [ ] **2.1.2 No Keyboard Trap**: Keyboard focus is not trapped inside overlays or widgets.
- [ ] **2.4.3 Focus Order**: Tabbing order matches the logical visual structure.
- [ ] **2.4.7 Focus Visible**: Active elements display a highly visible focus ring indicator.
- [ ] **2.4.11 Focus Not Obscured (Minimum)**: Focused items are not hidden behind sticky footers or header overlays (WCAG 2.2).
- [ ] **2.5.8 Target Size (Minimum)**: Target components measure at least 24x24 CSS pixels, or have spacing gaps to adjacent elements (WCAG 2.2).

#### Understandable (Category 3)

- [ ] **3.1.1 Language of Page**: The parent element has the language attribute defined (e.g., `<html lang="en">`).
- [ ] **3.2.1 On Focus**: Focusing on an element does not trigger page shifts or popups.
- [ ] **3.3.2 Labels or Instructions**: Input fields display persistent visual labels.
- [ ] **3.3.7 Redundant Entry**: Information entered in a step is auto-populated in subsequent steps where required (WCAG 2.2).

#### Robust (Category 4)

- [ ] **4.1.2 Name, Role, Value**: Custom interactive elements utilize correct ARIA attributes (e.g. `role="button"`, `aria-expanded`).
- [ ] **4.1.3 Status Messages**: Live updates (success notifications, processing indicators) are announced to screen readers via `aria-live` regions.

#### Semantic HTML Audit (Stable Craft)

Audit base HTML structures for proper tags (`<button>` for actions, `<a>` for navigation) **before** checking ARIA attributes. ARIA attributes cannot fix broken semantic DOM hierarchies.

#### Keyboard Tab Control (Stable Craft)

Verify tabbing focus loops manually. Prevent tabbing from escaping active modal containers or dropdown panels when they are open.

### Step 3: Interactive Flow Analysis

Map out the steps required to complete major workflows and identify friction points.

```markdown
### User Flow: Guest Checkout

#### Steps Map
1. Cart Page -> 2. Account Choice (Guest vs Login) -> 3. Shipping Form ->
4. Delivery Method Selection -> 5. Payment Details -> 6. Success Screen

#### Friction Metrics
*   **Total Steps**: 6
*   **Form Fields**: 12 (Autocomplete enabled)
*   **Cognitive Branch Points**: 1 (Choosing guest vs registration)
*   **Friction Points**:
    *   Step 2: Guest checkout button is visually smaller than the "Register" button (Severity 2).
    *   Step 5: Coupon code field expands and shifts the checkout payment button off-screen on mobile devices (Severity 3).
```

#### Error Recovery Routes

Ensure that error states do not clear user-submitted data. Maintain user entries during validation passes to reduce friction.

### Step 4: Cognitive Load Assessment

- **Information Density**: Screen layouts must keep logical groupings separated. Use the "squint test" (squinting at the screen to verify visual hierarchy) to check layout balance.
- **Progressive Disclosure**: Hide advanced configuration panels behind tabs or collapsible cards.
- **Hick's Law Enforcement**: Avoid offering too many equal choices on primary panels. Group choices or introduce multi-step paths.

### Step 5: Compile the Audit Report

Use the reporting template below. Ensure findings are prioritized and actionable.

```markdown
# UX/UI Auditing Report: [Project Name]

## 1. Executive Summary
[Provide 3-4 sentences outlining overall usability, top blocking issues, and areas of high design quality.]

## 2. Heuristic Audit Summary
| Heuristic | Violations | Critical Issues Summary |
|:---|:---|:---|
| Heuristic 3: User Control | 2 | No "Cancel" or "Undo" actions on record deletions. |
| Heuristic 9: Error Recovery | 1 | Inline form validations return generic "Invalid Field" messages. |

## 3. Accessibility Status (WCAG 2.2 AA)
*   **Baseline Compliance Status**: Non-Compliant / Partial Compliance
*   **Critical WCAG Failures**:
    *   **2.4.7 Focus Visible**: Search input element hides focus outline rings.
    *   **1.4.3 Contrast**: Light gray footer text has a contrast ratio of 2.1:1.

## 4. Top 3 Usability Recommendations (Prioritized)
1.  **Add confirmation dialogs and Undo actions to destructive options**: Resolve project deletion slips (Severity 4).
2.  **Restore focus rings on all focusable targets**: Enable keyboard navigation compliance (Severity 3).
3.  **Refactor mobile form fields**: Ensure the checkout button stays above the mobile viewport fold (Severity 3).
```

### Decision Rules

- **Accessibility Target Configuration**:
  - Target **WCAG 2.2 AA** for standard SaaS products, corporate portals, and public-facing websites.
  - Target **WCAG 2.2 AAA** for public utility systems, government resources, and education interfaces.
- **Form Field Display Rules**: Choose inline error messages directly adjacent to the input field instead of displaying errors at the top of the form or in a generic toast message.

### Output Contract

Return a detailed audit report listing:
1. Heuristic Violations (with severity scores)
2. WCAG Failures (with criterion references)
3. Keyboard/Screen Reader Logs
4. Prioritized list of actionable recommendations with severity scores

## Pitfalls

- **Confusing esthetics with usability**: Grading a user interface highly because it has clean visuals, despite blocking users with low text contrast or confusing navigation options. Usability focuses on efficiency, clarity, and task success — not visual polish alone.
- **Auditing only the happy path**: Testing only successful interactions. Usability and accessibility bugs reside in error fields, recovery paths, and empty states. Always test failure and edge-case flows.
- **Providing subjective feedback**: Using phrases like "I do not like the blue borders." Frame feedback using objective design patterns, WCAG rules, or Nielsen's usability heuristics. Cite the specific heuristic or WCAG criterion violated.
- **Relying on ARIA to fix broken semantics**: ARIA attributes cannot fix broken semantic DOM hierarchies. Always audit base HTML structure first (`<button>` for actions, `<a>` for navigation), then layer ARIA on top.
- **Skipping manual keyboard testing**: Automated tools (Axe, Lighthouse) catch ~30-40% of WCAG issues. Manual keyboard tab-flow and screen reader testing is mandatory for full coverage.
- **Clearing user data on validation errors**: Error states must not clear user-submitted data. Maintain user entries during validation passes to reduce friction and re-entry burden.

## Verification

Confirm the audit is complete by checking the quality bar:

- [ ] Evaluates layout against all 10 Nielsen Heuristics.
- [ ] Reviews components against WCAG 2.2 AA standards (or AAA if target requires).
- [ ] Verifies keyboard tab flows and visual focus states manually.
- [ ] Details prioritized recommendations with severity scores (0-4).
- [ ] Report includes executive summary, heuristic summary table, accessibility status, and top recommendations.
- [ ] All findings reference specific heuristic IDs or WCAG criterion numbers.
- [ ] Error recovery and empty states were tested, not just the happy path.

### Programmatic Verification Commands (Windows / PowerShell)

```powershell
# Verify Lighthouse accessibility score (target: >= 90 for AA compliance)
npx lighthouse https://example.com --only-categories=accessibility --output=json --quiet | Select-String "score"
```

```powershell
# Verify axe-core passes with zero critical violations
npx @axe-core/cli https://example.com --tags=wcag2aa --save=.\axe-report.json
# Check exit code: 0 = no violations, 1 = violations found
echo $LASTEXITCODE
```

## Related Skills

- `frontend-design` — for writing implementation CSS/HTML scripts.
- `form-cro` — for optimizing conversion forms (non-signup/account-creation flows).

## Changelog

- **2026-05-30**: Modernized accessibility criteria to target WCAG 2.2. Replaced second-person phrasing with direct instructions. Removed legacy boilerplate.
- **2026-05-31**: Re-verified W3C WCAG 2.2, Apple HIG, and Material Design sources.
