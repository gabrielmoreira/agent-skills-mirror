# 100-Line Design Contract

The `≤100 lines` lint rule enforced by `scripts/lint.js` is a **design
contract**, not a content budget. It encodes a single principle:

> **One file = one focused unit of responsibility.**
> When a file needs more than 100 lines to express its responsibility fully,
> that is a design signal — the responsibility should be decomposed into
> linked units.

## The Core Rule: Split, Never Compress

**Wrong response** when you hit the limit:

- Shrink explanations into one-liners.
- Remove examples or rationale.
- Combine unrelated sections to save space.
- Use abbreviations or terse "see X" references instead of writing the content.

**Correct response**:

- Keep every line of content.
- Create a new companion file for the overflow.
- Link the companion from the primary file with a short reference.
- Name the companion clearly so its scope is obvious at a glance.

The result is a suite of small, focused files — each readable in isolation,
linked together for full coverage. This is the same principle that applies to
code: a 500-line module should be split into focused helpers, not compressed.

## Why 100 Lines?

One hundred lines is the largest amount of content a reader (human or LLM)
can hold in working memory as a coherent unit. Files within this bound tend to:

- Have a single clear purpose.
- Be fully readable in one scroll without context loss.
- Be independently testable or verifiable.
- Minimize merge conflicts when edited in parallel.

Files that exceed it tend to accumulate multiple concerns, grow without
discipline, and become harder to reason about over time.

The threshold is _enforced early_ so the design reflex (split responsibility)
becomes automatic before the problem compounds.

## Split Patterns by File Type

### Markdown Documentation

A markdown doc hits the limit when it tries to be both a navigation hub and a
deep reference at the same time. Split by _purpose_:

```
primary-doc.md          ← nav/overview: index, quick-start, key links (~40–60 lines)
primary-doc-detail.md   ← deep reference: procedures, schemas, examples
primary-doc-advanced.md ← advanced topics, edge cases, troubleshooting
```

**Naming conventions:**

| Suffix           | Purpose                                    |
| ---------------- | ------------------------------------------ |
| `-detail.md`     | Deep reference, schemas, examples          |
| `-operations.md` | Procedures, commands, runbooks             |
| `-advanced.md`   | Edge cases, configuration, troubleshooting |
| `-typology.md`   | Taxonomy, categorization, type definitions |
| `-governance.md` | Policies, contracts, role rules            |
| `-workflow.md`   | Step-by-step process descriptions          |

**Linking pattern** in the primary file:

```markdown
For operational procedures, see [WIKI-operations.md](../../wiki/WIKI-operations.md).
For taxonomy and typology, see [WIKI-typology.md](../../wiki/WIKI-typology.md).
```

**Do not** consolidate all links into a compressed one-liner. Each link should
appear on its own line with a brief description of what the companion covers.

### JavaScript / TypeScript Modules

A JS file hits the limit when it mixes initialization, business logic, and
helpers in one scope. Extract by _responsibility layer_:

```
app.js              ← entry point: imports, setup, event wiring (~40–60 lines)
app-actions.js      ← user action handlers
app-state.js        ← state management
utils/render.js     ← pure render helpers
utils/api.js        ← API fetch helpers
```

**Extraction signals:**

- A function that is only called by one other function — extract to a util.
- A group of related constants — extract to a constants module.
- A class that has grown beyond one responsibility — split by concern.
- Event registration and handler implementation mixed together — separate them.

**Linking pattern:**

```javascript
// app.js
const { renderPanel } = require('./utils/render');
const { fetchMetrics } = require('./utils/api');
```

### CSS Files

A CSS file hits the limit when it mixes component rules, layout, and global
utilities. Extract by _component boundary_:

```
app.css             ← global reset, variables, base typography
nav.css             ← navigation component
baton.css           ← baton-flow component
views.css           ← view-level layout
context.css         ← context panel component
```

Each stylesheet covers exactly one component or concern. Import order in
`index.html` (or equivalent entry point) documents the composition.

### HTML Files

An HTML file hits the limit when it contains long repetitive markup, inline
styles, or inline scripts. Extract by _section_:

- Move repeated structures to template literals in JS.
- Move inline scripts to `*.js` files.
- Move inline styles to `*.css` files.
- Decompose page sections into clearly commented blocks with `<!-- SECTION -->`.

If the framework supports it, extract partials or components (e.g., Web
Components with `<template>` elements, or JS-rendered HTML fragments).

### Shell Scripts

A shell script hits the limit when it mixes orchestration, setup, and helper
logic in one file. Extract by _lifecycle phase_:

```
deploy.sh           ← entry point: argument parsing, phase dispatch
lib/deploy-sync.sh  ← sync subroutines (sourced by deploy.sh)
lib/deploy-hooks.sh ← hook installation subroutines
```

**Linking pattern:**

```bash
#!/usr/bin/env bash
# shellcheck source=lib/deploy-sync.sh
source "$(dirname "$0")/lib/deploy-sync.sh"
```

## SKILL.md Files

Skills live in `skills/` which is lint-exempt (skills have their own governance).
However, the split-and-link pattern still applies as best practice:

```
SKILL.md            ← overview, invocation, quick-reference (~40–60 lines)
SKILL-detail.md     ← full instruction body, examples, edge cases
SKILL-schema.md     ← data schemas, required fields, response formats
```

## Lint-Exempt Paths

The following paths are exempt from the 100-line limit because they hold
content that grows by design and cannot be decomposed further:

| Path              | Reason                                        |
| ----------------- | --------------------------------------------- |
| `scripts/global/` | Governance utilities; complex logic by design |
| `scripts/wiki/`   | Wiki pipeline scripts                         |
| `instructions/`   | AI runtime instructions; grow with governance |
| `research/`       | Living research docs; no fixed scope          |
| `docs/howto/`     | This file and other deep-dive how-tos         |
| `raw/`            | Source material; not edited after placement   |
| `planning/`       | Planning docs; no fixed scope                 |
| `wiki/wisdom/`    | Wiki knowledge base; grows with ingests       |
| `wiki/code/`      | Code symbol maps; generated                   |
| `wiki/work-log/`  | Ticket/PR mirrors; generated                  |
| `tests/`          | Test files; complexity grows with coverage    |
| `skills/`         | Skill files; governed separately              |
| `hooks/`          | Hook scripts; complex by design               |

**Specific exempt files** (grow by design regardless of location):

`CHANGELOG.md`, `README.md`, `package.json`, `index.md`, `log.md`,
`team-model-signatures.json`, `orchestrator-governance-parity.json`,
`claude-code-settings.schema.json`, `governance-decision-policy.json`

If a new file grows by design and cannot be split (e.g., a JSON catalog that
is appended to programmatically), add it to `IGNORE_FILES` in `scripts/lint.js`
with a comment explaining why it is exempt.

## Applying This During Development

### When implementing a feature

1. **Start with a small file.** If you expect the implementation to need more
   than 100 lines, design the module boundary _before_ writing the code.
2. **Split at natural seams.** Identify the responsibility boundary (setup vs.
   logic vs. output), then make that the file boundary.
3. **Link explicitly.** Every companion file should be reachable from the
   primary file within 1–2 clicks/reads. Do not orphan companions.

### When the lint gate fires during review

The CI `lint-required` check enforces this contract on every PR. If it fires:

1. **Do not compress content.** Never shorten descriptions, remove examples,
   or collapse multiple concerns into a one-liner to make the count fit.
2. **Identify the responsibility split.** Ask: "What is this file's _one_
   job? What content belongs in a companion?"
3. **Create the companion.** Follow the naming conventions above.
4. **Update the primary file** to link to the companion and trim only the
   content that has _moved_ (not content that was merely _redundant_).

### For AI agents

When an AI agent receives a lint violation:

```
❌ docs/foo.md: 112 lines (limit 100)
   → Split into linked files — do not compress content.
   → Guide: docs/howto/100-line-design-contract.md
```

The correct resolution is to:

1. Identify what is the _overview/nav_ responsibility vs. the _detail_
   responsibility of the file.
2. Create `docs/foo-detail.md` (or an appropriate suffix) for the detail
   portion.
3. Replace the detail content in `docs/foo.md` with a one-sentence
   description and a link to the companion.
4. Verify both files are ≤100 lines and all content is preserved.

**Never** instruct an AI to "shorten the description" or "remove the examples"
to make a lint gate pass.

## Quality Check

After splitting, verify:

- [ ] All content from the original file is present in either the primary or a companion.
- [ ] The primary file links to every companion with a brief description.
- [ ] Every companion is ≤100 lines.
- [ ] `npm run lint` passes.
- [ ] A reader starting from the primary file can reach all content in ≤2 hops.
