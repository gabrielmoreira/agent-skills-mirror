# Design system proposal (sent earlier in this conversation)

## What exists
React 19, Tailwind v4 (`src/styles/theme.css` holds the `@theme` tokens, with dark values in a `prefers-color-scheme` block), Radix Dialog, Vitest with Testing Library. No design system module. I wrote `DESIGN.md` at the root from theme.css.

## Spec changes to approve
1. Add the dark values from theme.css to DESIGN.md as `primary-dark` (#7C9BFF), `surface-dark` (#121417), `on-surface-dark` (#ECEEF2), `border-dark` (#2A2E35), so the spec covers both themes.
2. Rename `--color-muted` in theme.css to `--color-on-surface-muted`, to match the role naming.

## Opportunities
- Duplicate: `src/features/billing/Button.tsx` and `src/features/settings/components/Btn.tsx` are the same button (Btn uses raw hex and a 6px inline radius).
- Reinvented: `src/features/projects/ConfirmModal.tsx` hand-builds a dialog (no focus trap) while `@radix-ui/react-dialog` is installed and used in `src/features/settings/DeleteAccountDialog.tsx`.
- Scattered: card markup in `src/features/projects/ProjectCard.tsx:7`, `src/pages/BillingPage.tsx:12` and `src/pages/BillingPage.tsx:17`, `src/pages/SettingsPage.tsx:10`, drifting between rounded-lg/rounded-xl/rounded-[10px] and p-4/p-[18px].
- Loose: `src/features/projects/Avatar.tsx` is generic.
- Off-token: raw hex for primary, border, danger, and on-surface across Btn, ConfirmModal, ProjectCard, BillingPage, SettingsPage, Avatar; the settings input hand-styles its border and radius.

## Proposed system
Module at `src/design-system/`, flat, one folder per component with its test; tier in each component's doc comment and the README catalog.

- Atoms: Button (`variant: primary | secondary | danger | ghost`, `size: sm | md`, `loading`), Avatar (`name`, `src`, `size`), Input.
- Molecules: TextField (label, Input, hint, error), Card (`title`, children, `actions`).
- Organisms: ConfirmDialog (on Radix Dialog: `title`, `description`, `confirmLabel`, `tone: default | danger`, `onConfirm`).

Slices:
1. Module and tokens: create the module with its README; replace every raw hex value in the app with its token.
2. Button: build it, migrate both old buttons and every call site, delete Button.tsx and Btn.tsx. Needs 1.
3. Avatar and TextField: build them, migrate Avatar and the settings name field. Needs 1.
4. Card: build it, migrate ProjectCard and the billing and settings sections. Needs 1.
5. ConfirmDialog: build it on Radix, replace ConfirmModal and DeleteAccountDialog's dialog. Needs 2.
