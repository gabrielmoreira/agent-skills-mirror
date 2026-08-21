---
name: frontend-to-backend-requirements
description: "Writes a frontend-owned data and API requirements doc covering display needs, actions, and UI states without prescribing endpoints or field names, saved under .claude/docs/ai/<feature>/backend-requirements.md. Use when a frontend developer must document data needs for backend, or mentions backend/API requirements. Not for implementing the API or choosing REST vs GraphQL. Do not use for implementation plans (plan) or GOAL.md contracts (goal)."
version: 1.0.1
---

# Backend Requirements Mode

## Overview

This skill helps frontend developers communicate data needs to backend developers by describing the **what**, not the **how**. Backend owns implementation details—endpoints, field names, API structure, caching, and performance. Frontend owns what data is needed, what actions exist, what UI states to handle, and user-facing validation.

The output is a structured requirements document that invites collaboration, surfaces uncertainties, and leaves room for backend to propose solutions.

## When to Use

- A frontend developer needs to communicate API or data requirements to backend developers.
- User says "backend requirements", "what data do I need", "API requirements", or is describing data needs for a UI.
- Starting a new feature where frontend and backend need to align on data contracts.
- Reviewing or updating existing requirements after backend responds with questions or alternatives.
- Interface design, UX review, accessibility planning, responsive layouts, design systems, mobile/web UI, component behavior, interaction states, visual hierarchy, and usability improvements.

## Prerequisites

- A clear understanding of the feature being built (screen, flow, or component).
- Target users, primary task, platform, and viewport range identified.
- Existing design system or component library referenced if available.
- Accessibility requirements gathered (keyboard, screen reader, contrast, reduced motion).
- Windows host is primary (PowerShell). Directory creation uses PowerShell syntax.

## Procedure

### Step 1: Describe the Feature

Before listing requirements, establish context:

1. **What is this?** Identify the screen, flow, or component.
2. **Who uses it?** Identify user type and permissions.
3. **What's the goal?** Define what success looks like.

### Step 2: Create the Output Directory

```powershell
New-Item -ItemType Directory -Force -Path ".claude/docs/ai/<feature-name>"
```

### Step 3: List Data Needs

For each screen or component, describe:

**Data I need to display:**
- What information appears on screen?
- What's the relationship between pieces of data?
- What determines visibility or state?

**Actions user can perform:**
- What can the user do?
- What's the expected outcome?
- What feedback should they see?

**States I need to handle:**
- Loading, empty, error, success
- Edge cases (partial data, expired sessions, permission-limited, offline)

### Step 4: Surface Uncertainties

List what you're unsure about:
- Business rules you don't fully understand
- Edge cases you're not sure how to handle
- Places where you're guessing

These invite backend to clarify or push back.

### Step 5: Leave Room for Discussion

End with open questions:
- "Would it make sense to...?"
- "Should I expect...?"
- "Is there a simpler way to...?"

Include pushback prompts:
- "Let me know if this doesn't make sense for how the data is structured"
- "Open to suggestions on a better approach"
- "Not sure if this is the right way to think about it"
- "Push back if this complicates things unnecessarily"

### Step 6: Write the Output File

Write all output to `.claude/docs/ai/<feature-name>/backend-requirements.md` using the format below. **No chat output**—everything goes to the file.

```markdown
# Backend Requirements: <Feature Name>

## Context
[What we're building, who it's for, what problem it solves]

## Screens/Components

### <Screen/Component Name>
**Purpose**: What this screen does

**Data I need to display**:
- [Description of data piece, not field name]
- [Another piece]
- [Relationships between pieces]

**Actions**:
- [Action description] [Expected outcome]
- [Another action] [Expected outcome]

**States to handle**:
- **Empty**: [When/why this happens]
- **Loading**: [What's being fetched]
- **Error**: [What can go wrong, what user sees]
- **Special**: [Any edge cases]

**Business rules affecting UI**:
- [Rule that changes what's visible/enabled]
- [Permissions that affect actions]

### <Next Screen/Component>
...

## Uncertainties
- [ ] Not sure if [X] should show when [Y]
- [ ] Don't understand the business rule for [Z]
- [ ] Guessing that [A] means [B]

## Questions for Backend
- Would it make sense to combine [X] and [Y]?
- Should I expect [Z] to always be present?
- Is there existing data I can reuse for [W]?

## Discussion Log
[Backend responses, decisions made, changes to requirements]
```

### Step 7: Apply UI/UX 2026 Checklist

Before finalizing, verify the requirements account for:

1. **User task and information architecture** — Start from the user task, not decoration.
2. **Key states** — Map: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
3. **Accessibility** — Keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, semantic structure.
4. **Design-system primitives** — Use existing tokens for spacing, color, type, elevation, radius, and motion.
5. **Responsive layouts** — Stable dimensions, no text overlap across desktop and mobile.
6. **Realistic content** — Validate with long labels, error text, and touch/keyboard interaction.
7. **Concrete implementation guidance** — Not vague aesthetic notes.

### Step 8: After Backend Responds

Update the requirements doc:
1. Add responses to the Discussion Log section.
2. Adjust requirements based on feedback.
3. Mark resolved uncertainties with checkmarks.
4. Note any decisions made.

The doc becomes the source of truth for what was agreed.

## What You Own vs. What Backend Owns

| Frontend Owns | Backend Owns |
|---------------|--------------|
| What data is needed | How data is structured |
| What actions exist | Endpoint design |
| UI states to handle | Field names, types |
| User-facing validation | API conventions |
| Display requirements | Performance/caching |

## Good vs. Bad Requests

### Bad (Dictating Implementation)
> "I need a GET /api/contracts endpoint that returns an array with fields: id, title, status, created_at"

### Good (Describing Needs)
> "I need to show a list of contracts. Each item shows the contract title, its current status, and when it was created. User should be able to filter by status."

### Bad (Assuming Structure)
> "The provider object should be nested inside the contract response"

### Good (Describing Relationship)
> "For each contract, I need to show who the provider is (their name and maybe logo)"

### Bad (No Context)
> "I need contract data"

### Good (With Context)
> "On the dashboard, there's a 'Recent Contracts' widget showing the 5 most recent contracts. User clicks one to go to detail page."

## Pitfalls

- **Specifying implementation details** — Do not specify endpoints, HTTP methods, field names, or API structure. That is backend's call.
- **Prescribing instead of describing** — Say what you need, not how to provide it.
- **Omitting context** — Always explain why you need the data; it helps backend make better choices.
- **Hiding uncertainties** — Don't hide confusion. Surface unknowns and invite clarification.
- **Forgetting pushback prompts** — Explicitly ask for backend's input. Good collaboration means frontend describes the problem, backend proposes the solution.
- **Skipping states** — Missing edge cases like partial data, expired sessions, permission-limited views, or offline states leads to integration gaps.
- **Ignoring accessibility** — Keyboard flow, focus visibility, contrast, reduced motion, touch targets, and semantic structure must be part of the requirements, not an afterthought.
- **Not updating the Discussion Log** — After backend responds, update the doc. It becomes the source of truth for what was agreed.
- **Fragile responsive layouts** — Avoid viewport-scaled text or layouts that overlap on mobile. Use stable dimensions.
- **Ornamental drift** — Styling should follow the app's existing design system. Avoid decorative choices that break consistency.

## Verification

1. **Check output file exists and is well-formed:**
   ```powershell
   Test-Path ".claude/docs/ai/<feature-name>/backend-requirements.md"
   ```

2. **Verify no implementation details leaked:**
   ```powershell
   Select-String -Path ".claude/docs/ai/<feature-name>/backend-requirements.md" -Pattern "GET |POST |PUT |DELETE |PATCH |/api/|endpoint"
   ```
   If matches are found, rewrite those sections to describe needs without prescribing implementation.

3. **Verify all required sections present:**
   ```powershell
   Select-String -Path ".claude/docs/ai/<feature-name>/backend-requirements.md" -Pattern "## Context|## Screens|## Uncertainties|## Questions for Backend|## Discussion Log"
   ```

4. **Quality checklist verification:**
   - User can complete the core task quickly and repeatedly.
   - UI supports keyboard, screen readers, visible focus, and sufficient contrast.
   - Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
   - Controls use familiar affordances and expose state clearly.
   - Motion is purposeful and respects reduced-motion preferences.
   - Visual direction is intentional and consistent with the product domain.
   - All states documented: empty, loading, success, error, disabled, validation, permission, offline, long-content.
   - Uncertainties and questions for backend are explicitly listed.
   - Pushback prompts are included.

## Rules

- **NO IMPLEMENTATION DETAILS** — Don't specify endpoints, methods, field names.
- **DESCRIBE, DON'T PRESCRIBE** — Say what you need, not how to provide it.
- **INCLUDE CONTEXT** — Why you need it helps backend make better choices.
- **SURFACE UNKNOWNS** — Don't hide confusion, invite clarification.
- **INVITE PUSHBACK** — Explicitly ask for backend's input.
- **UPDATE THE DOC** — Add backend responses to Discussion Log.
- **STAY HUMBLE** — You're asking, not demanding.

## Current References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- W3C WCAG FAQ: https://www.w3.org/WAI/standards-guidelines/wcag/faq/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

## Related Skills

- UI/UX design and implementation skills for React/Angular/Tailwind component work, dashboards, forms, tables, and design systems.
- Accessibility audit skills for WCAG 2.2 compliance verification.
