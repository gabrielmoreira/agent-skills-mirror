# CROSS Ruling Research Protocol

## Overview

The Customs Rulings Online Search System (CROSS) contains 219,915+ searchable CBP rulings spanning 1989 to present. This protocol defines how to search, evaluate, and present CROSS rulings in classification analysis.

---

## Search Protocol

### Step 1: Primary Search — Direct CROSS URL
Search CROSS directly using the search URL (returns current results sorted by date):
```
web_fetch("https://rulings.cbp.gov/search?term={product+keywords}&collection=ALL&commodityGrouping=ALL&sortBy=DATE_DESC&pageSize=30&page=1")
```
- URL-encode the search term (spaces as `+`)
- Use concise product keywords (e.g., `outdoor+gas+grill`, `bluetooth+keyboard`)
- `collection=ALL` searches both NY and HQ rulings; use `collection=HQ` or `collection=NY` to narrow

### Step 2: Heading-Specific Refinement
If the primary search returns too many or too few results, refine by adding the HTS heading to the search terms:
```
web_fetch("https://rulings.cbp.gov/search?term={product+keywords}+{4-digit+heading}&collection=ALL&commodityGrouping=ALL&sortBy=DATE_DESC&pageSize=30&page=1")
```
- Try alternative headings if the first returns no results
- Use `collection=HQ` to focus on authoritative Headquarters rulings

### Step 3: Ruling Detail Fetch
For each relevant ruling found, fetch the full ruling page:
```
web_fetch("https://rulings.cbp.gov/ruling/{RULING_ID}")
```
- Extract: product description, classification, GRI applied, key reasoning, date, status
- Check for revocation/modification notices in the ruling text
- This is the primary method for achieving **Verified** evidence quality (see Evidence Quality Protocol below)

### Additional Patterns
See `references/search-strategies.md` for the complete set of validated search patterns including Boolean syntax for the CROSS interface.

---

## Evaluation Criteria

For each ruling found, assess and record:

### A. Ruling Identity
- **Ruling number:** NY N______ or HQ H______
- **Date issued**
- **Status:** Active, Revoked, Modified
- **Collection:** NY (New York) or HQ (Headquarters)

### B. Product Comparison
- **Ruled product description:** What was classified?
- **Factual similarity:** How closely does the ruled product match the product under analysis?
  - **High:** Same product type, same materials, same function, same use
  - **Medium:** Same product type but different configuration, materials, or use
  - **Low:** Related product type but significantly different characteristics
- **Distinguishing facts:** What differences exist between the ruled product and ours?

### C. Legal Analysis
- **HTS classification assigned:** Full subheading
- **GRI applied:** Which GRI resolved the classification?
- **Chapter/Section Notes relied upon:** Specific notes cited
- **Explanatory Notes cited:** WCO EN references
- **Key reasoning:** The dispositive legal analysis

### D. Authority Assessment
- **HQ vs. NY:** HQ rulings carry greater weight (national scope, complex matters)
- **Recency:** More recent rulings better reflect current CBP practice
- **Consistency:** Does this ruling align with other rulings on similar products?
- **Judicial review:** Has a CIT/CAFC decision addressed this classification?

---

## Prioritization Rules

When multiple rulings are found, prioritize for presentation:

1. **HQ over NY** — Headquarters rulings reflect national-level CBP policy
2. **Recent over old** — Current practice may differ from past rulings
3. **Factually close over distant** — Direct product matches over analogous products
4. **Active over revoked** — But note revoked rulings for context (why was it changed?)
5. **Consistent cluster over outlier** — Multiple rulings reaching the same conclusion is stronger than a single ruling

---

## Conflict Detection

**CRITICAL:** When researching rulings, actively look for:

### Ruling-to-Ruling Conflicts
- Two or more active rulings classifying analogous products differently
- Action: Note both classifications, explain the factual distinctions, trigger the conflicting-rulings flag from `references/human-review-triggers.md`

### Ruling-to-Court Conflicts
- A CROSS ruling that classifies under a heading or analysis that has been rejected by CIT or CAFC
- Action: Note the conflict, cite the court decision, recommend the court's position as controlling, trigger the CIT-conflict flag from `references/human-review-triggers.md`

### Revocation Chains
- Ruling A was revoked by Ruling B, which was modified by Ruling C
- Action: Trace the complete chain. Only the final active ruling is controlling. Note the evolution of CBP's position.

---

## Evidence Quality Protocol

Every ruling found via web_search or CROSS search must be assigned an evidence quality level before citation. Use the labels in `references/agentic-research-protocol.md`:

| Evidence Level | Condition | Citation Treatment |
|---------------|-----------|-------------------|
| **Verified** | Full ruling text retrieved and status/revocation checked against CROSS or another official source | Cite with confidence; may extract short "money quotes" from retrieved text |
| **Retrieved** | Full ruling text retrieved, but current status or revocation chain not independently checked | May support analysis; note status limitation |
| **Identified** | Ruling number + HTS + product type visible, but reasoning not retrievable | Cite as identified only; confirm full text at `rulings.cbp.gov/ruling/{ID}` |
| **Unverified** | Ruling number, snippet, or secondary mention only | Note as a research lead; do not rely on for classification support |

**Key rule:** "Money quotes" — specific reasoning excerpts cited in analysis — require **Retrieved** or **Verified** evidence level. Snippet-only rulings are "Identified" at best; they support the existence of a ruling but cannot be quoted as authority for a specific legal conclusion.

When presenting rulings, always include the evidence quality level so reviewers know the basis for each citation.

Also add each material ruling to the evidence ledger with retrieval date, authority level (HQ or NY), status, and the proposition supported.

---

## Output Format

Present ruling research results as follows:

### For Each Ruling:
```
**CBP Ruling {NY/HQ} {Number} (dated {Date})**
- **Product:** {description of classified product}
- **Classification:** {HTS subheading}
- **GRI Applied:** {GRI number and brief explanation}
- **Key Reasoning:** {1-2 sentence summary of dispositive analysis}
- **Factual Similarity:** {High/Medium/Low} — {brief explanation}
- **Status:** {Active / Revoked by {ruling} / Modified by {ruling}}
- **Evidence Quality:** {Verified / Retrieved / Identified / Unverified}
```

### Summary Analysis:
After presenting individual rulings, provide:
1. **Consensus position:** What classification do the majority of rulings support?
2. **Outliers:** Any rulings that deviate, and why?
3. **Trend:** Is CBP's classification approach evolving for this product type?
4. **Gaps:** What aspects of the product are not addressed by existing rulings?
5. **Recommendation:** How do the rulings inform our classification analysis?

---

## Target: 3-5 Relevant Rulings

Aim for 3-5 rulings that collectively:
- Cover the recommended classification heading
- Address alternative headings considered
- Include at least one HQ ruling (if available)
- Span different factual scenarios within the product type
- Are active and current (or, if revoked, provide useful context)

If fewer than 3 relevant rulings are found, note this and trigger the "No CROSS Ruling History" flag from `references/human-review-triggers.md`.
