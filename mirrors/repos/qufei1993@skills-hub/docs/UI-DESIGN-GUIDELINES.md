# Skills Hub UI Design Guidelines

This document defines the durable visual and interaction rules for Skills Hub. It is a compact reference for frontend work, not a pixel specification.

The original HTML prototype establishes the design direction. The current React implementation may refine dimensions, spacing, and component structure while preserving the rules below. Runtime tokens in `src/index.css` remain the source of truth for exact values.

## What this document governs

Use these guidelines to decide:

- visual hierarchy and information density;
- semantic use of color, typography, borders, and elevation;
- behavior and visual states of shared controls;
- navigation, overlays, feedback, responsive reduction, and accessibility;
- whether a new UI fits the existing product.

This document intentionally does **not** define:

- exact dimensions, breakpoints, or spacing values;
- a complete page or component inventory;
- CSS selectors, React structure, or implementation steps;
- copy that already belongs in i18n resources;
- temporary states taken from screenshots or one release.

Do not expand this file with details that are already obvious from the code. Add a rule only when it should influence multiple future UI decisions.

## Design posture

Skills Hub uses a neutral, modern utility aesthetic: calm, compact, and quietly confident. It is a desktop management tool, so clarity and operational density take priority over decoration.

- Make the current task and primary action obvious.
- Prefer whitespace, alignment, and subtle borders over extra containers.
- Keep surfaces flat by default; reserve elevation for temporary layers.
- Use one visual accent consistently instead of multiple decorative colors.
- Preserve real product density. Do not turn management screens into oversized marketing cards.
- Write direct interface copy using terms users recognize: Skills, tools, tags, scope, sync, and updates.

## Color system

Use semantic CSS variables. Do not hardcode colors in component styles when an existing role applies.

The light theme baseline is:

| Role | Baseline | Use |
| --- | --- | --- |
| App background | `#FAFAFA` | Workspace and navigation background |
| Panel surface | `#FFFFFF` | Cards, tables, forms, dialogs |
| Primary text | `#18181B` | Main labels and content |
| Secondary text | `#6B6B72` | Descriptions, metadata, inactive navigation |
| Subtle border | `#DEDEE1` | Separation and component boundaries |
| Primary accent | `#2F6FED` | Primary actions, focus, selection, active navigation |
| Success | `#059669` | Healthy sync and completed operations |
| Warning | `#D97706` | Attention and recoverable issues |
| Error | `#DC2626` | Failures, destructive actions, invalid states |

These values are reference anchors, not permission to duplicate literals. Use the tokens in `src/index.css`, including their dark-theme bindings and soft background variants.

Color rules:

- The accent represents action, focus, or selection; it is not decoration.
- Status colors communicate state only. Pair them with text or an icon, never color alone.
- Use soft semantic backgrounds for notices and selected rows; keep saturated color areas small.
- Maintain clear foreground contrast in both themes.
- New colors require a reusable semantic role and light/dark token bindings.

## Typography and iconography

- Use the project UI sans-serif stack for interface text.
- Use the monospace stack for paths, versions, commands, code, and tabular technical values.
- Establish hierarchy through weight, contrast, and spacing before adding another text size.
- Keep labels concise and descriptions secondary. Avoid decorative uppercase text and marketing-style headings in product screens.
- Use Lucide icons with consistent stroke treatment. Icons should clarify an action or object, not accompany every heading.
- Never rely on an icon without an accessible label when its meaning is not universally obvious.

## Layout and hierarchy

- Treat the sidebar, title/header area, content workspace, and temporary overlays as distinct structural regions.
- Align related controls and data to a shared grid. Prefer predictable scanning over visual novelty.
- Use tables or structured lists for dense management tasks; use cards for discovery, selection, or grouped settings.
- Keep one dominant action per region. Secondary and destructive actions must have lower emphasis.
- Avoid nested cards unless the inner boundary represents a real interaction or ownership boundary.
- Let content areas scroll independently where appropriate; keep persistent navigation stable.
- Empty space must support grouping or focus, not imitate a marketing landing page.

## Shared component behavior

### Buttons and controls

- Primary buttons trigger the main forward action. Secondary buttons use a neutral surface and border.
- Destructive actions use the error role and require confirmation when data or synchronization targets are removed.
- Disabled controls must look unavailable and explain the missing prerequisite nearby when it is not obvious.
- Inputs use a neutral resting state and a clear accent focus state. Validation appears next to the relevant field.
- Switches are for immediate binary settings; use checkboxes for multi-selection and segmented controls for mutually exclusive views or modes.

### Panels, tables, and cards

- Panels use a surface, subtle border, and restrained corner treatment. Default panels do not need shadows.
- Tables preserve row alignment and scanning. Hover, selected, disabled, warning, and error states must remain distinguishable.
- Discovery cards should expose identity, source, a short purpose statement, and the next action without duplicating detail views.
- Badges describe compact metadata or status. Do not use them as decoration or repeat information already clear from the surrounding text.

### Navigation and sidebar

- Active navigation is communicated by container state, text contrast, and icon treatment—not by a status dot alone.
- Expanded navigation may show labels and useful counts.
- Collapsed navigation keeps only icons and the active state. Hide count badges and status dots; reveal labels through an accessible tooltip when needed.
- Navigation controls switch real product areas. Do not add designer, viewport, or theme-demo controls to the product UI.

### Dialogs, drawers, and feedback

- Use a dialog for focused decisions and confirmations. Use a drawer for contextual inspection that benefits from preserving the underlying page.
- Overlays must have a clear title, close path, keyboard behavior, and action hierarchy.
- Toasts confirm short-lived outcomes; they must not contain information required to continue.
- Loading states state what is happening. Long operations should show progress or allow cancellation when cancellation is safe.
- Errors explain what failed and the next recovery action. Avoid vague apologies.

## Interaction and motion

- Every interactive element needs resting, hover, focus, active, disabled, and relevant loading or selected states.
- Keep transitions short and purposeful. Motion should explain entry, exit, or state change rather than decorate the interface.
- Preserve keyboard navigation and visible focus treatment.
- Respect reduced-motion preferences.
- Maintain action naming across the flow: the button, progress message, toast, and result should use the same verb.

## Responsive reduction

Skills Hub is desktop-first, but the interface must remain usable in constrained windows.

When space decreases, adapt in this order:

1. collapse persistent navigation;
2. reduce multi-column layouts;
3. move secondary controls without hiding primary actions;
4. hide or defer low-priority metadata;
5. allow dense data regions to scroll when restructuring would damage comprehension.

Do not scale the complete desktop interface down uniformly. Preserve readable text, usable targets, and task priority.

## Accessibility and localization

- Use semantic controls and meaningful labels before adding ARIA.
- Do not use color as the only indicator of state.
- Keep focus visible and preserve logical keyboard order in dialogs, drawers, menus, and forms.
- Ensure layouts tolerate longer English and Chinese strings without clipping essential actions.
- All user-visible product copy belongs in i18n resources with both English and Chinese entries.

## Review checklist

Before shipping frontend UI, confirm:

- the change uses existing semantic tokens and supports both themes;
- hierarchy exposes one clear primary task or action;
- dense information remains easy to scan;
- every control has complete interaction and keyboard states;
- loading, empty, error, and destructive flows provide a next step;
- collapsed navigation hides badges and status dots;
- the UI remains usable in constrained windows and with longer localized copy;
- no implementation-only controls, decorative color, or unnecessary containers were introduced.

When a feature needs to depart from these rules, document the reason in the feature specification or code review. Do not silently redefine the global design language.
