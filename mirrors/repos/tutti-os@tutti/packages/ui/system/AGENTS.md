# AGENTS.md

## Scope

This file applies to `packages/ui/system/*`.

`packages/ui/system` is the source package for `@tutti-os/ui-system`, the
shared Tutti UI component library. It owns shared CSS tokens, theme styles,
icon exports, presentation primitives, reusable host-agnostic business display
components, component metadata, storyboard inventory, and the bundled
`tutti-ui-system` agent skill.

Before changing components, icons, metadata, styles, storyboard examples, or
the bundled skill, read `ui-system.md`.

UI-system design compliance is a release gate for this package, not a follow-up
task. If a promoted component does not yet follow the shared token model,
surface language, primitive vocabulary, and storyboard evidence standard, do
not report it as complete.

## Public API

Stable public imports are:

- `@tutti-os/ui-system`
- `@tutti-os/ui-system/components`
- `@tutti-os/ui-system/metadata`
- `@tutti-os/ui-system/icons`
- `@tutti-os/ui-system/styles.css`
- `@tutti-os/ui-system/utils`

Rules:

- prefer adding exports to an existing public barrel before introducing a new
  public subpath
- do not expose `src/*` layout as public API
- do not encourage per-file deep imports such as
  `@tutti-os/ui-system/components/button`
- if package exports change intentionally, update both the package exports and
  the UI-boundary check script

## Component Library Rules

- keep `base` components low-level, generic, and
  frontend-foundation-focused
- allow `business` components only when they are reusable business display
  components that remain host-agnostic and side-effect-free
- business components may expose domain display props such as workspace, file,
  task, agent, status, permission, and callbacks, but must not own daemon,
  Electron, router, store, query, filesystem, persistence, or workflow calls
- before promoting a business component, scan source usage, build a
  code-evidence state matrix, and define the public props boundary from that
  evidence; after that, promote it directly into `packages/ui/system` and add
  storyboard coverage for the accepted states
- business components should compose `base` primitives instead of recreating
  buttons, fields, dialogs, cards, icons, or overlays
- promoted components and their storyboard examples must use UI-system semantic
  tokens and approved shared CSS variables; do not leave raw `hex`,
  `rgb(...)`, `rgba(...)`, ad hoc gradients, or app-local palette values in the
  final UI-system implementation unless they already come from approved shared
  tokens
- storyboard coverage must show the component's real promoted surface and
  states; do not rely on surrounding docs chrome or wrapper panels to mask
  component-level visual drift
- UI storyboard foundation content is JSON-driven. When changing documented
  token, color, typography, spacing, radius, motion, or overview display data,
  edit `apps/ui-storyboard/src/foundation/*.json` directly instead of
  hardcoding those values in `apps/ui-storyboard/src/App.tsx`
- migrated consumers must end on the same UI-system visual implementation for
  the promoted surface; temporary bridges are allowed only for wiring, not as a
  separate long-lived token or styling system
- treat this package as the shared shadcn and Radix host package
- when a primitive exists in the shadcn registry, acquire it through shadcn CLI
  targeted at this package instead of handwriting the component body
- keep `components.json` and package aliases usable enough that CLI download
  remains the default path for shared primitives
- after CLI acquisition, limit edits to narrow package-specific adaptation such
  as icon routing, import aliases, stable exports, and boundary-check fixes
- keep CSS variables as the source of truth for token values
- prefer semantic token naming over raw palette leakage in public APIs
- keep helper exports minimal and tied to primitive support, not general
  convenience reuse
- build primitives for a calm workbench shell, not for marketing-card theatrics
- every public component, icon, utility, or style entry must have metadata with
  a stable readable `id` and `layer`
- use the single `tutti-ui-system` skill for component reuse, extraction,
  base/business classification, metadata, and storyboard work

## React Component Splitting Rules

- default to one component per directory; keep the component file, tests,
  stories, local styles, and tightly coupled implementation-detail helpers
  colocated inside that directory
- default to one React component per file; allow multiple small stateless
  helpers in one file only when they are tightly coupled implementation detail
  of the exported component
- split presentational components away from host wiring; components promoted
  into ui-system must receive data, labels, status, and callbacks through props
  rather than owning side effects or app workflow
- if a component does not need internal state or refs, prefer a plain function
  component; introduce heavier component structure only when state, refs, or
  lifecycle-like coordination is actually required
- when behavior is reusable but host-owned, extract it into caller-owned hooks,
  adapters, or controller code instead of embedding that logic in the ui-system
  component body
- do not use mixin-style reuse or implicit component coupling; prefer explicit
  composition through child components, slots, helper modules, or narrow
  wrappers
- keep component APIs semantic and stable; do not repurpose DOM prop names such
  as `style` or `className` to carry business meaning when a clearer prop like
  `variant`, `tone`, `status`, or `layout` is intended
- use spread props sparingly on public components; pass explicit props whenever
  possible so the boundary stays readable and host-agnostic
- list and collection components must render with stable identity from caller
  data; do not rely on array index keys in promoted UI-system surfaces
- when a component grows multiple visual regions or branches, first try to
  split subparts into local render helpers or child components before adding
  more mode booleans to one large component
- avoid boolean-prop sprawl for mutually exclusive modes; prefer a finite
  variant, discriminated union, explicit slot, or separate subcomponent when
  states represent distinct rendering modes
- keep user-visible copy caller-owned by default; if text changes by host,
  locale, or workflow, expose it through props, labels, or children instead of
  hardcoding it inside the shared component
- use the filename as the component name and keep exported component names in
  PascalCase so file boundaries stay obvious during promotion, review, and
  migration

## Validation

- Run `pnpm typecheck`
- Run `pnpm check:ui-boundaries`
- If component metadata changed, run `node tools/scripts/check-ui-metadata.mjs`
- If storyboard inventory changed, run
  `pnpm --filter @tutti-os/ui-storyboard typecheck`
- If a change affects desktop integration, also run
  `pnpm --filter @tutti-os/desktop build`
- In the handoff, explicitly state whether tokens, primitives, storyboard
  surface, and migrated consumer all comply with the UI-system standard; if any
  of those are still divergent, the work is not complete

## Related Docs

- `ui-system.md`
- `docs/conventions/desktop-visual-language.md`
- `docs/conventions/local-git-hooks.md`
