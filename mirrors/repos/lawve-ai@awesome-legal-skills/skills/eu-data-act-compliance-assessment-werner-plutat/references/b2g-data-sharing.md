# B2G Data Sharing - Public Authority Data Requests (Chapter V)

## Overview

Chapter V (Articles 14-22) establishes a **public sector right to access privately held data** in exceptional circumstances.

This is among the Data Act's most controversial provisions - balancing public interest needs against commercial interests and trade secret protection.

## Two Request Grounds

### Emergency Requests (Article 15)

#### Scope and Conditions

**Public authorities** may request data from data holders where:

1. **Public emergency exists** - examples include:
   - Public health emergencies (pandemics, disease outbreaks)
   - Natural disasters (floods, earthquakes, extreme weather)
   - Large-scale accidents or industrial incidents
   - Environmental catastrophes
   - Major infrastructure failures

2. **Data is necessary** to respond to, prevent, or assist recovery from the emergency

3. **No other means available in time** - data cannot be obtained from public sources or other readily available sources within the necessary timeframe

4. **Request meets formal requirements** (Article 15(1)):
   - **Necessity** - why the data is needed for the emergency
   - **Purpose** - specific use of the data
   - **Data scope** - precise description of data requested (not blanket requests)
   - **Urgency** - why immediate access is required
   - **Public body making the request** and its legal basis

#### No Compensation for Emergency Requests

- Data holders **must provide data without compensation** (Article 15(4))
- Rationale: emergency response is a societal obligation

**Exception:** If providing data requires **"manifestly disproportionate effort"** (extraordinary technical, organizational, or financial resources beyond reasonable emergency response), the data holder may refuse or negotiate assistance terms.

#### Trade Secret Protection (Article 15(3))

Data holders may refuse or restrict emergency requests where:
- Disclosure would **seriously and irreversibly harm the data holder's commercial interests**
- No **adequate safeguards** for trade secret protection exist

**Safeguards public bodies must offer:**
- Confidentiality agreements
- Restricted access (only authorized personnel)
- Purpose limitation (data used only for emergency response)
- Time-limited access (data deleted after emergency ends)
- Technical measures (anonymization, aggregation where feasible)

**Burden:** Data holder must demonstrate the harm is **serious and irreversible**, not merely competitive disadvantage or temporary disclosure.

### Public Interest Requests (Article 17)

#### Scope and Conditions

**Public authorities** may request data where:

1. **Exceptional need** exists to:
   - Prevent a public emergency, OR
   - Assist recovery from a public emergency that has ended

2. **Data cannot be obtained** from other sources, including:
   - Public databases
   - Voluntary data sharing arrangements
   - Data already held by other public bodies

3. **Request is proportionate** - scope, duration, and intrusiveness are justified by the public interest objective

4. **Request meets formal requirements** (Article 17(1)):
   - **Legal basis** - national or EU law authorizing the request
   - **Purpose** - specific objective (prevention or recovery)
   - **Data scope** - precise and limited to what is necessary
   - **Proportionality assessment** - why the request is justified
   - **Duration** - time period for which access is needed

#### Compensation for Public Interest Requests (Article 20)

Unlike emergency requests, public interest requests trigger **compensation obligation**:

**Compensable costs:**
- **Technical costs** - data extraction, formatting, API setup
- **Organizational costs** - staff time, compliance overhead
- **Financial costs** - infrastructure, third-party services
- **Reasonable margin** - not just cost recovery, but a fair return

**Compensation calculation:**
- Based on **actual costs incurred** plus reasonable margin
- Must be **transparent and verifiable** (data holder provides cost breakdown)
- **Negotiated** between public body and data holder, or determined by national law

**Timeline:** Compensation must be provided **within a reasonable period** after data provision.

## Data Holder Response Obligations

### Must Respond "Without Undue Delay" (Articles 15(1), 17(2))

**Practical benchmarks:**
- **Emergency requests:** Within **24-48 hours** for acknowledgment; data provision timeline depends on urgency and technical feasibility
- **Public interest requests:** Within **7-14 days** for acknowledgment; data provision timeline negotiated based on scope

### Grounds for Refusal (Article 19)

Data holders may refuse requests where:

#### (a) Request is manifestly unfounded or excessive

**Manifestly unfounded:**
- No credible emergency or public interest justification
- Duplicative request (data already provided or available elsewhere)
- Request does not meet formal requirements (vague, overbroad, no legal basis)

**Excessive:**
- Scope far exceeds what is necessary for stated purpose
- Frequency of requests is unreasonable (repeated requests for same data)
- Burden on data holder is disproportionate to public benefit

#### (b) Disclosure would seriously harm commercial interests

- Trade secrets would be disclosed without adequate safeguards
- Competitive harm would be significant and irreversible
- Data holder's business model depends on exclusive data access

**Burden of proof:** Data holder must provide **detailed justification** specifying:
- Which data elements contain trade secrets or sensitive commercial information
- Why disclosure would cause serious harm
- Whether partial disclosure, aggregation, or safeguards could mitigate harm

#### (c) Provision would require manifestly disproportionate effort

**For emergency requests:**
- Only applies where effort is **extraordinary** (not standard technical challenges)
- Examples: Manual extraction from legacy systems with no export functionality, data held in formats requiring significant transformation

**For public interest requests:**
- Broader - any effort that significantly exceeds the public benefit or data holder's capacity
- Proportionality balancing: public interest weight vs data holder burden

### Notification of Refusal

If refusing, data holder must:
1. **Notify the public body without undue delay** (ideally within same timeline as acknowledgment)
2. **Provide detailed reasons** for refusal, referencing specific grounds (Article 19(a)-(c))
3. **Indicate whether refusal is temporary or permanent** - if temporary, propose timeline for resolution

## Confidentiality and Use Limitations (Article 16)

### Public Body Obligations

**Data received under B2G requests must:**

1. **Be used only for the specified purpose**
   - Emergency response / prevention / recovery only
   - No secondary use (e.g., law enforcement, taxation, general policymaking) without separate legal basis

2. **Be kept confidential** unless:
   - Public body determines disclosure is necessary for the emergency response, OR
   - Data holder consents to publication

3. **Be deleted after purpose is fulfilled**
   - No indefinite retention
   - Retention period should be specified in the request or agreed with data holder

4. **Be protected with appropriate security measures**
   - Access controls, encryption, logging
   - Only authorized personnel may access

### Onward Sharing to Other Public Bodies

- Public body may share data with **other competent authorities** where necessary for the same emergency/public interest purpose (Article 16(2))
- Must maintain same confidentiality and use limitation obligations

## Procedural Framework

### Step-by-Step: Receiving and Responding to a B2G Request

#### Step 1: Acknowledge Receipt
- Log the request (date, requesting authority, legal basis, data scope)
- Acknowledge receipt within 24-48h for emergencies, 7 days for public interest requests
- Assign internal case owner (legal + technical leads)

#### Step 2: Assess Validity
Check:
- [ ] Is the requesting body a competent public authority?
- [ ] Is there a valid legal basis (emergency or public interest)?
- [ ] Does the request meet formal requirements (necessity, purpose, scope, proportionality)?
- [ ] Is the data actually held by your organization?
- [ ] Can the data be obtained from other sources?

If NO to any: prepare refusal notice with detailed reasons.

#### Step 3: Assess Grounds for Refusal
Check:
- [ ] Is the request manifestly unfounded or excessive?
- [ ] Would disclosure seriously harm commercial interests or reveal trade secrets?
- [ ] Would provision require manifestly disproportionate effort?

If YES to any: prepare refusal notice OR propose safeguards/limitations.

#### Step 4: Evaluate Trade Secret Protection
If data contains trade secrets:
- [ ] Identify specific data elements that are protectable secrets
- [ ] Assess severity of harm if disclosed
- [ ] Explore safeguards:
  - Confidentiality agreement with public body
  - Restricted access (named individuals, secure facility)
  - Anonymization or aggregation
  - Time-limited access
  - Non-disclosure to third parties

If adequate safeguards possible: **provide data with conditions**.
If no adequate safeguards: **refuse with detailed justification**.

#### Step 5: Determine Compensation (Public Interest Requests Only)
Calculate:
- Technical costs (extraction, formatting, API setup)
- Organizational costs (staff hours at market rates)
- Infrastructure costs (compute, storage, bandwidth)
- Reasonable margin (10-20% markup typical)

Provide cost estimate to public body; negotiate if disputed.

#### Step 6: Provide Data or Refuse
**If providing:**
- Specify format, access method (API, secure file transfer, portal)
- Include metadata, schema, documentation
- Confirm use limitations and confidentiality expectations
- Request acknowledgment of receipt

**If refusing:**
- Written refusal with detailed reasons
- Cite specific refusal grounds (Article 19)
- Indicate whether temporary or permanent
- Propose alternative solutions if feasible (partial data, aggregated data)

#### Step 7: Document and Monitor
- Maintain records of request, response, data provided, and any incidents
- Monitor for unauthorized use or disclosure
- Engage with public body if issues arise

## Examples and Use Cases

### Emergency Request - Public Health

**Scenario:** National health authority requests anonymized mobility data during pandemic to model disease spread.

**Assessment:**
- Valid emergency: ✅ (pandemic)
- Data necessary: ✅ (mobility patterns critical for epidemiological modeling)
- No other source: ✅ (real-time mobility data not in public datasets)
- Trade secrets: ⚠️ (methodology for data collection may be proprietary)

**Resolution:**
- Provide **aggregated, anonymized** mobility data (no individual tracking)
- Confidentiality agreement: data not published, used only for modeling
- Time-limited: access ends when emergency declaration lifted
- **No compensation** (emergency request)

### Public Interest Request - Infrastructure Planning

**Scenario:** Municipal authority requests traffic sensor data to plan post-flood road reconstruction.

**Assessment:**
- Valid public interest: ✅ (recovery from natural disaster)
- Data necessary: ⚠️ (helpful but potentially available from public traffic cameras)
- Proportionality: ✅ (limited scope, time-bound)
- Trade secrets: ❌ (raw traffic counts not proprietary)

**Resolution:**
- Provide historical traffic data for affected areas
- Format: CSV with timestamps, location, vehicle counts
- **Compensation:** €5,000 (staff time for extraction + data validation)
- Use limitation: infrastructure planning only, no commercial use

### Refusal - Manifestly Excessive Request

**Scenario:** Research institute requests 10 years of detailed customer transaction data for "general climate policy research."

**Assessment:**
- Valid emergency: ❌ (no emergency exists)
- Valid public interest: ⚠️ (climate policy is public interest, but link to data is vague)
- Proportionality: ❌ (10 years, all customers, no clear nexus to specific policy need)
- Other sources: ✅ (aggregated climate/consumption data available from public statistics)

**Resolution:**
- **Refuse:** Request is manifestly excessive and not sufficiently justified
- Reason: Scope too broad, necessity not demonstrated, alternative sources exist
- Suggest: Research institute work with national statistics office for aggregated data

## DACH-Specific Considerations

### Germany

**Competent authorities:**
- Federal level: Ministries (BMI, BMG, etc.), BKA, BBK (Federal Office for Civil Protection)
- State level: State ministries, crisis management agencies
- Local: Municipalities, district administrations

**Legal basis for requests:**
- **Article 15 emergencies:** Katastrophenschutzgesetze (state disaster protection laws), IfSG (Infection Protection Act) for health
- **Article 17 public interest:** Specific statutory authorization required (general administrative law insufficient)

**Works council involvement:**
- If B2G data sharing affects employee data, **BetrVG § 87** consultation may be required
- Applies even to anonymized/aggregated employee movement or productivity data

### Austria

**Competent authorities:**
- Federal: Ministries, crisis coordination bodies
- State: Landesregierungen
- Specialized: AGES (health), BVT (security - though B2G data sharing is not law enforcement per se)

**Legal basis:**
- Katastrophenmanagementgesetz (disaster management)
- Epidemiegesetz (epidemic law)

### Switzerland

**Not directly applicable** (Switzerland is not EU member), but:
- Swiss government agencies may request similar data under Swiss law
- EU-Switzerland data flows subject to adequacy framework
- Swiss companies with EU operations may receive B2G requests from EU authorities for EU-related data

## Interaction with Other Legal Frameworks

### GDPR

**B2G data sharing of personal data:**
- Must comply with **GDPR Article 6** (lawful basis) - likely **legal obligation (6(1)(c))** or **public interest task (6(1)(e))**
- **Special categories (Article 9):** Health, biometric data require additional legal basis (often Article 9(2)(i) - public health)
- **Data subject rights** still apply - but may be restricted under Article 23 for public interest/emergency reasons
- **DPIAs required** for large-scale public interest processing (Article 35)

**Practical implication:** Data Act B2G requests do not override GDPR - both apply in parallel.

### NIS2 Directive

- Critical infrastructure operators (energy, transport, health, finance) are subject to **NIS2 incident reporting** and cooperation obligations
- B2G data sharing may overlap with NIS2 cooperation requirements
- Cybersecurity safeguards under NIS2 must be maintained when sharing data with public authorities

### Sector-Specific Regulations

- **ePrivacy Directive/future ePrivacy Regulation:** Telecom/electronic communications data sharing subject to additional confidentiality rules
- **Payment Services Directive (PSD2):** Financial transaction data has strict access controls
- **Health data (EHDS proposal):** European Health Data Space may provide separate framework for health data sharing

**Key point:** Data Act B2G provisions are a **baseline** - sector rules may impose stricter conditions or additional safeguards.

## Key Takeaways

1. **Two regimes:** Emergency (no compensation, urgent) vs public interest (compensation, preventive/recovery)
2. **Refusal is permitted** - manifestly excessive, trade secrets, disproportionate effort - but must be justified
3. **Trade secret protection is real** - public bodies must offer safeguards, data holders must assess proportionately
4. **Confidentiality and use limitation are binding** - public bodies cannot repurpose data for general government use
5. **Compensation for public interest requests** - actual costs plus reasonable margin
6. **GDPR still applies** - B2G data sharing does not create a GDPR exemption for personal data
7. **DACH jurisdictions vary** - check national implementation laws for specific authorities and procedures
