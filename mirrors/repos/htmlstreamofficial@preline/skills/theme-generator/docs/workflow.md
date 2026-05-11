# Workflow

Use this file as the default operating guide for the active theme skill.

## Task modes

Classify the request before doing any work:

- `preview`: generate CSS and return it without writing a project file
- `write`: create one new `<name>.css` theme file
- `validate`: review or fix an existing generated theme file

## Normalize the request

Convert natural language into the generator's small, explicit input set:

| Input | Required | Notes |
|------|----------|-------|
| `name` | yes | kebab-case theme name |
| `hue` or `primaryColor` | yes | use `primaryColor` only when user gave a brand hex |
| `style` | no | `vibrant` by default, `soft` for muted/pastel/desaturated requests |
| `useCustomDarkGray` | no | true only when user explicitly wants matching/cohesive dark neutrals |
| `tailwindGray` | no | choose `stone`, `neutral`, `zinc`, `slate`, or `gray` based on brand warmth |
| `fontSans` / `fontSerif` / `fontMono` | no | include only when requested |

Use `docs/palette-guidance.md` for hue ranges, mood mapping, contrast heuristics, and gray-family decisions.

### Natural-language interpretation

Use the user's language to infer the palette direction:

| User language | Default interpretation |
|--------------|------------------------|
| warm sunset, cozy, inviting | orange/amber primary, warm neutrals, medium contrast |
| professional, clean, SaaS | blue/indigo primary, slate or zinc neutrals |
| playful, candy, youthful | pink/purple/cyan primary, higher contrast |
| earthy, organic, calm | green/teal primary, stone neutrals |
| soft, muted, ash, dusty | `style: soft` |
| matching dark mode, cohesive dark, unified neutrals | `useCustomDarkGray: true` |

When the request is vague:

1. Make an opinionated, coherent palette choice.
2. Keep contrast readable.
3. Prefer a consistent system over a flashy but uneven palette.

Foreground rule:
- When mapping text or icon colors onto the primary brand color, choose the foreground by contrast against the generated primary states, not by hue bucket alone.
- Treat `--foreground-inverse` separately from primary foregrounds. In Preline it is reused on hardcoded vivid utility backgrounds such as red badges, so dark mode should keep it readable on saturated colors instead of tinting it into a dark neutral.
- Treat chart tokens as decorative UI tokens, not just data-series tokens. Dark mode must override any chart shades that would become too dark for gradient text, badges, or chart accents on dark surfaces.

## Discover the target directory

Use the bundled resolver instead of broad repo traversal:

```bash
node scripts/find-themes-dir.js
```

Trusted theme directories are checked in this order:

- `src/assets/css/themes/`
- `src/css/themes/`
- `src/styles/themes/`
- `assets/css/themes/`
- `styles/themes/`
- `dist/assets/css/themes/`
- `npm/preline/css/themes/`

Rules:

- Prefer source theme directories over generated outputs.
- Do not use repo-wide `find .` traversal for this task.
- If no trusted theme directory is found and the user did not provide a path, ask where the file should be written.

## Generate CSS

Use the local wrapper as the only execution entry point:

```bash
node scripts/run-theme-generator.js --name seafoam --hue 180 --style vibrant --tailwind-gray zinc --stdout
```

Write a theme file with:

```bash
node scripts/run-theme-generator.js --name seafoam --hue 180 --style vibrant --tailwind-gray zinc --output src/assets/css/themes/seafoam.css
```

Rules:

- Do not use `npx`.
- Do not interpolate raw user text into shell commands.
- Do not chain temp-file cleanup or other unrelated shell work into the command.
- Do not create or edit any project file other than the new theme file.

## Theme structure expectations

The wrapper should emit a production-style standalone `<name>.css` file:

1. Header comment
2. Optional theme-scoped `@layer utilities` overrides
3. `@theme theme-<name> inline { }`
4. Light selector
   - `:root[data-theme="theme-<name>"],`
   - `[data-theme="theme-<name>"]`
5. Dark selector
   - `[data-theme="theme-<name>"].dark`

Keep custom brand and gray palettes inside the file's `@theme` block. Keep semantic tokens in the selector blocks.

See `docs/final-output-style.md` for the final file rules and `docs/token-reference.md` only when detailed token coverage inspection is necessary.

## Dark-mode decision rule

Always generate both palettes in `@theme theme-<name> inline { }`:

- `--color-<name>-*` for the brand ramp
- `--color-<name>-gray-*` for the theme's neutral ramp

Dark-mode neutrals depend on user intent:

- Explicit matching/cohesive dark request: use the theme's custom gray palette in dark mode.
- Default path: keep light mode custom and use a Tailwind gray family in dark mode.

Primary foreground decision:
- Use the generated brand shades to determine whether white or dark text is more readable on the primary color in each mode.
- In dark mode, prefer a deeper primary step with white text when that profile remains readable; only fall back to lighter primary steps with dark text when white would fail.

Use CSS variables in semantic tokens and dark-mode overrides. Do not hardcode raw `oklch(...)` or hex values in semantic, chart, or map tokens.

## Validation focus

Before returning:

- confirm only one project file was created or edited
- confirm the theme key is `theme-<name>` everywhere
- confirm the file has full light and dark token coverage
- confirm chart and map tokens remain variable-based
- confirm dark-mode states remain readable

Use `docs/validation-checklist.md` as the final gate.

## Response shape

Match the response to the mode:

- Preview: return the CSS first, then the enable snippet if useful
- Write: return the created path, a short summary, and the enable snippet
- Validate: list findings first, then the applied or recommended fix

Enable snippet:

```html
<html data-theme="theme-<theme-name>">
```
