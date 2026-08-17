---
name: literature-review
description: Retrieve, verify, and synthesize scientific literature. Use for seminal-paper lookups, evidence summaries, method comparisons, and gap analyses. Every citation must come from a live lookup, never from memory; retractions are checked; the deliverable is argued prose with resolvable DOI links.
license: Apache-2.0
metadata:
  # Non-biomodel: sends user's query (and contact email when configured) to
  # Crossref and OpenAlex for literature lookup.
  third_party:
    # The leaf /rest-api-metadata-license-information/ page now 404s though
    # still in search indexes. Parent docs landing carries the license
    # statement ("Almost all of the metadata we hold is reusable without
    # restriction") and is less likely to rot. Docs page, not a ToU —
    # info_url. verified 2026-06-30
    - kind: service
      name: Crossref
      info_url: https://www.crossref.org/documentation/retrieve-metadata/
      privacy_url: https://www.crossref.org/operations-and-sustainability/privacy/
    - kind: service
      name: OpenAlex
      terms_url: https://openalex.org/OpenAlex_termsofservice.pdf
      privacy_url: https://openalex.org/OpenAlex_privacy_policy.pdf
wisp:
  schema_version: 1
  domains: [scientific-literature]
  research_stages: [retrieval, validation, synthesis]
  roles: [retrieval, critic, synthesizer]
  evidence_types: [literature]
  outputs: [literature-review, evidence-matrix]
  side_effects: network
---

# Literature review

Work through six steps: scope, sweep, expand, verify, write, lint. The failure
modes this skill exists to prevent are all silent — a fabricated DOI, a
retracted headline result, a reading list dressed up as a synthesis — so each
step below names the check that catches it.

## 1. Scope the request

Different phrasings want different deliverables:

| Request shape | Deliverable |
|---|---|
| "the paper for X" / "the original/seminal…" | one or two primary citations |
| "what's the evidence on X" | thematic synthesis |
| "compare A and B" | trade-off analysis ending in a recommendation |
| "where are the gaps" | named gaps, each anchored to what establishes it |

A vague lay query gets the scope a domain expert would default to, stated
explicitly ("taking this as human RCT evidence; animal work is separate").
Clarify with the user only when the answer would change what you retrieve.

## 2. Sweep

Never write from recall. Recall chooses the framing and the search terms;
retrieval supplies every citation. Start with `search_openalex` /
`crossref_lookup` from this skill's `kernel.py`, a PubMed query, or any
literature connector advertised in the session (`search_skills` with
`{"query":"literature PubMed Semantic Scholar bioRxiv ClinicalTrials"}` finds
installed guidance; load matches with `use_skill`).

For a named-paper lookup, the target is the highly cited primary publication
that later work cites — not a review of it, not a news piece. Even when you
know the paper cold, resolving its DOI is one tool call; skipping it turns a
citation into a claim about a citation.

## 3. Expand along the citation graph

Keyword sweeps miss two things systematically: the foundational paper a field
builds on, and the newest work that extends or contests your top hits. Take
the two or three most relevant results and run `expand_citations(doi)` — it
returns references (backward) and cited-by (forward) from OpenAlex. Fold the
on-topic finds back into the working set before drafting. A survey-grade
answer typically rests on fifteen or more distinct primary-paper DOIs; a
handful of reviews is a reading list.

## 4. Verify

Run `verify_dois` on everything you intend to cite. A DOI either resolves to
a paper that says what you claim, or it is a fabrication — there is no third
state. When you have author/year/journal but no DOI, look it up; never
pattern-complete one. For surprising or high-profile findings, check
Crossref's `update-to` field: sensational papers are findable *because* they
were sensational, and some were retracted. When the requested paper does not
exist — the claim collapsed or was never established — say exactly that and
point at what the evidence actually shows, instead of substituting the
nearest-matching citation.

## 5. Write the synthesis

Organize by question or theme, never paper-by-paper. The value is the layer
on top of the papers: what replicated, what didn't, where the field agrees on
effect but splits on mechanism, which older result a newer one superseded.
Two tests for the draft:

- **First-sentence test.** Read only each paragraph's opening sentence. In
  sequence they should form your argument; if they form a list of author
  names, you have an annotated bibliography.
- **Bullet test.** Consecutive lines starting `- Author Year showed…` are a
  paragraph you haven't written. Bullets are for genuinely enumerable things
  (a reference appendix, a comparison table); the argument itself is prose.

Calibrate stated confidence to the evidence: a phase-3 RCT is stated plainly,
a single-cohort finding is "one group reported", preprints are flagged as
preprints, contested areas get both sides plus an honest "unresolved". Engage
a contested premise rather than building on it.

Cite inline as `[Author Year](https://doi.org/10.xxxx/...)` so prose renders
as `(Author Year)` with the DOI in the href. URL-encode parentheses inside a
DOI as `%28`/`%29`. No numbered `[1]` references — they desync on reorder.
Headings are short noun phrases; with five or more topics, group under two or
three `##` and demote the rest to `###`.

## 6. Deliver and lint

The answer lives in the chat reply: open on the finding itself, lay out the
evidence with inline DOIs, close on what remains open. For anything beyond a
one-paper lookup, also save the full review to a project-relative Markdown
file and link it at the *end* of the reply. Process narration — "all DOIs
verified", "no retraction flags", "report saved" — belongs nowhere: not as
opener, footer, or subtitle. Verification lives in the tool trace.

Before saving, run `style_pass(draft)` from `kernel.py` once on the full
markdown, fix what it lists in one editing pass, and save. It is a lint, not
a gate — do not loop on it. If `style_pass` is not defined in the kernel,
read this skill's `kernel.py` and exec it first.
