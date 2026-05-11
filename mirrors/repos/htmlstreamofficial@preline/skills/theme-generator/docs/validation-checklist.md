# Validation checklist (must self-check before returning)

## Final source style
- [ ] Only one project file is created or edited: `<name>.css`
- [ ] The final file is a production-style `<name>.css` file
- [ ] `@theme theme-<name> inline { }` is present
- [ ] Any custom brand/gray palette lives inside `@theme theme-<name> inline { }` in the new theme file
- [ ] Semantic tokens prefer assigned vars such as `--color-primary-*`, `--background-*`, `--foreground`, `--border`, `--surface-*`, or shared palette vars when available
- [ ] The custom theme does not redefine shared aliases like `--color-primary-*` inside `@theme` when the repo base theme already owns them
- [ ] No raw `oklch(...)` or literal hex values remain in semantic, chart, or map token assignments in the final theme file

## Structure
- [ ] Theme key consistent: `theme-<name>` everywhere
- [ ] Light selector uses `:root[data-theme=...]`, `[data-theme=...]`
- [ ] Dark selector is `[data-theme="theme-<name>"].dark`
- [ ] Semantic token definitions are in selector blocks (NOT inside @theme block)
- [ ] No requirement to change HTML utility classes (only `data-theme`, optional `.dark`)

## Palette strategy
- [ ] Primary ramp maps `--primary-*` directly to theme-local palette vars
- [ ] Neutral/background tokens use assigned palette vars
- [ ] If a new custom palette is needed, it is declared inside the new theme file's `@theme` block, not by editing another file

## Token coverage
- [ ] Full coverage present across global tokens, states, and major component groups
- [ ] CSS syntax valid (balanced braces, no broken comments)
- [ ] If behavior overrides exist, they are theme-scoped only
- [ ] Chart/map tokens use variable references matching shipped theme patterns

## Dark mode consistency
- [ ] Dark mode uses CSS variables (`var(--color-*)`) not hardcoded color literals
- [ ] Dark mode uses one consistent grayscale family unless there is a deliberate, reference-backed reason not to
- [ ] Hover/focus/active states remain readable and distinguishable
- [ ] `--foreground-inverse` remains readable on vivid utility colors in dark mode (for example red badges/chips)
- [ ] Dark-mode chart/decorative tokens avoid very deep brand steps when those tokens are used in gradient text or accent UI
