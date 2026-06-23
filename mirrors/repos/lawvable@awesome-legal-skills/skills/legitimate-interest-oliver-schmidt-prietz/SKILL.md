---
name: legitimate-interest
description: |
  GDPR Legitimate Interest Assessment (LIA) — Guided assessment for Art. 6(1)(f) GDPR using the EDPB three-step test. Based on EDPB Guidelines 1/2024, EDPB Opinion 28/2024 (AI models), the OSS Case Digest on Legitimate Interest (McIntyre 2026), CNIL AI guidance (June 2025), ICO guidance, and key CJEU case law. Use when: (1) user needs to assess whether legitimate interest is appropriate, (2) user asks about Art. 6(1)(f), "Interessenabwägung", "berechtigtes Interesse", "balancing test", or "LIA", (3) user wants to document a legitimate interest assessment, (4) user mentions the three-step test, (5) user evaluates necessity or proportionality under Art. 6(1)(f), (6) user discusses direct marketing, fraud prevention, IT security, employee monitoring, AI training, web scraping, or credit checks in context of legal basis, (7) user handles a right to object (Art. 21), (8) user asks about children's data, profiling, or cross-border data sharing under legitimate interest, (9) user compares legitimate interest against other legal bases. Do NOT use for: consent assessments (Art. 6(1)(a)), contract performance (Art. 6(1)(b)), DPIA workflows, or pure ePrivacy/cookie compliance questions — though the skill does address the ePrivacy/GDPR overlap where relevant.
---

# GDPR Legitimate Interest Assessment (LIA)

Guide users through a comprehensive Art. 6(1)(f) GDPR assessment using the EDPB three-step test, producing a documented Legitimate Interest Assessment (LIA) suitable for accountability records.

## Legal Framework

**Primary Sources:**
- **GDPR Art. 6(1)(f)** — Legitimate interest legal basis
- **EDPB Guidelines 1/2024** on processing based on Art. 6(1)(f) GDPR (adopted 8 October 2024) — the core interpretive document
- **EDPB Opinion 28/2024** on AI models and processing of personal data (17 December 2024) — AI-specific LIA guidance; see [references/additional-regulatory-sources.md] §1
- **EDPB OSS Case Digest on Legitimate Interest** (March 2026, Dr. TJ McIntyre) — 62 OSS decisions + 5 EDPB binding decisions analysed; see [references/oss-enforcement-practice.md]
- **CNIL Recommendations on Legitimate Interest for AI Development** (19 June 2025) + companion web scraping focus sheet — the most operationally detailed national guidance on AI + LI; see [references/additional-regulatory-sources.md] §2
- **UK ICO Legitimate Interests Guidance** (updated 23 March 2026) — includes DUA Act 2025 "Recognised Legitimate Interest" new basis; note divergent necessity standard; see [references/additional-regulatory-sources.md] §3
- **WP29 Opinion 06/2014** on legitimate interests under Art. 7 Directive 95/46/EC (not formally endorsed by EDPB, but still referenced)
- **DSK Joint Guidance "AI and Data Protection"** (6 May 2024) — German DPA unified position
- **GDPR Recitals 47, 48, 49, 50** — contextual guidance on legitimate interest
- **NIS2 Directive** (Recital 121) — legitimates cybersecurity information-sharing under Art. 6(1)(f)

**Additional EDPB Guidance with LI Relevance:**
- EDPB Guidelines 3/2019 on video surveillance
- EDPB Guidelines 8/2020 on targeting of social media users
- EDPB Guidelines 1/2020 on connected vehicles and mobility
- EDPB ChatGPT Taskforce Report (23 May 2024)
- EDPB Guidelines 5/2020 on Consent (on switching legal bases)

For full regulatory source catalogue including national DPA guidance: [references/additional-regulatory-sources.md]

**Key CJEU Jurisprudence** (for full case details and citation format, see [references/cjeu-case-law.md]):
- C-252/21 *Meta v. Bundeskartellamt* (4 July 2023) — restrictive interpretation, personalised advertising
- C-26/22 & C-64/22 *SCHUFA Holding* (7 December 2023) — creditworthiness, compelling legitimate grounds
- C-621/22 *KNLTB* (4 October 2024) — commercial interests can be legitimate; data sharing with sponsors
- C-708/18 *Asociaţia de Proprietari* (11 December 2019) — CCTV, present and effective interest
- C-13/16 *Rīgas satiksme* (4 May 2017) — third-party interest in legal claims
- C-17/22 & C-18/22 *HTB Neunte Immobilien Portfolio* (12 September 2024) — investment fund data sharing
- C-394/23 *Mousse* (9 January 2025) — no hierarchy among legal bases
- C-654/23 *Inteligo Media* (2025) — ePrivacy Directive as lex specialis to GDPR

---

## Session Initialization

### 1. Display Disclaimer

> **IMPORTANT NOTICE**
> This tool guides you through a Legitimate Interest Assessment (LIA) based on the EDPB three-step test methodology under Art. 6(1)(f) GDPR. It does not constitute legal advice. The outcome should be:
> - Reviewed by your Data Protection Officer (DPO)
> - Validated by qualified legal counsel
> - Documented as part of your accountability records (Art. 5(2) GDPR)
>
> **Do you acknowledge this and wish to proceed?**

Wait for acknowledgment before proceeding.

### 2. When to Search the Web

Data protection enforcement evolves continuously. On activation, search for recent developments relevant to the user's scenario:

```
EDPB legitimate interest enforcement [current year]
```

Also search when:
- The user's scenario involves **AI/ML training or web scraping** — check for EDPB web scraping guidelines (announced in work programme), CNIL updates, and national DPA positions which are evolving rapidly
- The user mentions a **specific national jurisdiction** — search for the latest DPA guidance in that jurisdiction (e.g., "ICO legitimate interests guidance [current year]", "CNIL intérêt légitime IA [current year]")
- The user references a **specific CJEU case or pending referral** — verify the status and outcome, as new judgments frequently affect the Art. 6(1)(f) landscape
- The processing context involves a **rapidly evolving regulatory area** (DSA enforcement, AI Act implementation, ePrivacy Regulation progress)
- The user mentions **UK processing** — check for ICO recognised legitimate interest updates and DUA Act 2025 implementation status

### 3. Determine Assessment Mode

> "What would you like to do?"

| Mode | Description |
|------|-------------|
| **Full LIA** | Complete three-step assessment with documented output |
| **Quick Check** | Rapid feasibility screening — can Art. 6(1)(f) plausibly apply? |
| **Legal Basis Comparison** | Compare Art. 6(1)(f) against alternative bases for a specific processing |
| **Right to Object Response** | Assess compelling legitimate grounds after Art. 21 objection |

---

## Pre-Assessment Gate: Is Art. 6(1)(f) Even Available?

Before entering the three-step test, check threshold exclusions:

| Gate | Check | If YES |
|------|-------|--------|
| **G1** | Is the controller a public authority performing its tasks? | Art. 6(1)(f) NOT available (Art. 6(1), second indent). Exception: ancillary non-public activities (e.g., managing own premises) — document internally. |
| **G2** | Does the processing fall under ePrivacy Directive (Art. 5(3) or Art. 13)? | Consent likely required first. Check if the Art. 13(2) "soft opt-in" exception applies for existing customer electronic marketing. |
| **G3** | Does national law restrict or exclude Art. 6(1)(f) for this processing type? | Flag jurisdiction-specific restrictions. Check [references/jurisdiction-notes.md]. |
| **G4** | Is the controller trying to use Art. 6(1)(f) as a fallback because consent was refused or withdrawn? | Flag: switching legal bases post-hoc is problematic (EDPB Guidelines 1/2024, para. 9). |

If all gates pass → proceed to three-step test.

---

## Three-Step Test: Guided Assessment

### Information Gathering (Adaptive Conversational Flow)

Gather context through a conversational approach. Be efficient but thorough — a legitimate interest assessment is only as good as the factual basis it rests on. Ask as many follow-ups as needed to cover all required fields, but group related questions to avoid excessive back-and-forth.

#### Batch 1: Essential Questions (always asked)

> **Let's build your Legitimate Interest Assessment.**
>
> Please describe the processing activity in your own words. I need to understand:
>
> **1. What processing do you want to carry out and why?** (What personal data, for what purpose, what is the broader business interest?)
>
> **2. Who is involved?** (Who is the controller? Is a third party's interest being pursued? Who are the data subjects?)
>
> **3. What is the relationship with the data subjects?** (Customers, employees, website visitors, non-customers, children?)

#### Coverage Check (internal — after each user response)

After each response, silently check coverage of these fields:

| # | Field | Needed for |
|---|-------|------------|
| 1 | Processing description | All steps |
| 2 | Interest articulation | Step 1 |
| 3 | Controller identity / third party | Step 1 |
| 4 | Data categories | Step 2 + 3 |
| 5 | Data subjects & relationship | Step 3 |
| 6 | Scale / volume | Step 3 |
| 7 | Sector / context | Step 3 |
| 8 | Alternatives considered | Step 2 |
| 9 | Jurisdiction(s) | Pre-assessment gates + Step 3 |

#### Follow-Up Questions (as many as needed)

- If the user's initial response covers most fields, ask one focused follow-up for the gaps.
- If significant gaps remain, group related missing fields into a conversational follow-up. For example, if scale, sector, and jurisdiction are all missing, ask them together rather than in three separate turns.
- If the scenario is complex (multi-jurisdictional, involving special categories, AI/ML, children), it is better to ask an additional clarifying question than to proceed on assumptions. A flawed factual basis produces a flawed LIA.
- Where a field is partially covered, use confirmation prompts rather than full re-asks. Example: "You mentioned healthcare — is this specifically medical devices, or a broader health service?"
- If a field remains unresolvable after follow-up, mark it as `[UNCLEAR — proceeding with cautious assumptions]` and note the assumption. Flag this in the output so the user knows to verify.

---

### STEP 1: Pursuit of a Legitimate Interest

Read [references/step1-legitimate-interest.md] for detailed criteria and EDPB/CJEU examples.

Assess three cumulative criteria (EDPB Guidelines 1/2024, para. 17):

| Criterion | Test | Red Flags |
|-----------|------|-----------|
| **Lawful** | Is the interest contrary to EU or Member State law? | Promoting prohibited products (EDPB Example 1: e-cigarettes); circumventing legal requirements; practices now prohibited by DSA Art. 17 (OSS: shadow blocking case EDPBI:LT:OSS:D:2024:1361) |
| **Clearly articulated** | Is the interest precisely described, not vague? | "For the greater good" / "general security" (EDPB Example 2); "measure content performance" / "apply market research" (OSS: EDPBI:BE:OSS:D:2022:325 IAB Europe); "creating innovative products" (EDPB BD 2/2022 Instagram children). Vague articulation is the **most common pitfall** in OSS enforcement. |
| **Real and present** | Is the interest current and concrete, not hypothetical? | "In case we launch a product someday" (EDPB Example 3); retaining data for "theoretically possible future claim" (OSS: EDPBI:PL:OSS:D:2020:194) |

**Controller vs. Third Party Interest:**
- Controller's interest must relate to its actual activities (C-252/21 *Meta*, para. 124)
- Third-party interest: must still meet all three criteria; connection to controller's activities required
- Both can be pursued simultaneously (C-26/22 *SCHUFA*, para. 83)
- **Data subject interests ≠ third-party interests** — Art. 4(10) GDPR defines "third party" as someone OTHER than the data subject. A controller cannot act as "custodian" of data subject interests to justify processing against their will (OSS: EDPBI:DEBY:OSS:D:2024:1594 Worldcoin, para. 589)
- **Public interests** → generally Art. 6(1)(c) or (e), NOT Art. 6(1)(f). But wider public interest CAN be considered where it overlaps with specific third-party interests (OSS: EDPBI:SE:OSS:D:2025:1825 Flightradar)
- **Cannot rely on public authority's interest** when that authority could not itself use Art. 6(1)(f) (Court of Noord-Nederland, ECLI:NL:RBNNE:2025:83)

**CMP/Tech Provider Warning:** A controller cannot "disclaim the responsibility to ensure that there is a legal basis for the company's personal data processing by referring to a supplier's recommendations" (OSS: EDPBI:SE:OSS:D:2025:1738)

**Output for Step 1:**
- Clearly articulated interest statement
- Classification: Controller interest / Third-party interest / Both
- Lawfulness confirmation with reasoning
- Reality/presence confirmation
- Verdict: **PASS** / **FAIL** / **REQUIRES REFINEMENT**

If FAIL → Art. 6(1)(f) cannot be used. Suggest alternative legal bases.
If PASS → proceed to Step 2.

---

### STEP 2: Necessity of the Processing

Read [references/step2-necessity.md] for detailed analysis framework.

Assess whether the processing is **strictly necessary** for the identified interest (C-26/22 *SCHUFA*, para. 88):

| Factor | Assessment |
|--------|------------|
| **Less intrusive alternatives** | Could the interest be achieved equally effectively by other means? (C-252/21, para. 108) |
| **Data minimisation** | Is each data category necessary? Could fewer categories achieve the same result? (Art. 5(1)(c); C-252/21, para. 109) |
| **Proportionality** | Is the scope of processing proportionate to the interest? |
| **Controller vs. third-party** | If third-party interest: necessity is harder to demonstrate and less expected by data subjects (EDPB Guidelines, para. 30) |

**Key principle:** "Necessary" ≠ "useful" or "convenient". The CJEU requires **strict necessity** (C-26/22, para. 88).

**Necessity failures from OSS enforcement** (see [references/oss-enforcement-practice.md] §3):
- Hotel guest photos for fraud prevention → checking surnames/room numbers sufficed (EDPBI:ES:OSS:D:2021:338)
- Forcing phone number for customer service → email equally effective (EDPBI:DEBE:OSS:D:2022:477)
- Publishing debtor details online → legal remedies available instead (EDPBI:CZ:OSS:D:2019:56)
- Retaining ALL iris codes after account closure → places "every user under general suspicion" (EDPBI:DEBY:OSS:D:2024:1594 Worldcoin)
- Publishing child business account contact details → Instagram DM was an equally effective alternative (EDPB BD 2/2022)
- Behavioural advertising → realistic less intrusive alternatives exist (Urgent BD 1/2023 Meta)

**Critical principle from EDPB BD 2/2022:** Benefits to DATA SUBJECTS are not relevant to the necessity assessment under Art. 6(1)(f). If the justification is implementing data subject wishes → use consent instead.

**Technical architecture scrutiny:** SAs will examine whether a less intrusive technical design could achieve the same result. Controllers cannot hide behind "the system requires it" (EDPBI:DEBY:OSS:D:2024:1594).

**Analysis approach:**
1. List all data categories to be processed
2. For each category: justify why it is strictly necessary
3. Identify any less intrusive alternatives and explain why they are insufficient
4. Document the data minimisation analysis

**Output for Step 2:**
- Data categories with necessity justification
- Alternatives considered and reasons for rejection
- Data minimisation confirmation
- Verdict: **PASS** / **FAIL** / **REQUIRES SCOPE REDUCTION**

If FAIL → Processing cannot be based on Art. 6(1)(f). Suggest reducing scope or alternative bases.
If PASS → proceed to Step 3.

---

### STEP 3: Balancing Test

Read [references/step3-balancing.md] for the full balancing methodology, contextual factors, and case examples.

This is the core assessment. The controller must weigh its legitimate interests against the data subjects' interests, fundamental rights and freedoms.

#### 3a. Identify Data Subject Interests, Rights and Freedoms

Consider:
- Right to data protection and privacy (Art. 7, 8 Charter)
- Other fundamental rights that may be affected (expression, non-discrimination, property, physical/mental integrity)
- Financial, social, and personal interests
- Special vulnerability (children, employees, patients)
- **"Right to lie" / informational self-determination** — Data subjects may have a legitimate interest in concealing information in response to unjustified demands. Biometric/uniquely identifying systems deprive individuals of this capability (OSS: EDPBI:DEBY:OSS:D:2024:1594 Worldcoin — Bavarian LSA recognised this extends from labour law right to lie on intimate questions to broader identity concealment needs)
- **Debt publication → social exclusion** — Publication of debtor details can lead to "social exclusion, loss of employment and other negative implications" (OSS: EDPBI:CZ:OSS:D:2019:56)

#### 3b. Assess Impact of Processing

| Factor | Analysis |
|--------|----------|
| **Nature of data** | Simple contact data vs. sensitive/Art. 9 data vs. financial vs. location data. More sensitive = heavier weight against controller. |
| **Context** | Scale; controller-subject relationship (employer/employee requires different analysis); data combination; accessibility/publicity; vulnerable subjects |
| **Consequences** | Decisions by third parties; legal effects; discrimination risk; reputational harm; financial loss; exclusion from services; chilling effects; loss of control over data |
| **System failure modes** | For large-scale systems: also assess impact of false positives/negatives and potential compromise (OSS: EDPBI:DEBY:OSS:D:2024:1594 Worldcoin — false negatives in biometric matching → loss of access to essential services; central database compromise → "risks of magnitude that cannot yet be estimated") |

#### 3c. Reasonable Expectations

Critical factor (Recital 47 GDPR; C-252/21 *Meta*, para. 117):

| Indicator | Weight |
|-----------|--------|
| Existing relationship (customer vs. non-customer) | Customers have higher expectations of some processing |
| Nature of service | Free social network ≠ expectation of data-driven advertising (C-252/21) |
| Context of data collection | In-store vs. scraped from public profiles (EDPB Example 6) |
| Common practice ≠ reasonable expectation | Sector norms alone insufficient (EDPB Guidelines, para. 52) |
| Information provided | Transparency helps but does NOT create reasonable expectations by itself (para. 53) |
| **Product marketing vs. processing reality** | Anti-virus users expected privacy protection, NOT data resale for "trend analytics" (OSS: EDPBI:CZ:OSS:D:2022:1278 — public outcry was evidence of violated expectations) |
| **Data broker sourcing** | Data subjects cannot expect marketing from companies whose identity was never disclosed by the data broker (OSS: EDPBI:FR:OSS:D:2024:1257) |
| **Deceptive practices** | Almost by definition outside reasonable expectations — shadow blocking (OSS: EDPBI:LT:OSS:D:2024:1361; affirmed by Lithuanian court) |
| **Contact uploading** | Other platforms doing the same ≠ user expectation for THIS platform; similar technology ≠ same purpose (OSS: EDPBI:BE:OSS:D:2020:200) |

#### 3d. Finalise the Balance

If the balance tips against the controller:
1. Consider **mitigating measures** that go BEYOND GDPR obligations (para. 57):
   - Extended erasure rights (beyond Art. 17(1) grounds)
   - Unrestricted right to object (beyond Art. 21 limits)
   - Data portability for Art. 6(1)(f) processing
   - Pseudonymisation, aggregation, shorter retention
   - Opt-out mechanisms beyond legal minimum
2. Perform the balancing test AGAIN with measures in place (para. 58)
3. If still overridden → Art. 6(1)(f) CANNOT be used

**Practical mitigating measures example (OSS: EDPBI:EE:OSS:D:2025:1791 ride-hailing ratings):**
Controller reworked its system with LSA input to include: detailed privacy notice explanation; right to challenge ratings; in-app features showing calculations/retention/consequences; clarification of driver visibility of ratings; employee access restrictions; human review of automated suspensions. After these changes, Art. 6(1)(f) was accepted. This cooperative approach resulted in only a reprimand (not fine).

**Output for Step 3:**
- Identified rights and interests at stake
- Impact assessment summary
- Reasonable expectations analysis
- Mitigating measures (if applicable)
- Final balance verdict with reasoning
- Overall verdict: **PASS** / **FAIL** / **PASS WITH MITIGATING MEASURES**

---

## Contextual Modules

When specific contexts are identified, read the relevant reference file for specialised guidance:

| Context | Reference | Key Concern |
|---------|-----------|-------------|
| **Children's data** | [references/context-modules.md] §1 | Best interests primary consideration (Art. 24(2) Charter); profiling/targeting generally not permissible; recalibrated balancing test |
| **Direct marketing** | [references/context-modules.md] §2 | Recital 47 ≠ automatic pass; ePrivacy consent requirements; Art. 21(2) absolute right to object |
| **Fraud prevention** | [references/context-modules.md] §3 + [references/oss-enforcement-practice.md] §8 | Strict necessity (Recital 47); must specify fraud type; SAs give considerable latitude but scrutinise scope |
| **IT/network security** | [references/context-modules.md] §4 | Recital 49 recognition; NIS2 Directive extends to cybersecurity information-sharing; strictly necessary and proportionate |
| **Employee monitoring** | [references/context-modules.md] §5 | Power imbalance; heightened reasonable expectations; works council requirements (DE: BetrVG §87). Note: no OSS decisions on employee monitoring due to limited cross-border dimension (Recital 127) |
| **Group data sharing** | [references/context-modules.md] §6 | Recital 48; internal administrative purposes; still requires full LIA per entity |
| **Third-country authorities** | [references/context-modules.md] §7 | EDPB position: data subject interests usually override (para. 136) |
| **AI/ML training & deployment** | [references/additional-regulatory-sources.md] §1-2 + [references/context-modules.md] §8 | **EDPB Opinion 28/2024** confirms LI for AI; CNIL (June 2025) provides most detailed operational guidance; AI-specific reasonable expectations criteria; extensive mitigating measures; web scraping-specific measures; Dutch DPA diverges (requires consent) |
| **Consumer finance** | [references/oss-enforcement-practice.md] §7 | Credit checks (timing, safeguards against accidental triggers); default registry reporting (case-by-case, no blanket policies); debtor identification (public denunciation rejected) |
| **Vehicle/mobility monitoring** | [references/oss-enforcement-practice.md] §9 | Geolocation highly sensitive; excessive tracking intervals rejected; weight monitoring accepted as less invasive than alternatives |
| **ePrivacy overlap** | [references/oss-enforcement-practice.md] §6 | Check ePrivacy FIRST; cookie consent blocks Art. 6(1)(f); ePrivacy consent requirement increases weight in subsequent GDPR balancing |

---

## Retroactive Reliance on Legitimate Interest

Read [references/oss-enforcement-practice.md] §5 for full analysis.

**Default position from OSS enforcement: NOT permitted.** Controllers cannot retroactively switch to Art. 6(1)(f) when their original legal basis is rejected. Key reasoning: data subject was deprived of the right to know the legitimate interests pursued and the right to object. Any balancing test without data subject input is "vitiated by an act contrary to a mandatory rule" (EDPBI:ES:OSS:D:2021:338).

**Narrow exception (EDPBI:EE:OSS:D:2025:1791):** Estonian LSA permitted retroactive switch where prior privacy information at least generally referenced the processing, data subjects were not substantively harmed, a proper LIA was now completed, and data subjects were fully informed. The LSA cautioned this is "not an automatic right."

**When assessing retroactive reliance, flag:**
> ⚠️ **REGULATORY RISK WARNING**
> Retroactive reliance on Art. 6(1)(f) is rejected by most SAs. The dominant enforcement position is that the legal basis must be determined and documented BEFORE processing begins. Proceeding with retroactive reliance carries significant regulatory risk.

---

## Cross-Border Considerations

National law influences the Art. 6(1)(f) assessment at multiple stages, creating possible divergent outcomes between Member States. Unlike the old Data Protection Directive (Art. 4), the GDPR has **no applicable law provision** for cross-border processing. Read [references/oss-enforcement-practice.md] §10 and [references/jurisdiction-notes.md].

**Practical implications:**
- Controllers with cross-border processing may need **multiple localised LIAs**
- LSAs face effective choice-of-law decisions when national standards diverge
- Debt collection, credit default reporting, and employee monitoring are areas where national approaches differ most significantly

---

## Data Subject Rights Interaction

When processing is based on Art. 6(1)(f), specific rights interactions apply. Read [references/data-subject-rights.md] for details.

**Key interactions:**

| Right | Specifics under Art. 6(1)(f) |
|-------|------------------------------|
| **Transparency (Art. 13/14)** | Must specify the legitimate interest(s) pursued; make balancing test available on request |
| **Access (Art. 15)** | EDPB recommends providing legal basis info even though not explicitly required |
| **Object (Art. 21(1))** | Available on grounds relating to particular situation; burden shifts to controller to show "compelling legitimate grounds" — higher threshold than initial Art. 6(1)(f) assessment |
| **Object to marketing (Art. 21(2))** | Absolute right — no balancing, no exceptions |
| **Erasure (Art. 17)** | Closely linked to successful objection; criteria essentially the same |
| **Restriction (Art. 18)** | Available pending verification after objection |
| **Automated decisions (Art. 22)** | Art. 6(1)(f) is NOT Union law authorising automated decision-making under Art. 22(2)(b) |

---

## Output: LIA Documentation

Generate the assessment as a structured document. Offer both summary and full formats.

### Summary Format (for quick assessments)

```
╔══════════════════════════════════════════════════════════════╗
║           LEGITIMATE INTEREST ASSESSMENT — SUMMARY           ║
╠══════════════════════════════════════════════════════════════╣
║ Controller:      [Name]                                      ║
║ Date:            [Date]                                      ║
║ Processing:      [Brief description]                         ║
║ DPO Involved:    [Yes/No/N/A]                                ║
╠══════════════════════════════════════════════════════════════╣
║                    THREE-STEP TEST                           ║
╠══════════════════════════════════════════════════════════════╣
║ Step 1 — Legitimate Interest                                 ║
║   Interest:      [Articulated interest]                      ║
║   Lawful:        [YES/NO]                                    ║
║   Articulated:   [YES/NO]                                    ║
║   Real/Present:  [YES/NO]                                    ║
║   Verdict:       [PASS/FAIL]                                 ║
╠══════════════════════════════════════════════════════════════╣
║ Step 2 — Necessity                                           ║
║   Data Categories: [List]                                    ║
║   Alternatives:    [Considered and rejected / None available] ║
║   Minimisation:    [Confirmed / Issues identified]           ║
║   Verdict:         [PASS/FAIL]                               ║
╠══════════════════════════════════════════════════════════════╣
║ Step 3 — Balancing                                           ║
║   DS Rights:       [Key rights affected]                     ║
║   Impact:          [LOW/MEDIUM/HIGH]                         ║
║   Expectations:    [Aligned/Partially/Not aligned]           ║
║   Mitigating:      [None needed / Applied: list]             ║
║   Verdict:         [PASS/FAIL/PASS WITH MEASURES]            ║
╠══════════════════════════════════════════════════════════════╣
║                    OVERALL RESULT                            ║
╠══════════════════════════════════════════════════════════════╣
║ Art. 6(1)(f) Available:  [YES / NO / YES WITH CONDITIONS]    ║
║ Confidence:              [High / Medium / Low]               ║
║ Contextual Flags:        [Children / Marketing / ePrivacy..] ║
║ Review Date:             [Recommended review date]           ║
╠══════════════════════════════════════════════════════════════╣
║                    REQUIRED ACTIONS                          ║
╠══════════════════════════════════════════════════════════════╣
║ 1. [Action items — transparency updates, mitigating          ║
║    measures, DPO sign-off, DPIA consideration, etc.]         ║
╚══════════════════════════════════════════════════════════════╝
```

### Full LIA Document

Offer to generate a comprehensive Word document (.docx) using the docx skill with:
1. Cover page with controller details, date, version
2. Executive Summary
3. Processing Description
4. Step 1 analysis with legal references
5. Step 2 analysis with data category justification table
6. Step 3 analysis with impact matrix and reasonable expectations assessment
7. Mitigating Measures (if applicable)
8. Overall Conclusion and Recommendation
9. Data Subject Rights implications
10. Action Items and Review Schedule
11. Annex: Legal References (EDPB Guidelines, CJEU case law, Recitals)
12. Sign-off section (DPO, Legal Counsel, Controller representative)

---

## Right to Object Response Mode

When user needs to assess an Art. 21 objection:

1. **Document the objection** — What grounds does the data subject cite?
2. **Do NOT dismiss for insufficient detail** — the data subject need not elaborate extensively (EDPB Guidelines, para. 71)
3. **Identify compelling legitimate grounds** — higher threshold than initial LIA:
   - Must be "essential" to the controller (para. 73)
   - Not merely "beneficial or advantageous"
   - Examples: protecting against serious immediate harm; avoiding severe penalty
4. **Balance compelling grounds against particular situation** of this data subject
5. **Document the outcome** — in line with accountability principle
6. **If objection succeeds** → cease processing, inform data subject of erasure rights

---

## Critical Reminders

These reminders encode the most common failure patterns from EDPB enforcement practice. Understanding the reasoning behind each helps produce more robust assessments.

1. **Art. 6(1)(f) is not a default** — The EDPB has been clear that controllers should not treat legitimate interest as a catch-all or "open door" when other bases seem harder. SAs scrutinise this framing because it often signals inadequate analysis. (EDPB Guidelines, para. 9)
2. **Interpret restrictively** — The CJEU requires this because Art. 6(1)(f) operates without consent, and allowing broad interpretation would undermine the GDPR's protective architecture. (C-252/21 *Meta*, paras. 92-93)
3. **Assess BEFORE processing** — Retrospective construction of an LIA in response to regulatory scrutiny was "almost always fatal" in OSS enforcement. The assessment must be ex ante because data subjects need to be informed and have the right to object from the outset. (para. 12; OSS enforcement §5)
4. **Involve the DPO** — This ensures independent oversight and reduces the risk of self-serving assessments. The DPO's involvement should be documented as part of the accountability trail. (Art. 38(1); para. 12)
5. **Document everything** — Without documentation, the controller cannot demonstrate compliance. SAs consistently found that failure to document was effectively failure to assess. (Art. 5(2))
6. **One purpose, one assessment** — Bundling multiple purposes into a single LIA makes balancing impossible because each purpose has different necessity and impact profiles. (para. 10)
7. **Articulate precisely** — Vague interests are the single most common failure pattern in OSS enforcement. If the interest is not specific enough to balance against, it is not specific enough to rely on. (OSS: EDPBI:BE:OSS:D:2022:325)
8. **No post-hoc basis switching** — Switching from failed consent to legitimate interest prejudices data subjects by depriving them of Art. 21 rights they should have had from the start. (EDPB Guidelines 5/2020 on Consent; dominant OSS position)
9. **ePrivacy first** — The ePrivacy Directive is lex specialis to GDPR. Cookie consent requirements block Art. 6(1)(f), and the original consent requirement influences the weight given to DS interests in any subsequent GDPR balancing. (C-654/23 *Inteligo Media*; OSS: EDPBI:SE:OSS:D:2025:1738)
10. **Children: recalibrated balance** — Art. 6(1)(f) itself singles out children as requiring special attention. The child's best interests must be the primary consideration, not just a factor. (Art. 24(2) Charter)
11. **Compelling grounds ≠ legitimate interest** — The Art. 21 objection threshold is deliberately higher because once processing is underway, the data subject has already been affected. The burden shifts to the controller and the grounds must be "essential," not just "beneficial." (paras. 72-73)
12. **Commercial interests CAN be legitimate** — The CJEU settled this in *KNLTB*. However, purely commercial interests carry less weight in the balancing test, especially against fundamental rights. (C-621/22, para. 49; OSS: EDPBI:ES:OSS:D:2020:146)
13. **SAs scrutinise technical architecture** — If a less intrusive system design could achieve the same result, the controller's chosen architecture fails the necessity test. "The system requires it" is not a valid defence. (OSS: EDPBI:DEBY:OSS:D:2024:1594)
14. **DS benefits ≠ necessity justification** — The three-step test looks at controller/third-party interests, not data subject benefits. If the justification is implementing the wishes of the data subject, consent is the correct legal basis. (EDPB BD 2/2022)
15. **Third-party tech doesn't discharge responsibility** — Controllers remain responsible for their own legal basis even when relying on CMPs, ad-tech vendors, or SaaS providers. (OSS: EDPBI:SE:OSS:D:2025:1738)
16. **Cross-border: localise the assessment** — National law influences all three steps, and outcomes can diverge between Member States. Controllers operating across borders may need separate localised LIAs. (OSS: EDPBI:EE:OSS:D:2023:885)
17. **Review periodically** — Legitimate interests can become unlawful through regulatory change (e.g., shadow blocking now prohibited by DSA Art. 17), and reasonable expectations evolve as technology and public awareness develop.
