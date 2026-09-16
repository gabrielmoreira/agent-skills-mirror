---
name: tailwind-css
user-invocable: false
description:
  "Use for Tailwind v4 styling: add/fix classes, configure or migrate Tailwind, use tailwind-variants, or
  tw-animate-css."
---

# Tailwind CSS

Follow the installed Tailwind version and the repository's tokens, components, class-merging utility, CSS entrypoint,
and nearby UI. They take precedence over this skill; do not add packages, change integration, or migrate versions
without a request and local need.

## Routing

- Apply [coding preferences](references/coding-preferences.md) only where the project is silent.
- For v4 configuration, migration, directives, or generated classes, use [v4 rules](references/tailwind-v4-rules.md) and
  the matching official docs.
- Read [tailwind-variants](references/tailwind-variants.md), [tw-animate-css](references/tw-animate-css.md), or
  [ESLint](references/eslint.md) only when that integration exists locally or the request adds it.

Do not apply v4 syntax to an older installation. Preserve responsive, interaction, accessible, and dark-mode behavior;
do not redesign beyond the request.

## Completion

Define the intended visual and state change, reuse local conventions, and keep classes statically discoverable. If
source registration or generated mappings change, run the real Tailwind build and confirm the expected utilities. Run
relevant repository checks, then inspect the changed UI at representative viewports, themes, and interaction states.
When markup is transformed by JavaScript or a component library, inspect the final DOM too. Textual class review alone
is insufficient.

Finish with `### 🎨 Tailwind — ✅ styling updated` (or `### 🎨 Tailwind — 🔎 inspected, no files written`), a compact
viewport/theme/state/result table, and separate code-check and rendered-inspection evidence. Add `### ⚠️ Remaining` only
when needed; keep source UI copy and diagnostics undecorated.
