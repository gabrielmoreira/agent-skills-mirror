# DPIA Sentinel v1.0 — Deployment Guide

## Overview

GDPR Data Protection Impact Assessment Sentinel — a structured DPIA guidance skill for Claude that provides:

- **Threshold assessment** against Art. 35(3) mandatory triggers and EDPB nine-criteria analysis
- **Multi-jurisdictional blacklist/whitelist checks** across 7 EU Member States (DE, FR, IE, BE, NL, IT, PL)
- **Systematic processing description** following Art. 35(7)(a) requirements
- **Necessity and proportionality analysis** including LIA balancing tests
- **5x5 risk assessment** from the data subject's perspective with color-coded heat maps
- **Mitigation mapping** with pre/post scores and residual risk evaluation
- **Art. 36 prior consultation** decision support
- **AI dual-phase analysis** per EDPB Opinion 28/2024 (training vs. deployment)
- **Audit-ready .docx document generation** (full DPIA report, threshold memo, executive summary, Art. 36 package)

## File Structure

```
dpia-skill/
├── SKILL.md                              # Main skill instructions (deploy this)
└── references/
    ├── edpb-criteria.md                  # EDPB nine criteria + multi-jurisdictional framework
    ├── scoring.md                        # 5x5 risk scoring methodology
    ├── risk-catalog.md                   # Common DPIA risks by processing type
    ├── templates.md                      # Document templates (full DPIA, threshold memo, etc.)
    ├── sources.md                        # Regulatory source references
    └── jurisdictions/
        ├── de-dsk.md                     # Germany — DSK blacklist
        ├── fr-cnil.md                    # France — CNIL blacklist
        ├── ie-dpc.md                     # Ireland — DPC blacklist
        ├── be-apd.md                     # Belgium — APD blacklist
        ├── nl-ap.md                      # Netherlands — AP blacklist
        ├── it-garante.md                 # Italy — Garante blacklist
        ├── pl-uodo.md                    # Poland — UODO blacklist
        └── whitelists.md                 # FR, CZ, ES, AT whitelist exemptions
```

## Deployment

### Claude.ai (User Skills)

1. Go to **Settings → Profile → Custom Skills** (or equivalent)
2. Upload the entire `dpia-skill/` folder structure
3. The skill will auto-trigger when you mention DPIA, DSFA, Art. 35, or describe high-risk processing

### Claude Code / Custom MCP Setup

1. Copy the `dpia-skill/` folder to your skills directory:
   ```bash
   cp -r dpia-skill/ /path/to/your/skills/user/dpia-skill/
   ```
2. Ensure the skill is registered in your configuration

## Usage

### Quick Start

Just describe your processing activity:

> "We're planning to deploy an AI system that scores job applicants based on their CVs
> and video interviews. The system will be used across Germany, France, and the Netherlands.
> Do we need a DPIA?"

The skill will activate and guide you through the assessment.

### Trigger Phrases

- "Do I need a DPIA?" / "DSFA" / "Datenschutz-Folgenabschaetzung"
- "Art. 35" / "impact assessment" / "high-risk processing"
- "We want to deploy AI for..." / "profiling" / "large-scale monitoring"
- "Generate a DPIA report"

### Assessment Flow

| Phase | Description |
|-------|-------------|
| **Threshold** | Art. 35(3) triggers + nine-criteria analysis + national blacklist checks |
| **Description** | Systematic processing description per Art. 35(7)(a) |
| **Necessity** | Proportionality, data minimization, legal basis adequacy |
| **Risk Assessment** | 5x5 matrix, data subject perspective, risk register + heat map |
| **Mitigation** | Technical, organizational, and legal measures with residual scoring |
| **Residual Risk** | Overall position: Acceptable / Conditions / Art. 36 Consultation |
| **Documentation** | Audit-ready .docx generation |

## Document Types

| Template | Description |
|----------|-------------|
| Full DPIA Report | Complete Art. 35 assessment with 12 sections + annexes |
| Threshold Justification Memo | 2-3 page document explaining why a DPIA is NOT required |
| Executive Summary | 1-2 page board/leadership summary |
| Art. 36 Consultation Package | Submission package for SA prior consultation |

## Regulatory Basis

| Document | Reference |
|----------|-----------|
| GDPR Article 35 | DPIA obligation |
| GDPR Article 36 | Prior consultation |
| EDPB Guidelines WP 248 rev.01 | DPIA methodology and nine criteria |
| EDPB Opinion 28/2024 | DPIA for AI processing |
| EDPB Guidelines 01/2025 | Pseudonymisation as risk reducer |
| National SA Art. 35(4) lists | Mandatory DPIA blacklists (7 jurisdictions) |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial release: threshold assessment, multi-jurisdictional blacklist analysis, 5x5 risk scoring, EDPB AI opinion integration, 4 document templates, 7 jurisdiction files |

## License & Disclaimer

This skill provides structured guidance based on publicly available GDPR regulatory materials. It does not constitute legal advice. All DPIA decisions should involve your DPO (Art. 35(2)) and qualified legal counsel.

---

*Created by Oliver Schmidt-Prietz — OneZero Legal*
