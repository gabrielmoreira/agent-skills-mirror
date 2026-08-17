# Phase guide

One section per phase. Each phase reads the previous waypoints, researches its
questions, and writes its own waypoint (formats in `waypoints.md`). Sourcing
rules are in `standards.md`.

## Phase 1 — Identity

Runs when `waypoints/meta.json` is absent. Everything downstream keys off the
answers here.

1. Create `<workdir>/waypoints/`.
2. Resolve what the indication *is*: standard clinical definition, ICD-10
   codes, aliases, and — critically — whether it is a recognized diagnostic
   entity at all. Biological states ("immunosenescence"), non-accepted
   indications ("ageing"), and iatrogenic populations ("GLP-1 induced
   sarcopenia") must be labelled as such, because the answer reshapes the
   epidemiology, regulatory, and trial sections.
3. Place it in the clinical taxonomy: parent indication (often given in
   `additional_context`), therapy area, condition class.
4. Rough clinical maturity: one `search_trials(condition=...)` call against
   the clinical-trials MCP; record total, phase, and status counts.
5. Write `meta.json` and initialize `sources_evaluated.json`.

Single iteration; no deep research yet.

## Phase 2 — Epidemiology

Runs when `meta.json` exists and `epidemiology.json` doesn't. Question: who
are these patients, how many, and what happens to them?

- **Case definition.** Consensus diagnostic criteria (EWGSOP2, GOLD, …) and
  how the population is separated from its neighbours. Contested or evolving
  criteria are findings, not footnotes. Non-standard indications get proxy
  definitions instead: research criteria, trial enrollment criteria, expert
  consensus.
- **Burden.** Prevalence and incidence from systematic reviews and
  meta-analyses first, registry/CDC/WHO data second, single-center studies
  last (acceptable for rare disease — say so). Distinguish community-dwelling
  from clinical populations. Note the trend, not just the point estimate.
- **Who.** Age/sex/ethnicity distribution, dominant risk factors and
  comorbidities, geographic variation when material.
- **Trajectory.** Acute vs. chronic, progressive vs. relapsing, staging,
  mortality/morbidity, and the inflection points where intervention matters.

Run the PubMed MCP and web searches through parallel subagents. Write
`epidemiology.json` with per-subsection coverage levels.

## Phase 3 — Biology and standard of care

Runs when `epidemiology.json` exists and `biology_soc.json` doesn't. Feeds
report sections 2 (biology) and 3 (standard of care).

- **Mechanism.** Recent mechanism reviews via PubMed MCP; identify the
  pathways that matter for therapy — validated targets vs. hypotheses — at
  analyst depth, not textbook depth.
- **Biomarkers.** Three buckets with distinct trial uses: diagnostic
  (confirms the condition), prognostic (predicts course), pharmacodynamic
  (measures drug effect). Mark FDA-qualified vs. exploratory; this feeds the
  endpoint discussion in Phase 4.
- **Approved therapies.** Search `site:fda.gov`; for each drug record
  mechanism, approval year, and above all *limitations* — the limitations
  define the opportunity. Distinguish on-label from off-label use. "Nothing
  is approved" is itself a key finding.
- **Guidelines.** Specialty society algorithms (NCCN, AASLD, ATS/ERS, AGS…),
  US/EU divergence when relevant, recent changes.
- **Unmet need.** What current therapy leaves untreated: underserved
  subpopulations, symptom control vs. disease modification, quality-of-life
  burden.

Parallel subagents: PubMed for biology, web for guidelines, FDA for
approvals. Write `biology_soc.json`.

## Phase 4 — Regulatory path and trials

Runs when `biology_soc.json` exists and `regulatory_trials.json` doesn't.
Question: how does one actually run a registrational trial here?

First classify the indication's regulatory maturity, and say which class it
is in — it controls how much this phase can find:

- established (IPF, MASH): specific FDA guidance exists;
- emerging (sarcopenia): little or no formal guidance;
- novel (ageing): no framework at all — a short section is the correct
  output, not a gap to pad.

Then:

- **Endpoints.** Guidance documents via `site:fda.gov`; endpoints from
  successful registrational trials; clinical vs. surrogate vs. PRO; anything
  accepted as "reasonably likely to predict clinical benefit" (accelerated
  approval).
- **Precedents.** Approval packages, accepted designs, breakthrough/fast
  track/priority review history, advisory committee debates, Complete
  Response Letters.
- **Design parameters.** `search_trials(condition=..., phase="Phase 3")`
  patterns: enrollment sizes, endpoint timepoints, comparator choices,
  per-patient cost estimates where the literature has them.
- **Landmark trials.** The 3–5 trials that changed practice (not merely the
  newest): NCT ID, drug, sponsor, phase, results, impact. For active
  sponsors, fetch `/pipeline` or `/investors/presentations` and `Read`
  downloaded decks — they are figure-first.
- **Failures.** Significant failures with mechanism-level lessons, not "the
  drug didn't work".

Parallel subagents: FDA for guidance, CT.gov for patterns, PubMed for trial
history reviews. Write `regulatory_trials.json` including `trial_landscape`
counts.

## Phase 5 — Synthesis

Runs last. Read all four waypoints plus `sources_evaluated.json`; open no
new research threads. One targeted fetch to fill a specific missing value in
an existing waypoint field is allowed (record it in `sources_evaluated.json`);
anything broader is named as a gap.

Write `waypoints/indication_dossier_report.md` with this outline:

```markdown
# Indication Dossier: <name>

**Definition** / **ICD-10** / **Parent indication** (one line each; write
"Not a standard diagnostic entity" when true)

## 1. Population Definition & Epidemiology
### 1.1 Diagnostic Criteria   ### 1.2 Prevalence & Incidence
### 1.3 Demographics & Risk Factors   ### 1.4 Natural History

## 2. Disease Biology
### 2.1 Pathophysiology   ### 2.2 Biomarkers

## 3. Standard of Care
### 3.1 Approved Therapies   ### 3.2 Treatment Guidelines   ### 3.3 Unmet Need

## 4. Clinical Endpoints & Regulatory Path
### 4.1 Accepted Endpoints   ### 4.2 Regulatory Precedents
### 4.3 Trial Design Parameters

## 5. Key Trials
### 5.1 Landmark Trials   ### 5.2 Notable Failures

## Appendix: Sources
```

Section guidance:

- 1–3 are narrative prose with inline citations and specific numbers.
  Coverage bookkeeping lives in `research_output.json`; in the report, name
  only what is partial or missing — never label a section "covered".
- 4 mixes prose with tables for endpoint and design-parameter comparisons.
- 5 is structured per trial, each entry ending on the lesson for future
  design.
- Frame every section from the patient population's perspective (see
  SKILL.md framing).
- Sources appendix: continuous numbering, grouped under bold source-type
  subheadings, title as hyperlink, accessed date closing each entry.
- Figures only when a chart shows what prose cannot. After rendering, `Read`
  the image and check: does it add information, are title/axes/units/legend
  legible, do tick marks fit the data type (no fractional years or counts)?
  Any "no" deletes the figure.

Then write `research_output.json` (consolidated structured output, format in
`waypoints.md`) and finally flip `progress.json` to complete — report first,
progress flag last.
