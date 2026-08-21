---
name: end-to-end-research
version: 1.0.1
description: >-
  Runs full-cycle research: scope, multi-source collection, source evaluation,
  claim triangulation, contradiction resolution, and cited deliverables. Use when
  the user asks for research, deep research, investigate, literature review,
  competitive analysis, market research, due diligence, fact-check, survey the
  field, or multi-source investigation. Compose with multi-platform-agent-reach
  for platform routing and the `obsidian` skill for optional vault writes.
  Not for pure code edits, creative fiction, or single-file lookups.
---

# End-to-End Research

Take a question from raw ask to a verified, cited deliverable. This file is the **playbook** — follow it in order. Load reference files on demand, not upfront:

- **`reference.md`** — the encyclopedia. Load §1 during Phase 2 (query design), §3 during Phase 4 (evidence grading), §4 during Phase 6 (contradiction resolution), §5–§9 during Phase 5 (domain-specific synthesis frameworks), §10 during Phase 7 (output templates), §11 on failures, §12 for legal/ethical boundaries.
- **`examples.md`** — worked runs (technology evaluation, company snapshot, claim verification, docs landscape, market sizing). Load when you need a concrete pattern for the current question type.
- **`claim-schema.json`** — machine contract for structured findings. Load during Phase 7 (deep tier) to validate the claims pack before handoff.

## When to Use

- Any question whose answer requires **multiple external sources**: technology choices, vendor/company assessment, "what's the state of X", claim verification, market or competitive questions, literature surveys, due diligence.
- Trigger phrases: research, deep research, investigate, literature review, competitive analysis, market research, due diligence, fact-check, survey the field, "is it true that", "what do we know about".
- Stakes or ambiguity are high enough that a single search-and-answer would be guesswork, or the answer must be **defensible** — cited, dated, triangulated.

## When NOT to Use

| Situation | Route instead |
|---|---|
| Single documented fact (one search + one fetch answers it) | Answer directly; cite the one source. No pipeline. |
| Question about the local codebase | codebase-memory tools (`search_graph`, `get_architecture`) — not web research |
| Needs an experiment or metric run, not literature | `autonomous-research-loop` |
| Findings already exist; user wants consensus or formatting | `research-report-synthesis` directly |
| Pure memory read/write | `obsidian` skill / durable notes folders in the user's vault |
| Creative writing, brainstorming with no evidence requirement | Skip the pipeline; say so if rigor was implied |
| Question underspecified (no scope, unclear success criteria) | Ask ≤3 clarifying questions FIRST, then run this skill |

## Prerequisites

- **WebSearch** and **WebFetch** tools available (free path — must work standalone).
- **Memory MCP / codebase-memory** available for intake checks and delivery handoffs.
- **Paid APIs** (exa, OpenRouter/consult, or any metered provider): require **explicit user approval before first use in a session**, with a cost estimate. The free path must always work alone.
- **Windows host (PowerShell)**: shell is PowerShell. Quote URLs with single quotes (`'https://...'`) — `&` and `?` break bare commands. `curl` aliases to `Invoke-WebRequest`; use real tools instead. Write deliverables via the file-write tool as UTF-8, not `>` redirection (encoding surprises).
- **Binding user rules**: maximum thinking depth by default for planning, evaluation, and the verify gate; verify claims before asserting; cite sources always; no hallucinated facts — "I couldn't verify this" beats a confident guess, every time.

## Operating Principles

1. **Truth over speed.** A late correct answer beats a fast wrong one. Never trade verification for turnaround — trade *scope* instead: narrow the question, keep the rigor. If evidence is thin, deliver "insufficient evidence," never plausible filler.
2. **Cite everything.** Every non-obvious claim in the deliverable carries an `[S-###]` citation into the source registry, with access date. Uncited claims get cut or relabeled as inference.
3. **Triangulate.** Load-bearing claims need ≥2 **independent** sources — different `independence_group`, not the same upstream origin. Ten articles quoting one press release = one source. Trace to the origin.
4. **Fact ≠ claim ≠ inference.** Type every finding: **fact** (verified against primary evidence), **claim** (asserted by a source, unverified), **inference** (your reasoning from evidence), **opinion** (a source's judgment), **prediction** (forward-looking). Never let a claim wear a fact's clothes.
5. **Primary sources preferred.** Trace upstream: press article → press release → filing/repo/doc/paper. Cite the most upstream source you actually fetched. Official docs, filings, source code, and datasets outrank coverage of them.
6. **Recency discipline.** Date-stamp every source (`published_date`, `accessed_date`) and every claim (`as_of`). Flag volatile claims (pricing, versions, headcount, market share) with a `recheck_after` horizon. For fast-moving topics, treat anything >6 months old as "verify before relying on."
7. **Coverage honesty.** Report what you could NOT check — failed fetches, paywalls, rate limits, skipped platforms. Compute a confidence ceiling from coverage; never present degraded coverage as comprehensive. An empty result with reasons beats padded findings.
8. **No fabricated citations.** Every URL in the deliverable was returned by a search or fetched THIS session. Never reconstruct a "probable" URL from memory. Model-knowledge points are labeled as such and graded E/unverified.
9. **Steelman contradictions.** When sources conflict, resolve per the protocol (Phase 6; full version in `reference.md` §4) — don't pick the convenient side.
10. **Declare scope and stop conditions up front.** Unbounded research is a failure mode, not diligence.

## Depth Tiers

Pick a tier at intake and state it. Escalate mid-run only if findings warrant — and say so.

| Tier | Sources (min) | Time budget | Source mix | Verification |
|---|---|---|---|---|
| **quick** | 3–5 | 15–30 min | Top search results; 1 primary if cheap | Spot-check the load-bearing claim |
| **standard** | 8–15 | 1–2 h | Multi-type: official, press, community; ≥2 primary | Triangulate all key claims; date-stamp everything |
| **deep** | 20+ | Half day+ | Primary documents mandatory (filings, papers, code, datasets); adversarial search for disconfirming evidence | Full contradiction pass; every A/B claim traced to primary; per-claim confidence |

Defaults: fact-check → quick/standard; competitive, market, due diligence → standard/deep; literature review or "survey the field" → deep. If the user says "quick look," honor it — deliver that tier and note what a deeper tier would add.

## Procedure

```
Intake → Plan → Collect → Evaluate → Synthesize → VERIFY GATE → Deliver → (memory handoff)
             ↑________________loop on gaps________________|
```

Keep the Progress Checklist (bottom of this file) updated as you move through phases. It survives context compaction and mirrors the phase gates.

### Phase 1 — Intake & Scope

Produce an intake block before any search.

1. Restate the core question as **one answerable sentence**; if ambiguous, ask ≤3 clarifying questions — only ones that would change the plan.
2. Define success criteria: what does "answered" look like? (decision made / claim verified / landscape mapped).
3. Capture constraints: deadline, region, language, audience, budget — **paid APIs (exa, OpenRouter, etc.) require explicit user approval first**.
4. Pick depth tier; state it.
5. Log user-supplied assumptions as claims to verify, not facts.
6. Check memory (memory MCP / codebase-memory) for prior research on the topic — reuse settled work, re-verify stale findings.

**Exit gate:** one-sentence question + tier + success criteria + constraints written down.

### Phase 2 — Planning

1. Decompose into 3–8 sub-questions (`SQ1..SQn`), each independently answerable.
2. Build a source map per sub-question: which source *types* can answer it (official? filings? papers? forums? code?).
3. Draft the query plan: 2–4 seed queries per sub-question, broad → narrow. **Load `reference.md` §1** for operators, `site:`, `filetype:`, temporal filters, platform dialects.
4. Identify likely primary sources up front (vendor docs/IR page, the paper, the repo, the regulator).
5. Set stop conditions: minimum source count met AND saturation (no new material facts in last N fetches), OR time budget hit, OR success criteria met.
6. Route platforms: if the question spans surfaces (X, Reddit, HN, academic indexes), hand routing to **multi-platform-agent-reach** — run `agent-reach doctor` first if reach seems broken.

**Exit gate:** sub-questions + query plan + stop conditions exist. Quick tier: five lines suffice — but write them.

### Phase 3 — Collection

Search → select → fetch → extract. **Never cite a search snippet — fetch the page.**

1. Run seed queries via WebSearch; log every query (they go in the method note).
2. Select candidates by source-type priority (primary first), not rank position.
3. WebFetch each selected source; escalate to browser/Playwright only when fetch fails (JS rendering, interaction). Respect paywalls and robots — no circumvention; use the abstract/preview or find an open equivalent.
4. Register each source (`S-###`) with tier, type, dates, `independence_group`, `fetch_status`.
5. Extract findings as **claims** (schema below): one atomic, falsifiable statement per entry, with verbatim quote + locator.
6. Chase citations upstream: when a source cites another for a load-bearing claim, fetch the origin.
7. Sharpen later queries with terminology discovered in early sources.
8. Track saturation per sub-question: 3 consecutive fetches adding nothing new → close it.
9. Check stop conditions after each sub-question, not just at the end.

**Exit gate:** tier's source minimum met; every sub-question has ≥1 claim or an explicit "no evidence found + why."

### Phase 4 — Evaluation

Grade what you collected before building on it. **Load `reference.md` §3** for the full evidence grading detail.

1. Assign every source a reliability grade (A–E scale below; recorded as `tier` T1–T5 in the claims pack).
2. Flag conflicts of interest: vendor selling the thing, competitor attacking it, sponsored content, affiliate links.
3. Verify dates: publication AND last-updated; is the claim version/time-sensitive? Mark `volatile` + `recheck_after`.
4. Assign `independence_group`s: sources sharing an upstream origin (same press release, same study) form ONE group — triangulation counts groups, not sources.
5. Demote or drop D/E sources unless they are the *subject* of study (e.g., analyzing community sentiment).

**Source Reliability Scale (A–E)**

| Grade | Pack tier | Definition | Examples |
|---|---|---|---|
| **A** | T1 | Primary, authoritative, verifiable | Official docs/specs, regulatory filings, peer-reviewed papers, source code, first-party changelogs, court records, raw datasets |
| **B** | T2 | Reputable secondary with editorial standards | Major outlets with corrections policies, established analyst reports, conference talks by the builders |
| **C** | T3 | Informed but unvetted | Expert blogs, engineering posts, high-signal forum threads (HN, accepted SO answers), preprints |
| **D** | T4 | Weak provenance | Content-farm articles, SEO listicles, anonymous posts, AI-generated aggregators, undated pages |
| **E** | T5 | Unreliable / adversarial | Known misinformation sources, marketing dressed as analysis, unverifiable claims, model-knowledge-only points |

Rules: key claims need A/B support or two independent C's. Never rest a conclusion on D/E. Grade the *source for this claim*, not the brand — a great outlet's sponsored post is D. When unsure, grade down. A source's grade (A–E ↔ T1–T5) feeds the **claim's** evidence grade, which also weighs independence and verification status.

### Phase 5 — Synthesis

**Load `reference.md` §5–§9** for domain frameworks: competitive (§5), market (§6), technical due diligence (§7), literature review (§8), fact-checking (§9).

1. Build the claims table: all claims grouped by sub-question, with type, grade, confidence, and `as_of`.
2. Build the evidence matrix for decisions: options × criteria, each cell backed by claim IDs.
3. Keep the three layers separate in the draft: facts (verified), claims (attributed, unverified), inferences (yours — written as "I infer/assess").
4. Answer each sub-question explicitly, then compose the top-level answer.
5. List open questions with reasons (`no_source_found`, `conflicting_evidence`, `out_of_budget`, `inaccessible`, `too_fresh`) and what evidence would settle each.
6. Surface surprises — findings contradicting the user's stated assumptions get top billing, not burial.

### Phase 6 — Verification Gate

**Do not skip on standard/deep.** This is where hallucinations die. **Load `reference.md` §4** for the full contradiction resolution protocol.

1. Re-check every load-bearing citation at quote level: does the fetched text actually say what the claim says?
2. Verify all numbers and dates against sources character-by-character — numbers transpose, dates drift.
3. Resolve contradictions per protocol: (1) dates — newer primary usually wins; (2) independence — is one side a citation cluster?; (3) specificity — firsthand + specific beats general; (4) unresolved → report BOTH sides with grades and dates, mark claim `contested`.
4. Adversarial pass (deep tier): 2–3 queries explicitly hunting disconfirming evidence ("X problems", "X criticism", "X vs").
5. Set final per-claim confidence: `confirmed` / `probable` / `contested` / `unverified` / `refuted`.
6. Enforce the fact rule: a finding is typed `fact` only if verification status is `verified` or `spot_checked` — otherwise it's a `claim`.
7. Kill or downgrade anything that fails — edit the synthesis; don't caveat a broken claim into staying.

**Exit gate:** every claim in the deliverable is cited-and-checked, or explicitly labeled inference/unverified.

### Phase 7 — Deliverable

**Load `reference.md` §10** for output templates. **Load `claim-schema.json`** if deep tier.

1. Pick the format for the audience: executive brief (quick default), full report (deep default), decision memo, annotated bibliography.
2. Structure: **Answer → key findings (confidence-tagged) → evidence detail → conflicts & open questions → method note (queries run, what failed, stop condition hit) → source registry (graded, dated)**.
3. State the tier run and what a deeper tier would add.
4. Deep tier: emit the claims pack and validate it against `claim-schema.json` before any handoff.
5. Contested or high-stakes conclusions → hand off to **research-report-synthesis** for multi-model consensus (paid consult — ask first).
6. Offer (never force) a vault write of durable findings via the **obsidian** skill (durable notes folders — never a secrets folder; never a second memory product).

## Claim Schema (inline)

Record findings in the claims-pack shape from Phase 3 onward. Full contract with all enums and conditional rules: `claim-schema.json`. Minimal valid excerpt:

```json
{
  "meta": {
    "question": "Which managed vector DB fits a solo-dev game-companion API under $50/mo?",
    "depth_tier": "standard",
    "as_of": "2026-07-15",
    "coverage": { "source_classes_planned": 4, "source_classes_ok": 4, "degraded": [], "confidence_ceiling": "high" }
  },
  "sources": [
    {
      "id": "S-001",
      "url": "https://qdrant.tech/pricing/",
      "title": "Qdrant Cloud Pricing",
      "publisher": "Qdrant",
      "published_date": "2026-05-02",
      "accessed_date": "2026-07-15",
      "tier": "T1",
      "type": "official",
      "independence_group": "G1",
      "conflict_of_interest": "vendor pricing page — authoritative for own product, promotional elsewhere",
      "fetch_status": "fetched"
    }
  ],
  "claims": [
    {
      "id": "C-001",
      "statement": "Qdrant Cloud's free tier provides a 1GB cluster with no credit card required.",
      "sub_question": "SQ2",
      "type": "fact",
      "grade": "A",
      "confidence": "confirmed",
      "as_of": "2026-07-15",
      "volatile": true,
      "recheck_after": "2026-10-15",
      "evidence": [
        {
          "source_id": "S-001",
          "stance": "supports",
          "quote": "Start free with a 1GB cluster. No credit card required.",
          "locator": "Pricing page, free-tier card",
          "strength": "direct"
        }
      ],
      "independent_groups": 1,
      "verification": { "status": "verified", "method": "primary_source_fetch", "verified_date": "2026-07-15" }
    }
  ],
  "open_questions": [
    { "question": "Does the free tier throttle QPS?", "reason": "no_source_found", "recheck_after": "2026-08-15" }
  ]
}
```

Field rules (enforced by the schema): `type` ∈ fact | claim | inference | opinion | prediction. `confidence` ∈ confirmed | probable | contested | unverified | refuted. `volatile: true` requires `recheck_after`. `type: "fact"` requires verification status `verified` or `spot_checked`. Statements are atomic — split compound claims. A single T1 group suffices for a party's statements about its own product (as above); cross-party or load-bearing comparative claims need `independent_groups ≥ 2`.

## Integration Points

| Skill | When | What flows |
|---|---|---|
| **multi-platform-agent-reach** | Phase 2–3, when the question needs platform-specific search (X, Reddit, HN, academic) or routing across surfaces; `agent-reach doctor` if reach misbehaves | Sub-questions out → raw platform findings back as claims. Grade them yourself — platform content is usually C/D |
| **research-report-synthesis** | Phase 7, when conclusions are contested or high-stakes and multi-model consensus adds signal (consult MCP / OpenRouter — **paid, ask first**) | Claims pack + draft conclusions out → consensus-annotated conclusions back |
| **obsidian** | After delivery, for findings with shelf life (landscape maps, vendor evals, resolved fact-checks) | Deliverable + claims pack out → dated vault note so future recall knows staleness |
| **autonomous-research-loop** | Route there instead when the question is a measurable experiment ("does X improve Y"), not document research | The metric question, verbatim |

This skill owns the pipeline and the evidence standards; those skills own routing, consensus, and persistence. Don't reimplement their internals here.

## Pitfalls

- **Snippet citing.** Judging or quoting from search snippets without fetching. Snippets lie by truncation — `fetch_status` must be `fetched` or `archived_copy` for any quote.
- **Citation laundering.** Counting five articles that quote one press release as five sources. Independence groups exist to stop this.
- **Confirmation-only search.** Every query phrased to confirm the hypothesis; zero "X criticism / X failed / X vs" queries.
- **Recency blindness.** Presenting an old pricing page or API doc as current. Date-stamp or don't ship it.
- **Confidence inflation.** "X is the best" when evidence supports "X leads on criteria A and B per two B-grade sources as of July 2026."
- **Inference smuggling.** Your reasonable guess appearing in findings without an inference label.
- **URL reconstruction.** Emitting a remembered-but-unfetched URL. Grounds for failing the verify gate outright.
- **Unbounded rabbit-holing.** No stop conditions; the report ships late and bloated. Saturation is the signal to stop.
- **Paywall/ToS circumvention.** Public info only. No credential stuffing, no scraping against ToS (full boundaries: `reference.md` §12).
- **Skipping the gate because the draft reads well.** Fluency is not accuracy — plausible drafts are exactly where fabrications hide.
- **Answering a different question.** Scope drift from "which X for our use case" to "the history of X." Re-read the intake block before delivering.
- **PowerShell URL quoting.** Bare URLs with `&` or `?` break PowerShell commands. Always use single quotes: `'https://example.com?a=1&b=2'`.
- **`curl` alias trap.** On Windows, `curl` aliases to `Invoke-WebRequest`. Use WebFetch or the real tools instead; shell fetch is a last resort for binary downloads.
- **File encoding.** Writing deliverables via `>` redirection can produce unexpected encoding. Use the file-write tool as UTF-8.

## Verification

After completing the pipeline, confirm:

1. **Every claim is cited.** Scan the deliverable: each non-obvious statement has an `[S-###]` tag matching a source registry entry. Uncited statements are labeled inference or cut.
2. **Every URL was fetched this session.** No reconstructed URLs. `fetch_status` is `fetched` or `archived_copy` for every quoted source.
3. **Load-bearing claims triangulated.** Key claims have ≥2 independent groups (different `independence_group` values), or a single T1 for a party's own product statements.
4. **Dates present.** Every source has `published_date` and `accessed_date`. Every claim has `as_of`. Volatile claims have `recheck_after`.
5. **Fact rule enforced.** No claim typed `fact` without `verification.status` = `verified` or `spot_checked`.
6. **Contradictions resolved or reported.** No silent picks — conflicts are either resolved per protocol (Phase 6) or reported as `contested` with both sides.
7. **Coverage gaps disclosed.** Method note lists failed fetches, paywalls, rate limits, skipped platforms, and the stop condition hit.
8. **Deep tier: schema valid.** Claims pack validates against `claim-schema.json` before handoff.
9. **Scope intact.** Re-read the intake block. The deliverable answers the one-sentence question, not a drifted variant.

## Progress Checklist Template

Paste at start; keep updated (survives context compaction; mirrors the phase gates):

```markdown
## Research: <one-sentence question>
Tier: quick|standard|deep · Budget: <time> · Sources: <n>/<min> · Started: <date>

- [ ] 1 Intake: question + criteria + constraints + tier
- [ ] 2 Plan: SQ1..SQn + query plan + stop conditions
- [ ] 3 Collect: SQ1 ▢ SQ2 ▢ SQ3 ▢ ... (▣ = saturated)
- [ ] 4 Evaluate: sources graded ▢ · independence groups ▢ · volatility flags ▢
- [ ] 5 Synthesize: claims table ▢ · evidence matrix ▢ · open questions ▢
- [ ] 6 Verify: quotes rechecked ▢ · numbers/dates ▢ · contradictions ▢ · adversarial pass ▢ (deep)
- [ ] 7 Deliver: format ____ · schema validated ▢ (deep) · memory handoff offered ▢
Stop condition hit: <saturation | budget | answered>
Paid APIs used: <none | list — each pre-approved>
```

## Files

- **`reference.md`** — query design patterns (§1), source typology (§2), evidence grading A–E (§3), contradiction resolution protocol (§4), domain frameworks: competitive (§5), market (§6), technical due diligence (§7), literature review (§8), fact-checking (§9), output templates (§10), failure modes & recovery (§11), legal/ethical boundaries (§12).
- **`examples.md`** — worked runs: technology evaluation, company snapshot, claim verification, docs landscape, market sizing.
- **`claim-schema.json`** — JSON Schema for the claims pack; validate deep-tier output against it before handoff.
