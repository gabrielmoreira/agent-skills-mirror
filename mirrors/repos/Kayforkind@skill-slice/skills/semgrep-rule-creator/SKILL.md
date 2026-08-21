---
name: semgrep-rule-creator
description: "Creates custom Semgrep rules test-first (ruleid/ok cases, AST, taint mode) and iterates until semgrep --test is green. Use when writing detections for vulns, bug patterns, or taint data-flow. Not for running existing rulesets or generic SAST without a new rule."
version: 1.0.1
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
risk: unknown
source: community
---

# Semgrep Rule Creator

Create production-quality Semgrep rules with proper testing and validation. This skill enforces a strict, test-first, iterate-until-green workflow.

## When to Use

**Ideal scenarios:**
- Writing Semgrep rules for specific bug patterns
- Writing rules to detect security vulnerabilities in your codebase
- Writing taint mode rules for data flow vulnerabilities
- Writing rules to enforce coding standards

## When NOT to Use

Do NOT use this skill for:
- Running existing Semgrep rulesets
- General static analysis without custom rules (use the `static-analysis` skill instead)

## Prerequisites

- **Semgrep CLI installed** — verify with `semgrep --version`. Install via `pip install semgrep` if missing.
- **WebFetch access** — required to read Semgrep documentation before writing any rule (see Procedure Step 1).
- **Windows host (primary)** — commands below assume PowerShell. On Windows, use `semgrep --test --config <rule-id>.yaml <rule-id>.<ext>` from the rule directory. Forward slashes in YAML paths are fine; PowerShell accepts them.

## Rationalizations to Reject

When writing Semgrep rules, reject these common shortcuts:

- **"The pattern looks complete"** → Still run `semgrep --test --config <rule-id>.yaml <rule-id>.<ext>` to verify. Untested rules have hidden false positives/negatives.
- **"It matches the vulnerable case"** → Matching vulnerabilities is half the job. Verify safe cases don't match (false positives break trust).
- **"Taint mode is overkill for this"** → If data flows from user input to a dangerous sink, taint mode gives better precision than pattern matching.
- **"One test is enough"** → Include edge cases: different coding styles, sanitized inputs, safe alternatives, and boundary conditions.
- **"I'll optimize the patterns first"** → Write correct patterns first, optimize after all tests pass. Premature optimization causes regressions.
- **"The AST dump is too complex"** → The AST reveals exactly how Semgrep sees code. Skipping it leads to patterns that miss syntactic variations.

## Anti-Patterns

**Too broad** — matches everything, useless for detection:
```yaml
# BAD: Matches any function call
pattern: $FUNC(...)

# GOOD: Specific dangerous function
pattern: eval(...)
```

**Missing safe cases in tests** — leads to undetected false positives:
```python
# BAD: Only tests vulnerable case
# ruleid: my-rule
dangerous(user_input)

# GOOD: Include safe cases to verify no false positives
# ruleid: my-rule
dangerous(user_input)

# ok: my-rule
dangerous(sanitize(user_input))

# ok: my-rule
dangerous("hardcoded_safe_value")
```

**Overly specific patterns** — misses variations:
```yaml
# BAD: Only matches exact format
pattern: os.system("rm " + $VAR)

# GOOD: Matches all os.system calls with taint tracking
mode: taint
pattern-sinks:
  - pattern: os.system(...)
```

## Strictness Level

This workflow is **strict** — do not skip steps:

- **Read documentation first**: See Step 1 before writing any Semgrep rule.
- **Test-first is mandatory**: Never write a rule without tests.
- **100% test pass is required**: "Most tests pass" is not acceptable.
- **Optimization comes last**: Only simplify patterns after all tests pass.
- **Avoid generic patterns**: Rules must be specific, not match broad patterns.
- **Prioritize taint mode**: For data flow vulnerabilities.
- **One YAML file — one Semgrep rule**: Each YAML file must contain only one Semgrep rule; never combine multiple rules in a single file.
- **No generic rules**: When targeting a specific language, avoid `languages: generic`.
- **Forbidden `todook` and `todoruleid` test annotations**: `todoruleid: <rule-id>` and `todook: <rule-id>` annotations in test files are forbidden. Do not use them as placeholders for future rule improvements.

## Overview

This skill guides creation of Semgrep rules that detect security vulnerabilities and code patterns. Rules are created iteratively: analyze the problem, write tests first, analyze AST structure, write the rule, iterate until all tests pass, then optimize.

**Approach selection:**
- **Taint mode** (prioritize): Data flow issues where untrusted input reaches dangerous sinks.
- **Pattern matching**: Simple syntactic patterns without data flow requirements.

**Why prioritize taint mode?** Pattern matching finds syntax but misses context. A pattern `eval($X)` matches both `eval(user_input)` (vulnerable) and `eval("safe_literal")` (safe). Taint mode tracks data flow, so it only alerts when untrusted data actually reaches the sink — dramatically reducing false positives for injection vulnerabilities.

**Iterating between approaches:** It is okay to experiment. If you start with taint mode and it is not working well (taint doesn't propagate as expected, too many false positives/negatives), switch to pattern matching. Conversely, if pattern matching produces too many false positives on safe cases, try taint mode. The goal is a working rule — not rigid adherence to one approach.

**Output structure** — exactly 2 files in a directory named after the rule-id:
```
<rule-id>/
├── <rule-id>.yaml     # Semgrep rule
└── <rule-id>.<ext>    # Test file with ruleid/ok annotations
```

## Procedure

Copy this checklist and track progress:

```
Semgrep Rule Progress:
- [ ] Step 1: Read Documentation (REQUIRED)
- [ ] Step 2: Analyze the Problem
- [ ] Step 3: Write Tests First
- [ ] Step 4: Analyze AST Structure
- [ ] Step 5: Write the Rule
- [ ] Step 6: Iterate Until All Tests Pass
- [ ] Step 7: Optimize the Rule
- [ ] Step 8: Final Run
```

### Step 1 — Read Documentation (REQUIRED)

Before writing any rule, use `WebFetch` to read **all** of these links:

1. [Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)
2. [Pattern Syntax](https://semgrep.dev/docs/writing-rules/pattern-syntax)
3. [ToB Testing Handbook - Semgrep](https://appsec.guide/docs/static-analysis/semgrep/advanced/)
4. [Constant propagation](https://semgrep.dev/docs/writing-rules/data-flow/constant-propagation)
5. [Writing Rules Index](https://github.com/semgrep/semgrep-docs/tree/main/docs/writing-rules/)

Do not skip this step. The documentation reveals pattern operators, metavariable bindings, taint-mode syntax, and constant propagation behavior that you need.

### Step 2 — Analyze the Problem

1. Identify the vulnerability or pattern to detect.
2. Determine whether data flows from an untrusted source to a dangerous sink (→ taint mode) or whether it is a purely syntactic pattern (→ pattern matching).
3. Identify the target language and file extension (e.g., `python` → `.py`, `javascript` → `.js`).
4. Choose a `rule-id` in kebab-case (e.g., `insecure-eval`, `sql-injection-string-format`).

### Step 3 — Write Tests First

Create the output directory and test file **before** writing the rule:

```powershell
mkdir <rule-id>
```

Create `<rule-id>/<rule-id>.<ext>` with:

- **`# ruleid: <rule-id>`** annotations above each vulnerable case.
- **`# ok: <rule-id>`** annotations above each safe case.
- Edge cases: different coding styles, sanitized inputs, safe alternatives, boundary conditions.
- **Never** use `todoruleid` or `todook` annotations — they are forbidden.

Example test file (`insecure-eval.py`):
```python
# ruleid: insecure-eval
eval(request.args.get('code'))

# ok: insecure-eval
eval("print('safe')")

# ok: insecure-eval
eval(sanitize(user_input))
```

### Step 4 — Analyze AST Structure

1. Use `semgrep --dump-ast <file>` on a representative code snippet to see how Semgrep parses the code.
2. Identify the exact node types, metavariable positions, and syntactic variations the pattern must cover.
3. Note any variations that a naive pattern would miss (e.g., parenthesized expressions, method chains, keyword arguments).

### Step 5 — Write the Rule

Create `<rule-id>/<rule-id>.yaml` containing exactly **one** rule:

```yaml
rules:
  - id: insecure-eval
    languages: [python]
    severity: HIGH
    message: User input passed to eval() allows code execution
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
    pattern-sinks:
      - pattern: eval(...)
```

Key constraints:
- One YAML file = one rule. Never combine multiple rules.
- Avoid `languages: generic` — always specify the concrete target language.
- For taint mode: define `pattern-sources` (untrusted entry points) and `pattern-sinks` (dangerous operations). Optionally add `pattern-sanitizers` for safe transformations.
- For pattern matching: use `pattern`, `patterns`, `pattern-either`, or `pattern-regex` as needed.

### Step 6 — Iterate Until All Tests Pass

Run from the rule directory:

```powershell
semgrep --test --config <rule-id>.yaml <rule-id>.<ext>
```

1. Check output for 100% pass rate. "Most tests pass" is **not** acceptable.
2. If false negatives (missing `ruleid` matches): broaden the pattern or fix taint propagation.
3. If false positives (matching `ok` cases): narrow the pattern, add `pattern-not` exclusions, or switch to taint mode.
4. Re-run after every change. Repeat until all tests pass.

### Step 7 — Optimize the Rule

Only after 100% of tests pass:

1. Remove redundant pattern clauses.
2. Simplify metavariable usage.
3. Consolidate `pattern-either` branches where possible.
4. Re-run `semgrep --test` after every optimization to confirm no regression.

### Step 8 — Final Run

```powershell
semgrep --test --config <rule-id>.yaml <rule-id>.<ext>
```

Confirm 100% pass rate one final time before declaring the rule complete.

## Quick Reference

This chair authors **new** Semgrep rules from scratch. It does not ship a companion pack. For porting an existing rule to another language, use `semgrep-rule-variant-creator`.

- Commands, pattern operators, taint mode: [Rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax) and the Quick Start examples below.
- Workflow: Procedure Steps 1–8 in this file (test-first, iterate until `semgrep --test` is green).

## Examples

### Quick Start — Taint Mode

Rule (`insecure-eval.yaml`):
```yaml
rules:
  - id: insecure-eval
    languages: [python]
    severity: HIGH
    message: User input passed to eval() allows code execution
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
    pattern-sinks:
      - pattern: eval(...)
```

Test (`insecure-eval.py`):
```python
# ruleid: insecure-eval
eval(request.args.get('code'))

# ok: insecure-eval
eval("print('safe')")
```

Run:
```powershell
semgrep --test --config insecure-eval.yaml insecure-eval.py
```

### Quick Start — Pattern Matching

Rule (`hardcoded-password.yaml`):
```yaml
rules:
  - id: hardcoded-password
    languages: [python]
    severity: MEDIUM
    message: Hardcoded password detected
    patterns:
      - pattern: $OBJ = "..."
      - metavariable-regex:
          metavariable: $OBJ
          regex: ".*password.*"
```

## Pitfalls

- **Untested rules ship with hidden defects.** Always run `semgrep --test`. A pattern that "looks right" can still miss syntactic variations or match safe code.
- **Missing safe cases in tests.** Without `# ok:` cases, false positives go undetected. Always include sanitized inputs, hardcoded literals, and safe alternatives.
- **Overly broad patterns.** `pattern: $FUNC(...)` matches every function call. Be specific about the function name or use taint mode for context.
- **Overly specific patterns.** `pattern: os.system("rm " + $VAR)` misses `os.system(f"rm {var}")` and other formatting styles. Use taint mode or `pattern-either` to cover variations.
- **Premature optimization.** Simplifying patterns before tests pass causes regressions. Optimize last, re-test after every change.
- **Skipping the AST dump.** The AST reveals how Semgrep actually sees the code. Without it, patterns miss syntactic variations.
- **Using `languages: generic`.** Generic matching lacks language-aware parsing. Always specify the concrete target language.
- **Multiple rules per YAML file.** Each YAML file must contain exactly one rule. Combining rules complicates testing and maintenance.
- **Using `todoruleid` or `todook`.** These annotations are forbidden. Write real test cases instead of deferring.
- **Ignoring taint mode when data flow matters.** Pattern matching alone cannot track whether untrusted data reaches a sink. Prioritize taint mode for injection-style vulnerabilities.

## Verification

Confirm the rule is production-ready:

1. **Test pass rate — must be 100%:**
   ```powershell
   semgrep --test --config <rule-id>.yaml <rule-id>.<ext>
   ```
   Expected output: all `ruleid` cases matched, all `ok` cases not matched, 0 failures.

2. **Rule validates without errors:**
   ```powershell
   semgrep --validate --config <rule-id>.yaml
   ```
   Expected: `Valid configuration file` (or equivalent success message).

3. **Rule runs against real code without crashing:**
   ```powershell
   semgrep --config <rule-id>.yaml <target-directory>
   ```
   Confirm it produces findings (or cleanly reports none) without errors.

4. **Output structure is correct:**
   ```powershell
   ls <rule-id>
   ```
   Expected: exactly two files — `<rule-id>.yaml` and `<rule-id>.<ext>`.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Related Skills

- `semgrep-rule-variant-creator` — port an existing rule to another language; do not use this chair for that.
- `static-analysis` — for running existing Semgrep rulesets or general static analysis without custom rules.
