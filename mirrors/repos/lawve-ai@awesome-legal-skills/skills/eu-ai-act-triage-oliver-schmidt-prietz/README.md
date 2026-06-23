# EU AI Act Quick Assessment

Part of the [EU AI Act Compliance Skills Suite](../README.md).

## What This Skill Does

The Quick Assessment skill provides a rapid 15-25 minute triage for preliminary AI Act classification and compliance assessment. It answers the fundamental question every organization faces: "Does the EU AI Act apply to us, and if so, what do we need to do?"

Rather than committing to a full multi-hour analysis, users get a preliminary determination covering scope applicability, risk tier, organizational role, top obligations, compliance deadlines, jurisdiction-specific flags, and financial exposure — all in a single structured output.

The skill uses an adaptive 2-batch intake flow: three open-ended questions gather the essential context, followed by a targeted follow-up only if information gaps remain. This conversational approach replaces rigid questionnaires and keeps the assessment fast.

## How It Fits Into the Suite

The Quick Assessment is the recommended entry point for the suite. Its output includes an **Assessment Context** block that can be pasted directly into any of the four detailed skills, carrying forward all preliminary determinations and avoiding redundant questions.

```
 ► Quick Assessment ──> Classifier ──> Roles ──> Obligations ──> Report
   (you are here)
```

Users can also skip the Quick Assessment entirely and start with any detailed skill if they already have sufficient context about their system.

## Key Features

- **6-gate rapid classification sequence** — scope check (Art. 2), AI system test (Art. 3(1)), prohibited practice screen (Art. 5), high-risk assessment (Annex I + III), GPAI check, and transparency triggers (Art. 50)
- **Adaptive 2-batch intake** — conversational context gathering with generous extraction from natural-language responses; maximum 2 interaction turns
- **Preliminary output template** — structured dashboard covering classification, role, obligations, timeline, jurisdiction flags, financial exposure, and recommended next steps
- **Confidence ratings** — each determination is tagged with a confidence level (High / Medium / Low) so users know where deeper analysis is needed
- **Template offer** — optional generation of preliminary Prufprotokoll, Compliance Register, or Management Briefing using the report generator's templates
- **Cross-jurisdictional flags** — jurisdiction-specific requirements (works council co-determination, sector regulator obligations) flagged based on deployment country

## Invocation

**Slash command:** `/ai-act-quick`

**Example trigger phrases:**
- "Does the AI Act apply to us?"
- "Run a quick AI Act assessment"
- "Do a preliminary classification"
- "AI Act triage"
- "Schnellprufung" / "Ersteinschatzung"

## Reference Files

| File | Description |
|------|-------------|
| `references/quick-decision-tree.md` | Condensed classification logic, sector quick triggers, role/obligation/jurisdiction quick mapping |
| `references/jurisdiction-flags.md` | Dual-compliance-layer diagram and per-country checklist flags for 8 jurisdictions |
| `references/compliance-deadlines.md` | 4-phase compliance timeline with urgency mapping |

## Workflow Overview

| Phase | What Happens |
|-------|-------------|
| **Phase 1: Quick Context** | Adaptive 2-batch intake gathers system description, deployment context, and organizational relationship. Silent coverage analysis extracts 8 structured fields. |
| **Phase 2: Rapid Classification** | 6-step gate sequence processes answers internally — no additional questions unless critical information is missing. |
| **Phase 3: Preliminary Output** | Consolidated dashboard with classification summary, role assessment, top obligations, compliance timeline, jurisdiction flags, financial exposure, and recommended next steps. |
| **Phase 4: Template Offer** | Optional generation of preliminary templates (Prufprotokoll, Compliance Register, Management Briefing) marked as preliminary. |

## Output

The skill produces a structured preliminary assessment dashboard including:

- Classification summary with risk tier and confidence rating
- Role assessment with quasi-provider risk indication
- Top 5 obligations with urgency and effort estimates
- Applicable compliance deadline and days remaining
- Jurisdiction-specific flags (employment law, sector regulators)
- Financial exposure estimate (penalty tier, SME proportionality)
- Assessment Context block for downstream skills
- Recommended next steps with priority ratings

All determinations are marked as "Likely" to indicate they require validation through the detailed assessment skills.

## Legal Disclaimer

This skill provides a preliminary assessment for initial orientation under the EU AI Act (Regulation (EU) 2024/1689). It is designed for rapid triage and does not replace a full assessment. Results should be validated using the detailed assessment skills and reviewed by qualified legal counsel.

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file.

*Created by Oliver Schmidt-Prietz — OneZero Legal*
