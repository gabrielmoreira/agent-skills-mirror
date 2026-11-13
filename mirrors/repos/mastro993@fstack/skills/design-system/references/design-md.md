# DESIGN.md

Google's [DESIGN.md format](https://github.com/google-labs-code/design.md) (format version `alpha`, CLI `@google/design.md`, checked against 0.4.0) describes a design system in one file: YAML front matter holds the tokens, which are normative, and Markdown sections explain how to apply them. When the project pins a newer CLI, read its `spec` output before trusting this summary.

## Tokens

```yaml
---
version: alpha
name: Acme Dashboard
description: Dense, calm operations UI.
colors:
  primary: "#2F5BEA"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#16181D"
  border: "#E3E5EA"
  danger: "#C8372D"
  primary-dark: "#7C9BFF"
  surface-dark: "#121417"
  on-surface-dark: "#ECEEF2"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.45
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-primary-hover:
    backgroundColor: "#2549C4"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: 8px 16px
---
```

- **Groups**: `colors`, `typography`, `rounded`, `spacing`, `components`, plus `version`, `name`, `description`, and `omitted` (sections left out on purpose, as names or `{section, reason}`).
- **Values**: a color is any CSS color; a dimension is a number with `px`, `em`, or `rem`; `spacing` also takes plain numbers (column counts); `rounded` takes dimensions only.
- **Typography**: `fontFamily`, `fontSize`, `fontWeight` (a number), `lineHeight` (a unitless multiplier, preferred, or a dimension), `letterSpacing`, `fontFeature`, `fontVariation`. Typical systems have 9 to 15 levels (headline, title, body, label, caption).
- **Names**: lowercase kebab-case. Scale levels are descriptive (`xs`, `sm`, `md`, `lg`, `xl`, `full`). Color roles follow the Material pattern: a role and its `on-` pair (`primary` / `on-primary`, `surface` / `on-surface`).
- **References**: `"{colors.primary}"`, `"{rounded.md}"`: a dot path in braces, quoted.
- **Components**: one key per component and variant, with `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. States are sibling keys: `button-primary-hover`, `button-primary-active`, `button-primary-disabled`. These describe the design; the module's code implements it.

**Dark mode**: the format has no modes. Give each color that changes in dark mode a sibling named `<role>-dark`, and say so in the Colors section. The linter accepts these names, but `export` emits them as plain variables (`--color-surface-dark`), so the module's token file maps them into the dark theme by hand.

## Sections

`##` sections, every one optional, in this order when present (the alias in brackets is also accepted):

1. **Overview** [Brand & Style]: the product's personality, its audience, the feeling the UI should give.
2. **Colors**: each role, what it is for, and where it must not be used.
3. **Typography**: the levels and when to use each.
4. **Layout** [Layout & Spacing]: the grid or layout model and the spacing rhythm.
5. **Elevation & Depth** [Elevation]: how hierarchy shows (shadows with their blur, spread, and color; or borders and contrast in a flat design). No token group exists for it; specify it here.
6. **Shapes**: the radius language.
7. **Components**: guidance per component type: buttons, inputs, chips, lists, tooltips, checkboxes, radios, dialogs.
8. **Do's and Don'ts**: guardrails and common mistakes.

Unknown headings are kept, so a project may add its own (Motion, Iconography, Voice). A duplicate heading or a duplicate top-level YAML key makes the file invalid.

## Writing one from the code

1. Take values from the theme token files first: they are what the code already means. Without them, count the literals the code uses (colors, font sizes, paddings, radii, shadows) and keep the clusters that recur; one-offs become off-token opportunities, not tokens.
2. Snap near-duplicates to one value (`#2F5BEA` and `#2F5BEB`; `15px` beside a 4px scale) and record each snap as a proposed change for the code.
3. Name by role, not by hue: `danger`, not `red-600`. Keep the project's own names when the token files already use role names.
4. Fill `components` for the atoms and molecules the system proposes, referencing tokens rather than raw values.
5. Write the prose sections from what the code and the direction show; leave out what you can't support and list it under `omitted`.

## Linting

With Node available and the harness allowing it, run `npx -y @google/design.md@0.4.0 lint DESIGN.md`: it prints JSON `findings` (each with `severity`, `path`, `message`, `rule`) and a `summary`, and exits 1 on any error. Without it, check these rules by hand:

| Rule | Severity | Check |
| --- | --- | --- |
| `broken-ref` | error | Every `{…}` reference resolves, none is circular, and components use only known properties. |
| `contrast-ratio` | warning | Each component's `backgroundColor`/`textColor` pair reaches WCAG AA, 4.5:1. |
| `missing-primary` | warning | Colors exist but no `primary`. |
| `missing-typography` | warning | Colors exist but no typography. |
| `orphaned-tokens` | warning | A color no component references. |
| `section-order` | warning | Sections out of the order above. |
| `unknown-key` | warning | A top-level key that looks like a typo (`colours`). |
| `token-like-ignored` | warning | An unknown top-level key holding token-like values, which export silently drops. |

Clean means no errors. `orphaned-tokens` warnings for `-dark` colors and for roles that only text or borders use (`muted`, `border`) are expected; list them as explained rather than inventing components to silence them. Fix every other warning or explain it.

`npx -y @google/design.md@0.4.0 export --format <fmt> DESIGN.md` emits the tokens for code: `css-tailwind` (a Tailwind v4 `@theme` block: `--color-*`, `--radius-*`, `--spacing-*`, `--text-*`, `--font-*`), `json-tailwind` (Tailwind v3 `theme.extend`), `css-vars` (plain CSS custom properties), or `dtcg` (W3C design tokens JSON, for other stacks). `npx -y @google/design.md@0.4.0 diff <before> <after>` lists added, removed, and modified tokens per group, and exits 1 when the new file lints worse: useful in review.
