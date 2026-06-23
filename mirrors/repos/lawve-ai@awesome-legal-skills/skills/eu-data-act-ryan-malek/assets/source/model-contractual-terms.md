# Commission Recommendation on standard contractual clauses for data sharing and cloud computing contracts

Annex on model contractual terms / SCCs, 19 November 2025.

This file is a structured pointer to the published Recommendation. The Skill does not bundle the Recommendation in full because:

1. The document is lengthy and consists primarily of model clause text already optimised for direct copying.
2. Lawyers typically want to consult the canonical PDF directly rather than a re-keyed version.
3. The published version is freely available and updates may be published.

For authoritative drafting work, consult:

`https://digital-strategy.ec.europa.eu/en/library/standard-contractual-clauses-data-sharing-and-cloud-computing-contracts`

---

## Structure of the Recommendation

The Recommendation provides three sets of model clauses:

1. **B2B data-sharing clauses** — for use between data holder and data recipient (typically a third party authorised by the user under Art. 5).
2. **B2C / B2B clauses on data access** — covering the user-facing access regime (interaction with Art. 4 access).
3. **Cloud computing contractual clauses** — for use between DPS provider and customer (interaction with Art. 25 contract requirements).

For each set, the Recommendation publishes:
- A "must-have" core (mirroring regulation requirements).
- Recommended optional clauses.
- Drafting notes / explanatory commentary.

---

## How the Skill uses the Recommendation

The Skill's templates (in `assets/templates/`) reference but do not copy the Commission's clause text. Each template instead:

- States the operative regulation requirement (Art. 25 etc.).
- Provides drafting starter language consistent with the Commission's approach.
- Marks itself as "starting-point only" pursuant to the LICENSE disclaimer.

When a lawyer wants to align a Skill-produced draft with the Commission SCCs, the Skill recommends consulting the Recommendation's annex directly and adapting wording.

---

## Status

The Commission Recommendation is **non-binding**. Use of the model clauses is optional. However, parties that adopt the Commission's clauses benefit from a strong presumption of regulation-compliance for the matters covered.

---

## Drafting interactions with bundled Skill templates

| Skill template | Aligns with Recommendation set |
|----------------|---------------------------------|
| `dps-contract-clauses-art-25.md` | Cloud computing clauses |
| `precontract-disclosure-art-3-2.md` | B2B / B2C data access clauses (transparency portion) |
| `precontract-disclosure-art-3-3.md` | B2B / B2C data access clauses (related-service disclosures) |
| `trade-secret-confidentiality-agreement.md` | B2B data sharing — confidentiality measures section |
| `dps-public-page-art-28.md` | Cloud computing — international access disclosures |
| `international-access-customer-notice.md` | Cloud computing — international access notification |
