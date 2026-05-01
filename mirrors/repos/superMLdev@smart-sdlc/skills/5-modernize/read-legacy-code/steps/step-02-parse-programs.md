# Step 02 — Parse Programs and Map Business Functions

**Previous step:** `step-01-identify-legacy.md`
**Next step:** `step-03-extract-data-structures.md`

---

## Reading Strategy

Context window is finite. Prioritize by business importance, not file name alphabetically.

**Priority order:**
1. Entry programs (called from JCL EXEC PGM= or main transaction)
2. Programs referenced by multiple other programs
3. Programs with the most business logic (largest, most paragraphs)
4. Utility/common programs last (can be summarized, not fully analyzed)

---

## A. COBOL Program Reading

For each COBOL program (`.cbl`, `.cob`), extract:

### Program Header
```
Program: {PROGRAM-ID value}
Source file: {path/filename.cbl}
Type: BATCH | CICS-ONLINE | REPORT | UTILITY
Purpose: {inferred from program name + IDENTIFICATION DIVISION AUTHOR remarks}
```

### Data Division Summary
- **WORKING-STORAGE SECTION**: State variables, counters, flags, work areas
  - Flag: any fields named `WS-RETURN-CODE`, `WS-STATUS`, `WS-ERROR` → error handling variables
  - Flag: any fields with VALUE clauses containing magic numbers → potential business rules
- **FILE SECTION**: Which files are opened (INPUT, OUTPUT, I-O, EXTEND)
  - Extract: file names, organization (SEQUENTIAL, INDEXED, RELATIVE)
- **LINKAGE SECTION**: Parameters passed in/out (if subprogram called by another)

### Procedure Division — Paragraph Map
Map each named paragraph as a function:

```
Paragraph: {0100-INITIALIZE}
  Calls: {OPEN files, initialize work areas}
  Business significance: Setup only [implementation artifact]

Paragraph: {0200-VALIDATE-CUSTOMER}
  Calls: PERFORM 0210-CHECK-CREDIT-LIMIT, PERFORM 0220-CHECK-BLACKLIST
  Business significance: ⭐ BUSINESS RULE — validates customer before processing
  
Paragraph: {0210-CHECK-CREDIT-LIMIT}
  Logic found:
    IF WS-ORDER-AMOUNT > WS-CREDIT-LIMIT
      MOVE 'Y' TO WS-OVER-LIMIT-FLAG
  Business significance: ⭐ BUSINESS RULE — credit limit enforcement
  Rule: Order amount must not exceed customer credit limit
```

### PERFORM Call Graph
Map the call hierarchy within the program:

```
MAIN-PROCEDURE
  ├── 0100-INITIALIZE
  ├── 0200-VALIDATE-CUSTOMER
  │     ├── 0210-CHECK-CREDIT-LIMIT      ⭐ business rule
  │     └── 0220-CHECK-BLACKLIST         ⭐ business rule
  ├── 0300-PROCESS-ORDER
  │     ├── 0310-CALCULATE-TOTALS        ⭐ business rule
  │     └── 0320-APPLY-DISCOUNT          ⭐ business rule
  └── 0400-WRITE-OUTPUT
```

### CALL Statements (External Programs)
```
External calls:
  CALL 'CUSTINQ'    → Customer inquiry subprogram [file: CUSTINQ.cbl]
  CALL 'TAXCALC'    → Tax calculation subprogram [needs reading]
  CALL 'ERRHAND'    → Error handler [utility, lower priority]
```

### Business Rule Detection in COBOL

Flag paragraphs containing these patterns as likely business rules:

| Pattern | Example | Significance |
|---------|---------|-------------|
| `IF ... MOVE ... TO RETURN-CODE` | `IF AMT > LIMIT MOVE 'E' TO RC` | Validation rule |
| `COMPUTE ... ROUNDED` | `COMPUTE TAX = AMOUNT * .0825` | Calculation rule |
| `EVALUATE ... WHEN` | `EVALUATE CUST-TYPE WHEN 'P' ...` | Classification rule |
| `MOVE SPACES TO ERROR-MSG ... PERFORM VALIDATE` | Error message assignment | Validation |
| `IF STATUS = 'A' ... ELSE ... INVALID` | Status checks | State machine rule |
| Magic number VALUE clauses | `VALUE 999` in field definition | Threshold/limit |
| REDEFINES | Data interpreted multiple ways | Complex data rule |
| OCCURS DEPENDING ON | Variable length arrays | Cardinality rule |

---

## B. RPG Program Reading

For each RPG program (`.rpgle`, `.sqlrpgle`):

### Header Analysis
```
Program: {source-filename}
Type: {Service Program | Interactive | Batch | Module}
Purpose: {inferred from name and H-spec}
```

### File Specifications (F-specs)
- List all files (physical, logical, display) used
- Note: UPDATE, ADD, DELETE operations on which files

### Data Structures (D-specs)
- Record formats used
- Data structure definitions
- Named constants → often encode business rules

### Procedure Section (P-specs / subprocedures)
Map each subprocedure as a function, same approach as COBOL paragraphs.

### Business Rule Detection in RPG
- `IF` / `SELECT WHEN` blocks with threshold comparisons
- `%ERROR` handling → validation logic
- SQL WHERE clauses with business conditions
- Named constants: `DCL-C MAX_ORDER_QTY 9999;`

---

## C. J2EE / Legacy Java Reading

For each significant class:

### EJB Session Beans
```
Bean: {ClassName}
Type: Stateless | Stateful | MessageDriven
Methods (business interface):
  {methodName(params)} → {return type}
    Purpose: {business function from method body}
    Calls: {other EJBs, DAOs, utilities}
```

### Struts Actions / JSF Backing Beans
Extract the business logic from `execute()` or action methods.

### DAO / Repository Classes
Map database operations to entities.

---

## D. WCF / ASMX / Legacy .NET Reading

### Service Contracts (.svc / .asmx)
```
Service: {ServiceName}
Operations:
  [{OperationName}({params}) → {return}]
    Business function: {inferred}
    Authorization: {if found}
```

### Code-Behind (.aspx.cs / .aspx.vb)
Extract business logic from event handlers (Button_Click, Page_Load with business logic).

---

## Program Inventory Output

Write `{project-root}/_superml/legacy-inventory/programs.md`:

```markdown
# Program Inventory — {project_name}

> Generated by Sage on {date}. Read-only analysis.

## Summary
Total programs: {n}
Business-critical programs: {n}
Utility programs: {n}
Entry points: {n}

## Programs

### {PROGRAM-NAME}
- **File**: `{path/PROGRAM.cbl}`
- **Type**: {Batch | Online | Report | Utility}
- **Purpose**: {one sentence}
- **Key business functions**:
  - {paragraph/method name}: {business rule or function}
- **Calls**: {list of external programs called}
- **Called by**: {list of callers — from JCL or CALL statements}
- **Files accessed**: {list}
- **Business rules detected**: {n}
- **Clarity**: Clear | Needs-Expert-Review | [INFERRED — low confidence]
```

---

## Questions for Domain Expert

Collect all unclear points and write to `{project-root}/_superml/legacy-inventory/expert-questions.md`:

```markdown
# Questions for Domain Expert

These items were found in the code but their business meaning could not be determined
without domain expertise. Please review and answer.

## Q1 — {Program: ORDPROC, Paragraph: 0350-CHECK-HOLD}
Code found:
```cobol
IF CUST-HOLD-CODE = 'C' OR 'L' OR 'M'
   MOVE 'Y' TO WS-HOLD-FLAG
```
**Question**: What do hold codes 'C', 'L', and 'M' represent? What is the business meaning of each?

## Q2 — ...
```

⏸️ **STOP** — Present program inventory and expert questions. Get answers before proceeding to data structures.

---

## Save State

Update `{project-root}/_superml/modernize-state.yml`:
```yaml
step: "step-02-parse-programs"
status: "complete"
programs_inventoried: {n}
business_rules_detected: {n}
expert_questions: {n}
entry_programs: ["{list}"]
```

Load and follow `./step-03-extract-data-structures.md`.
