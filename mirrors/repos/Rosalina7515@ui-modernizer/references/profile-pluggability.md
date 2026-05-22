# Pluggable style profiles

Style profiles are first-class extensions to ui-modernizer. Anyone can:
1. **Use** a built-in profile (`modernize this UI like Linear`).
2. **Use** a local custom profile (`modernize this UI using ./my-brand.md`).
3. **Contribute** a new built-in profile (one PR with a single Markdown file).

## 1 · How the modernizer resolves a profile name

When the user says *"modernize this UI like X"*:

| X looks like | Resolution |
|---|---|
| A bare slug (e.g. `linear`, `notion`) | Load `references/style-references/<slug>.md` |
| A path containing `/` or ending `.md` | Treat as a local file path; validate via `scripts/validate-profile.mjs`; load if ok |
| Anything else | Fall back to "default blend" (no specific profile) |

## 2 · The four-step profile workflow inside the Skill

1. **Optional:** if the user has not picked a style, run `node scripts/list-profiles.mjs --pretty` and show the list so they can choose.
2. **Resolve** the profile path per the table above.
3. **Validate** (always — even for built-ins): `node scripts/validate-profile.mjs <path>`. Refuse to continue if errors > 0.
4. **Apply**: read the profile's `## Tokens`, `## Patterns`, `## Don'ts` sections; let them override the defaults from `design-system-2026.md`. Profile's `## Don'ts` is **strict** — never violate.

## 3 · Override hierarchy

```
brand color (detect-brand.mjs)
   ↓ override
profile tokens (e.g. linear.md "accent: bg-[#5e6ad2]")
   ↓ override
design-system-2026.md default (indigo / zinc)
```

If a detected brand color conflicts with a profile's accent: **brand color wins** (the user's actual brand identity > the chosen aesthetic flavor). Note the conflict in the report.

## 4 · How to contribute a profile (≤ 10 min)

1. Copy `references/style-references/notion.md` as a starting template.
2. Edit frontmatter (`name` must match the filename).
3. Fill in `## Tokens`, `## Patterns`, `## Don'ts`.
4. Run `node scripts/validate-profile.mjs references/style-references/<your>.md` — must exit 0.
5. Open a PR. CI will re-run validation.

## 5 · Things the spec deliberately leaves open

- **Color format** — hex, oklch, rgb, or `bg-zinc-*` Tailwind names all OK.
- **Length** — minimum 1 button + 1 card + 1 input in `## Patterns`. Up to you to go further.
- **Brand color injection** — optional `## Brand-color override` section if your profile has a hard-coded accent that should yield to detected brand colors.
