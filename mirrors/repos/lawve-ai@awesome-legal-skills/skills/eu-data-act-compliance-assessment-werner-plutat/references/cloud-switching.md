# Cloud Switching and Portability - Chapters VI-VII

## Overview

Chapters VI and VII of the Data Act address **vendor lock-in** in cloud and edge computing services by mandating **switching rights**, **fee elimination**, and **interoperability**.

These provisions apply to **data processing service providers** (cloud/edge providers) and aim to enable customers to switch providers or move to on-premises infrastructure without undue friction.

## Key Obligations

**Chapter structure note:**
- **Chapter VI** covers switching between data processing services (Articles 23-31)
- **Chapter VII** covers international access and transfer safeguards for non-personal data held in the EU (Article 32)
- Interoperability standardization continues in later provisions; do not treat Chapter VII as part of switching mechanics

### 1. Switching Assistance (Article 23)

**Data processing service providers must enable customers to:**

#### (a) Switch to another provider or transition to on-premises infrastructure

- Customer decision to switch must be respected
- Provider cannot contractually prevent switching
- Must facilitate both provider-to-provider and cloud-to-on-premises transitions

#### (b) Cease use of the service without contractual penalties

- No "exit fees" or "early termination charges" beyond legitimate costs (see Fee Phase-Out below)
- No requirement to continue paying for unused services after termination

#### (c) Export customer data, applications, and digital assets

**What must be exportable:**
- **Customer data** - all data uploaded, generated, or stored by the customer
- **Applications** - software, configurations, scripts deployed by the customer
- **Digital assets** - metadata, logs, access policies, encryption keys (where customer-controlled)

**Export format requirements:**
- **Structured** - organized in a logical, documented format
- **Commonly used** - industry-standard formats (JSON, XML, CSV, SQL dumps, OVF/VMDK for VMs, container images)
- **Machine-readable** - programmatically parseable without manual intervention
- **Functional equivalence** - data and applications must be usable in the target environment without loss of core functionality

**Exclusions (what need not be exported):**
- Provider's proprietary software or tools (unless licensed to customer)
- Other customers' data
- Provider's internal operational data

### 2. Reasonable Termination Notice Period (Article 24)

#### Minimum Notice Requirements

- **Minimum 2 months** notice for contract termination (Article 24(1))
- Counting starts from date of written termination notice
- Longer notice periods allowed if objectively justified (e.g., very large or complex deployments)

#### Maximum Contract Duration Limits

- No **minimum contract duration** that is longer than objectively necessary (Article 24(2))
- Provider cannot force multi-year lock-ins without justification

**What counts as "objectively necessary":**
- **Infrastructure investment:** If provider makes significant upfront investment (e.g., dedicated hardware, custom deployment), longer commitment may be justified
- **Volume discounts:** Tiered pricing with longer commitments acceptable if shorter-term options also available
- **Regulatory constraints:** Sector-specific requirements (e.g., financial services data residency with long deployment cycles)

**What does NOT count:**
- Generic market practice ("everyone does 3-year minimums")
- Desire to maximize revenue predictability
- Customer convenience (e.g., "annual billing is simpler")

#### Notice Period Alignment

- Provider must give **at least as much notice** to customer as customer must give to provider
- If contract requires customer to give 2 months' notice, provider must also give at least 2 months if terminating or non-renewing

### 3. Fee Phase-Out Timeline (Article 25)

#### The Fee Ban

**Prohibited fees (Article 25(3)):**
- Switching fees
- Data export fees
- Service termination fees
- Early exit penalties (beyond legitimate cost recovery)

**What remains permissible:**
- **Pro-rata charges** for services used until termination date
- **Legitimate cost recovery** for extraordinary export assistance (e.g., manual extraction from legacy systems not designed for export)
- **Outstanding fees** for services already rendered

#### Application Timeline

**For contracts concluded AFTER 12 September 2025:**
- Fee ban applies **immediately** from date of conclusion
- Zero switching/exit fees from day one

**For contracts concluded BEFORE 12 September 2025:**
- Fees **must be eliminated within 2 years** after 12 Sept 2025
- **Deadline: 12 September 2027**
- Providers must proactively amend existing contracts or phase out fees by Sept 2027

**Practical implication:**
- New contracts from Sept 2025: draft without exit fees
- Existing contracts: plan fee elimination by Sept 2027 (renegotiation, contract amendment, or automatic sunset clause)

### 4. Interoperability and Standards (Article 26-27)

#### Self-Regulatory Codes of Conduct (Article 26(1))

The Commission and Member States encourage development of **codes of conduct** covering:
- **Portability** - data and application migration processes
- **Interoperability** - API compatibility, data format harmonization
- **Cloud-to-edge and edge-to-cloud** transitions
- **Hybrid and multi-cloud** deployments

**Key initiatives:**
- **SWIPO (Switching and Porting) Code of Conduct** under development by cloud industry (CISPE, Gaia-X, others)
- **ISO/IEC standards** for cloud data portability (ISO/IEC 19941)
- **ETSI standards** for multi-cloud and edge interoperability

#### Standardization Requests (Article 27)

- European Commission may issue **standardization requests** to European standardization organizations (CEN, CENELEC, ETSI)
- Goal: develop **European standards** for interoperability and data portability where voluntary codes fail to emerge

**Practical implication:** Even if not yet formalized, cloud providers should track emerging standards and align export/API designs proactively.

## International Access and Transfer Safeguards (Article 32)

Providers of data processing services must take **all adequate technical, organizational, and legal measures** to prevent international or third-country governmental access to **non-personal data held in the Union** where such access would conflict with Union law or the national law of the relevant Member State.

**Core obligation (Article 32(1)):**
- Review foreign governmental requests affecting EU-held non-personal data
- Resist disclosure where the request conflicts with EU or Member State law
- Build internal escalation processes combining legal review, technical access controls, and executive sign-off

**Required measure types (Article 32(1)):**
1. **Technical measures** - access controls, encryption, localization controls, segregation, logging
2. **Organizational measures** - escalation workflow, trained legal/security teams, documented decision-making
3. **Legal measures** - contractual commitments, challenge procedures, conflict-of-laws assessment, transparency policy

**Permitted disclosure exceptions (Article 32(2)-(3)):**
1. **International agreement route** - disclosure based on a third-country court or tribunal order only where grounded in an international agreement, such as a mutual legal assistance treaty
2. **Urgency route** - urgent requests may proceed only with safeguards, including necessity assessment, proportionality, and later review

**Practical implications for providers with third-country parent groups:**
- Intra-group access models must account for Article 32, not just customer contract terms
- Law enforcement playbooks must distinguish personal-data GDPR requests from non-personal-data Article 32 requests
- Transparency reports and contract wording should explain how conflicting foreign access demands are handled

## Technical Requirements for Data Export

### Export Mechanisms

**Minimum acceptable:**
- **Self-service export tool** in customer portal (click to download)
- **API endpoint** for programmatic bulk export
- **Documented export format** and schema

**Best practice:**
- **Automated migration tools** (scripts, CLI tools, SDKs)
- **Direct provider-to-provider transfer** (e.g., AWS DataSync-equivalent)
- **Incremental export** (not just full dumps - allow delta exports for ongoing sync during transition)
- **Encryption-in-transit** and encryption-at-rest support for exported data

### Format and Usability Standards

| Data Type | Recommended Formats |
|-----------|---------------------|
| Structured data (databases) | SQL dumps, JSON, CSV, Parquet, Apache Avro |
| Unstructured data (files) | Original format (no transcoding), with directory structure preserved |
| Virtual machines | OVF, VMDK, VHD, QCOW2 |
| Containers | Docker images, OCI-compliant container images |
| Configuration/IaC | Terraform state files, CloudFormation templates (or neutral equivalents like Pulumi) |
| Metadata | JSON, YAML with documented schema |
| Logs | JSON Lines, CSV, Syslog-compatible formats |

### Functional Equivalence

**The exported data/application must work in the new environment.**

**This means:**
- **No proprietary dependencies** - if the application relies on provider-specific services (e.g., AWS Lambda, Azure Functions), provider must either:
  - Export in a portable format (e.g., containerized version)
  - Provide clear documentation on dependencies and equivalent services elsewhere
- **Retained configuration** - access controls, network configs, environment variables exportable
- **Data integrity** - checksums, validation tools provided to verify completeness

**Acceptable limitations:**
- Provider need not guarantee identical performance in target environment
- Provider need not support target platform (customer or new provider handles re-deployment)

## Contractual Implications

### Contract Terms to Review/Revise

**Prohibited or high-risk clauses:**
1. "Early termination fee: 50% of remaining contract value"
2. "Data export available only via professional services at €500/hour"
3. "Minimum 3-year commitment required for all plans"
4. "Customer may not export configuration data or metadata"
5. "Customer must provide 6 months' termination notice"

**Compliant alternatives:**
1. "No early termination fees; customer pays only for services used until termination date"
2. "Self-service data export available at no charge; optional assisted migration at cost"
3. "No minimum commitment; month-to-month available; annual plans offer discounts"
4. "Customer may export all customer data, applications, configurations, and metadata in [format]"
5. "Either party may terminate with 60 days' written notice"

### Notice and Communication Obligations

**Provider must inform customer:**
- **How to export data** (documentation, tools, support channels)
- **What formats are available**
- **Expected timeline** for export completion (especially for large datasets)
- **Any costs** associated with export assistance (if legitimate costs apply)
- **Point of contact** for migration support

**Best practice:** Publish a **switching guide** or **migration playbook** covering:
- Step-by-step export process
- Common pitfalls and solutions
- Target environment compatibility notes
- Sample scripts or tools

## Enforcement and Compliance

### Competent Authorities (Article 38)

- National **market surveillance authorities**
- In cloud context, likely **digital/telecom regulators** or **competition authorities**
- Germany: BNetzA (Federal Network Agency) potential candidate for cloud services

### Customer Rights

**Customers can:**
1. **Refuse to pay prohibited fees** - switching fees charged post-deadline are unenforceable
2. **Demand export assistance** - provider must comply with export requests
3. **Seek damages** - if provider obstructs switching or imposes unlawful barriers
4. **File complaints** with market surveillance authority

**Practical tip for customers:** If a provider resists switching, document all requests and responses - this is evidence for enforcement action or contract dispute.

## Common Pitfalls and Mistakes

### For Providers

1. **Assuming existing exit fees are grandfathered indefinitely**
   - No - you have until Sept 2027 to eliminate them

2. **Charging "data transfer fees" disguised as network egress costs**
   - Legitimate network costs may apply, but must be transparent and non-punitive
   - If egress to your own CDN is free but egress for switching is expensive, that's a red flag

3. **Providing export in unusable formats**
   - Proprietary, obfuscated, or incomplete exports do not satisfy the obligation

4. **Hiding export tools or documentation**
   - Must be "easy" to access - burying it in enterprise support tiers violates the spirit

5. **Requiring manual requests for each dataset**
   - Self-service, programmatic export is expected for standard use cases

### For Customers

1. **Waiting until the last minute to test export**
   - Validate export and import to target environment during contract term, not at renewal crunch

2. **Assuming "commonly used format" means identical functionality everywhere**
   - Test portability - some features may not transfer (acceptable), but core data must

3. **Not clarifying IP ownership**
   - Ensure contracts clearly state customer owns customer data, not just licenses it

## Cross-Regulation Interaction

### GDPR
- **Personal data portability** under GDPR Article 20 overlaps with Data Act export rights
- Data Act extends beyond personal data to all customer data
- Both apply where customer data includes personal data - use the more favorable right

### AI Act
- Training data and model data stored in cloud must be exportable under Data Act
- Ensures AI developers can switch cloud providers without losing training datasets

### NIS2 Directive
- Cloud service providers are **essential entities** under NIS2
- Security and incident reporting obligations complement Data Act switching obligations
- Export mechanisms must be secure to avoid creating data breach vectors

## Key Dates Summary

| Date | Obligation |
|------|------------|
| **12 September 2025** | Main Data Act provisions apply, including switching assistance for **new contracts** |
| **12 September 2027** | Fee elimination deadline for **existing contracts** (concluded before 12 Sept 2025) |
| **1 January 2027** | **Correction:** Earlier drafts referenced this date for fee phase-out, but **final text** uses 2-year transition from 12 Sept 2025 = **12 Sept 2027** |

## Key Takeaways

1. **Customers can switch without penalty** - fees, lock-ins, and export barriers are prohibited
2. **Export must be self-service and free** - for standard data/application exports
3. **2-month minimum notice** - both ways (customer and provider)
4. **Fee elimination by Sept 2027** for existing contracts, immediately for new contracts from Sept 2025
5. **Functional equivalence matters** - data must be usable in the target environment, not just technically exported
6. **Interoperability is the long-term goal** - codes of conduct and standards are emerging to reduce switching friction beyond legal minimums
