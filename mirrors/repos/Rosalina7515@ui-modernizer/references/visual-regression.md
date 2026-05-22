# Visual regression (v0.6+)

Visual regression is ui-modernizer's safety net for **accidental** visual breakage. The modernization run captures a structural + style snapshot **before** any edit, then re-captures **after**, and diffs the two.

The diff produces a `Risks` report — never auto-reverts anything. The user decides which changes are intentional ("yes I wanted to delete that button") and which are accidents.

## 1 · What gets captured

For every visible element on every detected route, we record:

- **Path** — stable CSS-path-like selector (`html>body>main[0]>section[0]>button[0]`) — lets us match the same element before and after.
- **Tag** — e.g. `button`, `h1`, `div`.
- **Role** — `getAttribute('role')`.
- **AriaLabeled** — whether `aria-label` or `aria-labelledby` is set.
- **Text** — first 40 chars (truncated, whitespace collapsed).
- **Style** (computed) — color, background, font-size, font-weight, line-height, padding (4-sided), border-radius, display, opacity.

Skipped: `<script>`, `<style>`, `<noscript>`, `<svg>` internals, `display:none`, `visibility:hidden`.
Capped: 5000 elements per page (more than enough for ~99% of pages).

## 2 · Risk categories

Every finding is one of three severities:

### 🔴 High — likely a real problem

| Kind | Trigger |
|---|---|
| `missing-element` | An interactive element (`button`/`a`/`input`/`form`/`label`) or an aria-labeled element existed before, gone after |
| `role-changed` (role lost) | `role="button"` → `(none)`, etc. |
| `aria-lost` | aria-label / aria-labelledby was present, now missing |
| `contrast-regression` | Text contrast dropped below WCAG AA (4.5:1) |

### 🟡 Medium — worth a glance

| Kind | Trigger |
|---|---|
| `missing-element` (non-interactive) | A non-interactive element disappeared without an aria label |
| `tag-changed` | An element's tag changed (`<div>` → `<section>`, etc.) |
| `role-changed` (role added) | `(none)` → `role="button"` (intentional usually, but worth a glance) |
| `contrast-drop` | Text contrast dropped notably but still above AA |
| `font-size-shrunk` | Font size shrunk by > 20% |

### 🔵 Info — almost always intentional

| Kind | Trigger |
|---|---|
| `added-element` | New element appeared (modernizer often adds wrapper divs — usually fine) |
| `color-shifted` | Color or background shifted on a heading or large text (the modernization itself does this — visible here so the user can sanity-check) |

## 3 · How to read the report

`report.md` will contain a new `## Risks` section after modernization. Structure:

```markdown
## ⚠️ Risks

> Visual regression detected the following deltas. Verify each one.

### Route `/`  — 1 high · 2 medium · 5 info

🔴 **HIGH** · `html>body>main[0]>nav[0]>button[2]` — button with aria label disappeared
   "Sign in"

🟡 **MEDIUM** · `html>body>main[0]>h1[0]` — font-size shrunk: 36px → 28px (-22%)

🔵 INFO · `html>body>main[0]>h1[0]` — color: rgb(17, 24, 39) → rgb(24, 24, 27)
```

For each route, totals are shown at the top so users can decide whether to investigate.

## 4 · When to act on a risk

- **Every 🔴 HIGH** should be inspected before considering the modernization done. Did the user mean to remove that button? Did the aria-label intentionally move?
- **🟡 MEDIUM** is typically inspected if you care about accessibility / detail.
- **🔵 INFO** is usually just FYI — the modernizer **does** shift colors and add wrappers intentionally, so this section is data, not a warning.

## 5 · Limitations

- **Requires Playwright + a working `npm run dev`.** Without those, the regression step is skipped (modernization still runs; report omits the Risks section).
- **Static routes only.** Routes requiring auth, dynamic params, or POST forms aren't visited automatically — pass them via `--routes` if you want them covered.
- **Single viewport (1440×900).** Responsive regressions at other widths aren't caught in MVP.
- **No interaction.** Hover / focus / open-state styles aren't snapshotted — only initial render.

These are honest gaps. v1.0+ may close some of them; for v0.6 the goal is "good signal, low false-positive rate, optional".

## 6 · Performance

Snapshot size on a typical page: ~500 KB JSON. On a 10-route project, before+after snapshots take ~10 MB disk. They live in `.ui-modernizer/snapshots/` and are ignored by git (the `.gitignore` covers `.ui-modernizer`).

Cleanup: delete `.ui-modernizer/` after you're satisfied with the run.
