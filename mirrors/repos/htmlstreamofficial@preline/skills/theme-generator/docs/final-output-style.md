# Final Output Style

Use this guidance whenever the user wants a final `<name>.css` file for a Preline-based project.

## Core rule

The deliverable is one file only: `<name>.css`.

Do not create or edit any other project files.

## What the final theme file should look like

- A standalone `<name>.css` file that can live in the project's themes folder.
- Theme activation via `data-theme="theme-<name>"` and optional `.dark`.
- Semantic tokens should prefer assigned variables after the theme palette has been mapped.

## Required conventions

- Do not assume project-specific paths other than the discovered themes directory.
- Do not assume the project already has other custom theme files.
- Do not force users to change HTML utility classes.
- Do not create or edit a shared `theme.css`, docs page, or any other file.
- Keep semantic tokens in the theme selector blocks, not inside `@theme`.
- Put any custom brand/gray palette needed for this theme inside `@theme theme-<name> inline { }` in the new theme file.
- If the repo already exposes shared aliases like `--color-primary-*` from its base theme, do not redefine them inside the custom theme file. Assign `--primary-*` directly from the theme-local palette instead.

## Variable strategy

Prefer assigned variables such as:

- `--color-primary-*`
- `--color-secondary-*`
- `--background-*`, `--foreground`, `--border`, `--surface-*`, `--muted-*`
- Tailwind palette vars like `--color-fuchsia-*`, `--color-orange-*`, `--color-neutral-*`
- shared Preline palette vars exposed by the project's base theme, if available

Allowed in the new theme file:

- theme-local palette vars like `--color-<theme-name>-*`
- theme-local gray palette vars like `--color-<theme-name>-gray-*`

But keep them inside `@theme theme-<name> inline { }` and avoid scattering raw palette references when an assigned semantic variable already exists.

Avoid in semantic, chart, and map tokens:

- raw `oklch(...)` assignments
- literal hex values

## If a unique palette is needed

Define it inside `@theme theme-<name> inline { }` in the new theme file.

Do not edit any shared/base theme file.

## Structural pattern

Use this order:

1. Header comment
2. Optional theme-scoped `@layer utilities` overrides
3. `@theme theme-<name> inline { }`
4. Light selector:
   - `:root[data-theme="theme-<name>"],`
   - `[data-theme="theme-<name>"]`
5. Dark selector:
   - `[data-theme="theme-<name>"].dark`

## Practical workflow

1. Discover the themes folder.
2. Generate one new `<name>.css` file.
3. If needed, define custom brand/gray palettes inside that file's `@theme` block.
4. Map the theme ramp by assigning `--primary-*` directly from the theme-local palette, then let shared aliases resolve from the base theme when available.
5. Keep chart and map tokens variable-based.
6. Re-run the validation checklist before returning.
