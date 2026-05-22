# `.ui-modernizer.json` — project-level config (v0.8+)

Drop a `.ui-modernizer.json` at the root of your project to encode team-level defaults:
which profile to use, which files to ignore, whether to enforce strictness, etc.

Loaded automatically by the Skill on Step 1, and by `scripts/dry-run.mjs` for CI previews.

## 1 · Minimal example

```json
{
  "profile": "linear",
  "maxFiles": 40
}
```

That's it. Everything else uses sane defaults.

## 2 · Full schema

```json
{
  "profile": "linear",                     // built-in slug or path to a local .md profile
  "brand": {
    "classPrefix": "brand"                 // overrides detect-brand.mjs auto-detection
  },
  "ignore": [
    "src/legacy/**",
    "**/*.test.tsx",
    "**/*.stories.tsx"
  ],
  "maxFiles": 30,                          // hard cap on files per run
  "strict": false,                         // refuse to run if any file is skipped (or fail CI on candidates)
  "screenshot": {
    "routes": ["/", "/dashboard", "/settings"],
    "skip": false                          // disable v0.6 visual regression entirely
  },
  "substitution": {
    "enabled": false,                      // v0.5 opt-in still required; this is the default
    "components": ["button", "input", "badge"],
    "skipIfNoComponentsJson": true
  },
  "ast": {
    "required": false                      // if true, refuse to run without @babel/parser
  }
}
```

## 3 · Field reference

### `profile` (string, default: `null`)

- Built-in slug: `"linear" | "vercel" | "stripe" | "shadcn" | "notion" | "raycast" | "apple"`.
- Local file: any path ending `.md` or containing `/`, e.g. `"./design/our-brand.md"`.
- `null` = default blend (no specific aesthetic).

### `brand` (object, default: `null`)

If set, **overrides** `detect-brand.mjs` auto-detection. Use when your project's color scale isn't named conventionally or you want the modernizer to always use a specific accent.

```json
{ "brand": { "classPrefix": "primary" } }
```

`classPrefix` must be one of: `brand`, `primary`, `accent`, `indigo`.

### `ignore` (string[], default: standard exclusions)

Glob patterns. Files matching any pattern are skipped. `**`, `*`, and `/` are supported. The defaults already cover `node_modules`, `.next`, `.nuxt`, `.svelte-kit`, `.git`, `dist`, `build`, and `.ui-modernizer*` — your `ignore` is *added* to these, not replacing them.

### `maxFiles` (integer, default: `30`)

Hard cap. The modernizer plans up to this many files; extras are listed in the report but not touched. Increase for big monorepos, decrease for tight PRs.

### `strict` (boolean, default: `false`)

Two effects:
- During **modernization**: refuses to start if any UI file would be skipped (due to glob, parse failure, or unrecognized extension). Forces you to make scope decisions explicit.
- During **dry-run**: equivalent to passing `--ci`, exits with code 1 if any stale patterns are found. Good for `pre-commit` and CI.

### `screenshot` (object)

Controls v0.6 visual regression.

- `routes`: array of paths to capture, default `["/"]`. Use this for multi-route apps.
- `skip`: `true` disables visual regression entirely (saves time when you don't need it).

### `substitution` (object)

Controls v0.5 component substitution. Note: substitution still requires the user to opt-in via their request phrasing (`"and use shadcn"`). This block configures what happens *when* opt-in is given.

- `enabled`: ignored in v0.8 (opt-in is via request phrasing). Reserved for future "always-on substitution" mode.
- `components`: which shadcn primitives are eligible for substitution. Default: all 7. Useful for restricting (e.g. team only wants `<Button>`, not `<Card>`).
- `skipIfNoComponentsJson`: if `true` (default), substitution is skipped when `components.json` is missing instead of running `shadcn init` interactively.

### `ast` (object)

- `required`: if `true`, refuse to run when `@babel/parser` isn't installed. Recommended for CI.

## 4 · Validate your config

```bash
node scripts/load-config.mjs --pretty
```

Output:
```
ui-modernizer config ✓
  source:    .ui-modernizer.json
  profile:   linear
  brand:     (auto-detect)
  maxFiles:  40
  strict:    false
  ignore:    5 glob(s)
  substitution: disabled
```

Or check via the Skill: just ask Claude "show my ui-modernizer config".

## 5 · Common recipes

### "I only want to modernize a specific folder"
```json
{
  "ignore": ["src/**", "!src/components/**"]
}
```

> Note: this naive ignore implementation doesn't support negation (`!`). To restrict to a subtree, list everything *else* as ignored. v0.9 may add proper negation.

### "Stop CI from merging un-modernized code"
```json
{ "strict": true }
```
Then in `.github/workflows/ci.yml`:
```yaml
- name: ui-modernizer dry-run
  run: node node_modules/ui-modernizer/scripts/dry-run.mjs --ci
```

(Or installed via `npx ui-modernizer --project` to put scripts at `.claude/skills/ui-modernizer/scripts/`.)

### "Use our brand purple, not indigo"
First make sure your `tailwind.config` defines a `brand` (or `primary`) palette, then:
```json
{ "brand": { "classPrefix": "brand" } }
```

### "Only substitute Button and Input, never Card"
```json
{
  "substitution": {
    "components": ["button", "input", "textarea", "label"]
  }
}
```
