# EU AI Act Obligations Mapper

Part of the [EU AI Act Compliance Skills Suite](../README.md).

## What This Skill Does

The Obligations Mapper takes the risk tier and organizational role established by the upstream skills and maps the full set of legal obligations that apply, producing an actionable compliance matrix with RACI assignments, effort estimates, and implementation priorities.

Rather than presenting obligations as an undifferentiated list, the skill organizes them into four batches — technical measures, organizational measures, management systems, and impact assessments — and walks through each batch with the user to assess current compliance status. The result is a gap analysis that shows exactly what needs to be done, by whom, and by when.

The skill draws on 16 reference files — the largest reference set in the suite — covering provider and deployer obligations across all risk tiers, management system requirements, GDPR cross-references, conformity assessment procedures, FRIA methodology, EU database registration, and a compliance roadmap with quarterly action calendars.

## How It Fits Into the Suite

The Obligations Mapper follows Role Determination and feeds into the Report Generator. It translates the legal classification (from the Classifier) and organizational role (from Role Determination) into concrete compliance requirements.

```
  Quick Assessment ──> Classifier ──> Roles ──> ► Obligations ──> Report
                                                  (you are here)
```

The skill's output provides the obligation matrix that the Report Generator incorporates into formal documentation.

## Key Features

- **Context-aware adaptive intake** — auto-populates from Assessment Context blocks; only asks about information gaps and existing compliance frameworks
- **Batched obligation assessment** — 4 structured batches (technical, organizational, management systems, impact assessments) replace 20+ individual questions, targeting 4-5 interaction turns total
- **RACI assignments** — each obligation mapped to Responsible, Accountable, Consulted, and Informed roles
- **Effort estimates** — Low / Medium / High effort ratings for each obligation to support resource planning
- **4-phase implementation roadmap** — obligations grouped into Immediate, Short-term (3 months), Ongoing, and Periodic categories with dependency mapping
- **GDPR cross-references** — parallel GDPR obligations identified at each relevant point (DPIA, transparency notices, data governance, incident reporting, processor agreements)
- **Conformity assessment guidance** — Art. 43 track selection (internal vs. third-party), EU Declaration, and CE marking decision matrix
- **FRIA methodology** — Art. 27 fundamental rights impact assessment with fillable template and worked example
- **EU database registration** — Art. 49 registration process for both provider and deployer tracks
- **Post-market monitoring** — Art. 72 monitoring system design, data collection, incident reporting (Art. 73)
- **Compliance roadmap** — quarterly action calendar, resource estimation by organization size, and phased roadmap template
- **3 worked case studies** — HR deployer, credit scoring provider, and GPAI provider scenarios

## Invocation

**Slash command:** `/ai-act-obligations`

**Example trigger phrases:**
- "Map AI Act obligations"
- "What do we need to do under the AI Act?"
- "Create a compliance checklist"
- "Check deployer obligations"
- "Pflichtenkatalog erstellen"

## Reference Files

| File | Description |
|------|-------------|
| `references/high-risk-deployer-obligations.md` | Full Art. 26 deployer obligations with technical/organizational breakdown |
| `references/high-risk-provider-obligations.md` | Art. 8-17 provider obligations: risk management, data governance, transparency, QMS |
| `references/low-risk-obligations.md` | Art. 50 transparency + Art. 4 competence obligations for non-high-risk systems |
| `references/gpai-obligations.md` | Art. 53/55 GPAI obligations: transparency, copyright, safety, systemic risk |
| `references/technical-measures.md` | Technical implementation measures for compliance |
| `references/organizational-measures.md` | Organizational measures: roles, processes, training, documentation |
| `references/management-systems.md` | Art. 9 risk management, Art. 17 QMS, Art. 72 post-market monitoring |
| `references/gdpr-crosswalk.md` | AI Act / GDPR obligation mapping |
| `references/art6-4-documentation.md` | Art. 6(4) documentation template for non-high-risk Annex III systems |
| `references/case-studies.md` | 3 obligation case studies with worked examples |
| `references/fria-template.md` | Art. 27 FRIA methodology, fillable template, fundamental rights catalogue, worked example |
| `references/conformity-assessment.md` | Art. 43 tracks (internal/third-party), EU Declaration, CE marking, decision matrix |
| `references/post-market-monitoring.md` | Art. 72 monitoring system design, data collection, incident reporting (Art. 73) |
| `references/eu-database-registration.md` | Art. 49 registration: provider/deployer tracks, required fields, step-by-step process |
| `references/regulatory-overlays.md` | Employment law, financial regulators, data protection overlay for multiple jurisdictions |
| `references/compliance-roadmap.md` | Timeline, quarterly calendar, resource estimation, roadmap template |

## Workflow Overview

| Phase | What Happens |
|-------|-------------|
| **Phase 1: Input Context** | Context-aware intake auto-populates from prior skill outputs; asks only about gaps and existing compliance frameworks. Maximum 2 interaction turns. |
| **Phase 2: Obligation Mapping** | Applicable obligation set loaded based on role + risk tier. Obligations presented in 4 batches with status assessment. GDPR cross-references flagged at relevant points. |
| **Phase 3: Implementation Roadmap** | Obligations grouped by timeline (Immediate / Short-term / Ongoing / Periodic) with dependency mapping and resource guidance. |
| **Phase 4: Matrix Output** | Complete compliance obligations matrix with RACI assignments, effort estimates, management system requirements, impact assessment checklist, GDPR cross-references, and Assessment Context block. |

## Output

The skill produces a compliance obligations matrix including:

- Technical measures table with legal basis, priority, status, RACI, and effort
- Organizational measures table with the same structure
- Management systems checklist (risk management, data quality, QMS, post-market monitoring)
- Impact assessments checklist (DPIA, FRIA)
- GDPR cross-reference table with recommended actions
- Summary statistics: total obligations, immediate gaps, items requiring legal judgment
- Assessment Context block for the Report Generator

## Legal Disclaimer

This skill provides structured guidance based on the EU AI Act (Regulation (EU) 2024/1689). It does not constitute legal advice. Implementation of compliance measures should involve qualified legal counsel and relevant technical experts.

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file.

*Created by Oliver Schmidt-Prietz — OneZero Legal*
