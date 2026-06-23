# Agentic Research Protocol

## Purpose

This protocol controls source selection, evidence quality, source freshness, and hallucination risk for all trade-law workflows. Use it before making any legal conclusion.

## Authority Hierarchy

Apply the hierarchy stated in `SKILL.md` and `references/formatting-standards.md`:

1. HTSUS legal text: headings, section notes, chapter notes, Additional U.S. Rules, GRIs.
2. CAFC decisions.
3. CIT decisions.
4. CBP HQ rulings.
5. CBP NY rulings.
6. CBP Informed Compliance Publications and official agency guidance.
7. Secondary commentary.

Secondary sources can orient research, but they cannot establish the holding of a court decision, the reasoning of a ruling, the current duty rate, or the scope of an agency requirement.

## Evidence Quality Labels

Use one of these labels for every source in the evidence ledger:

| Label | Meaning | Permitted Use |
|---|---|---|
| **Retrieved** | Full source text or data file was accessed and reviewed. | Can support legal conclusions and short quotations. |
| **Verified** | Full source text was retrieved and the relevant proposition was cross-checked against metadata, current status, or another official source. | Strongest support for conclusions, holdings, and quoted reasoning. |
| **Identified** | Source existence, citation, title, or metadata was found, but full text was not retrieved. | Can show a source exists; cannot support a holding, rate, or money quote. |
| **Unverified** | Source is mentioned by a search result, snippet, secondary source, or user-provided citation with no retrieval. | Use only as a lead or limitation; do not rely on it. |

For CROSS and court opinions, a "money quote" requires **Retrieved** or **Verified** status. For rates and HTS revision selection, prefer **Verified** status because currentness is part of the conclusion.

## Evidence Ledger

Maintain a compact ledger for every material conclusion:

```text
Evidence Ledger
- Conclusion: {classification / rate / origin / scope / PGA / UFLPA point}
- Source: {official title and URL}
- Authority level: {HTSUS / CAFC / CIT / CBP HQ / CBP NY / agency / secondary}
- Evidence label: {Retrieved / Verified / Identified / Unverified}
- Retrieval date: {date}
- Freshness: {current revision / current-year source / issue date / stale risk}
- Proposition supported: {what the source actually supports}
- Limitation: {if any}
```

For long deliverables, place the ledger in a source appendix and use short evidence notes in the main analysis.

## Source Freshness Rules

- **HTS:** Record selected revision, JSON URL, catalog checked/harvest date if available, and analysis date.
- **Chapter 99:** Verify current status and exclusions through official sources; rates and exclusions change.
- **CROSS:** Search live and retrieve individual rulings before relying on reasoning.
- **CIT/CAFC:** Retrieve opinion text and check subsequent history when it affects the conclusion.
- **AD/CVD:** Verify current order/scope and rates through Commerce/ITA, Federal Register, ACCESS, or official instructions when available.
- **MPF/HMF:** Verify current-year rates and thresholds; do not hard-code.
- **FTA/TAA/PGA/UFLPA:** Verify current official program or agency guidance.

## Retrieval Discipline

1. Start from official sources.
2. Use secondary sources only to identify primary sources or explain background when official sources are inaccessible.
3. If a source cannot be retrieved, state that limitation and downgrade the evidence label.
4. Do not infer a holding from a headnote, article, search result, or docket title.
5. Do not infer current legal status from an old ruling or notice without checking for revocation, modification, amendment, expiration, or appeal.

## Hallucination Controls

- Do not invent HTS text, ruling numbers, slip opinion numbers, AD/CVD case numbers, rates, effective dates, exclusion dates, or agency requirements.
- Do not "fill in" missing chapter notes from memory.
- Do not quote source language unless the source was retrieved.
- If search results disagree, present the conflict and resolve by authority hierarchy and freshness.
- When a current source is unavailable, state "not verified" rather than substituting a plausible rate or rule.

## Human Review Coupling

Run `references/human-review-triggers.md` after the evidence ledger is drafted. Trigger review when:

- Evidence is too weak for a legal conclusion.
- The conclusion depends on missing facts.
- Authorities conflict.
- The current status of a rate, exclusion, ruling, order, or agency requirement is unresolved.
