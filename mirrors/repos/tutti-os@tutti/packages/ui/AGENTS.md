# AGENTS.md

## Scope

This file applies to `packages/ui/*`.

`packages/ui/*` is for shared frontend foundations, not app-specific product
workflows.

If you are editing `packages/ui/system/*`, also read
[packages/ui/system/AGENTS.md](system/AGENTS.md).

## Current packages

- `packages/ui/system` as `@tutti-os/ui-system`
- `packages/ui/i18n-runtime` as `@tutti-os/ui-i18n-runtime`
- `packages/ui/notifications` as `@tutti-os/ui-notifications`
- `packages/ui/react-hooks` as `@tutti-os/ui-react-hooks`

`@tutti-os/ui-system` owns shared CSS tokens, theme styles, icon exports,
presentation primitives, and reusable business display components.
`@tutti-os/ui-i18n-runtime` owns host-agnostic i18n runtime helpers and scoped runtime composition for reusable frontend packages.
`@tutti-os/ui-notifications` owns host-agnostic notification service contracts and DI tokens for reusable frontend services.
`@tutti-os/ui-react-hooks` owns host-agnostic React hook helpers for reusable frontend packages, such as external-store snapshot and selector patterns.
These packages do not own business logic, app-specific workflows, host runtime
calls, workflow-owned domain modules, or domain-specific composed modules.

## Public API rules

Shared UI packages should expose narrow, stable surfaces:

- prefer adding exports to an existing package barrel before introducing a new
  public subpath
- do not expose `src/*` layout as public API
- do not encourage per-file deep imports
- if package exports change intentionally, update the matching package exports
  and boundary check script

## Action rules

- keep runtime helpers and hooks low-level, generic, and
  frontend-foundation-focused
- keep `@tutti-os/ui-react-hooks` focused on host-agnostic React hook patterns, not on domain hooks or non-React utilities
- when a shared frontend package needs external-store subscription wiring, prefer `@tutti-os/ui-react-hooks` over adding a new direct `useSyncExternalStore` wrapper locally
- keep adapter-level `getSnapshot()` identity fixes in the owning package; `@tutti-os/ui-react-hooks` does not replace reference-stable derived snapshots inside non-React adapters
- reusable packages outside `packages/ui/*` should consume `@tutti-os/ui-system` primitives and token-backed Tailwind utilities before adding package-local CSS
- if repeated package-local CSS needs emerge, move the shared foundation into `@tutti-os/ui-system`
- put `@tutti-os/ui-system` component, token, metadata, storyboard, and skill
  rules in `packages/ui/system`, not in this parent document

## Testing defaults

- Run `pnpm typecheck`
- Run `pnpm check:ui-boundaries`
- If a change affects desktop integration, also run `pnpm --filter @tutti-os/desktop build`

## Related docs

- [docs/conventions/desktop-visual-language.md](../../docs/conventions/desktop-visual-language.md)
- [packages/ui/system/ui-system.md](system/ui-system.md)
- [docs/conventions/local-git-hooks.md](../../docs/conventions/local-git-hooks.md)
- [docs/architecture/project-structure.md](../../docs/architecture/project-structure.md)
