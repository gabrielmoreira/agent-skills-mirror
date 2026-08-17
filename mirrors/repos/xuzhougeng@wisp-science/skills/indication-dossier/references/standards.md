# Sourcing standards and report style

Applies to every phase. Read once at the start of a dossier run.

## What counts as a finding

A finding is citable only when it carries all three of:

1. `source_url` — the URL of the primary source, exactly as fetched;
2. `source_type` — one of `ctgov`, `fda`, `ema`, `pubmed`, `preprint`,
   `patent`, `conference`, `company_ir`, `news`, `other`;
3. `quote` — verbatim supporting text from that source.

A finding missing any of these is incomplete and must be flagged, not cited.
URLs come only from successful fetches or MCP results — never construct or
guess one. When a journal link rots, try the DOI resolver
(`https://doi.org/<DOI>`); if that also fails, record the failure in
`anomaly_flags`.

## Never invent

Trial statistics, approval/filing/completion dates, prevalence and incidence
figures, drug names and approval status, patent numbers and expiries — these
are either sourced or absent. When the canonical primary source comes up
empty (Drugs@FDA for approvals, the sponsor's pipeline page for stage,
ClinicalTrials.gov for trial details), write "Not publicly available", add an
`anomaly_flags` entry, and move on. No placeholders.

## Retrieval mechanics

- Prefer domain MCP tools (clinical trials, literature) over generic web
  fetch — structured results, fewer parsing errors.
- `WebSearch` returns index snippets only. To read a PDF, `WebFetch` its URL
  (text extraction is built in). When the data lives in figures or tables —
  waterfall/KM/spider/forest plots, PK curves, AE tables, biomarker
  durability plots — download with `curl -L -o file.pdf '<url>'` and `Read`
  the file, then describe the visual content in the finding ("Figure 2
  waterfall shows 68% ORR"). Single-quote downloaded URLs and only follow
  plain `https://` links without shell metacharacters.
- Conference decks and posters are figure-first: download and `Read` by
  default instead of text-fetching.
- IR and guideline pages hide PDFs behind UUID paths (`/static-files/abc123`)
  that don't end in `.pdf`; `WebFetch` the page and harvest its markdown
  links to find them.
- Keep context lean: distill each source to structured findings as soon as
  it's read, and for long documents target sections via the abstract or
  table of contents rather than reading linearly.

## Insight vs. context

Before promoting something to an "insight", ask whether a specialist with
five years in the field would find it surprising or decision-relevant. If
not, it's context — still useful, but it doesn't lead a section.

## Report style

Write as an industry analyst: complete, specific, sourced.

- **Inline citations.** Every factual claim links its source:
  `[descriptive claim text](source_url)`. When no natural claim text exists,
  title the link with source name + document type. Reserve numbered `[1]`
  references for a source cited five or more times, or several sources on
  one claim.
- **Cite:** quantitative data, endpoints and results, competitor stage and
  timing, dates, safety data, patent numbers.
  **Don't cite:** general medical knowledge, your own interpretation, or
  arithmetic you performed on cited inputs (cite the inputs).
- **Deep links only.** ClinicalTrials.gov →
  `https://clinicaltrials.gov/study/NCT########`; PubMed →
  `https://pubmed.ncbi.nlm.nih.gov/<PMID>/` (PMID over DOI redirect);
  companies → the specific press release or deck; patents →
  `https://patents.google.com/patent/US########X#`. Never a homepage.
- **Disagreeing sources** are both cited, with a stated choice:
  "the press release reports [200 patients](url1) but ClinicalTrials.gov
  shows [180 enrolled](url2); we use the registry figure."
- **Final check.** Every number, stage, date, and efficacy figure carries a
  specific inline link; no "studies show" without naming them; citations
  written with the claim, never backfilled.
