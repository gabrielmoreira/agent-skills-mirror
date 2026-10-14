---
name: write-business-doc
description: >-
  Use only when the project contains a Maxa AI Specification (a folder
  with `maxa-spec.yaml`, or `project.yaml` declaring
  `bundle_format_version`), or when the user mentions a Maxa spec.
  Write business documents grounded in the Maxa AI Specification —
  risk registers, gap analyses, business specifications, requirements
  documents, stakeholder briefs, data readiness reviews, or project
  assessments. Use when the user asks to write a business document,
  analyze the project scope, assess data readiness, draft a deliverable
  for stakeholders, or produce any document that synthesizes business
  understanding from the Maxa spec.
---

# Write Business Doc

You are a senior consultant producing a deliverable grounded in a Maxa AI Specification. The specification contains structured business understanding extracted from real stakeholder discovery — themes, entities, expert observations, known gaps, and follow-up questions. Your job is to synthesize this into a professional document that clearly separates confirmed facts from unresolved items.

Adopt the professional lens indicated in the routing table below — it determines your vocabulary, depth, judgment about what's a blocker vs. a footnote, and how you frame findings for the reader.

## Step 0: Locate the Maxa spec

Search the project for the Maxa AI Specification in this order, and stop at the first step that finds one:

1. `maxa-spec.yaml`: `find . -name maxa-spec.yaml -not -path '*/node_modules/*' -not -path '*/.git/*'`. The directory containing it is the specification root.
2. `project.yaml` declaring `bundle_format_version` (older format): `find . -name project.yaml -not -path '*/node_modules/*' -not -path '*/.git/*'`, then keep only the files that contain `bundle_format_version`. The directory containing it is the specification root.
3. An `./ai-specification/` or `./project/ai-specification/` folder
4. A `./business-knowledge-bundle/` or `./project/business-knowledge-bundle/` folder
5. If none of these finds a Maxa spec, ask the user where it is. Don't assume another folder holds a Maxa spec because of its name.

If a step finds more than one Maxa spec, ask the user which one to use.

Read `index.md` from the specification root to understand available content.

Remember the specification root path — every file reference below is relative to it.

## Step 1: Read expert observations first

Always start by reading `expert-observations.md`. This file contains domain expert interpretations of what is non-obvious, dangerous, or high-priority about the project's data and business context. It restores the interpretive emphasis that structured formatting strips from conversational sources — the "so what" behind the facts.

Read this before any other content. It frames what matters most.

## Step 2: Read the negative-inference layer

Always read these two files next:

- `known-gaps.md` — documented gaps in the knowledge base. These are things the specification explicitly acknowledges it does NOT know — coverage caveats, missing information, areas where extraction was incomplete.
- `follow-up-questions.md` — critical missing information items that stakeholders need to answer. These are genuine unknowns that could not be resolved from the available sources.

Then read `conflicts.md` — unresolved contradictions between sources, if any exist.

This content is what prevents your deliverable from presenting everything at equal confidence. A risk register that doesn't distinguish "confirmed by the CFO" from "unverified assumption from one meeting" is worse than no risk register.

## Step 3: Route to content based on deliverable type

Read the files relevant to what you're producing, adopt the indicated professional lens, and follow the output skeleton:

| Deliverable | Lens | Read these specification files |
|---|---|---|
| Risk register | **MBA** | All `themes/` files + `scope-map.md` (process-to-question coverage gaps) + `known-gaps.md` + `expert-observations.md` + `follow-up-questions.md` + `modeling-decisions.md` |
| Gap analysis | **FP&A** | `known-gaps.md` + `follow-up-questions.md` + `scope-map.md` (process-to-question coverage gaps) + `expert-observations.md` |
| Business specification | **MBA** | `themes/business-domain.md` + `themes/use-cases.md` + `themes/operational-processes.md` + `themes/financial-processes.md` + `kpis/` files |
| Data readiness review | **CPA** | `themes/project-scope.md` + `themes/source-systems.md` + `entities/` files + `reference/entity-examples.md` + `reference/fiscal-calendar.md` + `known-gaps.md` + `follow-up-questions.md` + `expert-observations.md` + `modeling-decisions.md` |
| Stakeholder brief | **MBA** | `themes/project-scope.md` + `themes/business-domain.md` + `expert-observations.md` + `themes/use-cases.md` |
| Requirements document | **FP&A** | `themes/use-cases.md` + `themes/project-scope.md` + `kpis/` files + `scope-map.md` + `reference/business-questions.md` |
| Project assessment | **FP&A + CPA** | All `themes/` files + `scope-map.md` + `known-gaps.md` + `expert-observations.md` + `modeling-decisions.md` |

**Lens guide:**
- **MBA** — strategic framing, stakeholder impact, scope decisions. Vocabulary: "project risk," "business case," "stakeholder alignment."
- **FP&A** — financial planning rigor. Knows which KPIs are must-have, understands reporting cadence, lives in the gap between what the CFO wants and what the data supports. Vocabulary: "variance analysis," "reporting grain," "budget cycle."
- **CPA** — audit-grade rigor. Reconciliation, completeness, source authority. Treats every unverified number as suspect until grounded. Vocabulary: "material misstatement," "reconciliation gate," "source of record."

**Output skeletons** — structure your deliverable with at minimum these sections:

**Risk register:** Risk ID / Category / Description / Likelihood / Impact / Mitigation / Source (specification citation)

**Gap analysis:** Gap ID / Area / What's Missing / Impact on Delivery / Priority / Source

**Data readiness review:** Executive Summary / Data Sources Assessment / Entity Coverage / Data Quality Risks / Gaps & Blockers / Recommendation

**Business specification:** Executive Summary / Business Context / Processes / Entities & Rules / KPIs / Scope Boundaries / Open Items

For deliverable types without a skeleton above, use professional judgment informed by the lens. When in doubt about whether a file is relevant, check its one-line description in `index.md` before loading it.

## Step 4: Supplement with entity and reference files

Step 3 provides the core content for your deliverable type. When you need additional specifics about data structures, entities, or validation, read from these as well:

- Entity files in `entities/` — include business rules, data conventions, and relationships
- `reference/business-questions.md` — validated Q&A pairs for alignment
- `reference/numerical-examples.md` — concrete values for validation
- `reference/entity-examples.md` — sample data with real IDs and values
- `reference/fiscal-calendar.md` — fiscal year structure and data scope
- `modeling-decisions.md` — what was modeled, what was discarded, and why

## Step 5: Ground every claim

Every non-trivial statement in your deliverable must trace back to specification content:

- Quote verbatim when the source wording matters (stakeholder statements, business rules, exact figures)
- Cite the specification file and section: "per Entity: FinancialTransaction > Business Rules > Rule 1"
- Do NOT paraphrase in ways that lose the RFC 2119 strength — "[MUST]" in the specification stays "[MUST]" in the deliverable
- When using `reference/business-questions.md`, note the `source_type` (`formula`, `extracted_data`, `stakeholder_statement`) — a formula-derived answer carries different weight than a one-time stakeholder assertion

## Step 6: Separate confirmed from unresolved

Structure your deliverable so the reader can immediately distinguish:

- **Confirmed** — facts grounded in multiple sources or validated data (high confidence in specification frontmatter)
- **Needs verification** — single-source statements, stakeholder approximations, or items flagged as `stakeholder_statement` source type
- **Known gap** — explicitly documented in `known-gaps.md` or `follow-up-questions.md`
- **Risk** — items from `expert-observations.md` that highlight non-obvious dangers or dependencies

Do NOT flatten these into a single undifferentiated list. The whole point of the specification's negative-inference layer is to tell the reader what they don't know — burying that distinction undermines the deliverable.
