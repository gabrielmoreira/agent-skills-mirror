---
name: experience-ui-bundle-features-generate
description: "MUST activate when the project contains a uiBundles/*/src/ directory (React or Angular) and the user wants to add a pre-built feature — such as authentication (login, logout, protected routes, session management) or search (global search across pages and content) — instead of building it from scratch. Always run list first to see the current feature catalog, since it can include more than authentication and search. Always use this skill for installing pre-built features rather than hand-building them. DO NOT TRIGGER for Agentforce conversational client or file-upload features — use experience-ui-bundle-agentforce-client-generate and experience-ui-bundle-file-upload-generate respectively."
metadata:
  version: "1.2"
  domains: ["Experience"]
  relatedSkills: ["experience-ui-bundle-agentforce-client-generate", "experience-ui-bundle-file-upload-generate"]
  cliTools:
    - tool: ["npx"]
      semver: ">=7.0.0"
    - tool: ["npm"]
      semver: ">=7.0.0"
  accessCheck:
    - type: "license"
      value: "Experience Cloud (Customer Community / Customer Community Plus)"
    - type: "orgPref"
      value: "Sites"
---

# UI Bundle Features

Install pre-built, tested feature packages into a Salesforce UI bundle with the
`@salesforce/ui-bundle-features` CLI instead of hand-building them. This file is the
**framework-neutral workflow spine**; the framework-specific detail — example file
extensions, the files features rewrite, how a feature's entry component is mounted, and the
build command — lives in a per-framework reference under `<SKILL_DIR>/references/<framework>/`.

Always check for an existing feature before building something from scratch. The CLI is
framework-agnostic: it installs the framework-appropriate variant of each feature into the
detected bundle. Authentication and search are the most commonly used today; run
`list --verbose` for the full current catalog, since it can grow over time.

> **Ownership note:** Agentforce AI conversation clients and file-upload are owned by separate skills (`experience-ui-bundle-agentforce-client-generate`, `experience-ui-bundle-file-upload-generate`). If the catalog also lists an Agentforce or file-upload entry, do not install it from both places — confirm with the user which delivery path they want, and never install the same capability twice in one bundle.

> **Package name:** `@salesforce/ui-bundle-features` is the canonical package name. Some older templates/samples still reference the deprecated `@salesforce/ui-bundle-features-experimental` name — never use the `-experimental` suffix. If a command fails to resolve, confirm the published version with `npm view @salesforce/ui-bundle-features version` before assuming the package name is wrong.

## Step 0: Determine the framework

`<SKILL_DIR>` = the absolute path to **this skill's own directory** (the folder holding this
`SKILL.md`); resolve it from the skill path in context.

The framework is normally already decided by the calling context — passed down by the
coordinator skill that invoked this one, or stated in the user's request. Use that.

The frameworks this skill supports are exactly the reference folders under
`<SKILL_DIR>/references/`, each containing a `features.md` (so `react` →
`<SKILL_DIR>/references/react/features.md`). This is the single source of truth — adding a
framework means adding a reference folder, nothing here changes.

- **If the framework is known** — open `<SKILL_DIR>/references/<framework>/features.md` and
  keep it alongside this spine. It supplies the example extensions, the integration targets,
  the mount example, and the build command.
- **If it is unknown** (a standalone run where nobody said which) — run the deterministic
  detector on the UI bundle root before asking anyone:

  ```bash
  bash "<SKILL_DIR>/scripts/detect-framework.sh" "<path-to-uiBundles/<name>/ dir>"
  ```

  Branch on the exit code (do not parse prose):
  - `react` or `angular` (exit 0) → use that framework. **Do not ask the user** — detection is
    deterministic. Open `<SKILL_DIR>/references/<framework>/features.md`.
  - `ambiguous` (exit 2) → both frameworks present. List `<SKILL_DIR>/references/` and ask the
    user which bundle to install into. If they name a framework with no matching reference
    folder, it is not supported here — stop.
  - `unknown` (exit 3) → **no supported framework detected. Terminate.** Report that neither
    React nor Angular signals were found in the bundle, so features cannot be installed, and
    stop. Do not guess.

Throughout the steps below, `<framework>` means the folder chosen here.

## Workflow

1. **Search project code first** — check `src/` for existing implementations before installing anything. Scope searches to `src/` to avoid matching `node_modules/` or `dist/`.

2. **Search available features** — use `npx @salesforce/ui-bundle-features list` with `--search <query>` to filter by keyword. Use `--verbose` for full descriptions.

3. **Describe a feature — MANDATORY before wiring.** Run `npx @salesforce/ui-bundle-features describe <feature>` and read the feature's README via `npm view <package> readme` (using the `Package:` name from that output) before wiring it. The README is the contract: it tells you how the feature is meant to be wired — including any drop-in entry component and the file each integration example belongs in. Cross-check against the copied-in source under `describe`'s `Copy Operations` destination — that source (and its JSDoc/comments) is the version-matched truth for what's actually installed, in the detected framework's file types. Do not wire from assumptions about file names or component APIs. Skipping this is the most common reason a feature installs successfully but never actually runs.

4. **Install** — use `npx @salesforce/ui-bundle-features install <feature> --ui-bundle-dir <name>`. Key options:
   - `--dry-run` to preview changes
   - `--yes` for non-interactive mode (skips conflicts)
   - `--on-conflict error` to detect conflicts, then `--conflict-resolution <file>` to resolve them

   Install features **before** doing custom frontend/layout work in this bundle — features may rewrite the app layout and routing files (see the framework reference for their names), and installing after hand-built layout changes risks collisions.

If no matching feature is found, ask the user before building a custom implementation — a relevant feature may exist under a different name.

## Conflict Handling

In non-interactive environments, use the two-pass approach:

1. Run install with `--on-conflict error` to detect conflicts without applying them.
2. Before writing the resolution file, read `references/common/conflict-resolution-schema.json` for the allowed keys and enum values.
3. Write a resolution file at `<ui-bundle-dir>/conflict-resolution.json` (path is relative to the UI bundle directory being installed into, not the repo root). Key it by the exact paths the CLI printed as conflicts in pass 1, verbatim:
   ```json
   {
     "src/appLayout.tsx": "overwrite",
     "src/routes.tsx": "skip"
   }
   ```
   (The conflict paths are whatever the CLI printed for the detected framework — the keys above are illustrative.) Any conflicting path *not* listed defaults to `skip` — the CLI will not overwrite a file you didn't explicitly mark `overwrite`.
4. Re-run install with `--conflict-resolution <path-to-that-file>`.

## Post-install: Integrating Example Files

Features may include example files under an `__examples__/` directory (plural) showing integration patterns. These are often full, working pages with concrete names, not bare placeholder templates — in the detected framework's file types (see the framework reference). For each:

1. Read the example file to understand the pattern — treat it as a working reference implementation, not necessarily a stub.
2. Read the target file (shown in `describe` output).
3. Apply the pattern from the example into the target.
4. **CRITICAL — verify before deleting:**
   ```bash
   # Verify the build passes with the integrated pattern (build command per framework reference)
   npm run build || {
     echo "ERROR: Build failed after integration - do NOT delete __examples__/"
     exit 1
   }

   # Verify the pattern from the example is actually present in the target.
   # Adjust the grep to a key symbol/import/component from the example, over the
   # detected framework's source files (see the framework reference for a worked pattern).
   ```
   Only delete `__examples__/` after **both** the build passes and the pattern is confirmed present in the target.

If either check fails, **do NOT delete `__examples__/`** — the integration is incomplete. Fix the integration first, then re-run the verification.

## Post-install: Mount the OOTB component, don't hand-roll a parallel one

When a feature ships an integration point, the UI **must** use it rather than a parallel hand-rolled version. For features that ship an entry component, mount it (the framework reference shows the mount idiom); do **not** author a bespoke page that queries data directly. A custom results page against seed data or a raw GraphQL call bypasses the installed, tested feature, so the deployed sObject/CMS logic never runs. The only exception is when the user **explicitly** opts out and asks for a custom one — confirm that intent, don't infer it.

## Hint Placeholders

Some copy paths use `<descriptive-name>` placeholders (e.g., `<desired-page-with-search-input>`) that the CLI does not resolve. After installation, rename or relocate these files to the intended target, or integrate their patterns into an existing file. This is separate from the `__examples__/` convention above — a single copy path can use either mechanism.

## Auth Feature: Org-Side Prerequisites

Installing the authentication feature only copies files — it does not configure the org. This is framework-agnostic (pure org/metadata config). Before telling the user auth is done, flag that these org-side steps still need to happen (outside this skill's scope, but required for the feature to actually work):

- Digital Experiences (Experience Cloud) must be enabled, with Customer Community / Customer Community Plus licenses assigned to the relevant users, and Salesforce Sites enabled.
- The community and guest profiles need explicit Apex class access granted for the auth utility, login/registration, and password-reset classes — the CLI does not grant this automatically.
- Guest-profile sharing rules / org-wide defaults for any objects the auth flow touches.
- **Known limitation:** logout has a documented CSRF-handling gap (tracked as W-21253864) — call this out to the user rather than presenting logout as fully solved.

## CRITICAL: Resolve `<sfdxRoot>` After Every Install

The CLI may copy files under a literal `<sfdxRoot>` folder — an unresolved placeholder for this project's Salesforce DX metadata root (from `sfdx-project.json`'s `packageDirectories[].path`, e.g. `force-app/main/default`). Files left there are undeployable. This is framework-agnostic.

**After every install:**
```bash
find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'
```
If found, move each file to `<metadata-root>/<same-relative-subpath>` (keep `-meta.xml` sidecars attached) and delete the emptied placeholder dir(s).

**Verification:**
- [ ] Re-run `find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'` — output must be empty before proceeding.
