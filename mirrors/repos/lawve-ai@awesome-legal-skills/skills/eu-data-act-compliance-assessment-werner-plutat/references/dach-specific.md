# DACH-Specific Considerations - Germany, Austria, Switzerland

## Overview

The Data Act is an **EU Regulation** - directly applicable in all Member States without national transposition. However, **enforcement**, **designated authorities**, and **national implementation measures** vary.

This reference covers Germany, Austria, and Switzerland (DACH region) specifics.

## Germany

### Designated Authorities

**Market Surveillance Authority (Article 37-38):**
- **Bundeskartellamt (Federal Cartel Office)** - expected lead authority for Data Act enforcement under the draft German approach
  - Expertise in competition, market fairness, B2B contract regulation
  - Already enforces Digital Markets Act (DMA) in Germany
  - Likely competent for unfair contract terms (Chapter IV) and general data access obligations

**Sector-Specific Authorities:**
- **BNetzA (Federal Network Agency - Bundesnetzagentur):**
  - Telecommunications, energy, postal services
  - May have concurrent jurisdiction for data processing services in regulated sectors
  - Cloud switching and portability (Chapters VI-VII) for telecom/energy-adjacent services
- **BfDI (Federal Commissioner for Data Protection - Bundesbeauftragter für den Datenschutz und die Informationsfreiheit):**
  - GDPR-Data Act overlaps, especially personal data access rights and B2G requests involving personal data
  - Not primary Data Act authority, but coordination role where GDPR applies
- **Landesdatenschutzbehörden (State Data Protection Authorities):**
  - GDPR enforcement at state level
  - Relevant for B2G requests involving personal data at state/municipal level

**Coordination:**
- **Bundesregierung (Federal Government)** may issue implementing ordinances (Rechtsverordnungen) to clarify competences, penalties, or sector-specific rules

### Enforcement and Penalties

**Legal basis for penalties:**
- **Article 40 Data Act** requires Member States to establish effective, proportionate, and dissuasive penalties
- Germany is expected to implement this through a **Datendurchführungsgesetz (DADG)** or equivalent national implementing framework

**Germany's draft DADG approach:**
- **Administrative fines** up to **€5 million** for standard infringements
- Up to **2% of worldwide annual turnover** for entities designated as **DMA gatekeepers** in the relevant cases
- **Warning, cease-and-desist orders, corrective measures, and injunctions** for less severe or ongoing violations
- **Private enforcement:** Affected parties (users, data recipients, competitors) can bring claims in civil courts

**Critical correction:**
- The Data Act itself does **not** set an EU-wide 4% turnover cap
- Any turnover-based maximum comes from **national law**, not directly from the Regulation

**Criminal liability:**
- Unlikely for Data Act violations per se (administrative offense, not criminal)
- **Trade secret misuse** (if data holder or recipient violates confidentiality) may trigger criminal liability under **Geschäftsgeheimnisgesetz (GeschGehG)** - German Trade Secrets Act

### Unfair Contract Terms - National Law Overlay

**AGB-Recht (Standard Terms Control - BGB §§ 305 ff.):**
- Germany has **well-developed case law** on unfair terms in B2B contracts
- **Data Act Chapter IV** (unfair terms) will be interpreted in light of existing German AGB-Recht principles
- **§ 307 BGB** (general unfairness test): terms that unreasonably disadvantage the other party contrary to good faith are void

**Practical implication:**
- German courts may apply **stricter scrutiny** than Data Act minimum - if a term passes Data Act unfairness test but fails BGB § 307, it's still void
- **Data Act safe harbor** (individually negotiated or model terms) aligns with BGB § 305(1) exception for individually negotiated terms

### B2G Data Sharing - National Legal Basis

**Emergency requests (Article 15):**
- **Katastrophenschutzgesetze** (state-level disaster protection laws) provide legal basis
- **IfSG (Infektionsschutzgesetz - Infection Protection Act)** for public health emergencies (e.g., pandemic data requests)
- **BBK (Federal Office for Civil Protection and Disaster Assistance)** coordinates federal emergency response

**Public interest requests (Article 17):**
- Requires specific statutory authorization beyond general administrative powers
- **Anticipated implementation:** Bundestag may enact **Data Act Implementation Act** (Datengesetz-Durchführungsgesetz) specifying which authorities can make public interest requests for which purposes

**Trade secret protection:**
- **GeschGehG** (implementing EU Trade Secrets Directive) applies
- Data holders can invoke trade secret protection under Data Act + GeschGehG
- Public bodies must comply with GeschGehG confidentiality and safeguard obligations

### Works Council Involvement (BetrVG)

**When works council consultation required:**
- **BetrVG § 87(1) No. 6** - co-determination on introduction of technical systems for monitoring employee behavior or performance
- If connected product data or B2G data sharing involves **employee data** (e.g., fleet vehicle telematics, workplace IoT sensors), works council has **co-determination rights**

**Practical scenarios requiring BetrVG compliance:**
1. **Connected products in workplace** (e.g., smart manufacturing equipment generating operator performance data)
2. **Employee-used connected products** (e.g., company smartphones, wearables)
3. **B2G sharing of employee-related data** (e.g., public authority requests workplace mobility data for traffic planning)

**Process:**
- **Inform and consult** works council before implementing data access mechanisms
- If works council objects, **mediation** or **arbitration board (Einigungsstelle)** may be required
- **Failure to consult** can render data access agreements void or trigger injunction from works council

### Public Procurement Implications

**Connected products in public procurement:**
- German public bodies procuring connected products (e.g., smart city infrastructure, government fleet vehicles) must ensure:
  - **Compliance with Data Act transparency obligations** (Article 3) - tender specs should require vendors to disclose data access capabilities
  - **Access-by-design** for products designed after 12 Sept 2026
  - **Unfair contract terms** - procurement contracts cannot impose Data Act-violating terms on vendors, and vendors cannot impose them on contracting authority

**Vergaberecht (public procurement law):**
- Data Act compliance may be a **technical specification** or **contract performance condition** in tenders
- **GWB Part 4** (Vergaberecht) and **VgV (Procurement Ordinance)** govern federal/state procurement

### German Constitutional Overlay (Grundgesetz)

**Fundamental rights analysis:**
- While Data Act is EU regulation (no Grundgesetz conformity review by BVerfG - Constitutional Court), **application in Germany** engages fundamental rights:
  - **Article 12 GG (freedom of occupation)** - data access obligations and contract fairness rules affect commercial freedom
  - **Article 14 GG (property and trade secrets)** - trade secret protection under Data Act must be proportionate to GG Article 14
  - **Article 2(1) GG (general freedom of action) + Article 1(1) GG (human dignity)** - right to informational self-determination (personal data)

**Practical implication:**
- Courts interpreting Data Act obligations (e.g., proportionality of trade secret refusals, reasonableness of B2G requests) will apply **Grundgesetz proportionality test** as an additional lens
- Higher standard than EU Charter alone in some cases

### Key Contacts and Resources

| Authority | Jurisdiction | Website |
|-----------|-------------|---------|
| **Bundeskartellamt** | Competition, unfair terms, data access | bundeskartellamt.de |
| **BNetzA** | Telecom, energy, postal (potential cloud oversight) | bundesnetzagentur.de |
| **BfDI** | GDPR-Data Act personal data overlaps | bfdi.bund.de |
| **BBK** | Emergency management, B2G requests (emergencies) | bbk.bund.de |

---

## Austria

### Designated Authorities

**Market Surveillance Authority:**
- **Bundeswettbewerbsbehörde (BWB - Federal Competition Authority)** - likely lead Data Act authority
  - Competition law enforcement, market fairness
  - Parallel to Bundeskartellamt in Germany

**Sector-Specific Authorities:**
- **RTR (Rundfunk und Telekom Regulierungs-GmbH)** - telecom/media regulator, potential role for telecom data services
- **DSB (Datenschutzbehörde - Data Protection Authority)** - GDPR overlaps
- **E-Control** - energy regulator, relevant for smart grid/energy data

**Coordination:**
- Austrian **Federal Chancellery** (Bundeskanzleramt) or **Ministry of Justice** may issue implementation guidance

### Enforcement and Penalties

**Legal framework:**
- Austria expected to enact **national penalty provisions** under Article 44 Data Act
- Likely amendment to **UWG (Unfair Competition Act - Gesetz gegen den unlauteren Wettbewerb)** or **KartG (Cartel Act)**

**Penalty levels:**
- Comparable to GDPR penalties - up to **4% of turnover** for serious violations
- BWB can impose fines, issue cease-and-desist orders, require compliance measures

### Unfair Contract Terms - National Law

**ABGB (Austrian Civil Code - Allgemeines Bürgerliches Gesetzbuch):**
- **§ 879 ABGB** - contracts contrary to good morals (gute Sitten) are void
- **KSchG (Consumer Protection Act - Konsumentenschutzgesetz)** applies to B2C, but ABGB § 879 also relevant for B2B fairness

**Interaction with Data Act:**
- Austrian courts may interpret Data Act unfairness (Chapter IV) in light of § 879 ABGB
- **Sittenwidrigkeit (immorality)** test may provide additional protection beyond Data Act minimum

### B2G Data Sharing

**Emergency requests:**
- **Katastrophenmanagementgesetz (Disaster Management Act)** provides legal basis
- **State-level** crisis management authorities (Landesregierungen) coordinate regional emergencies
- **Federal Ministry of Interior** (BMI) for national emergencies

**Public interest requests:**
- Specific statutory authorization required - Austria may enact **Data Act Implementation Act** (Datengesetz-Durchführungsgesetz)

**Health emergencies:**
- **Epidemiegesetz** (Epidemic Act) for infectious disease emergencies
- **AGES (Austrian Agency for Health and Food Safety)** may request health-related data

### Key Contacts and Resources

| Authority | Jurisdiction | Website |
|-----------|-------------|---------|
| **Bundeswettbewerbsbehörde (BWB)** | Competition, Data Act enforcement | bwb.gv.at |
| **DSB (Datenschutzbehörde)** | GDPR-Data Act personal data overlaps | dsb.gv.at |
| **RTR** | Telecom, media | rtr.at |

---

## Switzerland

### Direct Applicability - Switzerland is NOT an EU Member State

**Critical point:**
- **Data Act does NOT apply directly** in Switzerland (not EU/EEA member)
- However, Swiss entities and Swiss operations **may be affected**:

### When Data Act Applies to Swiss Entities

**Extraterritorial application (Article 2(2)):**
- Data Act applies to entities **not established in the EU** where:
  - They **offer connected products or related services** to users in the EU, OR
  - They **provide data processing services** to customers in the EU, OR
  - They are **data recipients** receiving data from EU-based data holders

**Practical scenarios:**

1. **Swiss IoT manufacturer sells products in EU:**
   - Must comply with Data Act transparency (Article 3), user access (Article 4), access-by-design (Article 3(2) post-Sept 2026)
   - Must designate **EU representative** (Article 39)

2. **Swiss cloud provider offers services to EU customers:**
   - Must comply with cloud switching and portability obligations (Chapters VI-VII)
   - Must designate **EU representative**

3. **Swiss company receives data from EU data holders:**
   - Subject to Data Act use limitations (Article 5), GDPR compliance (if personal data)

**EU representative obligation (Article 39):**
- Natural or legal person **established in one EU Member State**
- Authorized to act on behalf of Swiss entity
- Addressable by EU authorities and users
- Contact details must be publicly available and communicated to users

### Swiss Legal Framework - Voluntary Compliance and Best Practice

**No direct enforcement in Switzerland, but:**

**revFADP (revised Swiss Federal Act on Data Protection):**
- In force since **1 September 2023**
- Aligns with GDPR (data subject rights, security, DPIAs)
- Does **not** cover non-personal data or Data Act-type access rights

**Swiss competition law:**
- **Kartellgesetz (KG - Cartel Act)** - no specific data access obligations, but unfair competition and abuse of dominance rules may apply

**Contractual incorporation:**
- Swiss entities may **voluntarily adopt Data Act standards** in contracts with EU partners to ensure compliance and avoid EU enforcement
- EU customers may **require Data Act compliance** as contract condition

### Cross-Border Data Flows - EU-Switzerland

**GDPR adequacy decision:**
- Switzerland has **adequacy status** under GDPR for personal data transfers
- Data Act-triggered personal data sharing between EU and Switzerland subject to GDPR + revFADP

**Non-personal data:**
- **No EU-Switzerland framework** equivalent to Data Act for non-personal data
- Contractual arrangements govern cross-border non-personal data sharing

### Swiss Authorities - Coordination with EU

**EDÖB (Federal Data Protection and Information Commissioner - Eidgenössischer Datenschutz- und Öffentlichkeitsbeauftragter):**
- Enforces revFADP
- Coordinates with EU DPAs on GDPR-related matters
- **Not competent for Data Act enforcement** (no Swiss legal basis)

**WEKO (Competition Commission - Wettbewerbskommission):**
- Swiss competition authority
- May examine unfair trading practices, but no Data Act-specific mandate

**No Swiss authority enforces Data Act** - enforcement is via **EU Member State authorities** for Swiss entities' EU operations.

### Practical Guidance for Swiss Entities

**Checklist for Swiss companies:**

1. **Assess EU exposure:**
   - [ ] Do you offer connected products or cloud services to EU customers?
   - [ ] Do you receive data from EU-based data holders?
   - [ ] Do you have EU subsidiaries or branches?

2. **If YES to any - determine Data Act obligations:**
   - [ ] Identify which Data Act chapters apply (user access, cloud switching, unfair terms)
   - [ ] Designate EU representative (Article 39)
   - [ ] Ensure transparency and access mechanisms for EU users
   - [ ] Review contracts for Data Act unfair terms compliance

3. **Integrate with GDPR/revFADP compliance:**
   - [ ] Personal data from EU: comply with GDPR
   - [ ] Personal data of Swiss residents: comply with revFADP
   - [ ] Non-personal data from EU: comply with Data Act

4. **Consider voluntary adoption for Swiss operations:**
   - [ ] Even for purely Swiss customers, Data Act standards may be best practice
   - [ ] Competitive advantage: "We meet EU Data Act standards"

### Key Contacts and Resources

| Authority | Jurisdiction | Website |
|-----------|-------------|---------|
| **EDÖB** | Swiss data protection (revFADP) | edoeb.admin.ch |
| **WEKO** | Swiss competition law | weko.admin.ch |

---

## DACH Comparison Table

| Aspect | Germany | Austria | Switzerland |
|--------|---------|---------|-------------|
| **Data Act applicability** | Direct (EU Member) | Direct (EU Member) | Extraterritorial only (non-EU) |
| **Lead enforcement authority** | Bundeskartellamt | Bundeswettbewerbsbehörde (BWB) | None (EU authorities for EU operations) |
| **GDPR/data protection authority** | BfDI + Landesdatenschutzbehörden | DSB | EDÖB (revFADP) |
| **Unfair terms national law** | BGB §§ 305 ff. (AGB-Recht) | ABGB § 879 (good morals) | KG (competition law, limited) |
| **Works council co-determination** | BetrVG (strong rights) | ArbVG (similar to BetrVG) | No statutory works council system |
| **B2G legal basis (emergency)** | Katastrophenschutzgesetze, IfSG | Katastrophenmanagementgesetz, Epidemiegesetz | N/A (no Data Act application) |
| **EU representative required** | No (EU Member State) | No (EU Member State) | Yes (if offering in EU) |

---

## Common DACH Compliance Pitfalls

1. **Assuming uniform enforcement across DACH:**
   - Germany, Austria, Switzerland have **different authorities, penalty levels, and national law overlays**
   - **Tailor compliance** to each jurisdiction

2. **Forgetting Switzerland is not EU:**
   - Swiss entities must assess **extraterritorial application** and designate EU representative

3. **Ignoring works council in Germany/Austria:**
   - Employee data access triggers **co-determination rights** - failure to consult can block implementation

4. **Underestimating national unfair terms law:**
   - BGB (Germany) and ABGB (Austria) may provide **stricter protection** than Data Act minimum

5. **Unclear B2G legal basis:**
   - Public interest requests require **specific statutory authorization** - generic administrative powers insufficient

---

## Key Takeaways

### Germany
- **Bundeskartellamt** lead authority, BNetzA for telecom/energy, BfDI for GDPR overlaps
- **BetrVG works council** rights for employee data
- **AGB-Recht** stricter than Data Act unfair terms minimum
- **GeschGehG** trade secret protection aligns with Data Act

### Austria
- **BWB** lead authority, DSB for GDPR overlaps
- **ABGB § 879** unfairness test may exceed Data Act
- **Katastrophenmanagementgesetz** for emergency B2G requests

### Switzerland
- **Extraterritorial application** for EU operations only
- **EU representative required** for Swiss entities offering in EU
- **revFADP** for personal data, no Data Act equivalent for non-personal data
- **Voluntary adoption** as best practice or contractual requirement
