# Classification Confidence Assessment

**Case Attribution Rule:** Do not quote or attribute a specific holding
to a case unless the opinion text (or a reliable secondary source such
as Justia, Google Scholar, or a court website) was retrieved in-session.
If the case was NOT retrieved, describe the doctrine generically and
label case mentions as "commonly cited for [principle]" rather than
asserting exact holdings or quoting language.

---

## Section 1: Confidence Scoring

Assign one of three confidence levels to every classification recommendation. The level reflects how defensible the classification would be if challenged.

### High Confidence

**ALL** of the following must be true:
- GRI 1 resolves the classification unambiguously
- Heading text clearly describes the product
- Section/chapter notes do not create ambiguity
- Two or more consistent CROSS rulings with High factual similarity
- No adverse CIT/CAFC authority
- No conflicting rulings
- Single candidate heading after GRI 1 analysis

**Presentation:** State the confidence level and the supporting factors. No special flags required.

### Moderate Confidence

**ANY** of the following is present:
- GRI 1 resolves but required interpretive analysis (common meaning hierarchy, EN reliance)
- GRI 3(a) resolved the classification (specificity analysis required judgment)
- CROSS support exists but with Medium factual similarity
- Only one CROSS ruling on point
- Minor open questions remain (e.g., ambiguous statistical suffix)
- EN supports the classification but no CROSS directly on point

**Presentation:** State the confidence level, identify the specific factors that prevent High confidence, and recommend a CBP binding ruling request for high-value or recurring shipments.

### Low Confidence

**ANY** of the following is present:
- GRI 3(b) essential character was dispositive and factors were split
- GRI 3(c) or GRI 4 was reached
- Conflicting CROSS rulings exist
- CIT/CAFC authority cuts against the recommended classification
- No CROSS rulings at all for this product or analogous merchandise
- Heading text is genuinely ambiguous after full interpretive analysis
- Product straddles two Sections of the HTSUS

**Presentation:** State the confidence level, identify all contributing factors, and trigger attorney review per `references/human-review-triggers.md` Trigger #12. Recommend a binding ruling request before entry.

---

## Section 2: Controversy Detection Checklist

Run this checklist after completing the classification analysis. Check each indicator that applies.

### Structural Indicators
- [ ] Three or more candidate headings identified
- [ ] Candidate headings fall in different Sections of the HTSUS
- [ ] Resolving GRI is 3(b) or higher (3(c), 4)
- [ ] Ambiguous chapter notes that could include or exclude the product
- [ ] Product is a composite good or combination article

### Authority Indicators
- [ ] Conflicting CROSS rulings on analogous products
- [ ] Most relevant CROSS ruling is more than 10 years old
- [ ] CIT/CAFC decision exists on distinguishable but related facts
- [ ] CIT/CAFC authority undermines CBP's approach to this heading
- [ ] No precedent at all (no CROSS, no court decisions)

### Commercial Indicators
- [ ] Novel product with no established classification history
- [ ] Industry with frequent classification disputes (electronics, textiles, food/pharma)
- [ ] High duty differential between candidate headings (>5 percentage points)
- [ ] Chapter 99 surcharges depend on which heading is selected

### Scoring

| Indicators Checked | Controversy Level | Action |
|--------------------|-------------------|--------|
| 0–1 | **Low** | No special action required |
| 2–3 | **Moderate** | Cap confidence at Moderate. Recommend CBP binding ruling |
| 4+ | **High** | Cap confidence at Low. Flag for attorney review per `references/human-review-triggers.md` |

---

## Section 3: Burden of Proof Awareness

Understanding who bears the burden of proof informs how confident the classification recommendation should be.

### At CBP (Pre-Litigation)

The importer bears a **reasonable care** burden under 19 U.S.C. § 1484. The importer must use reasonable care in classifying merchandise and providing information to CBP. Failure to exercise reasonable care can result in penalties under 19 U.S.C. § 1592.

### At CIT (Litigation)

CBP's classification carries a **presumption of correctness** under 28 U.S.C. § 2639(a)(1). The importer challenging CBP must prove the classification wrong.

### Impact on Confidence Assessment

- **Recommended classification AGREES with likely CBP position** → The presumption of correctness supports the recommendation. This is a positive confidence factor.
- **Recommended classification DISAGREES with likely CBP position** → The importer would bear the burden at CIT to prove CBP wrong. This is a negative confidence factor. Flag the evidentiary requirements: What specific evidence would the importer need to overcome the presumption?

### Contra Proferentem Interaction

If the classification conclusion depends on contra proferentem (ambiguity resolved in favor of the importer), this canon alone is insufficient to overcome CBP's presumption of correctness at CIT. The importer would need affirmative evidence beyond mere ambiguity. Flag for attorney review per `references/human-review-triggers.md`.
