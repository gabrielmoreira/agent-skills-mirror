---
type: skill
lifecycle: stable
inheritance: inheritable
name: frontend-design-review
description: Review and create distinctive frontend interfaces — design system compliance, three quality pillars (Frictionless, Quality Craft, Trustworthy), accessibility
tier: standard
applyTo: '**/*frontend*,**/*design*,**/*review*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Frontend Design Review


> Review UI implementations against design quality standards **OR** create distinctive, production-grade frontend interfaces

---

## Two Modes

### Mode 1: Design Review

Evaluate existing UI for:

- Design system compliance
- Three quality pillars (Frictionless, Quality Craft, Trustworthy)
- Accessibility
- Code quality

### Mode 2: Creative Frontend Design

Create distinctive interfaces that:

- Avoid generic "AI slop" aesthetics
- Have clear conceptual direction
- Execute with precision

---

## Design Review

### Design System Workflow

**Before implementing:**

1. Review component in your Storybook / component library for API and usage
2. Use Figma Dev Mode to get exact specs (spacing, tokens, properties)
3. Implement using design system components + design tokens

**During review:**

1. Compare implementation to Figma design
2. Verify design tokens are used (not hardcoded values)
3. Check all variants/states are implemented correctly
4. Flag deviations (needs design approval)

**If component doesn't exist:**

1. Check if existing component can be adapted
2. Reach out to design for new component creation
3. Document exception and rationale in code

### Review Process

1. Identify user task
2. Check design system for matching patterns
3. Evaluate aesthetic direction
4. Identify scope (component, feature, or flow)
5. Evaluate each pillar
6. Score and prioritize issues (blocking/major/minor)
7. Provide recommendations with design system examples

### Core Principles

- **Task completion**: Minimum clicks. Every screen answers "What can I do?" and "What happens next?"
- **Action hierarchy**: 1-2 primary actions per view. Progressive disclosure for secondary.
- **Onboarding**: Explain features on introduction. Smart defaults over configuration.
- **Navigation**: Clear entry/exit points. Back/cancel always available. Breadcrumbs for deep flows.

---

## Quality Pillars

### 1. Frictionless Insight to Action

**Evaluate:** Task completable in ≤3 interactions? Primary action obvious and singular?

**Red flags:**

- Excessive clicks
- Multiple competing primary buttons
- Buried actions
- Dead ends

### 2. Quality is Craft

**Evaluate:**

- **Design system compliance**: matches Figma specs, uses design tokens
- **Aesthetic direction**: distinctive typography, cohesive colors, intentional motion
- **Accessibility**: Grade C minimum (WCAG 2.1 A), Grade B ideal (WCAG 2.1 AA)

**Red flags:**

- Generic AI aesthetics
- Hardcoded values
- Implementation doesn't match Figma
- Broken reflow
- Missing focus indicators

### 3. Trustworthy Building

**Evaluate:**

- **AI transparency**: disclaimer on AI-generated content
- **Error transparency**: actionable error messages

**Red flags:**

- Missing AI disclaimers
- Opaque errors without guidance

---

## Creative Frontend Design

Before coding, commit to an aesthetic direction:

- **Purpose**: What problem does this solve? Who uses it?
- **Tone**: minimal, maximalist, retro-futuristic, organic, luxury, playful, editorial, brutalist, art deco, soft/pastel, industrial, etc.
- **Constraints**: Framework, performance, accessibility requirements.
- **Differentiation**: What makes this distinctive and context-appropriate?

### Aesthetics Guidelines

| Element | Guidance |
|---------|----------|
| **Typography** | Distinctive fonts that elevate aesthetics. Pair a display font with a refined body font. **Avoid**: Inter, Roboto, Arial, Space Grotesk. |
| **Color & Theme** | Cohesive palette with CSS variables. Dominant colors + sharp accents > timid, evenly-distributed palettes. |
| **Motion** | CSS-only preferred. One well-orchestrated page load with staggered reveals > scattered micro-interactions. |
| **Spatial Composition** | Asymmetry, overlap, diagonal flow, grid-breaking elements, generous negative space OR controlled density. |
| **Backgrounds** | Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, grain overlays. |

**AVOID:**

- Overused fonts
- Cliché color schemes
- Predictable layouts
- Cookie-cutter design without context-specific character

Match implementation complexity to vision. Maximalist = elaborate code. Minimalist = restraint and precision.

---

## Accessibility Quick Check

### Grade C (WCAG 2.1 A) — Minimum

- [ ] All interactive elements keyboard accessible
- [ ] Focus visible on all focusable elements
- [ ] Images have alt text
- [ ] Color is not the only means of conveying information
- [ ] Form fields have labels

### Grade B (WCAG 2.1 AA) — Target

- [ ] Color contrast ≥4.5:1 (text), ≥3:1 (large text, UI components)
- [ ] Focus indicators visible and clear
- [ ] Text resizable to 200% without loss of functionality
- [ ] Keyboard focus order logical
- [ ] Error messages identify the field and describe the error

### Grade A (WCAG 2.1 AAA) — Stretch

- [ ] Color contrast ≥7:1 (text)
- [ ] No timing-based interactions without controls
- [ ] Sign language for video content
- [ ] Extended audio descriptions

---

## Review Output Format

```markdown
## Summary
[One-line assessment: pass/needs work/blocking issues]

## Pillar Scores
| Pillar | Score | Notes |
|--------|-------|-------|
| Frictionless | ⚠️ | 4 clicks to complete primary task |
| Quality Craft | ✅ | Design system compliant |
| Trustworthy | ❌ | Missing AI disclaimer |

## Issues

### Blocking
1. [Issue]: [Description] → [Fix]

### Major
1. [Issue]: [Description] → [Fix]

### Minor
1. [Issue]: [Description] → [Fix]

## Recommendations
[Prioritized next steps with design system references]
```

---

## Review Type Modifiers

### PR Review Focus

- Code quality and patterns
- Design token usage
- Component API compliance
- Breaking changes to shared components

### Creative Review Focus

- Aesthetic distinctiveness
- Conceptual coherence
- Technical execution of vision
- Performance impact of effects

### Accessibility Audit Focus

- WCAG conformance level
- Assistive technology compatibility
- Keyboard navigation paths
- Screen reader announcements

### Design System Compliance Focus

- Token usage vs hardcoded values
- Component variants coverage
- Figma-to-code accuracy
- Documentation updates needed

---

## Quick Checklist

### Pre-Approval

**Design System:**

- [ ] Uses design system components (not custom implementations)
- [ ] Uses design tokens (not hardcoded colors/spacing)
- [ ] Matches Figma specs within tolerance
- [ ] All variants/states implemented

**React 19 Patterns (if applicable):**

- [ ] Forms use `useActionState` (not manual useState + fetch)
- [ ] Optimistic updates use `useOptimistic` hook
- [ ] Server state via TanStack Query (not local state for fetched data)
- [ ] Submit buttons use `useFormStatus` from design system
- [ ] No unnecessary `forwardRef` (React 19 accepts ref as prop)

**Aesthetic Quality:**

- [ ] Distinctive typography choice
- [ ] Cohesive color palette via CSS variables
- [ ] Intentional motion (or explicit choice of none)
- [ ] Appropriate visual density

**Frictionless:**

- [ ] Primary action ≤3 interactions
- [ ] Clear action hierarchy
- [ ] No dead ends
- [ ] Progress indicators for multi-step flows
- [ ] Optimistic UI for perceived performance

**Quality Craft:**

- [ ] Responsive/reflow works
- [ ] Focus indicators visible (`:focus-visible` with ring)
- [ ] Loading states present (skeleton > spinner)
- [ ] Error states handled with `role="alert"`

**Trustworthy:**

- [ ] AI content disclosed
- [ ] Errors are actionable
- [ ] User data handling transparent

---

## Modern Stack Reference

| Layer | Recommended | Notes |
|-------|-------------|-------|
| Framework | React 19 | useActionState, useOptimistic, use() |
| Styling | Tailwind + CSS vars | Design tokens via variables |
| Components | shadcn/ui + Radix | Open Code philosophy |
| Server state | TanStack Query | Caching, optimistic updates |
| Client state | Zustand | Simple, TypeScript-first |
| Forms | React Hook Form + Zod | Or native form actions |
| Testing | Vitest + Testing Library | Test behavior, not implementation |

## Related Skills

This skill complements:

- **ui-ux-design** — Accessibility patterns, design system foundations
- **Frontend** agent — React 19 patterns, full component examples
- **graphic-design** — Visual design principles, SVG graphics
- **code-review** — Technical review patterns

---

## Acknowledgments

Design review principles and quality pillar framework created by [@Quirinevwm](https://github.com/Quirinevwm).
Creative frontend guidance inspired by [Anthropic's frontend-design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design).
