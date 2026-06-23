# Contextual Application Modules

## Table of Contents
1. [Children's Data](#1-childrens-data)
2. [Direct Marketing](#2-direct-marketing)
3. [Fraud Prevention](#3-fraud-prevention)
4. [IT/Network Security](#4-itnetwork-security)
5. [Employment Context](#5-employment-context)
6. [Intra-Group Data Sharing](#6-intra-group-data-sharing)
7. [Third-Country Authority Requests](#7-third-country-authority-requests)
8. [AI/ML Processing](#8-aiml-processing)

---

## 1. Children's Data

**Source:** EDPB Guidelines 1/2024, paras. 91-97; Art. 6(1)(f) GDPR; Art. 24(2) Charter; UNCRC Art. 3(1)

### Key Principles

- Children deserve **specific protection** — less aware of risks, consequences, safeguards (Recital 38 GDPR)
- Art. 6(1)(f) expressly references children: "in particular where the data subject is a child"
- **Best interests must be a primary consideration** (Art. 24(2) Charter)
- Balancing test must be **recalibrated** — children's interests will "very often" outweigh controller's

### Practical Rules

| Scenario | Assessment |
|----------|------------|
| Interest coincides with child's interests (e.g., child safety features) | Art. 6(1)(f) may be available |
| Commercial interest conflicts with child's interests | Child's interests should generally prevail |
| Extensive profiling / targeted advertising to children | Generally NOT permissible via Art. 6(1)(f) |
| Marketing / user profile creation aimed at children | Specific protection applies (C-252/21, para. 111) |

**Note:** DSA (Regulation 2022/2065) separately prohibits targeted advertising based on profiling of children's data.

**Age differentiation:** Not all children are the same. Assessment should vary by age group, developmental level, and specific vulnerabilities (para. 97).

### Assessment Checklist for Children's Data

- [ ] Is Art. 6(1)(f) being used for purposes that serve the child's best interests?
- [ ] If commercial purpose: can you demonstrate no negative impact on the child?
- [ ] Is profiling or targeting involved? (If yes: generally not permissible)
- [ ] Have you considered the age group and developmental level?
- [ ] Are enhanced safeguards in place?
- [ ] Has the DPO specifically reviewed the children's data assessment?

---

## 2. Direct Marketing

**Source:** EDPB Guidelines 1/2024, paras. 109-120; Recital 47 GDPR; ePrivacy Directive Arts. 5(3) and 13

### The Recital 47 Clarification

Recital 47 states that processing for direct marketing purposes **may** be regarded as carried out for a legitimate interest. This is NOT an automatic pass:
- Does not mean direct marketing is always a legitimate interest (para. 110)
- Does not mean Art. 6(1)(f) can always be relied on for direct marketing
- Full three-step test still required

### ePrivacy Priority Check (MUST DO FIRST)

| Channel | ePrivacy Requirement | Art. 6(1)(f) Available? |
|---------|---------------------|------------------------|
| Email, SMS, MMS, messaging apps | **Prior consent required** (Art. 13(1) ePrivacy Directive) | **NO** — consent is the required basis |
| Existing customer electronic marketing of similar products | **Soft opt-in** exception (Art. 13(2) ePrivacy Directive) | Potentially YES — if conditions met |
| Cookie/tracking-based targeting | **Consent required** (Art. 5(3) ePrivacy Directive) | **NO** for the tracking; downstream processing also likely requires consent |
| Postal marketing | Not covered by ePrivacy | YES — subject to full three-step test |
| Telephone (varies by MS) | Check national implementation | Varies by jurisdiction |

### Balancing Factors for Marketing

| Factor | Favours Controller | Favours Data Subject |
|--------|-------------------|---------------------|
| Existing customer relationship | ✓ | |
| Similar products/services | ✓ | |
| Easy opt-out mechanism | ✓ | |
| Non-customer / prospective | | ✓ |
| Extensive profiling for targeting | | ✓ |
| Children as targets | | ✓✓ |
| Data from third-party sources | | ✓ |
| No prior relationship | | ✓ |

### Art. 21(2): Absolute Right to Object

The right to object to direct marketing processing is **absolute** under Art. 21(2) — no balancing, no "compelling legitimate grounds" defence. Controller must cease processing upon objection.

**Practical requirement:** Must inform data subjects of this right explicitly, clearly, and separately from other information (Art. 21(4)).

---

## 3. Fraud Prevention

**Source:** EDPB Guidelines 1/2024, paras. 100-108; Recital 47 GDPR

### Recognition and Limits

Recital 47: Processing "strictly necessary" for fraud prevention may constitute a legitimate interest.

**"Fraud prevention" includes:**
- Measures to prevent fraudulent behaviour
- Detection of fraud (risk of repetition; weakness analysis)
- But: must be assessed case-by-case whether detection measures are suitable for prevention (para. 102)

### Requirements

1. **Specify the fraud type** — generic "combating fraud" is insufficient (para. 106)
2. **Strict necessity** — process only what is strictly needed for preventing that specific fraud type
3. **Data minimisation** — minimise data in conjunction with Art. 5(1)(c)
4. **Storage limitation** — Art. 5(1)(e) applies to retention of fraud-related data
5. **Accuracy** — data used to assess fraud risk must be accurate and demonstrably relevant (para. 105)
6. **Proportionality** — fraud must be of "substantial importance"; trivial fraud unlikely to outweigh data subject interests (para. 105)

### Legal Basis Selection

If fraud detection/prevention is **mandated by law** → Art. 6(1)(c) is more appropriate, not Art. 6(1)(f) (para. 107).

Incidental fraud discovery during other processing → further processing rules under Art. 6(4) apply (para. 108).

---

## 4. IT/Network Security

**Source:** EDPB Guidelines 1/2024 referencing Recital 49 GDPR

### Recital 49 Recognition

Processing "to the extent strictly necessary and proportionate for the purposes of ensuring network and information security" may constitute a legitimate interest. This includes:
- Preventing unauthorised access to networks
- Preventing malicious code distribution
- Stopping denial-of-service attacks
- Preventing damage to computer and electronic communication systems

### Requirements

- **Strictly necessary** — only what is needed for the specific security purpose
- **Proportionate** — security processing must be proportionate to the threat
- **Minimisation** — log only what's needed; consider retention periods
- **Not a blanket authorisation** — each security measure needs its own assessment

### Typical Processing Activities

| Activity | Likely Legitimate | Conditions |
|----------|------------------|------------|
| Firewall logging | Yes | Minimise data, appropriate retention |
| Intrusion detection | Yes | Proportionate to threat level |
| Vulnerability scanning | Yes | Own systems only |
| Employee device monitoring | Maybe | Power imbalance considerations; proportionality |
| Full content inspection | Risky | Must justify why metadata insufficient |

---

## 5. Employment Context

**Source:** EDPB Guidelines 1/2024, paras. 43, 47; WP29 Opinion 06/2014

### Special Considerations

The **employer-employee power imbalance** fundamentally affects the LIA:
- Different assessment from service provider-customer relationship (para. 43)
- Controller should not assume all employees share the same interests (para. 47)
- "Especially true in the context of an employer-employee relationship" (para. 47)

### German-Specific: Works Council Rights

**BetrVG §87(1) Nr. 6:** Works council co-determination required for technical facilities that can monitor employee behaviour or performance.

**BetrVG §87(1) Nr. 1:** Co-determination on matters of workplace order and conduct.

**BDSG §26 (Beschäftigtendatenschutz):** Employee data processing provisions — check whether specific German rules apply in addition to GDPR.

### Assessment Factors

| Factor | Impact on Balance |
|--------|-------------------|
| Monitoring intensity | Higher intensity = heavier impact on employee |
| Employee awareness | Secret monitoring dramatically shifts balance |
| Purpose specificity | General surveillance vs. targeted investigation |
| Scope limitation | All employees vs. specific concern |
| Alternative measures | Could the same result be achieved without processing employee data? |
| Proportionality | Minor workplace issue ≠ justify extensive monitoring |

---

## 6. Intra-Group Data Sharing

**Source:** EDPB Guidelines 1/2024, para. 33 referencing Recital 48 GDPR

### Recital 48 Recognition

"Controllers that are part of a group of undertakings or institutions affiliated to a central body may have a legitimate interest in transmitting personal data within the group of undertakings for internal administrative purposes, including the processing of clients' or employees' personal data."

### Key Limits

- **No group-wide exemption** — each group entity that processes data must conduct its own LIA
- **Still subject to full three-step test** per entity
- Reasonable expectations matter: single-brand groups vs. loosely affiliated conglomerates
- Data subjects more likely to expect sharing within a single-brand entity than between seemingly unrelated companies under the same corporate umbrella

### Practical Approach

1. Map the data flows between group entities
2. For each flow: identify the legitimate interest per entity
3. Assess necessity per entity
4. Consider data subject expectations about the group structure
5. Document per entity, not just at group level

---

## 7. Third-Country Authority Requests

**Source:** EDPB Guidelines 1/2024, paras. 135-136

### EDPB Position

The interests or fundamental rights and freedoms of the data subject would **usually override** the controller's interest in complying with a request from a third country law enforcement authority in order to avoid sanctions for non-compliance (para. 136).

### Practical Implications

- Cannot rely on Art. 6(1)(f) as a default for disclosing data to third-country authorities
- Must consider Chapter V transfer safeguards separately
- Check whether a mutual legal assistance treaty (MLAT) or other international agreement provides a proper legal framework
- Consider Art. 48 GDPR (transfers not authorised by international agreements)

---

## 8. AI/ML Processing

**Primary Sources:**
- **EDPB Opinion 28/2024** on AI models and processing of personal data (17 December 2024) — the authoritative EU-level guidance
- **CNIL Recommendations on Legitimate Interest for AI Development** (19 June 2025) — most operationally detailed national guidance
- **CNIL Focus Sheet on Web Scraping Measures** (19 June 2025)
- **Hamburg DPA Discussion Paper on LLMs** (15 July 2024) — controversial, partially superseded by Opinion 28/2024
- **DSK Joint Guidance "AI and Data Protection"** (6 May 2024)

For the full detailed analysis of these sources including AI-specific mitigating measures catalogues and reasonable expectations criteria, read [additional-regulatory-sources.md] §1-2.

### Key Principles

**Legitimate interest is available** for both development and deployment of AI models. The EDPB confirmed this explicitly in Opinion 28/2024. The CNIL considers it the most likely legal basis for AI developers given the impracticality of consent at scale.

**Recognised AI legitimate interests (EDPB Opinion 28/2024, para. 69):**
- Developing a conversational agent to assist users
- Developing AI to detect fraudulent content or behaviour
- Improving threat detection in information systems

**The three-step test applies with full rigour** — AI processing does not get a lighter standard.

### AI-Specific Necessity Considerations

The EDPB sets a high bar (Opinion 28/2024, para. 73): if the purpose can be achieved through an AI model that does not involve personal data at all, then processing personal data is not necessary. Controllers must assess volume of personal data against less intrusive alternatives (synthetic data, anonymisation, smaller datasets). Technical safeguards like pseudonymisation can contribute to meeting the necessity test.

### AI-Specific Reasonable Expectations Criteria

The EDPB provides seven factors for assessing reasonable expectations in AI contexts (Opinion 28/2024, para. 93):
1. Whether personal data was publicly available
2. Nature of the relationship between data subject and controller
3. Nature of the service
4. Context in which personal data was collected
5. Source from which data was collected (and privacy settings offered)
6. Potential further uses of the model
7. Whether data subjects are actually aware their data is online

Simply including AI training in a privacy policy does NOT create reasonable expectations (para. 92).

### Mitigating Measures for AI

The EDPB and CNIL provide extensive mitigating measures catalogues covering technical measures (pseudonymisation, data masking, differential privacy), rights facilitation (pre-collection opt-out, extended erasure, regurgitation claim mechanisms), transparency measures (model cards, media campaigns, website lists), and web scraping-specific measures (respect robots.txt/ai.txt, exclude sensitive sources, limit to freely accessible data). See [additional-regulatory-sources.md] §1 for the full catalogue.

### Unlawful Development → Deployment Impact

If an AI model was developed with unlawfully processed personal data, the EDPB considers three scenarios with different consequences. The lawfulness assessment depends on whether the same/different controller deploys, whether the model is anonymised, and whether the deploying controller conducted appropriate due diligence. See [additional-regulatory-sources.md] §1 for details.

### National DPA Divergence

The Dutch Autoriteit Persoonsgegevens asserts that web scraping for AI training requires consent — the most restrictive position. The CNIL explicitly takes a more pragmatic approach, confirming legitimate interest is available. Controllers should monitor this divergence and apply the standard of the jurisdiction where data subjects are located.
