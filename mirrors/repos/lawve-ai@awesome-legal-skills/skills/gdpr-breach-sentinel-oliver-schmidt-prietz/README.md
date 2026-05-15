# Breach Sentinel v2.1 — Deployment Guide

> **Changelog:**
> - **v2.1** (2026-02-09): DPC score capping (bounds enforcement), Fast Path expanded to 11 data points, Emergency Mode DPA deadline question, multi-select breach types, UK GDPR nuances, "Under Investigation" pathway, sub-processor chain guidance, two-stage T0 analysis, docx skill fallback, quick decision tree, improved web research queries
> - **v2.0** (2026-02-07): Fast Path intake, Strategic Advisory, flexible mitigation playbooks, dynamic web research, SA contact lookup, AI Act integration, DPA deadline tracking, .docx generation, post-notification tracking, borderline score analysis
> - **v1.0**: Initial release — ENISA assessment, EDPB matching, templates

## Overview

GDPR Breach Response Sentinel — an advanced incident response skill for Claude that provides:

- **ENISA severity assessment** with borderline score analysis
- **EDPB case matching** against 18 documented breach scenarios
- **Strategic case advisory** — senior counsel-level analysis and recommendations
- **Dynamic web research** for enforcement precedents and SA-specific guidance
- **Flexible mitigation playbooks** tailored to the specific incident
- **SA contact directory** with jurisdiction-specific portal lookup
- **AI Act Art. 62 intersection** for breaches involving AI systems
- **Audit-ready .docx document generation** (Art. 33, Art. 34, compliance logs, etc.)
- **Post-notification case tracking**
- **DPA contractual deadline tracking** for processor scenarios

## File Structure

```
breach-sentinel/
├── SKILL.md                              # Main skill instructions (deploy this)
└── references/
    ├── enisa-methodology.md              # ENISA severity scoring tables + worked examples
    ├── edpb-cases.md                     # 18 EDPB breach case scenarios
    └── templates.md                      # Document templates (Art. 33, Art. 34, etc.)
```

## Deployment

### Claude.ai (User Skills)

1. Go to **Settings → Profile → Custom Skills** (or equivalent)
2. Upload the entire `breach-sentinel/` folder structure
3. The skill will auto-trigger when you mention data breaches, Art. 33/34, "Datenpanne", or related topics

### Claude Code / Custom MCP Setup

1. Copy the `breach-sentinel/` folder to your skills directory:
   ```bash
   cp -r breach-sentinel/ /path/to/your/skills/user/breach-sentinel/
   ```
2. Ensure the skill is registered in your configuration

## Usage

### Quick Start

Just tell Claude about a breach:

> "We just discovered that an external attacker exfiltrated our customer database. 
> About 2,000 records with names, emails, and payment data. We're based in Munich. 
> This happened yesterday at 3pm."

The skill will activate and walk you through the assessment.

### Trigger Phrases

- "We had a data breach" / "Datenpanne" / "Datenschutzverletzung"
- "Do we need to notify the SA?" / "72 hours" / "Art. 33"
- "Help me assess this breach" / "ENISA assessment"
- "Generate breach notification documents"

### Modes

| Mode | When to Use |
|------|-------------|
| **Guided** | You're unsure about details; skill asks questions one by one |
| **Fast Path** | You have all the facts; dump them and get an instant assessment |
| **Emergency** | <12 hours remaining on notification clock |

## Capabilities Summary

| Feature | Description |
|---------|-------------|
| ENISA Severity Calculation | Full SE = (DPC × EI) + CB with contextual adjustments |
| Borderline Score Analysis | Extra scrutiny for scores near 2.0/3.0/4.0 thresholds |
| EDPB Case Matching | Maps to 18 documented scenarios from Guidelines 01/2021 |
| Strategic Advisory | Senior counsel-level analysis: hidden risks, SA strategy, leverage points |
| Dynamic Web Research | Searches for current enforcement precedents and SA guidance |
| SA Contact Lookup | Finds notification portal URLs and jurisdiction-specific requirements |
| Germany SA Routing | Correctly routes to BfDI vs. LfDI/LDA based on entity type |
| Mitigation Playbook | Case-specific, flexibly structured action plan with owners and deadlines |
| AI Act Integration | Flags Art. 62 serious incident reporting for AI system breaches |
| DPA Deadline Tracking | Captures contractual processor deadlines alongside statutory 72h |
| Document Generation | Audit-ready .docx files for all breach documentation |
| Post-Notification Tracking | Ongoing case management dashboard |

## Regulatory Basis

| Document | Reference |
|----------|-----------|
| GDPR Articles 33 & 34 | Breach notification obligations |
| EDPB Guidelines 9/2022 v2.0 | Personal data breach notification |
| EDPB Guidelines 01/2021 v2.0 | Examples regarding breach notification |
| ENISA Severity Methodology | Risk assessment formula and scoring |
| EU AI Act (Reg. 2024/1689) | Art. 62 serious incident reporting |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | — | Initial release: ENISA assessment, EDPB matching, templates |
| 2.0 | 2026-02-07 | Fast Path intake, Strategic Advisory, flexible mitigation playbooks, dynamic web research, SA contact lookup, AI Act integration, DPA deadline tracking, .docx generation, post-notification tracking, borderline score analysis |
| 2.1 | 2026-02-09 | DPC score capping, Fast Path 11 data points, Emergency Mode DPA deadline, multi-select breach types, UK GDPR nuances, "Under Investigation" pathway, sub-processor chain guidance, two-stage T0 analysis, docx skill fallback, quick decision tree, improved web research queries |

## License & Disclaimer

This skill provides guidance based on publicly available GDPR regulatory materials. It does not constitute legal advice. All notification decisions should involve qualified legal counsel and your organization's DPO.

---

*Created by Oliver Schmidt-Prietz — OneZero Legal
