# Read Legacy Code — Workflow

**Goal:** Systematically read a legacy codebase and produce a structured inventory of programs, data structures, job flows, and dependencies that feeds directly into the knowledge graph and business rules extraction.

**Supported Legacy Technologies:**
| Technology | Files | What We Extract |
|-----------|-------|----------------|
| COBOL | `.cbl`, `.cob`, `.cpy` | Programs, copybooks, data structures, paragraphs, business logic |
| Mainframe JCL | `.jcl` | Job streams, step sequences, dataset dependencies |
| CICS | `.bms`, procedure DIVs with CICS EXECs | Transactions, maps, user interactions |
| DB2 / SQL | `.sql`, `.dbt`, embedded SQL | Table definitions, stored procedures, views |
| RPG / AS400 | `.rpg`, `.rpgle`, `.sqlrpgle`, `.pf`, `.lf`, `.dspf` | Records, fields, programs, files |
| J2EE | `ejb-jar.xml`, `*.java` with EJB annotations | Beans, services, entities |
| WCF / ASMX | `.svc`, `.asmx`, `*.wsdl` | Service contracts, operations, data contracts |
| Legacy .NET | `.aspx`, `.ascx`, `.vb`, `.cs` (pre-.NET 6) | Code-behind logic, business rules in UI |
| Perl / scripting | `*.pl`, `*.pm` | Data processing pipelines, business rules |

**Outputs** (all to `{project-root}/_superml/legacy-inventory/`):
| Artifact | File | Content |
|---------|------|---------|
| Program inventory | `programs.md` | All programs with purpose and dependencies |
| Data dictionary | `data-dictionary.md` | All data structures, fields, types, validations |
| Job flow map | `job-flows.md` | Batch job sequences and dependencies |
| Call graph | `call-graph.md` | Which programs call which |
| Integration map | `integrations.md` | External systems, files, databases accessed |

---

## Workflow Architecture

Sequential step-file execution. State tracked in `_superml/modernize-state.yml`.

**Critical Rules:**
- 🏛️ Sage is read-only — NEVER modify legacy source files
- ⏸️ Halt at STOP markers for confirmation
- 📎 Cite file and line for every finding
- ❓ When code intent is unclear, ASK — never invent business meaning
- ⚠️ Label every inference with `[INFERRED]` — never state assumptions as facts
- 🔴 Flag dead code, but never discard it silently — it may contain business rules

---

## Activation

1. Confirm the legacy codebase root: "I'll read `{project-root}`. Correct?"
2. Ask what technology is present (if not auto-detected):
   - COBOL / Mainframe (z/OS)
   - RPG / AS400 / iSeries
   - J2EE / Java EE
   - Legacy .NET (WCF, WebForms, ASMX)
   - Mixed / Other
3. Ask: "Are there any external documents I should read alongside the code?"
   - Functional specifications
   - Data dictionaries (PDF/Word)
   - Process flow diagrams
   - User manuals describing business rules
4. Ask: "Are there subject matter experts (SMEs) / domain experts I can ask questions to?"
   - If yes: note that unclear rules will be flagged for SME review
   - If no: unclear rules will be marked `[NEEDS-EXPERT-REVIEW]`

⏸️ **STOP** — confirm before proceeding.

---

## Steps

- `steps/step-01-identify-legacy.md` — Detect technology, file counts, structure shape
- `steps/step-02-parse-programs.md` — Read all programs/modules systematically
- `steps/step-03-extract-data-structures.md` — Map all data definitions (copybooks, schemas, records)
- `steps/step-04-trace-flows.md` — Trace job flows, call graphs, and integration points
