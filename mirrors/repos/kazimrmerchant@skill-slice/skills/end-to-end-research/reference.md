# End-to-End Research — Reference

The encyclopedia companion to `SKILL.md`. Load sections on demand; the playbook tells you when. Section numbers here are cited from the playbook (e.g., "reference.md §4").

---

## 1. Query Design Patterns

### 1.1 The broad → narrow ladder

Run queries in this order per sub-question; each rung informs the next:

1. **Orientation** — the topic in plain words. Purpose: learn the field's vocabulary, not to collect sources yet.
2. **Vocabulary-corrected** — re-query with the field's own terms discovered in step 1 ("vector database" → "ANN index", "HNSW", "payload filtering").
3. **Narrowed** — add qualifiers per sub-question: version, year, platform, constraint ("qdrant memory usage 5 million vectors self-hosted").
4. **Adversarial** — actively hunt disconfirmation: `X problems`, `X vs Y`, `X criticism`, `migrating away from X`, `X postmortem`. Every SQ gets at least one.
5. **Verification** — exact quotes, specific numbers, named entities, to trace provenance ("\"37% of respondents\" survey source").

### 1.2 Anchor discipline

Identify the **head anchors** — the rare, discriminating terms in the question (product names, acronyms, technical terms). Rules:

- Every query variant keeps ≥1 anchor verbatim or via a known alias. Expansion that drops the anchor is a random walk that returns sludge.
- Maintain an alias list per run (`MCP` ↔ "Model Context Protocol"; `GDExtension` ↔ "godot-cpp"). Aliases count as anchors.
- Apply the anchor test before fetching: does the result actually concern the anchor, or just the generic words around it?

### 1.3 Operator toolbox

| Operator | Works on | Use for |
|---|---|---|
| `"exact phrase"` | all major engines | pin multiword anchors; find the origin of a quote |
| `site:domain.com` | Google, Bing, DDG | constrain to official docs or one publisher |
| `-term` | Google, Bing, DDG | strip a dominant wrong sense (`jaguar -car`) |
| `filetype:pdf` | Google, Bing | papers, reports, filings, slide decks |
| `intitle:term` | Google, DDG | topic is the *subject* of the page, not a mention |
| `OR` | most engines | alias fan-out in one query (`"WFC" OR "wave function collapse"`) |
| `before:YYYY-MM-DD` / `after:` | Google | temporal window |
| `*` wildcard | Google | unknown middle term in a phrase (`"X raised * million"`) |

Caveats: engines silently ignore or rewrite operators under load — spot-check that results actually respect the constraint. DDG and Bing support fewer operators than Google; don't assume parity.

### 1.4 Temporal filtering

Three layers, most reliable last:

- **Engine-native**: Google `before:`/`after:` or date-range tools; use for first-pass narrowing.
- **Platform-native**: HN Algolia `numericFilters=created_at_i>…`, Reddit `t=week|month|year`, GitHub `created:>2026-01-01` / `pushed:>`.
- **Post-hoc**: extract dates from fetched pages and filter yourself — the only layer you fully control.

Date hygiene: **published ≠ last-updated ≠ accessed.** Capture all three when available. For undated pages: check page metadata (`article:published_time`), the sitemap, or the Wayback Machine's first snapshot as an upper bound on age.

### 1.5 Platform dialects

| Platform | Query shape | Notes |
|---|---|---|
| GitHub | `topic in:name,description,readme stars:>100 pushed:>2026-01-01` | code search is aggressive about auth/rate limits — route through `multi-platform-agent-reach` for volume |
| HN (Algolia) | `https://hn.algolia.com/api/v1/search?query=X&tags=story&numericFilters=created_at_i>TS` | the comments carry the signal; fetch the top 1–3 threads, not just titles |
| arXiv | `site:arxiv.org "term"` or the arXiv API (`all:X AND cat:cs.XX`) | preprints — always label unreviewed; check for a later published version |
| Google Scholar | quoted phrase + custom year range | citation counts measure influence, not truth |
| Reddit | prefer `multi-platform-agent-reach` routing | native search is weak; sort=new + time filter when direct |
| Stack Overflow | `[tag] "exact error text"` | answers rot fast — check answer dates against current versions |
| Vendor docs | `site:docs.vendor.com term` + version qualifier | verify the docs version selector matches the version under study |
| Wayback | `web.archive.org/web/*/URL` | pricing-page history, deleted posts, dating undated pages |

### 1.6 Query plan format

Write the plan before running it; log status per query as you go:

```
SQ2: What are Qdrant's operational requirements at ~5M vectors?
  Q2.1 [broad]        qdrant memory requirements million vectors        → served (3 new)
  Q2.2 [narrow]       qdrant capacity planning site:qdrant.tech         → served (1 new, T1)
  Q2.3 [adversarial]  qdrant problems OR outage OR "ran into" self-hosted → served (2 new, T3)
  Q2.4 [platform]     HN: qdrant, last 12mo, top threads                → no-new (saturation signal)
```

### 1.7 Negative results are data

"No results for X since 2025" is a finding, not a failure. Record it — it supports claims of abandonment, rarity, or novelty. Always distinguish **searched-and-absent** (evidence) from **didn't-search** (a gap for the coverage manifest).

---

## 2. Source Typology

### 2.1 Distance from the event

- **Primary** — the artifact itself: source code, filing, dataset, announcement, transcript, the paper reporting original work.
- **Secondary** — reporting or analysis of primaries: press coverage, reviews, survey papers.
- **Tertiary** — aggregations: encyclopedias, awesome-lists, LLM answers. Navigation aids only — follow them to the underlying source and cite *that*.

### 2.2 Type characteristics

| Type | Typical tier | Strengths | Weaknesses | Verify by |
|---|---|---|---|---|
| Official (docs, announcements, filings) | T1 | authoritative for its own facts | marketing gravity; silent about weaknesses | date/version check; adversarial queries elsewhere |
| Academic (papers) | T1–T2 | methodology, data, rigor | publication lag; preprints unreviewed; benchmarks age | venue quality; citations; replication mentions |
| Press | T2–T3 | synthesis, access to actors | compression errors; press-release laundering | trace to the primary it cites |
| Docs / changelogs | T1 | ground truth for intended behavior | docs drift from code | check version; check the repo when critical |
| Code / repos | T1 | can't lie about what it does | reading effort; a default isn't a recommendation | read tests and issues, not just README |
| Datasets / statistics | T1–T2 | quantitative anchor | definitions and methodology vary wildly | read the methodology note before the number |
| Social / forums | T3–T4 | early signal; practitioner truth; failure reports | unvetted, unrepresentative, gameable | corroborate; check author history/expertise |
| Blogs | T2–T4 | depth and opinion | variance is extreme; SEO farms mimic the form | author expertise; is original evidence present? |
| Video / talks | T2–T3 | demos; conference-grade material | hard to quote precisely | pull the transcript; then treat like a blog |

### 2.3 Independence

Two sources are independent iff neither derives from the other or from a shared origin. Tests that reveal a shared origin (→ same `independence_group`):

- They cite the same upstream document or spokesperson.
- Published within hours of each other with identical numbers or phrasing (wire story).
- One is a translation, syndication, or summary of the other.

Ten articles quoting one press release = one independence group = one source for triangulation purposes.

---

## 3. Evidence Grading (A–E)

| Grade | Definition | Deliverable language |
|---|---|---|
| **A** | ≥2 independent T1/T2 groups agree; no credible contradiction | state as fact: "X is…" |
| **B** | one T1, or ≥2 independent T2/T3 groups | light attribution: "per the docs…", "X reports…" |
| **C** | single T2/T3, plausible, uncontradicted | "reportedly", "according to <source>" |
| **D** | T4 convergence only, or T3 with a conflict of interest | "circulating but unverified" — include only if decision-relevant |
| **E** | single T4/T5, contested with no resolution, or model-knowledge only | never assert; list under Open Questions or as disputed |

**Downgrade triggers** (apply immediately, re-grade the claim):
- Source turns out older than the claim's volatility horizon.
- Conflict of interest discovered after registration.
- A quote can't be re-found at the gate spot-check.
- Independence collapse — two supporting sources turn out to share an origin.

**Upgrade path:** only by adding evidence. Never by rewording the claim or the citation.

---

## 4. Contradiction Resolution Protocol

Run when two registered sources disagree on a claim. In order:

1. **Re-read both in context.** Half of apparent contradictions are scope mismatches — different versions, regions, definitions, or dates.
2. **Time-order them.** A newer primary usually supersedes an older one. A newer T4 does *not* supersede an older T1.
3. **Trace provenance.** If both derive from the same origin, it's a transcription error somewhere in the chain, not a contradiction — find and cite the origin.
4. **Check definitions and units.** "Users" vs "MAU" vs "registered accounts"; GB vs GiB; ARR vs revenue; "free" vs "free tier".
5. **Check incentives.** Vendor vs competitor vs regulator. Weight statements *against* interest heavily (a vendor admitting a limitation is strong evidence).
6. **Escalate to a primary you haven't fetched yet** — filing, source code, dataset, original transcript.
7. **Resolve or present.** Three legal outcomes:
   - **Resolved** — keep the winner; record the loser in the claim's `contradicted_by` with the resolution reason.
   - **Disputed** — present both, weighted:
     ```
     DISPUTED — <claim statement>.
     Position 1 (<sources, tiers>): <summary>
     Position 2 (<sources, tiers>): <summary>
     Assessment: <which is better-evidenced and why, or "insufficient to adjudicate">
     Resolves when: <the falsifier — e.g., "next quarterly filing publishes">
     ```
   - **Never average.** Two contradictory numbers do not have a meaningful midpoint.

---

## 5. Competitive Analysis Framework

### 5.1 Snapshot checklist (per company)

- **Identity** — what they sell, to whom; one-line positioning in *their* words plus your restatement.
- **Product** — core capabilities, platforms, pricing model and current prices (volatile → `as_of` + `recheck_after`).
- **Traction proxies** — headcount trend (LinkedIn), open roles (what they're building next), GitHub activity if OSS, review volume *and velocity* (G2/Capterra/Steam as relevant), app-store ranks, web-traffic tier.
- **Money** — funding rounds, investors, revenue statements (type: `claim`, almost never verifiable for private companies).
- **GTM** — channels, partnerships, the ICP evident from case studies.
- **Moat & risks** — what's defensible; what's threatened.
- **Recent moves** — last 6–12 months: launches, pivots, key departures, pricing changes.

### 5.2 Where to look

| Signal | Source | Notes |
|---|---|---|
| Pricing history | Wayback Machine on `/pricing` | pricing changes *are* strategy |
| Roadmap | changelog, public roadmap, job posts | job posts leak roadmaps reliably |
| Health | layoff trackers, exec departures, review-site sentiment trend | each noisy alone — triangulate |
| Customer truth | reviews filtered to recent + detailed + verified | ignore star averages; read the 1–2★ and 4★ *text* |
| Team | LinkedIn company page, eng blog authorship | headcount *trend* beats headcount |
| Tech stack | job-post requirements, GitHub, eng blog | |

### 5.3 Feature matrix method

Rows = **jobs-to-be-done** (user needs), never vendor feature names. Columns = competitors. Cells = does-it / how-well / evidence id. Build the rows from user needs *first*, then fill — this prevents the frame capture where the market leader's feature list becomes your evaluation criteria.

### 5.4 Ethics line

Public information only. No pretexting (fake sales calls, fake job applications), no scraping behind logins, no soliciting material that's under NDA. If a fact is only knowable through those routes, it goes in Open Questions.

---

## 6. Market Research Framework

1. **Define the market precisely before sizing it**: product category × geography × buyer × time period. Most sizing disagreements are definition disagreements.
2. **Top-down** (analyst total × addressable fraction): fast, but laundered — "the market is $X B" quotes usually trace to 1–2 analyst reports feeding 200 articles (one independence group). Always find the analyst's methodology and base year.
3. **Bottom-up** (number of buyers × adoption rate × price): slower, defensible, forces explicit assumptions. Show the arithmetic in the deliverable so the reader can attack the assumptions, not the conclusion.
4. **Triangulate**: run both. Disagreement >3× means your market *definition* is wrong, not the math.
5. **Proxy signals** when direct numbers don't exist: search-volume trends, community sizes and growth rates, job postings naming the category, conference attendance, platform category revenues (App Store / Steam).
6. **Sanity checks**: does implied revenue-per-customer make sense? Does the claimed CAGR imply the entire population buys by 2030?
7. **Label every number**: source, base year, definition, grade. Market-size numbers are almost never grade A — say so in the deliverable.

---

## 7. Technical Due Diligence Framework

For evaluating a library, tool, or vendor before adoption:

- **Maintenance** — commit cadence (last 90 days), release cadence, bus factor (top-2 committer share of recent commits), median first-response time on recent issues, open:closed issue trend.
- **Adoption** — download trend (npm/PyPI weekly), dependents count, *named* production users (testimonials with company names beat stars). Stars measure marketing reach, not usage.
- **Security** — CVE history and fix latency, presence of a security policy and advisory feed, dependency freshness.
- **License** — exact SPDX identifier; copyleft implications for *your* distribution model; CLA presence; license *changes* in history (relicensing to BSL/SSPL-style terms is a live risk pattern — check the git history of the LICENSE file).
- **Docs & DX** — does the quickstart actually work (run it if cheap); do migration guides exist; is there breaking-change discipline in the changelog.
- **Community & governance** — maintainer responsiveness and tone, fork activity, governance model (single-vendor OSS means product decisions follow the vendor's business needs).
- **Benchmarks** — all vendor benchmarks are T3 *comparative* claims. They earn T2 only with: full config disclosure, competitors tuned (not defaults), public dataset, and independent replication. Absent those, they're marketing.
- **Exit cost** — data export path, API surface concentration, self-host option. Write the exit paragraph *before* recommending adoption.

Minimum evidence set: the repo (T1), a sample of recent issues (T1), ≥2 practitioner reports (T3), the changelog (T1).

---

## 8. Academic / Literature Review Protocol

1. **Seed** — 2–3 recent surveys or highly-cited papers (Scholar / Semantic Scholar; query `survey OR review` + topic).
2. **Snowball** — backward (their references) and forward (papers citing them), 1–2 hops.
3. **Screen** — title/abstract pass against inclusion criteria *written down before screening*: topic bounds, year range, venue class, method type.
4. **Venue quality** — peer-reviewed venue > workshop > preprint. Preprints are citable but labeled unreviewed; check whether a published version supersedes them.
5. **Extract per paper** — problem, method, data, headline result *with its conditions*, limitations the authors admit, limitations you observe.
6. **Extraction table** — `paper | year | venue | method | dataset | key result | caveats | grade`.
7. **Synthesize by theme, not by paper** — where does the field agree, disagree, and stay silent? The silences are often the finding.
8. **Saturation** — stop snowballing when new papers stop introducing references you haven't already seen.
9. **Report PRISMA-lite counts** — found → screened → included, with exclusion reasons. This is your coverage manifest for literature.

---

## 9. Fact-Checking Protocol

1. **Decompose** the claim into atomic checkable statements: who / what / when / where / how much. Verify each separately — compound claims hide false conjuncts inside true ones.
2. **Provenance trace** — find the FIRST assertion: search exact phrases, sort by earliest date, follow citation chains upstream. The origin's tier bounds the claim's maximum grade.
3. **Lateral reading** — leave the source; check what *other* sources say about this source and this claim, before reading more of the source itself.
4. **Hunt counter-evidence explicitly** — adversarial queries (`"<claim>" debunked`, `"<claim>" false`, the negation phrased naturally).
5. **Specifics by kind**:
   - Numbers → the original dataset or report, its definition, its base year.
   - Quotes → the original context (full transcript or video); verify attribution, not just wording.
   - Images → reverse image search; earliest appearance; check whether it depicts a different event.
6. **The first-report trap** — breaking claims mutate as they spread, and "multiple outlets report" is usually one wire story (one independence group). Grade above D requires a second *independent* confirmation, not a second copy.
7. **Verdict scale**: **Confirmed** (independent primaries) / **Mostly true** (accurate core, wrong details — list them) / **Mixed** / **Unsupported** (no evidence found, none against) / **False** (contradicted by primaries) / **Unverifiable** (evidence inaccessible — say why).
8. **Report the verdict WITH the evidence chain** so the reader can audit the reasoning, not just trust the label.

---

## 10. Output Templates

### 10.1 Executive brief (quick tier default)

```markdown
# <Question> — Brief
As-of <date> · Confidence <HIGH|MODERATE|LOW> · <n> sources (<k> independent groups)
**Answer:** <2–4 sentences with [S-###] cites>
**Key facts:**
- <cited, dated bullet> [S-001]
- <cited, dated bullet> [S-003]
**Caveats:** <what's uncertain, volatile, or unchecked>
**Sources:** <numbered registry: title · publisher · date · tier · url>
```

### 10.2 Full report (deep tier)

```markdown
# <Title>
As-of · tier · confidence ceiling · COVERAGE manifest (classes ok/planned, failures)
## Executive summary        (answer + top 3 findings)
## Background & scope       (the intake block, verbatim)
## Findings by sub-question (claims with evidence, graded; disputed items in DISPUTED format)
## Conflicts & resolutions
## Open questions & recommended next steps
## Method note              (queries run, platforms used, what failed — auditability)
## Claims table             (full, schema-shaped)
## Source registry
```

### 10.3 Decision memo

```markdown
# Decision: <the choice to make>
**Recommendation:** <one line> (confidence <H/M/L>)
**Options considered:** | option | fit to criteria | key evidence | risks |
**Why <winner>:** 3–5 cited reasons
**What would change this:** falsifiers and watch items with recheck dates
**Reversibility & exit cost:** <paragraph>
```

### 10.4 Annotated bibliography

Per source: full citation · tier · 2–3 sentence annotation (what it contributes, its bias or limits) · which claim ids it supports. Sort by contribution, not alphabet.

---

## 11. Failure Modes & Recovery

| Failure | Symptom | Recovery |
|---|---|---|
| Relevance sludge | results match generic words, not the anchor | tighten anchors, add `-negatives`, switch engine, platform-route |
| Zero results | genuinely nothing returns | translate to field-native vocabulary; drop the rarest qualifier one at a time; log "searched and absent" as data |
| Rate-limited / 403 | fetches failing on a platform | back off, use an alternate platform for the same source class, log in coverage — never silently drop the sub-question |
| Paywall | key source inaccessible | abstract, press release, Wayback snapshot, author's own copy (personal site / institutional repository), quote inside a secondary — mark grade accordingly; never fabricate contents |
| Contradiction deadlock | §4 protocol exhausted | ship as DISPUTED with weights and a falsifier ("resolves when …") |
| Source vanishes mid-run | 404 on gate re-check | Wayback; if unarchived, downgrade the claim and note it |
| Budget exhausted | tier ceiling hit with SQs open | deliver partial: answered SQs at full rigor + explicit gaps + offer continuation. Never dilute the gate to "finish" |
| Topic too fresh | only T4 sources exist yet | say so; verdict "unverified — circulating"; set `recheck_after` |
| LLM-content contamination | AI-generated pages dominate results | prefer dated primaries; platform-route to human communities; slop signatures: no author, no dates, generic phrasing, internally inconsistent specifics |
| Context compaction risk | long deep-tier run | persist checklist + claims table to a working file after every phase |

---

## 12. Legal & Ethical Boundaries

- **Public information only.** No login-walled scraping, no credential misuse of any kind, no CAPTCHA or anti-bot circumvention, no user-agent spoofing to evade blocks.
- **Respect paywalls.** Use the legal alternates in §11. Never reproduce paywalled full text; keep quotations within fair-use proportions and always attribute.
- **Respect robots.txt and ToS** for automated fetching; keep request rates polite.
- **No pretexting.** Don't pose as a customer, journalist, or job candidate to extract non-public information.
- **PII restraint.** Don't compile dossiers on private individuals. Public-figure research sticks to information about their public role.
- **Quote honestly.** No quote mining; link the original context.
- **Leaked or breached material** that has surfaced publicly: don't fetch or quote it. If its *existence* is decision-critical, note that it exists, flag the provenance, and stop there.
