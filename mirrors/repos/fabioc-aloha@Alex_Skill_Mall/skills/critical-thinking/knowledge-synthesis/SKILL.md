---
type: skill
lifecycle: stable
inheritance: inheritable
name: "knowledge-synthesis"
description: Cross-project pattern recognition — abstract, generalize, connect, store at the highest true level
tier: core
applyTo: '**/*knowledge*,**/*synthesis*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Knowledge Synthesis Skill


> Extract the reusable from the specific. Store at the highest level that remains true.

## The Synthesis Process

### 1. Abstract — Strip project-specific details

| Before (project-specific)                                       | After (abstracted)                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------- |
| "In the AI assistant extension, skill links break when files are renamed"   | "Connection metadata breaks when target files are renamed"          |
| "We migrated knowledge files to skills/"                        | "When reorganizing knowledge files, update all internal references" |
| "the AI's dream runs brain-qa.cjs"                                | "Automated health checks should run validation scripts"             |

**Test**: Would this insight help someone who's never seen this project?

### 2. Generalize — Find the abstraction level

| Level                | Example                                                       | Store As             |
| -------------------- | ------------------------------------------------------------- | -------------------- |
| Project-specific     | "the AI assistant uses frontmatter applyTo patterns"                      | Don't store globally |
| Technology-specific  | "YAML frontmatter files break silently on rename"             | GI-\* insight        |
| Architecture pattern | "Self-referencing metadata needs rename-aware tooling"        | GK-\* pattern        |
| Universal principle  | "Metadata that references other files is fragile by nature"   | GK-\* (high value)   |

**Store at the highest level that remains true.** If generalizing makes it wrong, stay specific.

### 3. Connect — Link to existing knowledge

Before creating new knowledge, check: does this extend an existing pattern?

| Signal                                  | Action                                             |
| --------------------------------------- | -------------------------------------------------- |
| "We solved this before in project X"    | Extend existing GK-\* with new example             |
| "This is the third time I've seen this" | Promote from insight (GI-_) to pattern (GK-_)      |
| "This contradicts what we knew"         | Update existing pattern, note the exception        |
| "This is entirely new"                  | Create new GI-\* insight, observe before promoting |

### 4. Store — Right format, right location

| Type    | Prefix | Criteria                                            | Location    |
| ------- | ------ | --------------------------------------------------- | ----------- |
| Pattern | GK-\*  | Proven in 2+ projects, abstracted, actionable       | `patterns/` |
| Insight | GI-\*  | Single observation, timestamped, may not generalize | `insights/` |

**Quality bar**: 10 great patterns > 100 mediocre notes.

## Pattern Triggers

| Signal During Work              | Synthesis Opportunity                          |
| ------------------------------- | ---------------------------------------------- |
| "We did this before"            | Recurring solution → pattern candidate         |
| Same bug in different context   | Missing knowledge → capture the fix pattern    |
| "This works everywhere"         | Universal principle → high-value pattern       |
| "I wish I'd known this earlier" | Onboarding knowledge → insight worth capturing |
| "This is not obvious"           | Non-obvious insight → capture the _why_        |

## Promotion Candidacy Decision Table (TR5)

When deciding whether to promote a finding to global knowledge:

| Criterion | Threshold | If Fails |
|---|---|---|
| Observed in 2+ independent projects | Required | Keep as GI-* insight; wait for second observation |
| Passes cross-project isolation stripping | Required | Strip project specifics first; if nothing useful remains, discard |
| Abstraction still true after generalizing | Required | Stay at lower abstraction level |
| Not a near-duplicate of existing GK-* | Required | Extend existing pattern instead of creating new |
| Actionable — reader can do something with it | Required | Rewrite with concrete action; if impossible, discard |
| Non-obvious — not common knowledge in the domain | Recommended | Demote to reference note; don't waste pattern space |
| Includes at least one concrete example | Recommended | Add example before promoting |
| Timestamped with discovery context | Recommended | Add `discoveredFrom` and date |

**Minimum bar**: All "Required" rows must pass. Failing any "Required" criterion = not ready for promotion.

## Research-Promotion Decision Table (KW1)

When a project-local finding is a candidate for promotion to global `memory/`, evaluate this table. This extends TR5's candidacy check with the mandatory cross-project-isolation stripping test from `cross-project-isolation.instructions.md`.

| # | Check | Pass | Fail | Action on Fail |
|---|-------|------|------|----------------|
| 1 | **Multi-project signal** — observed in 2+ independent contexts | Evidence from separate projects or domains | Single project only | Hold as local insight (GI-*); promote only after second sighting |
| 2 | **File paths stripped** — no `src/services/billing/handler.ts:42` style paths | Generic references ("a service handler module") | Absolute or project-relative paths present | Rewrite with generic descriptions |
| 3 | **Project names stripped** — no identifying project names | "A Fabric workspace management project" | "In the FabricManager project..." | Replace with generic description |
| 4 | **Client names stripped** — no employer clients, customers | "A client billing API" | "Contoso's billing API" | Replace with generic reference |
| 5 | **Domain entities generalized** — no domain-specific PII-adjacent data | "A domain entity schema" | "Patient record schema in FHIR format" | Generalize to domain category ("regulated domain", "compliance-heavy domain") |
| 6 | **Repo URLs omitted** — no private repo links | No GitHub/GitLab URLs | `github.com/org/private-repo` present | Remove entirely |
| 7 | **Stranger test** — would this help someone who has never seen the source project? | Pattern is self-contained and actionable | Requires project context to understand | Not abstract enough; rewrite or discard |
| 8 | **Code snippets ≤5 lines** — longer snippets leak architecture | Short illustrative examples | 10+ line code blocks | Trim to essential pattern; replace specifics with placeholders |
| 9 | **No configuration values** — connection strings, endpoints, resource names absent | Technology names only (React, Azure Functions) | Endpoint URLs, resource IDs, connection strings | Strip all configuration; keep only technology references |
| 10 | **Existing pattern check** — not a duplicate of current GK-* | Novel insight or significant extension | Near-duplicate of existing pattern | Extend existing entry instead of creating new one |
| 11 | **Quantified outcomes stripped of attribution** — "reduced build time by 40%" not "Project X reduced..." | Anonymous metrics | Attributed to specific project or client | Remove attribution; keep the metric |
| 12 | **PII memory filter pass** — passes `pii-memory-filter.instructions.md` self-check | "Would I be comfortable if this appeared in a GitHub issue?" = yes | Contains names + identifiers, health data, financial data, credentials | Do not promote; strip PII first or discard |

**Workflow**: Local finding → pass all 12 rows → write to `memory/` with `scope: global-safe` → log promotion via PE1 decision log with `promotedFrom` provenance.

## Promotion Checklist (Insight → Pattern)

Before promoting a GI-\_ insight to GK-\_ pattern:

- [ ] Abstracted from original project context
- [ ] Named with clear, searchable slug
- [ ] Tagged with relevant categories
- [ ] Connected to existing patterns (if related)
- [ ] Includes at least one concrete example
- [ ] The generalization is still _true_ (not over-abstracted)

## Anti-Patterns

| Don't                        | Why                                   | Do Instead                      |
| ---------------------------- | ------------------------------------- | ------------------------------- |
| Store every learning         | Creates noise, reduces signal         | Filter for non-obvious insights |
| Copy-paste project specifics | Not reusable outside original context | Abstract first                  |
| Create near-duplicates       | Fragments knowledge                   | Extend existing patterns        |
| Over-generalize              | "Always do X" is usually wrong        | Include scope and exceptions    |
| Skip examples                | Abstract knowledge is hard to apply   | Include 1-2 concrete examples   |

## Synthesis During Meditation

Phase 4 of meditation is the natural synthesis point:

1. Review session insights (Phase 1 output)
2. For each insight: Abstract → check if existing pattern covers it → extend or create
3. Link new entries to related skills
4. Verify the global knowledge index is updated

## Cross-Domain Pattern Synthesis

Phase 3 of meditation analyzes episodic memories for cross-domain synthesis to move beyond consolidation into generation.

### The Transfer Test

Before accepting a cross-domain connection, validate all three:

| Criterion   | Question                                            | Fail Example                                               |
| ----------- | --------------------------------------------------- | ---------------------------------------------------------- |
| Structural  | Is the similarity in _structure_, not just _words_? | "Both use JSON" (superficial)                              |
| Actionable  | Would someone in domain B find this useful?         | "Data viz is like meditation: both need focus" (vague)     |
| Independent | Does it hold without domain A context?              | "Use frontmatter applyTo for dashboards" (too specific)    |

### Cross-Domain Connection Types

| Type                         | Description                                                   | Example                                                                                   |
| ---------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Technique transfer**       | A method from domain A solves a problem in domain B           | "Colorblind-safe palette enforcement (data) applied to brand asset validation (design)"   |
| **Pattern isomorphism**      | Same structural pattern appears independently in both domains | "Health checks: connection validation (cognitive) mirrors dependency audit (security)"    |
| **Principle generalization** | A domain-specific rule is actually a universal truth          | "Store at the highest true level (synthesis) = single source of truth (architecture)"     |
| **Gap bridging**             | Domain A has a solution for a known gap in domain B           | "Automated drift detection (cognitive) could solve doc-code sync (documentation)"       |

### Synthesis Output Format

For each validated cross-domain connection, produce:

```markdown
## Cross-Domain Insight: [title]

**Source domain**: [domain A]
**Target domain**: [domain B]
**Connection type**: technique transfer | pattern isomorphism | principle generalization | gap bridging
**Transfer test**: structural ✓ | actionable ✓ | independent ✓

**Insight**: [1-2 sentence description of the connection]
**Evidence**: [episodic memories that support this connection]
**Proposed action**: [new skill link, new skill, or extension to existing pattern]
```
