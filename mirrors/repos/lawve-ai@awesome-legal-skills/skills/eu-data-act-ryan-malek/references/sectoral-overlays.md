# Sectoral overlays — forced gate

The Data Act is horizontal. Sectoral instruments may impose stricter, additional, or alternative obligations that the skill does not cover. This file is the gate the skill checks against the per-matter facts before producing any output.

## Scan the facts for these triggers

When per-matter facts contain any of the following, surface the corresponding overlay warning before output. Multiple triggers can apply simultaneously.

### Automotive — type-approval regime

**Triggers:** motor vehicle, car, truck, bus, OEM, vehicle manufacturer, in-vehicle data, telematics, V2X, ADAS, OBD-II, type-approval.

**Overlay:** Regulation (EU) 2018/858 (motor vehicle type-approval and market surveillance). Imposes its own data-access regime for repair and maintenance information; sectoral data-access rules under discussion via the proposed automotive Data Act.

**Warning text the skill prepends:**

> The facts indicate a motor vehicle context. Regulation (EU) 2018/858 (type-approval) imposes its own access regime for repair and maintenance information that interacts with Data Act Articles 3–5. Sectoral lex specialis may pre-empt or modify horizontal Data Act obligations. This Skill does not cover Reg. 2018/858. The lawyer must independently verify the sectoral regime before relying on this output.

### Medical devices — MDR / IVDR

**Triggers:** medical device, IVD, in-vitro diagnostic, MDR, IVDR, CE mark for medical, MDCG, notified body, clinical evidence, Eudamed, Class IIa/IIb/III device, implantable.

**Overlay:** Regulation (EU) 2017/745 (MDR), Regulation (EU) 2017/746 (IVDR). Imposes safety, vigilance, and post-market surveillance obligations that may engage Data Act Article 4(2) safety/security carve-out and trade-secret restrictions differently than horizontal default.

**Warning text:**

> The facts indicate a medical device context. Regulation (EU) 2017/745 (MDR) and / or Regulation (EU) 2017/746 (IVDR) impose safety, vigilance, and post-market surveillance obligations that interact with Data Act Article 4(2) and the trade-secret regime. The Data Act safety/security carve-out (Art. 4(2)) may operate differently against this background. This Skill does not cover MDR/IVDR. The lawyer must independently verify the sectoral regime.

### Financial services — DORA

**Triggers:** financial entity, ICT third-party provider, critical ICT service, bank, insurer, investment firm, payment institution, e-money institution, MiFID, UCITS, AIFM, CCP, CSD, DORA.

**Overlay:** Regulation (EU) 2022/2554 (Digital Operational Resilience Act). Imposes its own ICT risk management, third-party concentration, and exit/switching requirements for financial entities that may pre-empt or supplement Chapter VI Data Act DPS switching rules.

**Warning text:**

> The facts indicate a financial-services context (financial entity or ICT third-party provider). Regulation (EU) 2022/2554 (DORA) imposes its own switching, exit, and concentration-risk regime for ICT services that may pre-empt or supplement Data Act Chapter VI. Customer-side DORA obligations on financial entities and ICT third-party-provider obligations interact with the Article 23–32 framework. This Skill does not cover DORA. The lawyer must independently verify.

### Cybersecurity — NIS2

**Triggers:** essential entity, important entity, NIS2, cybersecurity directive, OES, DSP, critical infrastructure, energy operator, transport operator, water utility, public administration, digital infrastructure provider, ICT service management.

**Overlay:** Directive (EU) 2022/2555 (NIS2). Cybersecurity risk-management and incident reporting obligations that affect what data may be withheld under Art. 4(2) and what must be disclosed to authorities.

**Warning text:**

> The facts indicate a NIS2 context (essential or important entity, or supplier into one). Directive (EU) 2022/2555 cybersecurity obligations interact with the Data Act Art. 4(2) safety/security carve-out and with trade-secret restrictions on disclosing data that could undermine cybersecurity. This Skill does not cover NIS2. The lawyer must independently verify.

### Cyber Resilience Act — CRA

**Triggers:** connected product with a software component, IoT, smart device, software product placed on the EU market, CRA, cybersecurity-by-design, vulnerability handling, secure update channel.

**Overlay:** Regulation (EU) 2024/2847 (Cyber Resilience Act). Imposes cybersecurity-by-design, vulnerability handling, and conformity assessment obligations. It constrains how Data Act Art. 4 real-time access is implemented, including authentication, encryption, and secure update channels. Build CRA and Data Act compliance together.

**Warning text:**

> The facts indicate a Cyber Resilience Act context. Regulation (EU) 2024/2847 imposes cybersecurity-by-design, vulnerability handling, and conformity assessment obligations that constrain how Data Act real-time access is implemented, including authentication, encryption, and secure update channels. This Skill does not cover the CRA. The lawyer must build CRA and Data Act compliance together and independently verify the CRA position.

### AI Act

**Triggers:** AI system, AI model, GPAI, foundation model, high-risk AI, biometric, AI system provider, AI Act, Annex III, Annex IV, conformity assessment for AI, onboard tactical AI, predictive AI, automation AI, decision-support AI.

**Overlay:** Regulation (EU) 2024/1689 (AI Act). Training-data provenance, transparency, and recordkeeping obligations may interact with related-service data classifications and with trade-secret protections. Any onboard tactical, predictive, automation, or decision-support AI is potentially high-risk and may collide with Data Act trade-secret protection through training-data documentation requirements.

**Warning text:**

> The facts indicate an AI Act context. Regulation (EU) 2024/1689 obligations on data provenance, transparency, technical documentation, and high-risk system recordkeeping interact with Data Act related-service data classifications and trade-secret protections. Onboard tactical, predictive, automation, or decision-support AI may be high-risk and may collide with Data Act trade-secret protection through training-data documentation requirements. This Skill does not cover the AI Act. The lawyer must independently verify.

### eIDAS / digital identity

**Triggers:** eIDAS, electronic identification, EUDI wallet, qualified trust service, qualified electronic signature, qualified seal.

**Overlay:** Regulation (EU) No 910/2014 as amended by Regulation (EU) 2024/1183 (eIDAS 2). Identity-verification standards relevant to Data Act access requests.

**Warning text:**

> The facts touch on electronic identification. eIDAS / eIDAS 2 (Reg. 910/2014 as amended by Reg. 2024/1183) governs identity verification standards relevant to Data Act access requests. This Skill does not cover eIDAS. The lawyer must independently verify which identity standards apply.

### Energy — sectoral data hubs

**Triggers:** energy data, smart metering, distribution system operator, DSO, transmission system operator, TSO, electricity, gas market.

**Overlay:** Sectoral energy regulation (Electricity Directive 2019/944, Gas Directive 2009/73 as amended, network codes) imposes its own data-access and metering data regimes. National regulators play a substantial role.

**Warning text:**

> The facts indicate an energy-sector context. Sectoral energy regulation imposes its own data-access regime for metering, balancing, and customer data that interacts with Data Act access rights. National regulatory authorities have substantial role. This Skill does not cover energy sectoral law. The lawyer must independently verify.

### Public sector / Open Data Directive

**Triggers:** public-sector body, public undertaking, open data, PSI, re-use of public-sector information, B2G data sharing.

**Overlay:** Open Data Directive (EU) 2019/1024 and the Data Governance Act (EU) 2022/868. Distinct regimes for public-sector data; B2G data sharing is also governed by Chapter V of the Data Act, not addressed in detail in this skill v1.

**Warning text:**

> The facts indicate a public-sector context. The Open Data Directive (Dir. 2019/1024) and the Data Governance Act (Reg. 2022/868) govern public-sector data; Data Act Chapter V (B2G access in exceptional need) is also relevant. This Skill v1 focuses on Chapters II and VI; Chapter V and adjacent public-sector regimes are not covered in depth here.

## How the skill applies this gate

1. Read the per-matter facts captured in step 3 of the SKILL.md workflow.
2. Match each trigger keyword set above (case-insensitive, simple substring match is fine for v1).
3. For every match, prepend the corresponding warning text to the deliverable's introduction or first numbered paragraph.
4. If two or more sectoral overlays apply, surface a consolidated note: "Multiple sectoral regimes potentially apply: [X], [Y]. The lawyer must reconcile them independently."
5. If the user explicitly says "horizontal only — sectoral overlays already addressed," the gate may be skipped, but the deliverable still records: "User confirmed sectoral overlays addressed independently of this Skill."

## Member-state implementing law

Independent of any sector, member-state implementing law and competent-authority designations under Article 37 always apply. Member States designate competent authorities and may set their own penalty regimes. The skill does not enumerate Member State law. Verify per-Member-State before relying on penalty figures. Do not enumerate specific Member State penalty amounts because they change. The skill always notes:

> Member-state implementing law and competent-authority designations under Article 37 are not covered by this Skill. The lawyer must verify the position in the relevant member state.

This is a separate, always-on gate — not conditional on facts.

## Out of scope of this gate

- Pure horizontal Data Act questions with no sector indicator.
- General data-protection (GDPR) questions — covered separately in `references/gdpr-overlay.md`.
