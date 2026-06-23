# OSS Enforcement Practice — EDPB Case Digest Reference

**Source:** EDPB OSS Case Digest on Legitimate Interest (March 2026, Dr. TJ McIntyre), commissioned under the Support Pool of Experts Programme. Based on 62 OSS decisions and 5 EDPB binding decisions adopted between December 2018 and June 2025.

---

## Table of Contents
1. [Common Controller Failure Patterns](#1-common-controller-failure-patterns)
2. [Step 1 in Practice: Identifying Legitimate Interests](#2-step-1-in-practice)
3. [Step 2 in Practice: Necessity Test](#3-step-2-in-practice)
4. [Step 3 in Practice: Balancing Test](#4-step-3-in-practice)
5. [Retroactive Reliance on Legitimate Interest](#5-retroactive-reliance)
6. [ePrivacy Overlap Issues](#6-eprivacy-overlap)
7. [Consumer Finance Decisions](#7-consumer-finance)
8. [Anti-Fraud Measures](#8-anti-fraud)
9. [Vehicle/Mobility Monitoring](#9-vehicle-monitoring)
10. [Cross-Border Divergence](#10-cross-border-divergence)
11. [Novel Legitimate Interests](#11-novel-interests)

---

## 1. Common Controller Failure Patterns

The case digest identifies four primary reasons controllers fail to establish Art. 6(1)(f) (Conclusion, pp. 24-25):

### Failure 1: No documented LIA before processing

Controllers failed to conduct or document a proper legitimate interests assessment before commencing processing. This was "almost always fatal" to reliance on Art. 6(1)(f), as SAs consistently emphasised the assessment must be conducted **ex ante**, not retrospectively constructed in response to regulatory scrutiny.

**Decisions:** EDPBI:ES:OSS:D:2021:338, EDPBI:CZ:OSS:D:2022:1278

### Failure 2: Vague interest articulation

Generic language was rejected as lacking specificity. Controllers must precisely articulate their interest to enable the necessity/balancing tests and to provide adequate notice for data subjects to exercise their rights.

**Example — EDPBI:BE:OSS:D:2022:325 (IAB Europe/TCF):**
The LSA found that terms like "measure content performance" and "apply market research to generate audience insights" provided "little or no insight into the scope of the processing, the nature of the personal data processed or for how long the personal data processed will be retained."

**Example — EDPB Binding Decision 2/2022 (Meta/Instagram child users):**
Meta's interests were "identified and described in a vague fashion" — interest in "creating, providing, supporting, and maintaining innovative products and features that enable people under the age of majority to express themselves" was not sufficiently specific to assess whether the interests were real and lawful.

### Failure 3: Necessity test failure

Even where a legitimate interest was accepted in principle, SAs frequently found processing went beyond what was necessary. Where controllers asserted technical necessity, SAs were prepared to consider whether a less intrusive technical approach could be adopted.

**Key decision — EDPBI:DEBY:OSS:D:2024:1594 (Worldcoin):** Close examination of the technical architecture chosen, finding the controller could not justify retention of all iris codes simply because their system was designed that way.

### Failure 4: Reasonable expectations violation

Processing that did not respect the reasonable expectations of data subjects was the most common balancing test failure. These decisions generally raised transparency issues also, with controllers often found to have breached Arts. 13/14 GDPR simultaneously.

---

## 2. Step 1 in Practice

### Interest vs. Purpose Distinction

In OSS practice, more sophisticated controllers frame their LIAs using the correct terminology (interest ≠ purpose). Less sophisticated controllers tend to conflate these concepts or assert legitimate interest generically.

**Positive example — Urgent Binding Decision 1/2023 (Meta):** Meta provided a detailed range of interests further divided into sub-interests.

**Negative example — EDPBI:SE:OSS:D:2025:1738:** An online media firm, relying on advice from its consent management platform, used a cookie banner stating reliance on legitimate interest for profiling and precise geodata but could not specify what the legitimate interest actually was, nor demonstrate any balancing test. The LSA noted: "a controller [cannot] disclaim the responsibility to ensure that there is a legal basis for the company's personal data processing by referring to a supplier's recommendations."

### Commercial Interests

All decisions in the dataset recognised (or assumed) that purely commercial interests could qualify as legitimate, even before the CJEU confirmed this in C-621/22 *KNLTB*. However, EDPBI:ES:OSS:D:2020:146 stressed that a purely commercial interest should be given **less weight** in the balancing test and should not prevail over a fundamental right.

### Lawfulness Criterion — "Contrary to Law"

**EDPBI:LT:OSS:D:2024:1361 (Shadow blocking):** Controller "shadow blocked" users on an online marketplace (reducing visibility without their knowledge). The LSA accepted the interest (platform security) was legitimate, but the practice itself has since been prohibited by Art. 17 of the Digital Services Act (Regulation 2022/2065). This illustrates that an interest can become "contrary to law" through regulatory change.

### Societal and Public Interests

**Rule:** EDPB Guidelines 1/2024 clarify that Art. 6(1)(f) requires processing for specific controller/third-party interests — NOT general public interests (which belong under Art. 6(1)(c) or (e)).

**EDPBI:DEBY:OSS:D:2024:1594 (Worldcoin):**
Worldcoin sought to justify iris scanning as promoting "privacy of internet users in general" and "universal access to the global economy for everyone." The LSA characterised these as public interests a private operator could not assert. The LSA also rejected treating data subject interests as third-party interests, citing Art. 4(10) GDPR: "A controller acting (only) in the interests of the data subject should of course not be allowed to process the data of the data subject independently of (or against) their will. Otherwise, a data controller could virtually become the custodian of the interests of the data subject."

**EDPBI:SE:OSS:D:2025:1825 (Flightradar):**
However, wider public interest CAN be taken into account when it overlaps with specific third-party interests. The LSA accepted that Flightradar acted "to some extent in a public interest, which may be considered to weigh relatively heavy in the assessment." Evidence included aviation industry R&D use, media reporting, and national authority investigations.

**BUT:** The LSA disregarded Flightradar's argument that police used the data for criminal investigations, citing C-252/21 *Meta* that a commercially oriented controller cannot rely on law enforcement interests unrelated to its commercial activity.

**Open question from case digest:** Can a controller rely on the legitimate interest of a public authority as third party when that public authority could not itself rely on Art. 6(1)(f)? The Dutch Court of Noord-Nederland (ECLI:NL:RBNNE:2025:83) answered NO — it would be illogical.

---

## 3. Step 2 in Practice

### Necessity Failures from OSS Decisions

| Decision | Processing | Why Not Necessary |
|----------|-----------|-------------------|
| **Urgent BD 1/2023 (Meta)** | Behavioural advertising | Realistic less intrusive alternatives to online behavioural advertising exist |
| **EDPBI:ES:OSS:D:2021:338** | Hotel use of guest photographs for fraud prevention | Other means available: checking surnames/room numbers, requiring signatures |
| **EDPBI:DEBE:OSS:D:2022:477** | Forcing customers to provide phone number for customer service | Email was equally effective and less intrusive; for fraud, blocking the transaction sufficed |
| **EDPBI:CZ:OSS:D:2019:56** | Publishing debtor details online | Legal remedies for debt enforcement available instead |
| **EDPBI:DEBY:OSS:D:2024:1594 (Worldcoin)** | Retaining all iris codes after account closure | Worldcoin could check with connected services if a ban existed; blanket retention placed "every user under general suspicion" |
| **EDPB BD 2/2022 (Instagram children)** | Publishing child business account contact details | Instagram direct messaging was an equally effective alternative |

### Critical Principle from Binding Decision 2/2022

The benefits processing may bring to **data subjects themselves** are NOT relevant to the necessity assessment. Art. 6(1)(f) limits interests to those of the controller or third party. If the necessity asserted is implementing the wishes of the data subject, the appropriate legal basis should be **consent**.

### Technical Architecture Scrutiny

SAs will examine the controller's chosen technical architecture and consider whether a less intrusive design could achieve the same result (EDPBI:DEBY:OSS:D:2024:1594). Controllers cannot hide behind "the system requires it" arguments.

---

## 4. Step 3 in Practice

### Data Subject Interests — Expansive View

OSS decisions take an expansive view of data subject interests:

**EDPBI:CZ:OSS:D:2019:56:** Online publication of debt details could lead to "social exclusion of such persons and their family members, loss of employment and other negative implications."

**EDPBI:EE:OSS:D:2025:1791:** Risk of passenger being refused taxi rides because of negative driver review.

**EDPBI:DEBY:OSS:D:2024:1594 (Worldcoin) — "Right to Lie":**
The Bavarian LSA recognised that data subjects have a **right to conceal information** in response to unjustified demands, and biometric identification systems deprive individuals of this capability. The LSA gave the example of German labour law permitting lying about intimate questions (pregnancy, illness, trade union membership, religion, debts) during job interviews, and noted the broader importance of the ability to lie about one's identity — relevant "not only for prisoners of war and political dissidents, but can be relevant to each and every one."

### Impact Assessment — System Failure Modes

**EDPBI:DEBY:OSS:D:2024:1594 (Worldcoin):**
The LSA assessed not only intended processing impacts but also **failure modes**:
- False negatives in biometric matching → users lose access to essential services → social/economic disadvantage
- Central database compromise → "risks of magnitude that cannot yet be estimated"
- Complete loss of informational self-determination (Informationelle Selbstbestimmung under Arts. 1 and 2(1) German Basic Law)

### Reasonable Expectations — Key Patterns

**Common practice ≠ reasonable expectation:**
- **EDPBI:BE:OSS:D:2020:200 (Social network contact uploading):** Controller argued non-users should expect contact uploads because WhatsApp, Gmail, LinkedIn, etc. do the same. Belgian SA rejected this: practices of other services are not relevant; the requirement of a proper legal basis applies to all providers. Two key points: (1) technically similar processing doesn't determine expectations when purpose differs; (2) common practice among providers ≠ lawful.

**Relationship context determines expectations:**
- **EDPBI:CZ:OSS:D:2022:1278 (Anti-virus software):** Users of anti-virus software expected processing for software improvement, NOT "trend analytics" or disclosure to a third party for commercial resale. The Czech SA stressed users acquired anti-virus software specifically to protect their privacy, and the controller marketed products on these grounds. The SA also considered **significant public outcry** after data sharing emerged as evidence users could not have reasonably anticipated the transfer.

**Deceptive practices by definition violate expectations:**
- **EDPBI:LT:OSS:D:2024:1361 (Shadow blocking):** "The essence of shadow blocking, i.e. the deliberate non-disclosure of information to the user, goes contrary to the principles of GDPR" — affirmed by Lithuanian Regional Administrative Court (eI3-1348-428/2025).

**Transparency failure ≠ automatic balancing failure (but usually contributes):**
- **EDPBI:SE:OSS:D:2022:506:** Anti-fraud data sharing with third party was accepted despite inadequate Art. 13 notice, because credit purchase fraud prevention was objectively within reasonable expectations. Described as a "minor deficiency."
- **EDPBI:DEBB:OSS:D:2020:145:** Port scanning accepted despite privacy notice not explaining it, though the LSA acknowledged "such a method is not expected by an ordinary user."

### Mitigating Measures — Practical Example

**EDPBI:EE:OSS:D:2025:1791 (Ride-hailing passenger ratings):**
Controller reworked its LIA with LSA input. Measures that shifted the balance:
- Detailed explanation of rating process in privacy notice
- Right to challenge ratings
- In-app features showing rating calculations, retention period, consequences, challenge rights
- Clarification that drivers see average rating before accepting fare
- Employee access restrictions for viewing ratings
- Time-limited driver access to passenger average ratings
- Human intervention and manual review for automated account suspensions

After these changes, the LSA concluded Art. 6(1)(f) was a valid basis. Given the cooperative approach, only a reprimand (not fine) was imposed.

---

## 5. Retroactive Reliance

### Dominant Position: NOT Permitted

Most OSS decisions held that a controller cannot retroactively switch legal basis to legitimate interest when the original basis is rejected. Key reasoning (EDPBI:ES:OSS:D:2021:338):
- Data subject deprived of right to know the legitimate interests pursued
- Data subject deprived of right to object to processing
- Any balancing test without data subject input is "vitiated by an act contrary to a mandatory rule"

**Decisions rejecting retroactive switch:** EDPBI:NO:OSS:D:2021:292, EDPBI:CZ:OSS:D:2022:1278, EDPBI:SE:OSS:D:2023:817, EDPBI:ES:OSS:D:2021:338

### Exception: EDPBI:EE:OSS:D:2025:1791

The Estonian LSA permitted a ride-hailing company to retroactively switch from Art. 6(1)(b) to Art. 6(1)(f) for passenger ratings, because:
- Prior Terms of Use/Privacy Policy had referred in a general way to legitimate interest for safety/security
- Data subjects were not substantively harmed by the initial wrong legal basis
- Controller provided sufficient evidence to justify the change
- Controller was required to: (1) have a properly formalised LIA, and (2) make necessary notifications to data subjects

The Estonian LSA cautioned: "The principles of legality, fairness and transparency laid down in the GDPR must be viewed as a whole, so as not to create a dangerous precedent in which the data controller can always rely on a new legal basis for previously collected data. It is therefore not an automatic right."

### Practical Guidance

When assessing whether a controller can retroactively rely on Art. 6(1)(f):
- **Default position:** No — assess must be ex ante
- **Narrow exception possible only if:** prior privacy information at least generally referenced the processing, data subjects not substantively prejudiced, proper LIA now completed and documented, data subjects now fully informed
- **Always flag the regulatory risk** — most SAs will reject this

---

## 6. ePrivacy Overlap

### Key Problem

The OSS mechanism covers GDPR only — no equivalent one-stop-shop for ePrivacy Directive. Enforcement of ePrivacy differs by Member State (some DPAs, some telecoms regulators). This creates practical gaps.

### Practical Patterns from OSS Decisions

**Cookie consent requirement blocks Art. 6(1)(f):**
- ePrivacy Art. 5(3) generally requires consent for cookies → Art. 6(1)(f) NOT available for cookie-based processing
- EDPBI:SE:OSS:D:2025:1738: Swedish LSA could not consider cookie legality (reserved to telecoms regulator) but could assess subsequent processing of cookie-obtained data under GDPR

**ePrivacy consent requirement affects subsequent GDPR processing:**
- Swedish LSA (EDPBI:SE:OSS:D:2025:1738): "If the collected data is further processed at a later stage on the basis of legitimate interest as a legal basis, this specific privacy protection risks being eroded." The consent requirement under ePrivacy provides "particularly strong privacy protection" that must be considered in the Art. 6(1)(f) balancing test.

**Some LSAs addressed ePrivacy within OSS decisions:**
- EDPBI:RO:OSS:D:2020:163: LSA found breach of national ePrivacy transposition for analytics/marketing cookies without consent
- EDPBI:FR:OSS:D:2023:697: LSA found ePrivacy breach for Google reCaptcha cookies without consent

**Port-scanning gap — EDPBI:DEBB:OSS:D:2020:145:**
Online auction site port-scanning visitors assessed only under GDPR Art. 6(1)(f). The question of whether port-scanning constitutes "gaining access to information already stored in the terminal equipment" (ePrivacy Art. 5(3)) went completely unaddressed due to siloed enforcement.

### Guidance for LIA Practitioners

1. **Always check ePrivacy FIRST** — if ePrivacy consent is required (cookies, electronic marketing), Art. 6(1)(f) is likely blocked
2. **Soft opt-in exception** (ePrivacy Art. 13(2)): existing customer electronic marketing of similar products may use Art. 6(1)(f) — but check national transposition
3. **Subsequent processing** of data obtained via ePrivacy-consented cookies: the original consent requirement increases the weight of data subject interests in any Art. 6(1)(f) balancing test
4. **Document the ePrivacy analysis separately** — even if the DPA is the competent authority for both

---

## 7. Consumer Finance

### Credit Checks

**Zalando decisions (EDPBI:DEBE:OSS:D:2024:1279, 1280, 1282):**
- Retailers have a legitimate interest in credit checks before concluding credit transactions
- Credit check should only be triggered after customer **actively selects** a credit payment option
- Must safeguard against accidental triggers (e.g., user accidentally clicking credit option)
- Adequate safeguard example: check only after customer placed goods in basket, entered address, selected "Purchase on invoice" and confirmed by clicking "further" button
- Alternative safeguard: requiring social security number entry before credit transaction (EDPBI:DEBE:OSS:D:2024:1279)

### Credit Default Registries

**EDPBI:EE:OSS:D:2022:319 and EDPBI:MT:OSS:D:2022:375:**
- Art. 6(1)(f) is the appropriate basis for reporting to credit default registries (not Art. 6(1)(b) performance of contract)
- Controller must carry out detailed assessment per case — blanket policy of referring ALL unpaid debts not compatible with Art. 6(1)(f)
- Two distinct legitimate interests: (a) debt collection; (b) informing financial system about indebtedness
- Must comply with transparency obligations by notifying data subject of possible inclusion in default register
- Especially important when debts were purchased by a third party

### Public Identification of Debtors

**EDPBI:CZ:OSS:D:2019:56:**
Czech SA: "In countries where the rule of law applies, [debt collection must] be carried out in a way foreseen by law and not by public denunciation of the debtors."
- Publication of debtor details (even partial: first initial + last name + amount) was sufficient to identify debtors
- Not necessary (legal remedies available instead)
- Not proportionate (social exclusion, employment loss risks)
- Not foreseeable by data subject
- Not time-limited

**BUT: EDPBI:EE:OSS:D:2023:885** — Polish SA confirmed this practice IS routine in Poland following a 2014 Supreme Administrative Court decision. See §10 Cross-Border Divergence.

### Contacting Debtors

**EDPBI:EE:OSS:D:2022:447:**
- Processing personal data of **family members** to contact debtors: NOT based on legitimate interest (not necessary — judicial proceedings available; family members cannot expect data processing for someone else's debts)
- Contacting via social media accounts with similar names: high risk of wrong person → data transfer without legal basis

---

## 8. Anti-Fraud

### Latitude Given by SAs

OSS decisions gave considerable latitude to controllers for anti-fraud measures:

**EDPBI:SE:OSS:D:2022:506:** Forwarding order details to third-party fraud prevention service accepted. Outsourcing was necessary because controller lacked in-house expertise to evaluate risk factors (anonymisation service use, IP address patterns).

**Free trial abuse prevention:**
- EDPBI:SE:OSS:D:2021:196 (music streaming): Retaining identifiers to prevent multiple free trial sign-ups — accepted
- EDPBI:RO:OSS:D:2020:163 (stock photography): Same — accepted
- Key safeguard: identifiers kept in cryptographically modified form, not plaintext

**Port scanning — EDPBI:DEBB:OSS:D:2020:145:**
Online auction site port-scanning ALL visitors (not just high-risk as claimed) to detect compromised devices. LSA accepted despite:
- Port scanning applied to ALL visitors (controller claimed only high-risk)
- Privacy notice did not explain it
- LSA acknowledged "such a method is not expected by an ordinary user"
This decision is questionable and may reflect the ePrivacy gap noted above.

---

## 9. Vehicle/Mobility Monitoring

### Geolocation Data — Highly Sensitive

**EDPBI:FR:OSS:D:2022:430 (Car rental):**
- Geolocation at 500m intervals, every engine on/off and door open/close
- Real-time transmission; stored for entire relationship + 3 years
- French SA: excessive and beyond necessity for theft management

**EDPBI:FR:OSS:D:2023:697 (Scooter rental):**
- Location every 30 seconds while active; stored 24 months
- French SA: excessive

Both decisions cited EDPB Guidelines 1/2020 on connected vehicles: "location data is particularly revealing of the life habits of data subjects... may possibly reveal sensitive information such as religion through places of worship, or sexual orientation through places visited."

### Weight Monitoring — EDPBI:EE:OSS:D:2023:785

Scooter logged rider weight to detect tandem use (alert if weight >1.4× median). LSA accepted:
- Legitimate interest in safety (deterring tandem riding)
- Users could reasonably anticipate enforcement of tandem rules
- Weight monitoring less invasive than alternatives (e.g., video surveillance)
- Alert was warning only — no automated stopping/restriction → not Art. 22

---

## 10. Cross-Border Divergence

### The Core Problem

National law influences the Art. 6(1)(f) assessment at multiple stages, creating possible divergent outcomes between Member States.

**EDPBI:EE:OSS:D:2023:885 (Debt publication — Poland vs. Estonia):**
- Estonian SA: online publication of debtor details excessive under Estonian law
- Polish SA: routine practice following 2014 Supreme Administrative Court decision
- Estonian SA dismissed complaint because controller targeted only the Polish market — applying Polish standards
- **Issue:** GDPR has no applicable law provision for cross-border processing (unlike the old Data Protection Directive Art. 4). The OSS mechanism identifies the LSA but not the applicable law.

**EDPBI:EE:OSS:D:2022:384 (Credit defaults — Spain vs. Estonia):**
- Estonian controller reported Spanish resident's debt to Spanish default register
- Controller relied on Estonian Data Protection Act §10
- Estonian SA found Estonian law could not support the claim because the credit agreement had a Spanish choice-of-law clause

### Implications for Practitioners

- Controllers with cross-border processing may need **multiple localised LIAs**
- LSAs face effective choice-of-law decisions when national standards diverge
- Legal certainty concerns for both controllers and regulators
- The Worldcoin decision (EDPBI:DEBY:OSS:D:2024:1594) adds another dimension: the Bavarian SA relied on German Basic Law guarantee of informational self-determination — should this national constitutional standard apply to data subjects in other Member States?

---

## 11. Novel Legitimate Interests

Beyond well-established interests, some LSAs recognised novel ones:

| Interest | Decision | Status |
|----------|----------|--------|
| Rating taxi passengers for driver safety | EDPBI:EE:OSS:D:2025:1791 | Accepted (with mitigating measures) |
| Preventing banned users from evading service bans | EDPBI:IE:OSS:D:2022:360 | Accepted in principle |
| Recording/sharing global air traffic data for third-party uses | EDPBI:SE:OSS:D:2025:1825 | Accepted |
| Developing AI systems for fraud detection, user assistance, threat detection | EDPB Opinion 28/2024 | Accepted in principle |
| Preventing free trial abuse | EDPBI:SE:OSS:D:2021:196, EDPBI:RO:OSS:D:2020:163 | Accepted |

**Key observation from digest:** In almost every case the interest put forward was recognised as **in principle legitimate** — controllers failed at the necessity and balancing tests, not at the threshold question of whether the interest qualified.

---

## OSS Decision Quick Reference Index

| Decision ID | Controller/Context | Key Issue | Outcome |
|---|---|---|---|
| EDPBI:BE:OSS:D:2022:325 | IAB Europe/TCF | Vague interest articulation | Failed — too generic |
| EDPBI:BE:OSS:D:2020:200 | Social network contacts | Reasonable expectations | Failed — uploading contacts |
| EDPBI:CZ:OSS:D:2019:56 | Debtor publication | Necessity + balancing | Failed — public denunciation |
| EDPBI:CZ:OSS:D:2022:1278 | Anti-virus data sharing | Reasonable expectations | Failed — not expected |
| EDPBI:DEBB:OSS:D:2020:145 | Port scanning | Anti-fraud | Accepted (questionably) |
| EDPBI:DEBE:OSS:D:2022:477 | Forced phone collection | Necessity | Failed — email sufficient |
| EDPBI:DEBE:OSS:D:2024:1279-1282 | Zalando credit checks | Credit check timing | Accepted with safeguards |
| EDPBI:DEBY:OSS:D:2024:1594 | Worldcoin iris scanning | Multiple issues | Failed — multiple grounds |
| EDPBI:EE:OSS:D:2022:319 | Credit default reporting | Legal basis selection | Art. 6(1)(f) required |
| EDPBI:EE:OSS:D:2022:384 | Credit default cross-border | Choice of law | Spanish law applied |
| EDPBI:EE:OSS:D:2022:447 | Contacting debtors via family | Necessity + expectations | Failed — not necessary |
| EDPBI:EE:OSS:D:2023:785 | Scooter weight monitoring | Anti-tandem | Accepted |
| EDPBI:EE:OSS:D:2023:885 | Debt publication cross-border | National divergence | Dismissed (Polish standard) |
| EDPBI:EE:OSS:D:2025:1791 | Ride-hailing ratings | Retroactive basis + mitigating | Accepted after rework |
| EDPBI:ES:OSS:D:2020:146 | Prank call recording | Commercial interest weight | Commercial = less weight |
| EDPBI:ES:OSS:D:2021:338 | Hotel guest photos | Retroactive basis | Rejected — no retroactive |
| EDPBI:FR:OSS:D:2022:430 | Car rental geolocation | Excessive tracking | Failed — disproportionate |
| EDPBI:FR:OSS:D:2023:697 | Scooter rental geolocation | Excessive tracking | Failed — disproportionate |
| EDPBI:FR:OSS:D:2024:1257 | Phone store marketing | Data broker sourcing | Failed — no expectations |
| EDPBI:LT:OSS:D:2024:1361 | Shadow blocking | Deceptive practice | Failed — not expected/proportionate |
| EDPBI:MT:OSS:D:2022:375 | Credit default (ASNEF) | Legal basis + transparency | Art. 6(1)(f) accepted with conditions |
| EDPBI:PL:OSS:D:2020:194 | Bank data retention | Speculative future claims | Failed — not real/present |
| EDPBI:SE:OSS:D:2021:196 | Free trial abuse (music) | Anti-abuse retention | Accepted (crypto-modified) |
| EDPBI:SE:OSS:D:2022:506 | Third-party fraud service | Anti-fraud outsourcing | Accepted |
| EDPBI:SE:OSS:D:2025:1738 | Cookie-based profiling | CMP reliance + ePrivacy | Failed — no LIA documented |
| EDPBI:SE:OSS:D:2025:1825 | Flightradar | Third-party/public interest | Accepted |
| Urgent BD 1/2023 | Meta behavioural ads | Necessity | Failed — alternatives exist |
| BD 2/2022 | Meta/Instagram children | Multiple issues | Failed — children, necessity |
