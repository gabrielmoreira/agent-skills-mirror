# Method

This file controls analysis method. Use it before drawing regulatory conclusions.

## Test definitions limb by limb against stated facts

Articles 2(5), 2(6), 2(8), and 2(13) each have multiple independent limbs. Walk each limb against what the lawyer actually said. If a limb is not established by stated facts, it is an open question - not a conclusion.

Do not infer limbs from product type, product name, or analogy. "It is a vehicle therefore it has telemetry" or "it is a smart device therefore it generates use data" are assumptions, not analysis.

Common circular trap: the lawyer confirms a related service exists, and the skill concludes the underlying product is a connected product on that basis alone. Art. 2(6) presumes Art. 2(5); using one to prove the other is circular. Test Art. 2(5) directly.

## Separate fact categories

Distinguish three categories of fact in any analysis:

- **Stated** - the lawyer said this directly.
- **Reasonable inference** - drawn from stated facts. Label it as an inference.
- **Assumption** - needed to proceed but not stated.

Surface every assumption in a "Facts assumed" or "Open questions" section. Never present an assumption as a conclusion.

## Front-load role mapping when side-advised is non-trivial

If the lawyer's role under the regulation is genuinely uncertain, produce a small table at the top of the deliverable before the full analysis:

| Role | Trigger | Consequence |
|------|---------|-------------|
| Importer-as-manufacturer | [stated fact or open question] | [consequence] |
| Distributor | [stated fact or open question] | [consequence] |
| Data holder via related-service operation | [stated fact or open question] | [consequence] |
| DPS provider | [stated fact or open question] | [consequence] |

Use only roles that are live on the facts.

## Run distributor-vs-manufacturer triage first

Before assuming data-holder status, confirm whether the EU-side entity places the product under its own name under the Art. 2 manufacturer chain or merely resells.

If the lawyer says "exclusive distributor," that is ambiguous. Ask the swing question before going further: own brand vs reselling under manufacturer's brand.

## Walk the trade-secret ladder

Refusal under Art. 4(8) or 5(11) without first attempting Art. 4(6) or 5(9) - identify + measures + disclose - is procedurally defective. The default position under Recital 31 is disclosure with measures.

Use `references/trade-secret-ladder.md` for the full ladder and templates.

## Check Art. 13 whenever contracts are touched

T&Cs, dealer agreements, fleet-portal terms, third-party data-sharing agreements, and audits should include an Art. 13 review.

Use `references/art-13-unfair-terms.md` for the unfair B2B terms test.

## Verbatim citations only

Quote from `assets/source/regulation-2023-2854.md` and `assets/source/faq-v1.4.md`. Never paraphrase from memory. If a needed Article, Recital, or FAQ Q-number is not in the source files, report a skill defect - do not fall back to general knowledge.

First citation in any document uses the full title: Regulation (EU) 2023/2854 of the European Parliament and of the Council of 13 December 2023 on harmonised rules on fair access to and use of data and amending Regulation (EU) 2017/2394 and Directive (EU) 2020/1828 (the "Data Act"), Article 3(2).

Subsequent citations use the short form: Data Act, Art. 3(2), or, where unambiguous, Reg. Art. 3(2).

Always include the sub-point when one exists: write Art. 25(2)(d), never Art. 25(2)d or Art. 25.2.d.
