# Gotchas

High-signal failure modes the skill must guard against. Keep this file reactive and scannable.

## Article 2 numbering trap

The numbering inside Article 2 is non-obvious. These five definitions are commonly miscited:

- **(30) "customer"** - NOT switching, NOT exportable data.
- **(32) "digital assets"** - NOT exportable data.
- **(34) "switching"** - the actual switching definition.
- **(37) "functional equivalence"**.
- **(38) "exportable data"** - for Articles 23 to 31 and Article 35.

Always verify the point number against `assets/source/regulation-2023-2854.md` before citing.

## Article 31 vs Article 32 confusion

- **Article 31** - "Specific regime for certain data processing services": lighter regime for custom-built and non-production test/beta DPS.
- **Article 32** - "International governmental access and transfer": third-country access regime for non-personal data.

When the user says "the cloud third-country access article," they mean 32, not 31.

## Functional equivalence is IaaS-only

- **30(1) functional equivalence** - IaaS only.
- **30(2) open interfaces** - PaaS and SaaS.
- **30(3) interoperability standards** - PaaS and SaaS, with a 12-month compatibility horizon after standards are published.

Do not assert SaaS providers owe functional equivalence. They do not. See FAQ Q58a.

## DPS time windows are distinct

- **Notice period** - up to 2 months from the customer's switching request.
- **Mandatory transitional period** - 30 calendar days, starting after the notice period ends.
- **Minimum retrieval period** - at least 30 calendar days, starting after the transitional period ends.
- **Technical-infeasibility extension** - provider must justify in writing within 14 working days; alternative transitional period is up to 7 months.
- **Customer extension right** - customer may extend the transitional period once.

## Reduced switching charges window closes 12 January 2027

- **11 January 2024 to 12 January 2027** - reduced switching charges allowed; cannot exceed direct switching cost.
- **From 12 January 2027** - no switching charges for the switching process.

Standard service fees and early-termination penalties remain permitted in either window.

## Article 50 cohort dates

| Date | Trigger | Source |
|------|---------|--------|
| **12 September 2025** | General application date. Chapter II rights start. Chapter VI applies in full to all DPS contracts with no grandfather. Chapter III data-availability obligations from this date forward. Chapter IV applies to B2B data-sharing contracts concluded after this date. | Art. 50 |
| **12 September 2026** | Article 3(1) access by design applies to connected products and related services placed on the market after this date. | Art. 50 |
| **12 January 2027** | All switching charges prohibited for the switching process itself. | Art. 29(1) |
| **12 September 2027** | Chapter IV only. Applies to pre-existing B2B data-sharing contracts concluded on or before 12 September 2025 that are indefinite or expire at least 10 years from 11 January 2024. | Art. 50 |

Do not apply the 12 September 2027 grandfather to Chapter VI DPS switching obligations.

## Article 3(1) does not mandate direct access for everything

Article 3(1) requires direct access only "where relevant and technically feasible." FAQ Q22 confirms manufacturer discretion. Indirect access on simple electronic request can be sufficient.

## Data Act is not a GDPR Article 6 legal basis

When the user is not the data subject, the Data Act does not provide a GDPR Article 6 legal basis for disclosing personal data. The data holder must establish a separate basis or anonymise the data.

## GDPR prevails on conflict

In any conflict between the Data Act and the GDPR concerning personal data, GDPR prevails under Art. 1(5). See `references/gdpr-overlay.md` for depth.

## Trade-secret ladder cross-check

For trade-secret withholding or refusal, use `references/trade-secret-ladder.md`. Do not skip the ladder.

## The Commission FAQ is not authoritative

Frame FAQ reliance as the Commission's interpretation, not binding.

## Article 5(3) - DMA gatekeepers are excluded as third parties

DMA gatekeepers cannot be eligible third parties under Article 5. Third-party transfer flows should include a recipient attestation that it is not a designated gatekeeper.

## Article 4(10) - user non-compete and no insights about the manufacturer

The user may not use requested data to develop a competing connected product, share with a third party with that intent, or derive insights about the manufacturer's or data holder's economic situation, assets, or production methods.

## Article 4(13) - data holder needs a contract to use non-personal data

A data holder may use readily available non-personal data only on the basis of a contract with the user and may not derive insights that could undermine the user's commercial position.

## Sectoral lex specialis may pre-empt or override

Sectoral instruments may impose stricter, additional, or alternative obligations. Use `references/sectoral-overlays.md` for the warning gate.

## Member-state implementing law and competent authority vary

Article 37 designates competent authorities at member-state level. Penalty regimes and enforcement posture can vary; verify member-state law before relying on penalty figures.

## "Without undue delay" has no numeric SLA

The Regulation does not set a numeric time limit for Chapter II responses. Do not invent a day-count deadline.

## Prototypes are out of scope, but early commercial products are not

FAQ Q7 excludes un-finalised prototypes that have not completed manufacturing. A first commercial release is not out of scope on that basis.

## "Customised tenant" is not "custom-built service"

A multi-tenant SaaS with customer-specific configuration is not "custom-built" under Article 31(1).

## Article 4(2) safety/security restriction is narrow

Art. 4(2) lets the data holder contractually restrict or prohibit access, use, or further sharing where processing the data could undermine **security requirements of the connected product**, as laid down by Union or national law, resulting in a serious adverse effect on the health, safety, or security of natural persons. On refusal, notify the Art. 37 competent authority.

Do not present Art. 4(2) as a five-item checklist. The statutory hooks are: (a) a product-security requirement under Union or national law, (b) processing that would undermine it, (c) serious adverse effect on natural persons, and the procedural notification duty on refusal. Wrap the analysis around the regulation's words, not a manufactured list.

Do not conflate Art. 4(2) with Art. 1(6). Art. 4(2) is about **product-security requirements** under sectoral or horizontal product law (medical device cybersecurity, automotive cybersecurity, etc.). Art. 1(6) is about **Member State competence over public security, defence and national security**. Different scopes, different operative consequences.

## Chapter VI does not catch every connected-product service

Chapter VI applies to "data processing services" as defined in Art. 2(8): a service enabling on-demand network access to a shared, scalable, elastic pool of computing resources. Cloud / edge / IaaS / PaaS / SaaS-style offerings.

A telemetry portal, fleet-ops dashboard, or diagnostic backend bundled with a connected product is usually a **related service** (Art. 2(6)), not a DPS. Same offering can be both, but it is not automatic. Test Art. 2(8) against stated facts before applying Chapter VI switching, fees, or international-access rules.

## Often-missed provisions

- **Article 11** - technical protection measures may back confidentiality controls; users and third parties must not circumvent them.
- **Article 25(5)** - customer may extend the transitional period once.
- **Article 25(4)** - provider has a 14-working-day window to justify technical infeasibility.
- **Article 26(b)** - DPS public register of data structures, formats, standards, and open interoperability specifications.
- **Article 28(2)** - website URL must be listed in every DPS contract.
- **Article 29(4)-(6)** - pre-contract and public fee disclosure during the reduced-charges window.
- **Article 31** - custom-built and test/beta carve-outs have different scope and disclosure duties.
- **Articles 8 and 9** - data-recipient terms (Art. 8 fairness conditions) and compensation (Art. 9) sit between data holder and data recipient. Art. 5 transfer is free to the user but the commercial side with the third-party recipient lives in Arts. 8 and 9. Surface this whenever the deliverable touches third-party transfer mechanics.
- **Article 27** - destination providers also owe good-faith cooperation in switching.
- **Article 5(1)** - direct user access does not extinguish the Art. 5 third-party-transfer obligation.
- **Recital 31 final sentence** - Data Act trade-secret refusal does not displace GDPR access rights.
- **Article 7** - SME and micro-enterprise carve-outs require size and condition checks.
- **Article 12** - member-state law may extend Chapter II to SMEs in specific sectors.
