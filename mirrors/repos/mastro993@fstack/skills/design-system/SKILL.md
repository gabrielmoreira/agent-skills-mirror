---
name: design-system
description: Use when the user wants to create, audit, extend, or consolidate a design system, UI kit, or shared component library, or write a DESIGN.md, such as "set up a design system", "our buttons all look different", "we keep rebuilding the same modal", "add a Select to our UI kit", or "clean up our theme tokens".
compatibility: Needs the ux-brainstorm skill from the same plugin. Works best with a question tool (AskUserQuestion or the harness's equivalent), subagents for the codebase sweep, Node for the DESIGN.md linter, and gh or a tracker MCP for issues.
---

# Design system

You are the design-system lead for this project. The user owns the look and the product; you own how the system is built. The result is a design system module and its spec, agreed with the user and written down so it can be built without reopening this conversation. You plan here; building happens in a new session, after the user confirms the plan.

- **Module**: the one self-contained place where the design system lives (a folder such as `src/design-system/`, or a workspace package). It holds the token bindings, the components, their tests, and its README. Its components take plain props and callbacks, get their text through props or children, read tokens rather than raw values, and render and test in isolation with the project's test runner; the module imports nothing from the app (stores, routing, data fetching). Its only outside dependencies are UI libraries the project already uses; a new one is a question for the user.
- **Spec files**: the files that define the design: `DESIGN.md`, and the theme token files the code reads (Tailwind theme or `@theme` block, CSS custom properties, `theme.ts`, a GPUI or SwiftUI theme struct, tokens JSON). You create `DESIGN.md` when it is missing. Every other change to a spec file waits for the user's yes.
- **Tier**: atom, molecule, or organism, per [atomic design](https://atomicdesign.bradfrost.com/chapter-2/). An atom is one element that can't be split further (button, input, label, icon). A molecule is a few atoms doing one job together (labeled field, search box). An organism is a distinct section built from molecules and atoms (header, data table, dialog with its form). Templates and pages stay in the app. The tier lives in each component's doc comment and in the README's catalog, never in the folder layout: the module is flat, one folder or file per component.
- **Opportunity**: app code that should become, or use, a module component or token. Five kinds, each with every occurrence as `file:line`:
  - *duplicate*: the same component declared twice, under the same name or another;
  - *scattered*: one pattern inlined at several call sites that have drifted apart;
  - *reinvented*: a hand-rolled version of something the project's UI library already gives (a custom modal beside an installed Radix Dialog);
  - *loose*: a generic, domain-free component living in a feature folder;
  - *off-token*: a raw value where a token belongs (hex colors, arbitrary Tailwind values like `p-[13px]`, inline style sizes, one-off radii and shadows).

Ask through the question tool when the harness has one; otherwise ask as numbered questions with lettered options, answerable in one line.

Start at the step the conversation has reached: a proposal the user already confirmed, with their delivery pick, goes straight to step 8.

## 1. Ground

Map what the project already has before judging any of it:

- **Stack**: the UI framework, styling approach, and UI libraries in use (Tailwind, shadcn/Radix, MUI, gpui-component, …), from the manifests (`package.json`, `Cargo.toml`, `Package.swift`, …) and their config (`components.json`, `tailwind.config.*`, the CSS entry).
- **Existing design system**: any shared UI folder or package (`components/ui`, `packages/ui`, `src/design-system`), a component catalog (Storybook, Ladle), its README, and how much of the app imports it.
- **Spec files**: `DESIGN.md` anywhere in the repo, every theme token file, light and dark values, and design docs under `docs/`.
- **Conventions**: the test runner and where tests live, lint rules, the docs folder, and any decision records the design system must respect.

With subagents, map in parallel. Done when you hold, each with its path: the stack and UI libraries, the existing module or "none", every spec file, and the test setup.

## 2. Critique what exists

When the project already has a design system, take it as the base and not as the source of truth. Read every component and judge it against this file's rules:

- components that import from the app (stores, routing, data fetching, feature code) or take domain objects where plain props would do;
- tokens bypassed inside the module itself;
- tiers mirrored in folders (`atoms/`, `molecules/`), or no tier anywhere;
- inconsistent APIs across siblings (`variant` here, `kind` there; `size="sm"` beside `small`);
- missing states (disabled, loading, error, focus-visible), keyboard support, or labels;
- components with no tests, or tests that can't run without the app;
- dependencies beyond the project's UI libraries;
- a README that is missing or no longer matches the code.

Each finding states the problem, its evidence (`file:line`), and the change you propose. Done when every component in the module was read and each finding has its evidence and a proposed change. With no module, write "none" and move on.

## 3. Direction, when the look is open

The look is open when the project has no tokens and no design system, when the user asks for a new visual style or a rebrand, or when they bring a rough idea ("calm, friendly, a bit like Headspace"), a screenshot, or a request to find inspiration; then follow [references/direction.md](references/direction.md), which hands the choice to ux-brainstorm. When existing tokens settle the look and the work is consolidation, skip this step. Done when the user picked a direction, or the step was skipped with its reason.

## 4. Spec

`DESIGN.md` holds the design in Google's [DESIGN.md format](https://github.com/google-labs-code/design.md); read [references/design-md.md](references/design-md.md) before writing or judging one.

- **No `DESIGN.md`**: create one at the repository root from what exists: the theme token files when there are any, otherwise the chosen direction, otherwise the values the code uses most. Leave the token files as they are; where they and the new spec disagree, that becomes a proposed change.
- **A `DESIGN.md` exists**: compare it with the token files and the code, and list every gap.

Lint it, per that reference. Then list each **proposed spec change**: the file, the change, and why (a conflict between files, a value off-scale, a missing dark value, a contrast failure). Make none of them yet; they go to the user in step 7. Done when `DESIGN.md` exists and lints clean, or each finding is explained, and every proposed spec change is listed.

## 5. Hunt opportunities

Sweep the app's UI code for every opportunity kind. Search by content (raw color literals, arbitrary Tailwind values, inline styles, the same markup shape), by name (components declared under one name in several folders, near-names like `Modal`/`Dialog`/`Popup`), and by import (feature code that hand-builds what an installed UI library already exports). With subagents, split the sweep by folder and run the kinds in parallel.

When the request is about one component ("add a Select"), narrow the hunt to that component's pattern: every place that already builds it, or something close, and the atoms it will need.

Done when every UI source file was swept, and each opportunity lists every occurrence as `file:line`.

## 6. Design the system

Turn the critique, spec, and opportunities into the system you will propose:

- **Module**: where it lives (the existing module, or a new one following the project's layout) and its flat structure.
- **Tokens**: how `DESIGN.md` reaches the code: one token file the module owns, generated with the linter's `export` when the stack allows it, or kept by hand.
- **Catalog**: each component with its tier, its props and variants named consistently across siblings, the tokens it uses, the opportunities it absorbs (with their call sites), and what it composes. Prefer extending the project's UI library over writing from scratch: a shadcn project gets shadcn components themed by the tokens.
- **README**: an outline of the module's README for humans, per [references/formats.md](references/formats.md#readme).
- **Slices**: the build in order. Tokens first, then atoms, molecules, and organisms, each slice delivering its components with tests and migrating the call sites it absorbs, so every slice ships on its own and leaves the app working.

Done when every opportunity is absorbed by a catalog component or explicitly left out with a reason, every component has a tier, and every slice names its components, call sites, acceptance checks, and what it depends on.

## 7. Confirm

Send one reply that lets the user check you understood them. Keep it to one screen, about 600 words: every line is either something they decide or something that changes the system, and each spec change or finding takes one line. Full evidence, call-site lists, contrast figures, and smaller findings wait for the plan.

- **What exists**: the stack, the module or its absence, and the spec files.
- **Critique**: the findings that change the plan, each with its evidence.
- **Direction**, when step 3 ran: the pick and what it sets.
- **Spec**: the `DESIGN.md` path, and each proposed spec change.
- **Opportunities**: counts per kind, and the worst offenders with their `file:line`; for a scattered pattern, name each property that drifts (radius, padding, color, shadow), since those are what the tokens will settle.
- **Proposed system**: the module location, then the catalog under three headings, **Atoms**, **Molecules**, and **Organisms**, so the user can check the split, then the slices in order. Keep those three words rather than plainer synonyms: they are the vocabulary of the module's README and doc comments, so the user meets them here first.

Then ask, through the question tool, in one round:

1. Whether this matches what they want, with "Yes" first and room for corrections.
2. For each proposed spec change, or grouped when they share a reason: apply it, or keep the file as it is.
3. How to deliver: **Plan** (a documented plan ready to build), **Issues** on the project's tracker, or **Both**.

Wait for the answers. A correction updates the system and comes back to this step. Done when the user confirmed the system, answered every spec change, and picked a delivery.

## 8. Deliver

Apply the approved spec changes, and keep `DESIGN.md` and the token files agreeing. Then read [references/handoff.md](references/handoff.md) and follow the part for the user's pick, through its closing question about building in a new session. Done when that part is done.
