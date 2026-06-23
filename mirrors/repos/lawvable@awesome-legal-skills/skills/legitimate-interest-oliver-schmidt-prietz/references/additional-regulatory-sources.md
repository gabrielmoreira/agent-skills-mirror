# Additional Regulatory Sources on Legitimate Interest

## Table of Contents
1. [EDPB Opinion 28/2024 — AI Models and Legitimate Interest](#1-edpb-opinion-282024)
2. [CNIL Guidance — Legitimate Interest for AI Development (June 2025)](#2-cnil-ai-guidance)
3. [UK ICO — Legitimate Interests Guidance (updated March 2026)](#3-uk-ico)
4. [German DPA Guidance (DSK, Hamburg, Baden-Württemberg, Bavaria)](#4-german-dpas)
5. [Other National DPA Guidance and Positions](#5-other-national-dpas)
6. [Video Surveillance — EDPB Guidelines 3/2019](#6-video-surveillance)
7. [Social Media Targeting — EDPB Guidelines 8/2020](#7-social-media-targeting)
8. [Connected Vehicles — EDPB Guidelines 1/2020](#8-connected-vehicles)

---

## 1. EDPB Opinion 28/2024

**Full title:** Opinion 28/2024 on certain data protection aspects related to the processing of personal data in the context of AI models (adopted 17 December 2024)

**Requested by:** Irish DPC under Art. 64(2) GDPR

**Scope:** Four questions: (1) AI model anonymity; (2) legitimate interest for AI development; (3) legitimate interest for AI deployment; (4) consequences of unlawful processing in development phase.

### Key Findings on Legitimate Interest for AI

**General confirmation:** Legitimate interest CAN serve as a legal basis for both development and deployment of AI models (paras. 59-108).

**Three-step test applies fully** — building on Guidelines 1/2024 (para. 66).

#### Step 1 — Legitimate Interest Examples for AI

Recognised examples (para. 69):
- Developing a conversational agent to assist users
- Developing AI to detect fraudulent content or behaviour
- Improving threat detection in information systems

Must still be: lawful, clearly articulated, real and present (para. 68).

**Lawfulness check must include other regulatory frameworks** — e.g., AI Act prohibited practices (Art. 5), DSA targeted advertising to minors prohibition (Art. 28), copyright/IP law (Directive 2019/790) (fn. 54).

#### Step 2 — Necessity for AI

Critical question (para. 73): "If the pursuit of the purpose is also possible through an AI model that does not entail processing of personal data, then processing personal data should be considered as not necessary."

Key factors:
- Volume of personal data must be proportionate (para. 73)
- Assess less intrusive alternatives (synthetic data, anonymised data, smaller datasets)
- First-party vs. third-party data: less intrusive alternatives may vary (para. 74)
- Technical safeguards (pseudonymisation, data masking) contribute to necessity test (para. 75)

#### Step 3 — Balancing for AI

**Development phase risks (paras. 77-80):**
- Interest in self-determination and control over own data
- Privacy risks from scraping against DS wishes or without knowledge
- Large-scale/indiscriminate collection creates sense of surveillance → self-censorship → freedom of expression risk (Art. 11 Charter)
- Risk of extraction, membership inference, model inversion attacks

**Deployment phase risks (paras. 80-81):**
- Inappropriate content to vulnerable individuals → mental health (Art. 3(1) Charter)
- Job application pre-selection → right to engage in work (Art. 15 Charter)
- Discrimination based on personal characteristics (Art. 21 Charter)
- Physical and safety risks from malicious use
- BUT also potential positive impacts: better healthcare access, education, accessibility

**Reasonable expectations for AI (paras. 91-95):**

Key criteria for SAs to assess:
1. Whether personal data was publicly available
2. Nature of relationship between data subject and controller (and whether a link exists)
3. Nature of the service
4. Context in which personal data was collected
5. Source from which data was collected (website/service + privacy settings offered)
6. Potential further uses of the model
7. Whether data subjects are actually aware their personal data is online at all

**Critical point (para. 92):** Simply including AI training information in a privacy policy does NOT mean data subjects can reasonably expect it — must be analysed on specific circumstances.

**First-party vs. third-party data (para. 94):** Reasonable expectations differ depending on whether data was made public by the data subject, directly provided to the controller, or obtained from another source (e.g., via web scraping).

#### Mitigating Measures for AI (paras. 96-108)

**Development phase measures:**

Technical:
- Pseudonymisation to prevent combination of data based on individual identifiers (para. 101b)
- Data masking / substitution with fake data (e.g., replacing names/emails with fake versions) — especially appropriate for LLM training where actual content of identifiers is irrelevant (para. 101c)
- Anonymisation measures from §3.2.2 that don't fully anonymise but still reduce identifiability (para. 100a)

Rights facilitation:
- Reasonable waiting period between data collection and training use — allows DS to exercise rights (para. 102a)
- Unconditional opt-out from the outset (goes beyond Art. 21 GDPR) (para. 102b)
- Extended right to erasure beyond Art. 17(1) grounds (para. 102c)
- Mechanism for DS to submit regurgitation/memorisation claims (para. 102d)

Transparency:
- Public communications beyond Arts. 13/14 requirements — additional details on collection criteria, datasets used, with special protection for children/vulnerable persons (para. 103a)
- Alternative information forms: media campaigns, email, graphic visualisation, FAQs, transparency labels, model cards, voluntary annual transparency reports (para. 103b)

**Web scraping-specific measures (paras. 104-106):**
- Exclude content from publications with data about persons at risk of harm (para. 105a)
- Exclude certain data categories / certain sources by subject matter sensitivity (para. 105b)
- Respect robots.txt, ai.txt, or other exclusion mechanisms (para. 105c)
- Time-based collection limits (para. 105d)
- Create an opt-out list allowing DS to object before collection occurs (para. 106)

**Deployment phase measures (para. 107):**
- Output filters preventing storage/regurgitation/generation of personal data (para. 107a)
- Digital watermarking of AI-generated outputs (para. 107a)
- Accelerated exercise of DS rights — erasure from output, deduplication, post-training techniques (para. 107b)

#### Impact of Unlawful Development on Deployment (paras. 109-132)

Three scenarios:

**Scenario 1 — Same controller, personal data retained:**
- Whether development and deployment are separate purposes (thus separate processing activities) must be assessed case-by-case
- If subsequent processing based on Art. 6(1)(f): unlawfulness of initial processing must be taken into account in the LIA (para. 123)

**Scenario 2 — Different controller deploys:**
- Deploying controller must conduct accountability assessment to ascertain the model was not developed by unlawfully processing personal data (para. 129)
- Assessment should consider: source of data, whether any SA/court finding of infringement exists
- AI Act EU declaration of conformity is NOT conclusive proof of GDPR compliance, but may be considered (para. 131)

**Scenario 3 — Model anonymised after unlawful development:**
- If model is demonstrated anonymous → GDPR does not apply to subsequent operation
- Unlawfulness of initial processing does NOT impact subsequent operation of anonymous model
- BUT: any new personal data processing in deployment phase is separately governed by GDPR

#### Right to Object for AI

EDPB explicitly recalls (para. 65): whenever legitimate interest is relied upon, Art. 21 right to object applies and must be ensured. Two aspects for SAs: (1) whether controller can demonstrate compelling overriding legitimate grounds; (2) whether right to object can be exercised in practice.

---

## 2. CNIL AI Guidance

**Full title:** Recommendation on relying on the legal basis of legitimate interests to develop an AI system (published 19 June 2025)

**Companion document:** Focus sheet on measures for data collection by web scraping (19 June 2025)

### Key Positions

- CNIL confirms legitimate interest is the most likely legal basis for AI developers (consent impractical at scale)
- Builds explicitly on EDPB Opinion 28/2024
- More detailed operational guidance than EDPB — considered the most comprehensive national DPA guidance on this topic
- Provides practical scenarios for applying the three-step test in AI development contexts

**Examples of legitimate interests for AI development:**
- Scientific research
- Facilitating public access to information
- Product/service improvement
- Fraud prevention
- Improving cybersecurity

**Mandatory measures for web scraping:**
- Precise data collection criteria
- Exclusion of certain data categories from collection
- Timely deletion of irrelevant data collected
- Respect exclusion mechanisms (robots.txt, CAPTCHA)
- Limit collection to freely accessible data (no login/account required)
- Publish updated list of websites affected by scraping
- Inform data subjects (e.g., via website publishers)

**Additional recommended measures:**
- Exclude websites that expressly object to scraping for AI training
- Draw up list of excluded websites
- Develop technical solutions facilitating pre-collection objection by data subjects

**Divergence with Dutch DPA:** The Netherlands Autoriteit Persoonsgegevens has asserted that web scraping for AI training should only occur with prior consent. CNIL explicitly takes a more pragmatic position, confirming that legitimate interest is available.

---

## 3. UK ICO

**Guidance:** Legitimate interests (updated 23 March 2026 to reflect Data (Use and Access) Act 2025)

### Key Differences from EDPB Approach

**Necessity standard:** ICO uses "targeted and proportionate" rather than EDPB's "strictly necessary" — the ICO states it "doesn't mean that it has to be absolutely essential." This is a **more permissive standard** than the EDPB/CJEU approach.

**Three-part test (same structure):**
1. Purpose test — Is there a legitimate interest behind the processing?
2. Necessity test — Is the processing necessary for that purpose?
3. Balancing test — Do the individual's interests override the legitimate interest?

**LIA documentation:** Not explicitly required by UK GDPR but strongly recommended as accountability evidence. No standardised format — can be short or detailed depending on complexity.

### UK Recognised Legitimate Interest (DUA Act 2025)

**New lawful basis (separate from standard legitimate interests)** introduced under Data (Use and Access) Act 2025, effective August 2025:

Five pre-approved purposes — **no balancing test required** (only necessity test):
1. Responding to disclosures requested by bodies performing public functions
2. Safeguarding national security, public security, or defence
3. Responding to emergency situations
4. Preventing, detecting, or investigating crimes
5. Safeguarding children or vulnerable adults

**Key distinctions from EU:**
- Public authorities CAN'T rely on recognised legitimate interest for their public tasks
- Special category and criminal offence data processing permitted under RLI (with additional conditions)
- Additional conditions may be added by regulation in future

**Practical note for cross-border controllers:** If operating in both EU and UK, the EDPB's stricter standard should be applied as a baseline. The UK's more permissive approach cannot be relied upon for EU processing.

---

## 4. German DPA Guidance

### DSK Joint Guidance — "AI and Data Protection" (6 May 2024, v1.0)

The Datenschutzkonferenz (DSK — joint body of all German federal/state DPAs) published unified guidance for AI deployment covering:
- Use case and purpose definition required before deployment
- Legal basis must be established — refers to Baden-Württemberg DPA paper for detailed analysis
- Art. 22 GDPR strictly interpreted — effective human oversight required
- Preference for closed AI systems over open systems (better control)
- DPIA requirement for high-risk AI processing

### Hamburg DPA — Discussion Paper on LLMs and GDPR (15 July 2024)

**Controversial position:** LLMs may not "store" personal data in GDPR terms — model parameters are abstract mathematical representations, not records:
- Storing an LLM model does not itself constitute personal data processing
- Training data extraction attacks require "disproportionate effort" → may not meet Breyer "reasonably likely means" test
- DS rights (access, rectification, erasure) apply only to inputs and outputs, not the model itself

**EDPB disagreed** in Opinion 28/2024 — AI models trained on personal data "cannot, in all cases, be considered anonymous" and must be assessed case-by-case (para. 34).

**Status:** Discussion paper intended to stimulate debate, not formal guidance. Superseded in practical terms by EDPB Opinion 28/2024.

### Baden-Württemberg DPA — "Rechtsgrundlagen im Datenschutz beim Einsatz von KI"

Paper on legal bases for AI use — referenced by DSK guidance as the primary source for legal basis analysis. Covers all six legal bases with AI-specific analysis.

### Bavaria (BayLDA)

Flyer and checklist on GDPR-compliant AI — practical orientation for SMEs deploying AI.

---

## 5. Other National DPA Guidance and Positions

### Netherlands (Autoriteit Persoonsgegevens)

**Position on web scraping for AI:** Asserts that legitimate interest CANNOT be relied upon for web scraping for AI training — consent is required. This is the most restrictive national position in the EU and diverges from both the EDPB Opinion 28/2024 and the CNIL guidance.

### Italy (Garante)

Active enforcement on AI and legitimate interest — notable actions against ChatGPT/OpenAI (2023-2024) and enforcement of data subject rights in AI context. Specific national rule: Art. 2-decies of the Italian Data Protection Code provides that data processed in violation of data protection rules cannot be used (relevant for Scenario 1 of EDPB Opinion 28/2024).

### Spain (AEPD)

Guidance on legitimate interest for video surveillance. National rules under LOPDGDD Art. 19-20 on legitimate interest for commercial situations and credit default processing.

### EDPB ChatGPT Taskforce Report (23 May 2024)

Addressed data protection issues around ChatGPT across multiple DPAs. Key relevant findings:
- Different processing stages in AI development may constitute separate processing activities (para. 14)
- Publicly accessible data ≠ data "manifestly made public" by the data subject for Art. 9(2)(e) purposes (para. 18)
- Art. 14(5)(b) GDPR exception (disproportionate effort for information provision) is strictly limited (para. 27)

---

## 6. Video Surveillance — EDPB Guidelines 3/2019

**Relevance to LIA:** Video surveillance is one of the most common legitimate interest scenarios. The guidelines address:
- Necessity and proportionality of CCTV
- Signage and transparency requirements
- Retention period limits
- Special considerations for employees, public spaces, residential areas
- Legitimate interests recognised: property protection, safety, evidence collection

**Note from case digest:** No OSS decisions on video surveillance were found — this is because video surveillance typically lacks the cross-border dimension required for the OSS mechanism.

---

## 7. Social Media Targeting — EDPB Guidelines 8/2020

**Relevance to LIA:** Targeting of social media users based on observed behaviour, inferred data, or provided data raises specific legitimate interest questions.

Key points:
- Reasonable expectations of users on social media platforms (para. 66): "the mere fulfilment of information obligations is not sufficient to consider that data subjects can reasonably expect a given processing"
- Power dynamics between platforms and users
- Particular concerns about targeting of minors

---

## 8. Connected Vehicles — EDPB Guidelines 1/2020

**Relevance to LIA:** Location data from connected vehicles is highly sensitive.

Key passage (para. 63): "location data is particularly revealing of the life habits of data subjects. The journeys undertaken are very characteristic in that they enable one to infer the place of work and of residence, as well as a driver's centres of interest (leisure), and may possibly reveal sensitive information such as religion through places of worship, or sexual orientation through places visited."

Cited in multiple OSS decisions on rental vehicle monitoring (EDPBI:FR:OSS:D:2022:430, EDPBI:FR:OSS:D:2023:697).

---

## Source Hierarchy for LIA Assessment

When conducting a legitimate interest assessment, apply sources in this order of authority:

1. **GDPR text** (Art. 6(1)(f), Recitals 47-50) — binding
2. **CJEU case law** — binding interpretation
3. **EDPB Guidelines 1/2024** — authoritative, to be given "utmost account" by SAs
4. **EDPB Opinion 28/2024** (for AI) — authoritative, Art. 64(2) opinion
5. **EDPB OSS Case Digest** (McIntyre 2026) — illustrative enforcement practice
6. **National DPA guidance** (CNIL, ICO, DSK, etc.) — authoritative within jurisdiction, persuasive elsewhere
7. **WP29 Opinion 06/2014** — historical, not formally endorsed by EDPB, but still referenced
8. **National court judgments** — binding within jurisdiction, persuasive elsewhere
9. **Academic commentary** — persuasive only
