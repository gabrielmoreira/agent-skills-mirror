# NIS2 Navigator

**Version:** 1.0.0-beta  
**License:** AGPL-3.0  
**Author:** Oliver Schmidt-Prietz (OneZero Legal)  
**Type:** Claude Skill

> ⚠️ **Beta Release** — This is a v1 beta. The skill is functional and built on verified official sources, but has not yet undergone formal evaluation testing. Feedback, corrections, and contributions are welcome.

## What It Does

NIS2 Navigator is a Claude Skill that runs a structured NIS2 compliance assessment in approximately 20 minutes, producing three deliverables:

1. **Scope Classification** — Determines whether an entity falls under NIS2 and classifies it as essential or important, based on Annex I/II sector mapping, size thresholds, group structures, and special-status rules
2. **Art. 21 Gap Analysis** — Scores all 10 risk management measures on a 0–4 maturity scale (max 40 points), with lightweight ISO 27001:2022 Annex A references per measure
3. **Compliance Roadmap** — Prioritized remediation plan (P1/P2/P3) with concrete actions, effort estimates, and a management body briefing template

## Jurisdiction Coverage

| Jurisdiction | Depth | Status |
|---|---|---|
| **EU Directive** | Full | Baseline for all assessments |
| **Germany (BSIG-neu)** | Deep | In force since 6 Dec 2025 |
| **Italy (D.Lgs. 138/2024)** | High-level profile | In force since 16 Oct 2024 |
| **Austria (NISG 2026)** | High-level profile | Transposed, enters force 1 Oct 2026 |
| **France (Loi Résilience)** | High-level profile | Pending — expected H2 2026 |
| **Netherlands (Cbw)** | High-level profile | Pending — expected Q2 2026 |
| **Spain (Ley de Ciberseguridad)** | High-level profile | Pending — still in draft |

The EU-level assessment (scope + gap analysis + roadmap) works for entities in any Member State. The jurisdiction profiles add national specifics where transposition diverges from the Directive.

## Official Sources

Built on and referencing:

- EU Directive 2022/2555 (NIS2)
- Commission Implementing Regulation (EU) 2024/2690
- ENISA Technical Implementation Guidance (June 2025)
- BSI #nis2know Infopakete and Roadmap
- BSI-Standards 200-1/200-2/200-3
- BSI Betroffenheitsprüfung (scope self-assessment tool)
- BSI RUN maturity methodology
- ANSSI ReCyF (March 2026)
- National transposition laws for covered jurisdictions

## File Structure

```
nis2-navigator/
├── SKILL.md                            Main workflow (225 lines)
├── README.md                           This file
├── LICENSE.txt                         AGPL-3.0
└── references/
    ├── regulatory-sources.md           EU and BSI source catalog
    ├── sector-classification.md        Annex I/II mapping, size thresholds
    ├── art21-measures.md               10 measures, scoring criteria, ISO refs
    ├── germany-nis2umsucg.md           German BSIG-neu deep dive
    ├── eu-jurisdiction-profiles.md     IT, FR, NL, AT, ES profiles
    └── templates.md                    Report, executive summary, mgmt briefing
```

## Installation

Install the `.skill` package in Claude, or copy the folder into your Claude Skills directory.

## Limitations (v1 Beta)

- **Not legal advice.** The skill produces structured compliance guidance, not legal opinions. Results should be validated by qualified counsel.
- **Non-German jurisdictions are high-level only.** The profiles highlight key national differences but do not provide the same depth as the German coverage.
- **Transposition status is a moving target.** France, Netherlands, and Spain had not completed transposition at time of writing (March 2026). The skill includes a web search trigger on activation to check for updates.
- **No IEC 62443 / OT coverage.** Industrial/OT environments are not addressed in v1. Planned for v2.
- **No formal eval testing yet.** The skill has been built iteratively with subject-matter input but has not been run through the skill-creator evaluation framework.

## Changelog

### v1.0.0-beta (March 2026)
- Initial release
- Full EU Directive coverage (scope, Art. 21 gap analysis, roadmap)
- Deep German BSIG-neu integration (BSI registration, § 30/32/34/38, reporting channels, Nachweispflicht)
- High-level jurisdiction profiles for IT, FR, NL, AT, ES
- CIR 2024/2690 detection for digital infrastructure entities
- DORA lex specialis handling
- Commission January 2026 amendment proposal flagged for awareness
- Management body liability briefing template

## Disclaimer

This skill is provided as-is under the AGPL-3.0 license. It does not constitute legal advice. The author accepts no liability for compliance decisions made based on this tool's output. Always verify with qualified legal counsel.
