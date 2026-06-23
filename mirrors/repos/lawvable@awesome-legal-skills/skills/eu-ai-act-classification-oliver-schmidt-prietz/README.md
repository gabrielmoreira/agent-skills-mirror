# EU AI Act System Classifier

Part of the [EU AI Act Compliance Skills Suite](../README.md).

## What This Skill Does

The System Classifier determines whether a technology qualifies as an AI system under Art. 3(1) of the EU AI Act and classifies its risk tier. This is the foundational legal determination that shapes everything that follows — prohibited, high-risk, GPAI with systemic risk, limited risk, or minimal risk each carry fundamentally different obligation sets.

The skill walks through a structured three-phase analysis: a scope gate checking Art. 2 exclusions (including dedicated open-source checklists), the full 7-criteria AI system definition test aligned with the OECD AI framework and ISO 22989, and a multi-step risk classification covering Art. 5 prohibited practices, Annex I product safety, Annex III application-based high-risk categories, GPAI model assessment, and Art. 50 transparency triggers.

Where classification is ambiguous — and it often is — the skill applies boundary analysis with gray zone scenarios, edge case tables, and multi-category interaction maps drawn from its 12 reference files, the largest reference set in the suite.

## How It Fits Into the Suite

The System Classifier typically follows the Quick Assessment and feeds into Role Determination. Its output establishes the risk tier that governs which obligations apply.

```
  Quick Assessment ──> ► Classifier ──> Roles ──> Obligations ──> Report
                        (you are here)
```

The classifier's Assessment Context block carries the risk tier, classification basis, GPAI status, and Art. 50 triggers forward to all downstream skills.

## Key Features

- **7-criteria Art. 3(1) test** — structured walk-through of machine-based operation, autonomy degree (ISO 22989 scale), adaptability, goals, inference capability, output generation, and environmental influence
- **Description-informed scope gate** — the Q1 system description drives targeted exclusion checks rather than presenting a generic exclusion list
- **Analyst-driven Art. 5 screening** — internal relevance scoring across all 8 prohibited practice categories, with deep-dive only on flagged items using boundary analysis and gray zone scenarios
- **Auto-pre-screened Annex III assessment** — system description signals automatically mapped to the 8 Annex III categories before user confirmation
- **Art. 6(3) exception analysis** — 4-condition exception test with profiling re-exception check
- **GPAI systemic risk assessment** — Art. 3(63)/(65) classification with 10^25 FLOP threshold and Code of Practice reference
- **Art. 50 transparency framework** — multi-layered marking architecture including the Code of Practice's metadata and watermarking requirements
- **Open-source dual checklists** — Checklist I for AI systems (Art. 2(12)) and Checklist II for GPAI models (Art. 53(2))
- **5 worked case studies** — smart thermostat, HR screening, chatbot, medical imaging, and predictive maintenance scenarios

## Invocation

**Slash command:** `/ai-act-classifier`

**Example trigger phrases:**
- "Classify an AI system under the AI Act"
- "Determine the AI Act risk tier"
- "Check if this is an AI system"
- "Assess prohibited practices"
- "KI-Verordnung Risikoklassifizierung"

## Reference Files

| File | Description |
|------|-------------|
| `references/ai-system-definition.md` | Full Art. 3(1) 7-criteria framework with OECD alignment |
| `references/scope-exclusions.md` | Art. 2 exclusions with open-source checklists (AI systems + GPAI) |
| `references/prohibited-practices.md` | All 8 Art. 5 categories with boundary analysis, gray zones, and multi-category interaction map |
| `references/high-risk-annexes.md` | Annex I (18 categories) + Annex III (8 categories) with edge cases and jurisdiction notes |
| `references/art6-exception.md` | Art. 6(3) exception: 4 conditions, profiling re-exception, practical application guide |
| `references/gpai-systemic-risk.md` | GPAI classification: FLOP threshold, systemic risk indicators, Code of Practice |
| `references/art50-transparency.md` | Art. 50 framework with Code of Practice multi-layered marking architecture |
| `references/sector-guidance.md` | Sector-specific guidance: Healthcare, Finance, HR, Law Enforcement, Education |
| `references/case-studies.md` | 5 classification case studies with worked examples |
| `references/enforcement-framework.md` | Penalty tiers (3 tiers up to EUR 35M / 7%), enforcement architecture, risk assessment |
| `references/jurisdiction-requirements.md` | National authorities, employment law (7 countries), sector regulators |
| `references/compliance-deadlines.md` | Master compliance timeline with 4 phases and transition rules |

## Workflow Overview

| Phase | What Happens |
|-------|-------------|
| **Phase 1: Scope Gate** | System description gathered, scope exclusions checked (description-informed), open-source checklists applied if relevant. |
| **Phase 2: AI System Test** | 7-criteria Art. 3(1) test walked through one criterion at a time with examples and reasoning. |
| **Phase 3: Risk Classification** | 5-step sequence: Art. 5 prohibited practices (analyst-driven screening) > Annex I product safety > Annex III application-based (auto-pre-screened) with Art. 6(3) exception > GPAI model check > Art. 50 transparency triggers. |
| **Phase 4: Dashboard Output** | Classification report with risk tier, legal basis, flags, Assessment Context block, and next steps. |

## Output

The skill produces a classification dashboard including:

- AI system determination (Art. 3(1)) with confidence level
- Risk tier classification with legal basis
- Art. 6(3) exception analysis (if applicable)
- Scope exclusion assessment
- GPAI model status and systemic risk determination
- Art. 50 transparency obligation triggers
- Flags for prohibited practices, quasi-provider risk, profiling, or open-source implications
- Assessment Context block for downstream skills

## Legal Disclaimer

This skill provides structured guidance based on the EU AI Act (Regulation (EU) 2024/1689), Commission guidelines, and the OECD AI framework. It does not constitute legal advice. Final classification decisions should involve qualified legal counsel with AI Act expertise.

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file.

*Created by Oliver Schmidt-Prietz — OneZero Legal*
