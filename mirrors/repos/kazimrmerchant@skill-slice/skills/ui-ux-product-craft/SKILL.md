---
name: ui-ux-product-craft
description: "Designs product screens from the core task outward: component choice, WCAG 2.2 keyboard and contrast, tokens, responsive layouts, action-oriented copy, and empty/loading/error states. Use when the user needs new UI, interaction patterns, microcopy, or a goal-to-layout plan. Not a heuristic audit report (review-ux-ui) and not a moderated session protocol (usability-testing)."
version: 1.0.1
---

# UI/UX Product Craft and Interaction Design

Systematic engineering principles for creating highly polished, accessible, user-centered, and operational interfaces that bridge the gap between product goals and UI layouts.

## Sources Verified (2026-05-31)

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- W3C WCAG FAQ: https://www.w3.org/WAI/standards-guidelines/wcag/faq/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

> Re-check official/current docs before relying on provider-specific APIs, policy, pricing, security behavior, or platform rules.

---

## When to Use

Use this skill when the agent needs to:

- Design new screens or redesign existing interfaces
- Improve usability, navigation, or interaction patterns
- Choose correct UI components (buttons vs links vs toggles vs selects)
- Audit accessibility (WCAG 2.2 contrast, keyboard, ARIA, focus management)
- Write or refine interface copy and micro-copy
- Turn vague product goals into practical, implementable UI layouts
- Build responsive layouts that work across mobile and desktop
- Create design-system tokens or component specifications
- Review visual hierarchy, density, and scanning behavior
- Implement focus traps, modals, or interactive component behavior in code

**Trigger keywords:** design screen, UI, UX, usability, accessibility, WCAG, interaction pattern, component, modal, focus trap, responsive layout, design system, interface copy, micro-copy, visual hierarchy, dark pattern, contrast, ARIA, keyboard navigation, empty state, loading state, error state.

---

## Prerequisites

Collect these inputs before starting. Ask the user for any missing critical items:

- **Target users** and their primary task
- **Platform** (web, iOS, Android, desktop)
- **Viewport range** (e.g., 320px–1440px)
- **Existing design system** (if any) — tokens, components, brand guidelines
- **Accessibility requirements** (WCAG level A, AA, or AAA)
- **Data density** expected (sparse vs dense data tables)
- **Interaction states** needed (empty, loading, error, success, disabled, offline)
- **Success metric** for the screen (e.g., checkout completion rate, task time)

Ask for screenshots or reference URLs when visual fidelity matters.

---

## Procedure

### Step 1 — Apply Task-Outward Design Framework

Design from the core user task outward, not from decoration inward. Follow this dependency chain:

```
Core Goal & Value Metric
  → Primary Actions & Success Path
    → Required Inputs & Metadata
      → Navigation & Backout Controls
        → Edge States: Error, Empty, Load, Disabled
```

1. **Identify the Core Task:** What is the primary value metric or goal of this screen? (e.g., completing checkout, checking server health).
2. **Success Path:** Highlight the primary CTA clearly using sizing, contrast, and layout hierarchy.
3. **Required Inputs:** Display only the inputs needed to execute the current task. Group secondary fields or collapse them under "advanced options".
4. **Navigation & Backouts:** Users must always have a visible way to cancel, undo, go back, or close a state without losing their context.
5. **Handle Edge States:** Systematically build views for loading states, empty query results, inline input validations, network offline states, and insufficient permissions.

### Step 2 — Select Correct Interaction Components

Use the matrix below to choose the right component for each interaction. Using unique controls for standard tasks increases cognitive load.

| Component Type | Best Used For | Instant Impact? | Key Accessibility Target | Common Misuse |
| :--- | :--- | :--- | :--- | :--- |
| **Button** | Commands, form submits, modal opening | Yes | Focusable, space/enter triggers | Navigating to new pages |
| **Link (`<a>`)** | Navigating context or exterior pages | No (routes view) | Has valid `href` and screen reader label | Triggering backend API writes |
| **Toggle** | Activating/deactivating features | Yes (immediate action) | `aria-checked` state synced | Multi-option select sets |
| **Checkbox** | Opt-in parameters, list selections | No (requires submit) | Bounded label with `id` matching `htmlFor` | Instant feature activation |
| **Select Dropdown** | Picking one from 6+ choices | No (requires confirm) | Keyboard navigable options | Selection of 2-3 options |

**Interaction rules:**

- **Buttons:** Trigger immediate system actions, commands, or data submissions. Never use raw text strings as buttons.
- **Anchor Links:** Route to a different page, relative URL, or scroll anchor. Never assign action click handlers to empty links (`href="#"`).
- **Segmented Control:** Switch modes or views within the same page context. Keep limits between 2 to 5 options.
- **Checkboxes & Toggles:** Checkboxes represent selections within lists; toggles represent immediate online/offline actions.
- **Menus & Select Fields:** Group lists of options. Use custom searchable overlays when lists exceed 10 options.

### Step 3 — Apply Accessibility Requirements Early

Integrate accessibility from the first design pass, not as a post-audit fix:

1. **Keyboard flow:** Map the full Tab order before writing code. Every interactive element must be reachable via Tab and activatable via Enter/Space.
2. **Focus visibility:** Ensure focus rings display clearly when active. Never use `outline: none` without adding `:focus-visible` replacements.
3. **Labels:** Every input has a visible `<label>` bound via `htmlFor`/`id`. Never rely solely on placeholders.
4. **Contrast:** Verify at least `4.5:1` for normal body copy and `3:1` for large headings.
5. **Color independence:** Status indicators (error vs success) must use secondary shapes, symbols, or text — never color alone.
6. **Reduced motion:** Respect `prefers-reduced-motion` for all animations and transitions.
7. **Touch targets:** Minimum 44×44px on mobile (Apple HIG) / 48×48dp (Material).
8. **Text resizing:** Layout must not break when text is scaled to 200%.
9. **Semantic structure:** Use `<button>`, `<a>`, `<nav>`, `<main>`, `<section>` — never `<div onclick>` for interactive controls.

### Step 4 — Define Design Tokens (If No Existing System)

When no design system exists, define tokens for:

- **Spacing:** 4px/8px base scale (e.g., 4, 8, 12, 16, 24, 32, 48, 64)
- **Color:** Primary, secondary, surface, background, error, warning, success, neutral — each with light/dark variants
- **Type:** Font family, size scale, weight, line-height, letter-spacing
- **Elevation:** Box-shadow levels (0–5)
- **Radius:** Border-radius scale (e.g., 4, 8, 12, 16, full)
- **Motion:** Duration (150ms, 200ms, 300ms) and easing curves

### Step 5 — Design Responsive Layouts

1. Use `max-width` rules (`max-width: 100%`) or container queries — never hardcoded pixel widths (`width: 800px`) on parent containers.
2. Test with realistic content: long labels, multi-line error text, empty states, maximum data density.
3. Verify no text overlap or clipping at the smallest target viewport (e.g., 320px).
4. Confirm dark/light variants render correctly for all states.

### Step 6 — Write Action-Oriented Copy

- Buttons must explain the exact outcome: `Save Changes` not `Submit` or `Proceed`.
- Errors must explain *what happened* and *how the user can recover* — never show raw system stack traces.
- The first view must display clear context so the user immediately understands what the system does.

### Step 7 — Deliver Implementation Guidance

Return a design or implementation plan with:

1. **User goal** and success metric
2. **Layout structure** (wireframe-level description or ASCII/mermaid diagram)
3. **Component list** with types from the matrix above
4. **States** (empty, loading, success, error, disabled, permission-limited, offline, responsive variants)
5. **Accessibility checks** (contrast, keyboard, ARIA, focus, color independence)
6. **Responsive behavior** (breakpoints, max-widths, touch targets)
7. **Copy notes** (button labels, error messages, empty-state text)
8. **Verification steps** (how to confirm the design works)

For code tasks, include exact files/components and testing guidance.

---

## Examples

### Example 1: Accessible Modal/Dialog (React + Tailwind CSS)

Implements keyboard escape, backdrop overlay, focus management, and ARIA attributes.

```tsx
import React, { useEffect, useRef } from 'react';

interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      role="presentation"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        className="w-full max-w-lg p-6 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col gap-4 animate-in fade-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <h2
            id="modal-title"
            className="text-lg font-semibold text-slate-900 dark:text-slate-50"
          >
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>

        <div className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
          {children}
        </div>

        <div className="flex justify-end gap-3 mt-4 border-t border-slate-100 dark:border-slate-800 pt-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};
```

### Example 2: Focus Trap Hook (TypeScript)

Wraps dialogs or interactive panels to prevent keyboard Tab focus from leaking outside the active container.

```typescript
import { useEffect, RefObject } from 'react';

export function useFocusTrap(containerRef: RefObject<HTMLElement | null>, isActive: boolean) {
  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (firstElement) {
      firstElement.focus();
    }

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    container.addEventListener('keydown', handleTab);
    return () => {
      container.removeEventListener('keydown', handleTab);
    };
  }, [containerRef, isActive]);
}
```

---

## Pitfalls

### Anti-Pattern 1: The "Ghost Input" (Placeholder-as-Label)

- **Problem:** Relying solely on input placeholders as form labels. Once a user types, the label vanishes, forcing the user to delete text to check what the field requires.
- **Fix:** Always show visible field labels or use floating label structures.

### Anti-Pattern 2: Low Contrast Interactive Elements

- **Problem:** Using light gray text inputs or buttons on white backgrounds.
- **Fix:** Implement explicit borders and dark typography to achieve at least `4.5:1` contrast ratio.

### Anti-Pattern 3: Hardcoded Pixel Widths

- **Problem:** Using `width: 800px` on parent containers causes layout breaks on small screens.
- **Fix:** Use `max-width: 100%` or container query structures.

### Anti-Pattern 4: Non-Semantic Clickable Divs

- **Problem:** Using `<div onclick>` as buttons. Screen readers bypass these entirely because they are not recognized as interactive controls.
- **Fix:** Use semantic `<button>` elements.

### Anti-Pattern 5: Dark Patterns

- **NEVER** design workflows that manipulate user behavior through deceptive structures:
  - Pre-selecting paid option boxes
  - Using confusing double-negatives
  - Hiding exit links or cancel buttons

### Anti-Pattern 6: Missing `aria-describedby` on Dynamic Validation

- **Problem:** Form validation errors appear visually but are not announced to screen reader users.
- **Fix:** Always append warnings directly to the target input using `aria-describedby` links so screen readers announce errors immediately when fields are selected.

### Anti-Pattern 7: `outline: none` Without Replacement

- **Problem:** Removing focus outlines with no `:focus-visible` alternative makes keyboard navigation invisible.
- **Fix:** Use Tailwind's `:focus-visible` pseudo-class to ensure focus rings display only during keyboard navigation, avoiding unwanted rings during mouse clicks.

### Failure Handling Priority

If requirements conflict, prioritize in this order:
1. **Usability** — can the user complete the task?
2. **Accessibility** — can all users complete the task?
3. **Product fit** — does it serve the business goal?
4. **Novelty** — only if it does not harm the above three.

If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant.

---

## Verification

### Accessibility & WCAG Compliance Checklist

Run through every item before deploying design changes:

- [ ] **Contrast:** All visual elements display at least `4.5:1` for normal body copy and `3:1` for large headings.
- [ ] **ARIA labels:** Image buttons (trash, edit, settings gear icons) have `aria-label` tags when they lack visible text.
- [ ] **Keyboard navigability:** Every button, link, and input is reachable via `Tab` and activatable via `Enter`/`Space`.
- [ ] **Focus rings:** Display clearly when active. No `outline: none` without `:focus-visible` replacement.
- [ ] **Color independence:** Status indicators use shapes, symbols, or text — not color alone.
- [ ] **Reduced motion:** Animations respect `prefers-reduced-motion`.
- [ ] **Touch targets:** Minimum 44×44px (Apple) / 48×48dp (Material) on mobile.
- [ ] **Text resize:** Layout survives 200% text scaling without overlap or clipping.

### UX Review & Heuristic Audit Checklist

- [ ] **Context visibility:** The first view displays clear context — the user immediately understands what the system does.
- [ ] **Action-oriented copy:** Buttons explain the exact outcome (`Save Changes` not `Submit`).
- [ ] **Layout wrapping:** Long variable labels do not clip or overlap layout borders on mobile responsive sizes.
- [ ] **Clean errors:** System errors explain *what happened* and *how to recover* — never raw stack traces.
- [ ] **Edge states:** Empty, loading, error, disabled, permission-limited, and offline states are all designed.
- [ ] **Backout controls:** Users can always cancel, undo, go back, or close without losing context.

### Quality Checklist

- [ ] User can complete the core task quickly and repeatedly.
- [ ] UI supports keyboard, screen readers, visible focus, and sufficient contrast.
- [ ] Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
- [ ] Controls use familiar affordances and expose state clearly.
- [ ] Motion is purposeful and respects reduced-motion preferences.
- [ ] Visual direction is intentional and consistent with the product domain.
- [ ] Diagrams have boundaries, labels, legends, and update ownership.
- [ ] Assets are inspectable, maintainable, and source-controlled where possible.

### Expert Visual Design Verification

When this skill is used for visual hierarchy, diagrams, or brand-interface work:

1. Verify visual choices support meaning and task flow — not decoration over weak structure.
2. Test with realistic content, small screens, wide screens, dark/light variants.
3. Confirm export requirements (resolution, format, accessibility of exported assets).
4. Verify current platform guidance when building for Apple, Android, or a specific design system.

---

## Related Skills

- **frontend-implementation** — for translating UI designs into production code
- **accessibility-audit** — for deep WCAG compliance testing
- **design-system-tokens** — for establishing token-based design systems
- **content-and-copywriting** — for interface copy and micro-copy refinement
