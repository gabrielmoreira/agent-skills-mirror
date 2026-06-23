# Jurisdiction-Specific Notes for Art. 6(1)(f) GDPR

## Overview

While Art. 6(1)(f) GDPR is directly applicable across the EU/EEA, national law may impose additional requirements or restrictions. This reference covers key jurisdiction-specific considerations.

**Note:** This is not exhaustive. Always verify current national law for the specific jurisdiction.

---

## Germany (DE)

### Key National Rules

**BDSG §26 — Employee Data Processing (Beschäftigtendatenschutz)**
- Specific rules for processing employee data
- Art. 6(1)(f) may be available but subject to stricter proportionality requirements
- BDSG §26 provides a more specific legal basis for employment relationships

**BetrVG §87(1) Nr. 6 — Works Council Co-Determination**
- Technical facilities capable of monitoring employee behaviour or performance require works council co-determination
- Applies regardless of whether monitoring is the purpose
- Failure to involve works council can make the processing unlawful

**BDSG §28 — Processing for Scoring/Creditworthiness**
- Specific rules for credit scoring and creditworthiness assessments
- Subject to restrictions in BDSG §31

**Telemediengesetz (TTDSG) / TDDDG**
- German implementation of ePrivacy requirements
- Cookie consent requirements (§25 TDDDG)
- Check for direct marketing: electronic communications require consent

### German DPA Guidance

German DPAs (DSK — Datenschutzkonferenz) have issued specific guidance on legitimate interest in various contexts. Monitor DSK positions on:
- Video surveillance (Orientierungshilfe Videoüberwachung)
- Employee monitoring
- Direct marketing
- Credit scoring

---

## Austria (AT)

### DSG — Datenschutzgesetz
- §1 DSG: Fundamental right to data protection with constitutional rank
- Austrian courts may apply a higher threshold for legitimate interest given constitutional protection
- Check Austrian DPA (DSB) practice for specific processing contexts

---

## France (FR)

### Key Considerations
- CNIL (Commission nationale de l'informatique et des libertés) has published detailed guidance on legitimate interest
- CSE (Comité Social et Économique) consultation may be required before deploying processing systems affecting employees
- Stricter interpretation for employee monitoring and workplace surveillance
- CNIL cookies/trackers guidance implements Art. 5(3) ePrivacy strictly

---

## Netherlands (NL)

### Key Considerations
- Post-KNLTB (C-621/22), the Autoriteit Persoonsgegevens may apply stricter scrutiny to commercial data sharing
- UAVG (Uitvoeringswet AVG) supplements GDPR
- Dutch DPA has been particularly active on legitimate interest enforcement

---

## Ireland (IE)

### Key Considerations
- Data Protection Commission (DPC) is Lead SA for many large tech companies
- DPC decisions form significant precedent for Art. 6(1)(f) in digital services context
- Many OSS decisions in the EDPB case digest originate from DPC as Lead SA

---

## Belgium (BE)

### Key Considerations
- APD/GBA (Autorité de protection des données / Gegevensbeschermingsautoriteit)
- Active enforcement on legitimate interest, particularly for direct marketing
- Specific guidance on cookie walls and legitimate interest

---

## Italy (IT)

### Key Considerations
- Garante per la protezione dei dati personali
- Specific telemarketing rules (Registro delle Opposizioni)
- Employment context: Statuto dei Lavoratori (Art. 4) restricts employee monitoring

---

## Spain (ES)

### Key Considerations
- LOPDGDD (Ley Orgánica de Protección de Datos y Garantía de los Derechos Digitales)
- Art. 19 LOPDGDD: specific provisions on legitimate interest for certain commercial situations
- AEPD guidance on legitimate interest for video surveillance

---

## United Kingdom (UK)

### Post-Brexit Status

The UK is no longer an EU/EEA Member State. UK data protection is governed by the UK GDPR (retained EU law as amended) and the Data Protection Act 2018, now significantly amended by the Data (Use and Access) Act 2025 ("DUA Act"). The ICO (Information Commissioner's Office) is the supervisory authority. The EU-UK adequacy decision (adopted June 2021) remains in force but is subject to periodic review.

### UK GDPR Legitimate Interests — Key Differences from EU

**Lower necessity threshold:** The ICO applies "targeted and proportionate" rather than the EDPB/CJEU "strictly necessary" standard. The ICO states it "doesn't mean that it has to be absolutely essential." This is a materially more permissive standard. Cross-border controllers operating in both EU and UK should apply the stricter EDPB standard as a baseline — the UK's more permissive approach cannot be relied upon for EU processing.

**Same three-part test structure:** (1) Purpose test, (2) Necessity test, (3) Balancing test.

**LIA documentation:** Not explicitly required by UK GDPR but strongly recommended by ICO as accountability evidence. No standardised format.

### Recognised Legitimate Interest (DUA Act 2025)

**New lawful basis introduced August 2025** — separate from and additional to standard legitimate interests. Five pre-approved public interest purposes where **no balancing test is required** (necessity test only):

1. **Public function disclosures** — responding to disclosures requested by bodies performing public functions
2. **National security / public security / defence** — processing necessary to support these purposes
3. **Emergency situations** — responding to events or situations under the Civil Contingencies Act 2004
4. **Crime** — preventing, detecting, or investigating crimes
5. **Safeguarding** — safeguarding children or vulnerable adults from harm

**Key rules for RLI:**
- Public authorities CANNOT rely on RLI for their public tasks
- Special category and criminal offence data CAN be processed under RLI (with additional conditions from DPA 2018)
- Must still assess necessity — the balancing test is removed but the processing must be necessary for the pre-approved purpose
- Must still comply with all other data protection requirements (transparency, data minimisation, security, etc.)
- Data subjects retain the right to object
- Additional conditions may be added by regulation in future

**Practical note:** RLI has a very narrow scope — only the five listed purposes. It does NOT replace standard legitimate interests for commercial processing, marketing, fraud prevention, or any other common LIA scenario. Most organisations will continue to use standard legitimate interests with the full three-part test.

### UK-Specific Direct Marketing Rules

**PECR (Privacy and Electronic Communications Regulations 2003):**
- Consent required for electronic marketing (email, SMS, automated calls) — similar to ePrivacy Directive
- "Soft opt-in" exception for existing customers (similar products/services)
- Legitimate interests available for postal marketing
- ICO actively enforces PECR alongside UK GDPR

### UK ICO AI Guidance

The ICO has published guidance on AI and data protection, including on legal bases for AI training. The ICO's position is broadly aligned with the pragmatic CNIL approach rather than the restrictive Dutch AP position. The ICO has welcomed views on how data subject rights requests (especially erasure and rectification) are being handled in practice for AI/ML systems. Monitor ICO website for updates.

### When UK Rules Apply

| Scenario | Applicable Law |
|----------|---------------|
| UK-only controller, UK data subjects | UK GDPR + DPA 2018 + DUA Act 2025 |
| EU controller processing UK data subjects | UK GDPR applies to UK processing; GDPR to EU processing |
| UK controller processing EU data subjects | GDPR applies to EU processing (Art. 3(2)); UK GDPR to UK processing |
| Dual EU-UK operations | Apply both regimes; use stricter standard as baseline for shared systems |

### Practical Guidance for Dual-Jurisdiction Controllers

- Maintain a single LIA using the stricter EDPB standard, with a UK-specific annex noting where the ICO allows more flexibility
- Where RLI is available for the UK processing (five pre-approved purposes), document this separately
- Monitor the EU-UK adequacy decision status — revocation would affect transfer mechanisms
- UK-specific marketing under PECR soft opt-in does not automatically comply with EU ePrivacy requirements — check both

---

## General Cross-Border Considerations

### One-Stop-Shop (OSS)
- For cross-border processing: Lead SA handles enforcement
- But national law of each affected Member State may supplement GDPR requirements
- Art. 6(1)(f) assessment should consider national specificities where data subjects reside

### When Jurisdiction Matters Most

| Context | Jurisdiction Impact |
|---------|-------------------|
| Employee data | HIGH — national labour law varies significantly |
| Direct marketing | HIGH — ePrivacy implementation differs |
| Video surveillance | MEDIUM — national guidance varies |
| Children's data | MEDIUM — age thresholds may differ (Art. 8 consent: 13-16 years depending on MS) |
| Credit scoring | HIGH — national rules supplement GDPR (esp. DE, FR) |
| Public sector | HIGH — national law determines scope of Art. 6(1) second indent |
