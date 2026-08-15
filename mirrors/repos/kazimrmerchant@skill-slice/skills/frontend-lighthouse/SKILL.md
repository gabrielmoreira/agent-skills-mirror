---
name: frontend-lighthouse
description: "Adds a portable Lighthouse CI gate: lighthouserc.cjs Core Web Vitals budgets (LCP, CLS, TBT), category floors, median-of-N runs, and GitHub Actions artifacts against the production build. Use when adding performance gates, setting CWV budgets, or debugging flaky LHCI. Not for one-off DevTools audits on a Vite/Next dev server, motion-craft review (review-animations), or raising budgets instead of fixing the report."
version: 1.0.1
category: frontend
risk: safe
source: community
source_repo: stareezy-1/frontend-architecture-skill
source_type: community
date_added: "2026-06-29"
tags: [frontend, lighthouse, performance, core-web-vitals, ci]
tools: [lighthouse, node, github-actions]
license: "MIT"
license_source: "https://github.com/stareezy-1/frontend-architecture-skill/blob/main/LICENSE"
---

## Overview

This skill describes a **CI performance gate** — a Lighthouse CI config plus a workflow — not a component library or a visual style. It pairs with the **frontend-seo** and **frontend-architecture** skills: SEO writes the metadata, Lighthouse proves it ships fast.

The goal: every pull request is **blocked unless the production build meets explicit Core Web Vitals budgets and category score floors**. Budgets live in **one** `lighthouserc.cjs`, runs are **median-of-N** so the gate doesn't flake, and the same config runs locally and in CI.

## When to Use

- Use when adding a Lighthouse CI performance gate to a web app.
- Use when setting Core Web Vitals budgets for LCP, CLS, and TBT as the lab proxy for INP.
- Use when configuring category score floors for performance, SEO, accessibility, and best practices.
- Use when debugging flaky Lighthouse runs or making reports visible as CI artifacts.

## Prerequisites

- Node.js 22 (match the repo's pinned version to avoid lockfile drift)
- pnpm (or npm/yarn)
- `@lhci/cli` installed as a dev dependency

## Procedure

### 1. Install the Lighthouse CLI

```powershell
pnpm add -D @lhci/cli
# or: npm i -D @lhci/cli
# or: yarn add -D @lhci/cli
```

### 2. Create the Lighthouse Config

Create `lighthouserc.cjs` at your app root (e.g., `apps/web/lighthouserc.cjs`). Use `.cjs` (CommonJS) so it loads without ESM/TS transpilation. Every budget must be a **named constant** with a comment explaining the threshold — never a bare number inside an assertion.

```js
/**
 * Lighthouse CI configuration — Core Web Vitals budgets for the marketing surface.
 *
 * Enforces Google's mobile "good" CWV thresholds:
 *   - Largest Contentful Paint (LCP) ≤ 2500 ms
 *   - Cumulative Layout Shift (CLS)  ≤ 0.1
 *   - Interaction to Next Paint (INP) ≤ 200 ms
 *
 * INP is a *field* metric with no direct lab audit, so in the lab we gate on
 * Total Blocking Time (TBT) — Lighthouse's recommended lab proxy — at the same
 * budget, and assert the experimental INP audit directly as a warning where the
 * build exposes it.
 *
 * Collection runs against the *production* server (build + start) on Lighthouse's
 * default mobile (Moto G4 / slow 4G) emulation.
 */

/** The fixed port the production server is started on for the audit. */
const PORT = 3100;
const BASE_URL = `http://localhost:${PORT}`;

/** Pages whose budgets are enforced in CI. */
const MARKETING_URLS = [`${BASE_URL}/`];

/**
 * Core Web Vitals budgets on mobile — Google's "good" thresholds.
 * These are the values that earn the best Lighthouse scores.
 */
const LCP_BUDGET_MS = 2500; // good
const INP_BUDGET_MS = 200; // good (TBT lab proxy)
const CLS_BUDGET = 0.1; // good

module.exports = {
  ci: {
    collect: {
      // Build is run separately in CI; here we only serve the production output.
      startServerCommand: `pnpm start --port ${PORT}`,
      startServerReadyPattern: "Ready in", // framework's "server ready" log line
      startServerReadyTimeout: 120000,
      url: MARKETING_URLS,
      // Median of multiple runs keeps the gate stable against per-run jitter.
      numberOfRuns: 3,
      settings: {
        // Default mobile emulation; opt into desktop via env for a second run.
        preset:
          process.env.LHCI_FORM_FACTOR === "desktop" ? "desktop" : undefined,
        // Only gate the categories we care about; skip PWA category noise.
        onlyCategories: [
          "performance",
          "seo",
          "accessibility",
          "best-practices",
        ],
      },
    },
    assert: {
      // Median across runs is the value compared against each budget.
      aggregationMethod: "median-run",
      assertions: {
        // --- Core Web Vitals budgets (the contract) ---------------------
        "largest-contentful-paint": [
          "error",
          { maxNumericValue: LCP_BUDGET_MS },
        ],
        "cumulative-layout-shift": ["error", { maxNumericValue: CLS_BUDGET }],
        "total-blocking-time": ["error", { maxNumericValue: INP_BUDGET_MS }],
        // Direct INP audit where the Lighthouse build exposes it (else ignored).
        "interaction-to-next-paint": [
          "warn",
          { maxNumericValue: INP_BUDGET_MS },
        ],

        // --- Category floors (target top Lighthouse scores) -------------
        "categories:performance": ["error", { minScore: 0.9 }],
        "categories:seo": ["error", { minScore: 0.95 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["error", { minScore: 0.9 }],
      },
    },
    upload: {
      // Keep reports in the CI run's filesystem; no external LHCI server.
      target: "filesystem",
      outputDir: "./.lighthouseci",
    },
  },
};
```

**Hard Rules for Config:**
- Every budget is a named constant with a unit in its name (`LCP_BUDGET_MS`) and a comment.
- `aggregationMethod: "median-run"` is non-negotiable — single-run gates flake constantly.
- `numberOfRuns` ≥ 3 (odd numbers give a clean median).
- Assert on TBT for INP in the lab; treat the experimental `interaction-to-next-paint` audit as a `warn`, not an `error` (it isn't present in every Lighthouse build).
- Keep `onlyCategories` to exactly what you gate — fewer audits, faster, less noise.

### 3. Add the npm Script

Update `package.json`:

```jsonc
{
  "scripts": {
    "lhci": "lhci autorun --config=./lighthouserc.cjs"
  }
}
```

### 4. Add the GitHub Actions Workflow

Create `.github/workflows/lighthouse.yml`. Runs on PRs that touch the app or the workflow itself. Builds the production output, runs the gate, and **always** uploads the reports (even on failure) so a red check is debuggable.

```yaml
name: Lighthouse CWV

on:
  pull_request:
    branches: [main]
    paths:
      - "apps/web/**"
      - ".github/workflows/lighthouse.yml"

permissions:
  contents: read

jobs:
  lighthouse:
    name: Lighthouse CWV (marketing pages)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4 # version comes from root package.json packageManager

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - name: Install dependencies
        working-directory: .
        run: pnpm install --frozen-lockfile

      - name: Build web app
        run: pnpm build

      # build + start the production server, run Lighthouse on mobile emulation,
      # fail the job if any budget in lighthouserc.cjs is exceeded.
      - name: Run Lighthouse CI
        run: pnpm lhci

      - name: Upload Lighthouse reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: lighthouse-reports
          path: apps/web/.lighthouseci
          if-no-files-found: ignore
```

**Hard Rules for Workflow:**
- Trigger on the app path **and** the workflow file so config changes are self-testing.
- `if: always()` on the upload step — you need the report most when the gate fails.
- Gate on the **production** build (`pnpm build` then the `start` server in `collect`).
- Match the CI Node/pnpm versions to the repo's pinned versions to avoid lockfile drift.

### 5. Framework Adapters

The config is framework-neutral except `startServerCommand` and `startServerReadyPattern`.

| Framework     | `startServerCommand`                                              | `startServerReadyPattern`                   |
| ------------- | ----------------------------------------------------------------- | ------------------------------------------- |
| **Next.js**   | `pnpm start --port 3100` (after `next build`)                     | `"Ready in"`                                |
| **Remix**     | `pnpm start` (serve the built app)                                | server's listening log line                 |
| **Astro**     | `node ./dist/server/entry.mjs` (SSR) or `npx serve dist` (static) | the adapter's ready line / serve's URL line |
| **SvelteKit** | `node build` (node adapter)                                       | `"Listening on"`                            |
| **Vite SPA**  | `npx vite preview --port 3100`                                    | `"Local:"`                                  |

For purely static output you can skip the server and point `collect.staticDistDir` at the build folder instead of `startServerCommand` — Lighthouse serves it internally.

## Pitfalls

- **Gating the dev server:** Dev-server numbers are meaningless for a budget. Always run against `build` + `start`.
- **Single-run flakiness:** Single-run gates flake constantly. `aggregationMethod: "median-run"` with `numberOfRuns` ≥ 3 is non-negotiable.
- **`interaction-to-next-paint` errors:** It should be `warn`, not `error`; the audit is missing in some Lighthouse versions.
- **"server not ready" timeout:** Fix `startServerReadyPattern` to match the framework's actual ready log, and raise `startServerReadyTimeout`.
- **Real regressions masked by budget bumps:** Open the uploaded report artifact, read the failed audit's "Opportunities"/"Diagnostics", fix the cause (oversized image, render-blocking JS, layout shift from unsized media) — don't just bump the budget. Start strict and only loosen with a recorded reason.
- **Desktop vs mobile divergence:** Run both form factors; mobile is the stricter gate and should be the default.

## Verification

Run the gate locally to reproduce exactly what CI does before opening a PR.

**Mobile (default):**
```powershell
pnpm build
pnpm lhci
```

**Desktop form factor (Windows PowerShell):**
```powershell
$env:LHCI_FORM_FACTOR="desktop"; pnpm build
$env:LHCI_FORM_FACTOR="desktop"; pnpm lhci
```

**Conventions Checklist (enforce in review):**
- [ ] All budgets are named constants with units and comments — no magic numbers in assertions.
- [ ] Gate runs against the **production** build, never the dev server.
- [ ] `aggregationMethod: "median-run"` with `numberOfRuns` ≥ 3.
- [ ] CWV budgets at Google "good" thresholds (LCP ≤ 2500, TBT ≤ 200, CLS ≤ 0.1).
- [ ] INP gated via TBT (`error`); experimental INP audit is `warn`.
- [ ] Category floors set as `error` (perf ≥ 0.9, SEO/a11y ≥ 0.95, best-practices ≥ 0.9).
- [ ] `onlyCategories` lists exactly the gated categories.
- [ ] CI triggers on the app path **and** the workflow file; reports upload with `if: always()`.
- [ ] Local `pnpm lhci` reproduces the CI run.
- [ ] Budgets are tightened over time, loosened only with a recorded reason.
