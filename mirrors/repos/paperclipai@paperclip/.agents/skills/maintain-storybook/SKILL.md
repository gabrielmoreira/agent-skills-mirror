---
name: maintain-storybook
description: Keep Paperclip stories and their downstream catalog aligned with the feature map and production UI. Use to reconcile story drift, classify prototypes, update fixtures, or maintain feature coverage.
---

# Maintain Storybook

Read the [Storybook catalog contract](../../../maps/storybook-map/README.md),
the relevant [feature recipes](../../../maps/feature-map/README.md), and
[DESIGN.md](../../../DESIGN.md). The feature map is an upstream input. This skill
owns stories, their fixtures/support, and `maps/storybook-map/`; it does not edit
the feature or agent-access maps. Report upstream drift to
`maintain-verification-skill` with source evidence.

## Reconcile the requested scope

For a feature/change, follow its capability IDs to catalog entries and shared
dependencies. For a full inventory, account for every configured story file,
including historical examples. Start with `node scripts/storybook-catalog.mjs`.
Record the source revision and whether the pass covers source, rendering,
interactions, or visual comparisons. Inventory completeness is not behavioral
coverage. Do not expand a targeted maintenance request into an all-product audit.

Compare each affected story's rendered subject, props, fixture responses, actions,
and assertions with the production implementation and recipe. Follow imported
wrappers: a production Button inside a locally recreated page does not make that
page a production-component story. A real production page using mocked APIs is
valid isolation; record component provenance and data simulation separately.
Inspect mock methods/paths, payload shapes, errors, identity, gates, and reset
behavior. An API method returning success without the relevant state transition
can hide drift. Do not replace errors with generic successful mocks to pass.

Prefer mounting the shipped subject and mocking its external boundary. Retain
local layout wrappers and fixture data when they serve that isolation. Replace a
duplicate product implementation only when the current component expresses the
same scenario without losing the original purpose. Production bugs and larger
redesigns are separate findings, not reasons to rewrite expected behavior.

Classify current examples, proposals, historical explorations, and unresolved
cases explicitly. Use `unreviewed` when evidence does not establish parity.
Retain useful superseded work with its rationale and replacement reference;
do not delete a story merely because it is old, mocked, or duplicated by name.
Record mixed suites honestly and split them only when that improves review.

## Preserve identity and keep the index useful

Assign existing stable `area/capability` references, with one primary reference
and optional related references. Foundations and unmapped proposals need explicit
reasons rather than invented capabilities. Cross-cutting stories have one source
and several references. Do not count historical/proposed stories as current
feature coverage.

Preserve story exports and IDs. Before moves/title changes, capture the existing
built `index.json`; use explicit meta IDs when needed and compare IDs afterward.
Place stories under `ui/storybook/stories/<primary-feature-area>/`. Use the feature
map's section and feature names as their sidebar prefix; keep useful scenario
groupings beneath that prefix. Put shared fixture modules in `ui/storybook/support/`.
Keep the catalog's `stableId` equal to the explicit CSF meta ID even when the title
changes. Unmapped component examples belong under Foundations; the catalog guide
belongs under Overview. The checker verifies these conventions.
Keep review links and snapshot names working. Prefer classification/index fixes
before bulk directory moves. Record every directly rendered production subject in
the catalog's review sources, including relative imports and primitives when they
are the demonstrated subject. Do not cap the number of source references.
Update review fingerprints only after inspecting the changed source; do not refresh hashes merely
to silence drift checks.

Update the catalog and run `node scripts/storybook-catalog.mjs --write` to refresh
its generated index, then run the checker without flags. The script validates
inventory/references/review fingerprints, not semantic parity or runtime health.
Use `review-storybook` for affected rendering and interactions. Reuse the existing
Storybook/Playwright tools; add no separate launcher, runtime, or baseline system.
Do not accept new screenshot baselines as part of a catalog cleanup.

Report what was corrected, retained, and still needs review, naming exact files
and capabilities. Keep source-only results separate from executed results and
name blocked checks. A full pass must not hide unreviewed stories or claim that
fixture interactions establish production API, permission, or provider behavior.
