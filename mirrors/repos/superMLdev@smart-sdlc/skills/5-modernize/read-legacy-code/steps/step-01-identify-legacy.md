# Step 01 — Identify Legacy Technology and Structure

**Previous step:** (none)
**Next step:** `step-02-parse-programs.md`

---

## 1. File Extension Survey

Count and categorize all legacy files:

```bash
# COBOL
find . -name "*.cbl" -o -name "*.cob" | wc -l
find . -name "*.cpy" | wc -l
find . -name "*.jcl" | wc -l
find . -name "*.bms" | wc -l

# RPG
find . -name "*.rpg" -o -name "*.rpgle" -o -name "*.sqlrpgle" | wc -l
find . -name "*.pf" -o -name "*.lf" -o -name "*.dspf" | wc -l

# J2EE / Legacy Java
find . -name "ejb-jar.xml" -o -name "struts-config.xml" -o -name "faces-config.xml" | wc -l

# Legacy .NET
find . -name "*.svc" -o -name "*.asmx" -o -name "*.aspx" | wc -l
find . -name "*.wsdl" | wc -l
```

---

## 2. Technology Classification

Based on findings, classify the legacy stack:

### COBOL / Mainframe z/OS

Signals:
- `.cbl` / `.cob` files present
- `IDENTIFICATION DIVISION` in file content
- `.jcl` files with `//JOBNAME JOB` headers
- `EXEC PGM=` references
- `CICS EXEC` statements → online transaction processing
- `EXEC SQL` → DB2 embedded SQL
- `.cpy` files → shared data definitions (copybooks)

Classify sub-type:
```
Mainframe Sub-type:
  Batch processing: ✅/❌  (JCL jobs present)
  Online (CICS):   ✅/❌  (CICS EXEC statements found)
  Database (DB2):  ✅/❌  (EXEC SQL found)
  Assembler:       ✅/❌  (.asm/.mac files)
  IMS:             ✅/❌  (DLI calls found)
  VSAM files:      ✅/❌  (SD/FD with ORGANIZATION IS INDEXED)
```

### RPG / AS400 / IBM iSeries

Signals:
- `.rpg` / `.rpgle` / `.sqlrpgle` files
- Physical files (`.pf`) → database tables
- Logical files (`.lf`) → views/indexes
- Display files (`.dspf`) → screen layouts
- CL programs (`.clle`) → command language scripts

### J2EE / Legacy Java EE

Signals:
- `ejb-jar.xml` deployment descriptors
- Classes annotated `@Stateless`, `@Stateful`, `@MessageDriven`
- `struts-config.xml`, `struts-action.xml` → Struts MVC
- `faces-config.xml` → JSF
- `.wsdl` + JAXWS annotations → web services
- Hibernate `*.hbm.xml` mapping files

### Legacy .NET

Signals:
- `.svc` files → WCF services
- `.asmx` files → ASMX web services
- Web.config with `<system.serviceModel>` → WCF config
- `.aspx` + code-behind `.aspx.cs` / `.aspx.vb` → WebForms
- `Global.asax` → application lifecycle hooks

---

## 3. Inventory Top-Level Structure

List directories and their apparent purpose:

```
Legacy Project Structure:
  /PROGRAMS/        → {n} COBOL programs
  /COPYBOOKS/       → {n} copybook files (shared data definitions)
  /JCL/             → {n} job control language files
  /PROC/            → {n} JCL procedures (reusable job steps)
  /SQL/             → {n} SQL scripts / DB2 DDL
  /CICS/            → {n} CICS transaction definitions / BMS maps
  /DOCS/            → {documentation found}
```

---

## 4. Identify External Documents

Search for documentation:
```
docs/           Any markdown, PDF, or Word file descriptions
*.txt           Plain text specs
PROC*.doc       Process documentation
DESIGN*.doc     Design documents  
FUNC*.doc       Functional specs
```

For each document found, note:
- File name and type
- Whether it describes business rules, processes, or data
- Whether it appears current or outdated (date in filename or content)

If the user said they have external documents, ask them to describe what's available:
> "You mentioned external documents. Can you tell me what you have? (e.g., functional specifications, data dictionaries, process flow diagrams, user manuals)"

Note all document sources in state file for knowledge graph step.

---

## 5. Scale Assessment

Estimate complexity:

```
Scale Assessment:
  Programs:      {n}
  Copybooks:     {n}
  JCL Jobs:      {n}
  DB Tables:     {n estimated from SQL/DDs}
  
  Complexity:    Small (<20 programs) | Medium (20–100) | Large (100–500) | Enterprise (500+)
  
  Estimated reading time:
    Small:      1 AI session
    Medium:     2–3 sessions
    Large:      Phased — recommend by subsystem
    Enterprise: Recommend domain partitioning — do one domain at a time
```

For Large/Enterprise:
> "🏛️ This is a large system ({n} programs). I recommend we tackle it by **business domain/subsystem**. Can you list the main business areas? (e.g., Customer Management, Order Processing, Billing, Reporting)"

⏸️ **STOP** — confirm technology classification and scope. For large systems, confirm domain partitioning approach.

---

## 6. Save State

Write `{project-root}/_superml/modernize-state.yml`:
```yaml
step: "step-01-identify-legacy"
status: "complete"
primary_technology: "{COBOL|RPG|J2EE|dotnet-legacy}"
sub_types: ["{batch}", "{online-CICS}", "{DB2}"]
program_count: {n}
copybook_count: {n}
jcl_count: {n}
complexity: "{Small|Medium|Large|Enterprise}"
external_docs: ["{list if any}"]
domain_scope: "{all | partitioned: domain-name}"
```

Load and follow `./step-02-parse-programs.md`.
