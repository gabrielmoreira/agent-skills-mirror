# Step 3: Balancing Test — Detailed Reference

## Legal Framework

The third condition requires that "the interests or fundamental freedoms and rights of the concerned data subjects do not take precedence over the legitimate interest(s) of the controller or of a third party" (EDPB Guidelines 1/2024, para. 6).

This depends on the **specific circumstances** of the particular case (C-252/21 *Meta*, para. 110).

**Purpose:** Not to avoid ANY impact on data subjects, but to avoid **disproportionate** impact (para. 33).

---

## Part A: Data Subjects' Interests, Rights and Freedoms

### Fundamental Rights (broader than just privacy)

| Right | Source | When Relevant |
|-------|--------|---------------|
| Data protection | Art. 8 Charter | Always |
| Privacy / private life | Art. 7 Charter | Always |
| Liberty and security | Art. 6 Charter | Surveillance, tracking |
| Freedom of expression | Art. 11 Charter | Content moderation, monitoring |
| Freedom of thought, conscience, religion | Art. 10 Charter | Profiling, behavioural analysis |
| Freedom of assembly | Art. 12 Charter | Location tracking, event monitoring |
| Non-discrimination | Art. 21 Charter | Profiling, automated decisions |
| Right to property | Art. 17 Charter | Financial data processing |
| Physical and mental integrity | Art. 3 Charter | Health data, wellbeing impact |
| Rights of the child | Art. 24 Charter | Children's data processing |

### Other Interests

Include ALL interests that may be affected (para. 38):
- Financial interests (risk of financial loss)
- Social interests (reputation, relationships)
- Personal interests (autonomy, dignity, emotional wellbeing)

---

## Part B: Impact Assessment

### B1. Nature of Data

**Higher sensitivity = heavier weight against controller** (para. 41)

| Data Type | Sensitivity | Special Considerations |
|-----------|-------------|----------------------|
| Art. 9 special categories (health, biometric, genetic, racial/ethnic, political, religious, sexual orientation, trade union) | **HIGHEST** | Art. 9(2) conditions ALSO required; data set containing even one sensitive item is deemed sensitive in its entirety (C-252/21, para. 89) |
| Art. 10 criminal convictions/offences | **VERY HIGH** | Additional Art. 10 conditions required |
| Financial data (bank, salary, credit) | **HIGH** | Considered more private by data subjects |
| Location data | **HIGH** | Reveals movement patterns, habits |
| Communications metadata | **HIGH** | Can reveal associations, relationships |
| Behavioural/browsing data | **MEDIUM-HIGH** | Can enable profiling |
| Simple contact data (name, email, phone) | **MODERATE** | Lower inherent sensitivity but context matters |
| Professional/public role data | **LOWER** | Generally considered less private |

**Critical CJEU rule on sensitive data inference:** The question is whether it is *objectively possible* to infer sensitive information from processed data — regardless of whether the controller intends to (C-252/21, para. 69). E.g., purchasing data may reveal religious beliefs or health conditions.

### B2. Context of Processing

Assess each factor (para. 43):

| Factor | Lower Impact | Higher Impact |
|--------|-------------|---------------|
| **Scale** | Small number of subjects, limited volume | Large-scale, high volume per subject |
| **Controller status** | Equal commercial relationship | Power imbalance (employer/employee) |
| **Data combination** | Single source, isolated | Combined with other datasets |
| **Accessibility** | Internal use only | Shared broadly, published |
| **Data subject status** | Average adult consumer | Vulnerable: minors, patients, employees, elderly |

### B3. Consequences

Consider both direct and indirect consequences (paras. 45-46):

**Direct consequences:**
- Third-party decisions based on the data (e.g., credit denial, insurance pricing)
- Legal effects on the data subject
- Exclusion or discrimination
- Reputational damage
- Financial losses
- Exclusion from essential services with no alternative

**Indirect/broader consequences:**
- Loss of control over personal information (emotional impact)
- Chilling effects on protected behaviour (freedom of expression, research)
- Feeling of continuous observation (C-252/21, para. 118 — Meta's continuous monitoring)
- Erosion of autonomy and self-determination

**Harmful downstream effects:**
- C-621/22 *KNLTB*: sharing tennis member data with gambling sponsor → exposure to addiction risks (para. 56)

---

## Part C: Reasonable Expectations

### Core Principle

"The interests and fundamental rights of the data subject could in particular override the interest of the data controller where personal data is processed in circumstances where data subjects do not reasonably expect further processing." — Recital 47 GDPR

### Assessment Framework

**Relationship characteristics:**

| Factor | Expectation More Likely | Expectation Less Likely |
|--------|------------------------|------------------------|
| Customer relationship | Processing for service delivery | Sharing with unrelated third parties |
| Long-standing relationship | Some marketing of similar products | Novel uses unrelated to original context |
| Single brand group | Some intra-group sharing | Multi-brand conglomerate sharing where brands appear unrelated |
| Data collected directly | Processing for stated purpose | Secondary purposes not mentioned |
| Professional context | Colleague data sharing for work | Sharing with external parties |

**Data subject characteristics:**

| Factor | Higher Expectations | Lower Expectations |
|--------|--------------------|--------------------|
| Minors | Expect strong protection | N/A |
| Public figures | N/A | Some reduced expectation for public-facing data |
| Professional role | N/A | Data related to professional capacity |
| Vulnerable individuals | Expect strong protection | N/A |

### Critical Clarifications from EDPB

1. **Common practice ≠ reasonable expectation** (para. 52) — Just because an industry commonly processes certain data doesn't mean data subjects expect it. C-252/21 *Meta*: despite social network advertising being common, users don't reasonably expect off-platform tracking for personalised ads.

2. **Information provided ≠ reasonable expectation** (para. 53) — Merely including processing in a privacy notice does NOT create reasonable expectations. But failing to provide information CAN contribute to surprise.

3. **Contractual provisions may have bearing** — C-17/22 *HTB*: partnership agreements can influence expectations (para. 64).

---

## Part D: Finalising the Balance

### Step-by-Step

1. **Weight the controller's interest** — How important is this processing? Is it core to operations or peripheral?

2. **Weight the data subject impact** — Considering all factors above, how significant is the interference?

3. **Assess proportionality** — Is the interference proportionate to the interest pursued?

4. **Check reasonable expectations** — Would data subjects be surprised?

5. **Preliminary balance** — Which side is weightier?

### If Balance Tips Against Controller

**Mitigating measures** may shift the balance (para. 56). These must go **BEYOND normal GDPR compliance** (para. 57):

| Measure | Type | Example |
|---------|------|---------|
| Extended data subject rights | Rights enhancement | Allowing erasure beyond Art. 17(1) grounds; right to object without Art. 21 limitations |
| Technical safeguards | Data protection | Pseudonymisation above legal minimum; end-to-end encryption; strict access controls |
| Organisational safeguards | Process | Dedicated oversight; regular audits; automated deletion |
| Transparency enhancements | Information | Layered balancing test disclosure; real-time dashboards; proactive notification |
| Reduced scope | Minimisation | Shorter retention; fewer categories; opt-out mechanisms |
| Data portability | Empowerment | Offering portability even for Art. 6(1)(f) processing |

**After implementing measures:** Perform the balancing test **again** (para. 58).

**If still overridden:** Art. 6(1)(f) CANNOT be used, period (para. 60).

### Documentation

The controller must demonstrate that:
- The balancing test was conducted appropriately
- The legitimate interest is not **objectively** overridden (para. 59)
- All factors were genuinely considered
- The outcome is documented per accountability principle (Art. 5(2))

---

## DPIA Consideration

If high risks are identified during this assessment, consider whether a Data Protection Impact Assessment (DPIA) is required under Art. 35 GDPR (para. 49).

Triggers for DPIA consideration:
- Large-scale processing
- Systematic monitoring
- Processing of sensitive data
- Vulnerable data subjects
- Innovative technology use
- Processing that prevents data subjects from exercising rights
