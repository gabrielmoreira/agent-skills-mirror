# EU AI Act Examination Report Generator

Part of the [EU AI Act Compliance Skills Suite](../README.md).

## What This Skill Does

The Report Generator produces formal, structured AI Act compliance assessment reports suitable for legal files, audit trails, and regulatory inquiries. It consolidates the outputs from all prior skills — classification, role determination, and obligation mapping — into a single documented assessment (Dokumentierter Prufbericht) with full legal citations, reasoned determinations, and actionable recommendations.

The skill offers four distinct output formats to serve different audiences: a comprehensive Full Assessment Report for legal files, a Classification Record (Prufprotokoll) for formal audit trails, a Compliance Register Entry for GRC tool integration, and a Management Briefing (Entscheidungsvorlage) as a 2-page board decision document. German legal terms are preserved alongside English throughout.

For users working in Claude Code with file system access, the skill includes a professional .docx export phase that generates a Word document with cover page, table of contents, headers/footers, and consistent table styling.

## How It Fits Into the Suite

The Report Generator is the final skill in the recommended workflow. It draws on the outputs of all upstream skills to produce comprehensive documentation.

```
  Quick Assessment ──> Classifier ──> Roles ──> Obligations ──> ► Report
                                                                  (you are here)
```

The skill can also be used standalone — it gathers all necessary inputs through its own adaptive intake if no prior Assessment Context is available.

## Key Features

- **4 output format templates** — Full Assessment Report, Classification Record (Prufprotokoll), Compliance Register Entry, and Management Briefing (Entscheidungsvorlage)
- **Context-first adaptive intake** — auto-extracts up to 11 fields from prior skill outputs; asks only about gaps and report-specific details (client reference, preparer, date)
- **Input validation with cross-checks** — classification consistency check (flags if stated risk tier contradicts system description), role consistency check (flags if deployer description suggests provider), and completeness check (flags missing DPIA or FRIA for high-risk systems)
- **9-section report structure** — Introduction, System Description, Scope Exclusions, Scope of Application (AI system test + role + territorial), Intended Purpose, Risk Classification, Applicable Obligations, Risk Flags & Recommendations, and Conclusion
- **Quality check phase** — post-generation verification of citation completeness, reasoning documentation, uncertainty flagging, GDPR cross-references, and follow-up actions
- **Professional .docx export** — Word document with cover page (own section), table of contents, headers/footers, consistent table styling, and "Confidential" footer marking (requires docx-processing skill)
- **Legal citation accuracy** — dedicated citation index reference ensures article references are precise
- **Dual-language terminology** — German legal terms (Anbieter, Betreiber, Prufprotokoll, Entscheidungsvorlage) preserved alongside English
- **3 worked case studies** — high-risk HR report excerpt, Art. 6(3) exception analysis, and minimal-risk chatbot assessment

## Invocation

**Slash command:** `/ai-act-report`

**Example trigger phrases:**
- "Generate an AI Act report"
- "Create a compliance assessment report"
- "Document the AI Act analysis"
- "Create a Prufbericht"
- "Export as Word document"

## Reference Files

| File | Description |
|------|-------------|
| `references/report-template.md` | Full assessment report structure (9 sections) |
| `references/legal-citations-index.md` | Citation accuracy reference for all key articles |
| `references/interpretation-aids.md` | Commission guidelines status tracker and assessment frameworks |
| `references/output-templates.md` | 3 structured templates: Prufprotokoll, Compliance Register, Management Briefing |
| `references/case-studies.md` | 3 report excerpt samples: high-risk HR, Art. 6(3) exception, minimal-risk chatbot |
| `references/jurisdiction-checklists.md` | Employment law overlay, per-country checklists, cross-border guidance |
| `references/compliance-timeline.md` | Timeline, quarterly calendar, roadmap template |
| `references/docx-formatting.md` | Word document styling: typography, table styles, cover page, per-template structure |

## Workflow Overview

| Phase | What Happens |
|-------|-------------|
| **Phase 1: Input Collection** | Context-first adaptive intake extracts up to 11 fields from prior skills; asks about gaps and report-specific details (client reference, preparer, date). Maximum 2 interaction turns. |
| **Phase 1.5: Input Validation** | Cross-checks for classification consistency, role consistency, and completeness. Flags any inconsistencies for user confirmation before report generation. |
| **Phase 2: Report Generation** | Template selection (4 formats), then structured report generation with full legal citations, reasoned determinations, obligation matrices, risk flags, and recommendations. |
| **Phase 3: Quality Check** | Post-generation verification: citation completeness, reasoning documentation, uncertainty flagging, GDPR cross-references, follow-up actions, and limitations. |
| **Phase 4: Word Export** | Optional .docx generation with cover page, TOC, headers/footers, table styling, and confidentiality marking. Requires Claude Code CLI and docx-processing skill. |

## Output

The skill produces (depending on selected template):

- **Full Assessment Report** — 9-section comprehensive report with scope analysis, AI system determination, role assessment, risk classification, obligation matrix, risk flags, recommendations, and conclusion
- **Classification Record (Prufprotokoll)** — formal audit trail documenting the classification decision with legal basis and reasoning
- **Compliance Register Entry** — structured entry for GRC tooling with obligation tracking and status fields
- **Management Briefing (Entscheidungsvorlage)** — 2-page board decision document with executive summary, key determinations, financial exposure, and recommended actions

All formats include legal citations, confidence ratings, and a disclaimer. The optional .docx export produces a professionally formatted Word document.

## Legal Disclaimer

This skill provides structured documentation based on the EU AI Act (Regulation (EU) 2024/1689). It does not constitute legal advice. The report should be reviewed and validated by qualified legal counsel before being used for regulatory purposes.

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file.

*Created by Oliver Schmidt-Prietz — OneZero Legal*
