---
name: semgrep-rule-variant-creator
description: "Ports an existing Semgrep YAML rule into per-language variants with applicability verdicts, AST dumps, and test-first ruleid/ok files. Trigger on translating a detection to Go, Java, Python, JavaScript, or another target in a polyglot tree. Not for authoring a new rule from scratch (semgrep-rule-creator) and not a scan runner for already published rules."
version: 1.0.1
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Search
risk: unknown
source: community
---

# Semgrep Rule Variant Creator

Port existing Semgrep rules to new target languages with mandatory applicability analysis, test-first validation, and an independent four-phase cycle per language.

## When to Use

**Use this skill when:**
- Porting an existing Semgrep rule to one or more target languages (e.g., "port `sql-injection` to Go and Java")
- Creating language-specific variants of a universal vulnerability pattern
- Expanding rule coverage across a polyglot codebase
- Translating rules between languages with equivalent constructs

**Do NOT use this skill for:**
- Creating a new Semgrep rule from scratch — use `semgrep-rule-creator` instead
- Running existing rules against code
- Languages where the vulnerability pattern fundamentally doesn't apply
- Minor syntax variations within the same language

## Prerequisites

1. **Semgrep CLI installed and on PATH.** Verify:
   ```powershell
   semgrep --version
   ```
2. **An existing Semgrep rule** — either a YAML file path or inline YAML rule content.
3. **One or more target languages** specified by name (e.g., `go`, `java`, `python`, `javascript`, `ruby`, `c`, `cpp`).
4. **Read the `semgrep-rule-creator` skill first** — it is the authoritative reference for rule creation fundamentals (taint mode vs pattern matching, test-first methodology, anti-patterns, iteration, optimization). This skill applies those same principles in a new language context.

### Official docs — when to load each

| Doc | When to load |
|-----|--------------|
| [Pattern examples](https://semgrep.dev/docs/writing-rules/pattern-examples) | Before Phase 3 — per-language constructs; do not assume 1:1 syntax. |
| [Rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax) | YAML operators, metavariables, taint vs pattern mode. |
| [Testing rules](https://semgrep.dev/docs/writing-rules/testing-rules) | Phase 2–4 annotations (`ruleid:` / `ok:`) and `--test` behavior. |

## Input Specification

This skill requires:
1. **Existing Semgrep rule** — YAML file path or YAML rule content.
2. **Target languages** — one or more languages to port to (e.g., "Golang and Java").

## Output Specification

For each applicable target language, produce an independent directory:

```
<original-rule-id>-<language>/
├── <original-rule-id>-<language>.yaml     # Ported Semgrep rule
└── <original-rule-id>-<language>.<ext>    # Test file with annotations
```

Example output for porting `sql-injection` to Go and Java:

```
sql-injection-golang/
├── sql-injection-golang.yaml
└── sql-injection-golang.go

sql-injection-java/
├── sql-injection-java.yaml
└── sql-injection-java.java
```

## Overview

Each target language goes through an **independent four-phase cycle**. Complete the full cycle for one language before starting the next — errors compound and become hard to debug if you create all variants first and test later.

```
FOR EACH target language:
  Phase 1: Applicability Analysis → Verdict
  Phase 2: Test Creation (Test-First)
  Phase 3: Rule Creation
  Phase 4: Validation
  (Complete full cycle before moving to next language)
```

### Strictness level

This workflow is **strict** — do not skip steps:
- **Applicability analysis is mandatory.** Do not assume patterns translate.
- **Each language is independent.** Complete the full cycle before moving to the next.
- **Test-first for each variant.** Never write a rule without test cases.
- **100% test pass required.** "Most tests pass" is not acceptable.

## Procedure

### Phase 1: Applicability Analysis

Before porting, determine if the pattern applies to the target language.

1. Apply the applicability questions below; do not assume the pattern translates.
2. Analyze the original rule's vulnerability class and pattern against the target language:
   - Does the vulnerability class exist in the target language?
   - Does an equivalent construct exist (function, pattern, library)?
   - Are the semantics similar enough for meaningful detection?
3. Record a verdict:
   - `APPLICABLE` → Proceed with variant creation.
   - `APPLICABLE_WITH_ADAPTATION` → Proceed but note significant changes needed.
   - `NOT_APPLICABLE` → Skip this language and document why in the output.
4. If `NOT_APPLICABLE`, stop here for this language and move to the next target language.

### Phase 2: Test Creation (Test-First)

**Always write tests before the rule.** No exceptions.

1. Create the output directory for this language:
   ```powershell
   New-Item -ItemType Directory -Force -Path "<original-rule-id>-<language>"
   ```
2. Create the test file at `<original-rule-id>-<language>/<original-rule-id>-<language>.<ext>` using target-language idioms:
   - Minimum **2 vulnerable cases** annotated with `// ruleid: <rule-id>`
   - Minimum **2 safe cases** annotated with `// ok: <rule-id>`
   - Include language-specific edge cases that differ from the original language
3. Example test file (Go):
   ```go
   // ruleid: sql-injection-golang
   db.Query("SELECT * FROM users WHERE id = " + userInput)

   // ok: sql-injection-golang
   db.Query("SELECT * FROM users WHERE id = ?", userInput)
   ```

### Phase 3: Rule Creation

1. Open Semgrep [pattern examples](https://semgrep.dev/docs/writing-rules/pattern-examples) and [pattern syntax](https://semgrep.dev/docs/writing-rules/pattern-syntax) for the target language.
2. **Dump the AST** of the test file to understand target-language node structure:
   ```powershell
   semgrep --dump-ast -l <lang> <original-rule-id>-<language>\<original-rule-id>-<language>.<ext>
   ```
3. **Translate patterns** from the original rule to target-language syntax based on the AST dump. Do not translate syntax 1:1 — research target-language idioms.
4. **Update metadata** in the new rule YAML:
   - `rules[].id` → `<original-rule-id>-<language>`
   - `rules[].languages` → `[<lang>]`
   - `rules[].message` → adapt if language-specific
5. **Adapt for idioms** — handle language-specific constructs, library equivalents, and data-flow differences. Verify API semantics match; surface similarity hides differences.
6. Write the rule to `<original-rule-id>-<language>/<original-rule-id>-<language>.yaml`.

### Phase 4: Validation

1. Follow the validation commands below and Semgrep [testing rules](https://semgrep.dev/docs/writing-rules/testing-rules). For taint misses, use `--dataflow-traces` as in the Quick Reference.
2. **Validate the YAML:**
   ```powershell
   semgrep --validate --config "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml"
   ```
3. **Run the tests:**
   ```powershell
   semgrep --test --config "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml" "<original-rule-id>-<language>\<original-rule-id>-<language>.<ext>"
   ```
4. **Checkpoint:** Output MUST show `All tests passed`. If not, iterate on the rule (not the tests) until it passes. "Most tests pass" is not acceptable.
5. **For taint-mode rules**, debug data flow if tests fail:
   ```powershell
   semgrep --dataflow-traces -f "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml" "<original-rule-id>-<language>\<original-rule-id>-<language>.<ext>"
   ```
6. **After tests pass**, optimize the rule — remove redundant patterns, tighten metavariable constraints, and ensure no false positives in the safe cases.
7. **Move to the next target language** and repeat from Phase 1.

## Pitfalls

| Rationalization | Why It Fails | Correct Approach |
|-----------------|--------------|------------------|
| "Pattern structure is identical" | Different ASTs across languages | Always dump AST for target language |
| "Same vulnerability, same detection" | Data flow differs between languages | Analyze target language idioms |
| "Rule doesn't need tests since original worked" | Language edge cases differ | Write NEW test cases for target |
| "Skip applicability — it obviously applies" | Some patterns are language-specific | Complete applicability analysis first |
| "I'll create all variants then test" | Errors compound, hard to debug | Complete full cycle per language |
| "Library equivalent is close enough" | Surface similarity hides differences | Verify API semantics match |
| "Just translate the syntax 1:1" | Languages have different idioms | Research target language patterns |

**Additional hard rules:**
- Never skip Phase 1 (applicability analysis). A pattern that makes sense in Python may not exist in Go.
- Never write the rule before the test file. Test-first is mandatory.
- Never lower the pass threshold. 100% of test cases must pass.
- Never reuse the original rule's test file for a ported variant — language edge cases differ.
- If required inputs, permissions, safety boundaries, or success criteria are missing, stop and ask for clarification.

## Verification

Run these commands to confirm each variant is correct:

```powershell
# 1. Validate YAML syntax
semgrep --validate --config "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml"
# Expected: Configuration is valid

# 2. Run tests — must show all passed
semgrep --test --config "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml" "<original-rule-id>-<language>\<original-rule-id>-<language>.<ext>"
# Expected: All tests passed

# 3. (Taint rules only) Verify data flow traces
semgrep --dataflow-traces -f "<original-rule-id>-<language>\<original-rule-id>-<language>.yaml" "<original-rule-id>-<language>\<original-rule-id>-<language>.<ext>"
```

**Pass criteria:**
- `semgrep --validate` reports the configuration is valid.
- `semgrep --test` reports `All tests passed` with every `ruleid:` case flagged and every `ok:` case clean.
- The output directory structure matches the Output Specification for every applicable language.
- For any `NOT_APPLICABLE` language, a documented reason exists in the output.

## Quick Reference

| Task | Command |
|------|---------|
| Run tests | `semgrep --test --config rule.yaml test-file` |
| Validate YAML | `semgrep --validate --config rule.yaml` |
| Dump AST | `semgrep --dump-ast -l <lang> <file>` |
| Debug taint flow | `semgrep --dataflow-traces -f rule.yaml file` |

## Related Skills

- **`semgrep-rule-creator`** — Authoritative reference for rule creation fundamentals. Consult first when uncertain about rule structure, taint mode vs pattern matching, or anti-patterns.

## Documentation

Before porting rules, read relevant Semgrep documentation:

- [Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax) — YAML structure and operators
- [Pattern Syntax](https://semgrep.dev/docs/writing-rules/pattern-syntax) — Pattern matching and metavariables
- [Pattern Examples](https://semgrep.dev/docs/writing-rules/pattern-examples) — Per-language pattern references
- [Testing Rules](https://semgrep.dev/docs/writing-rules/testing-rules) — Testing annotations
- [Trail of Bits Testing Handbook](https://appsec.guide/docs/static-analysis/semgrep/advanced/) — Advanced patterns

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
