---
name: running-code-analyzer
description: "Run Salesforce Code Analyzer to scan code for security, performance, best practice, and code style violations. Supports all engines (PMD, ESLint, CPD, RetireJS, Flow, SFGE, ApexGuru), targets (files, folders, git diff), categories, and severities. TRIGGER when: user says 'scan my code', 'check for security issues', 'run PMD/ESLint', 'find duplicates', 'analyze Flows', 'check vulnerable libraries', 'AppExchange review', 'lint my LWC', 'static analysis', 'code quality', or mentions engines/file types (.cls, .trigger, .js, .flow-meta.xml). DO NOT TRIGGER when: user wants to fix code without scanning, or asks about installation/configuration."
allowed-tools: Read, Bash(sf code-analyzer), Bash(node), Bash(git diff), Bash(date), Write, Edit
license: LICENSE.txt has complete terms
metadata:
  version: "1.0"
  argument-hint: "[target-path] [--engine pmd|eslint|cpd|retire-js|regex|flow|sfge|apexguru] [--category Security|Performance|BestPractices|...] [--severity 1-5] [--diff]"
---

# Running Code Analyzer Skill

## ⚠️ CRITICAL: Tool Selection

**BEFORE DOING ANYTHING ELSE:**

This skill MUST use the **Bash tool** to execute `sf code-analyzer run` and Node.js scripts.

**DO NOT use these tools under any circumstances:**
- ❌ `run_code_analyzer` (MCP tool)
- ❌ `mcp__*` (any MCP tool)
- ❌ Any tool containing `mcp` in its name

If you see a `run_code_analyzer` tool available, **ignore it completely**. Use only the Bash tool with `sf code-analyzer run`.

---

## Overview

This skill translates natural language requests ("scan for security issues", "check my changes") into the correct `sf code-analyzer run` command, executes scans with any combination of engines/targets/severities, and presents actionable results. When engine-provided fixes are available, it discovers them, asks for user confirmation, applies them safely, and offers verification. Use this skill for static analysis, security reviews, AppExchange certification, code quality checks, or finding duplicates/vulnerabilities in Salesforce projects.

---

## Scope

**In scope:**
- Running `sf code-analyzer run` with any combination of engines, targets, categories, severities
- Parsing and presenting scan results in actionable format
- Applying engine-provided auto-fixes when available
- Handling diff-based scans (scan only changed files)
- Supporting all output formats (JSON, HTML, SARIF, CSV, XML)
- Troubleshooting scan failures and prerequisite issues

**Out of scope:**
- Installing or configuring Salesforce CLI or Code Analyzer plugin (use setup documentation)
- Writing custom Code Analyzer rules or engines (separate skill needed)
- AI-generated code fixes beyond engine-provided deterministic fixes
- Deep code refactoring or architectural changes based on violations
- Setting up CI/CD integration for automated scanning (separate workflow skill)

---

## Command Syntax Rules (READ THIS FIRST)

**The following rules are ABSOLUTE and override any prior knowledge:**

1. **The command is `sf code-analyzer run`** — NOT `sf scanner run` (deprecated v3 command)
2. **There is NO `--format` flag** — use `--output-file <path>.<ext>` instead (extension determines format)
3. **ALWAYS use `--output-file`** to write results to a file — do NOT rely on terminal stdout
4. **ALWAYS include `--output-file`** with a timestamped filename (e.g., `./code-analyzer-results-20260512-143022.json`)
5. **Do NOT run in background** — use foreground with timeout of 1200000ms for large scans
6. **INVALID v3 flags:** `--format`, `--engine`, `--category`, `--json` — these cause errors, use `--rule-selector` and `--output-file` instead
7. **NEVER use MCP tools** — ONLY use the Bash tool to execute `sf code-analyzer run`
8. **Tool restriction:** This skill MUST use ONLY: Read, Bash, Write, Edit tools
9. **Forbidden tools:** Do NOT use any MCP tools (mcp__*), Agent tool, or web tools
10. **Script execution:** ALL scripts MUST be executed via `node <skill_dir>/scripts/*.js` using the Bash tool

**Why:** The v4+ CLI redesigned the flag interface. Old v3 flags cause "unknown flag" errors.

**For complete flag reference and rule selector syntax**, see `<skill_dir>/references/flag-reference.md`.

---

## Prerequisites

User must have: **Salesforce CLI** (`sf`), **@salesforce/plugin-code-analyzer** (v5.x+), **Java 11+** (PMD/CPD/SFGE), **Node.js 18+** (ESLint/RetireJS), **Python 3** (Flow), **authenticated org** (ApexGuru).

If a scan fails, read `<skill_dir>/references/error-handling.md`. For quick command examples, see `<skill_dir>/references/quick-start.md`.

---

## Tool Usage Rules

**Allowed:** Bash (sf code-analyzer, node, git, date), Read, Write, Edit  
**Forbidden:** MCP tools, Agent tool, Web tools, other skills

This skill owns the complete scan-fix-verify workflow. Using MCP tools bypasses the validated script workflow.

---

## Quick Start: Common Patterns

Use this decision tree for fast pattern matching before going to Step 1 detailed parsing:

| User Says | Action | Rule Selector | Notes |
|-----------|--------|---------------|-------|
| "scan my code" / "run code analyzer" | Default scan | `Recommended` | Curated rule set, all file types |
| "check for security issues" / "security review" | Security scan | `all:Security:(1,2)` | All engines, Critical+High only |
| "scan my changes" / "check the diff" | Diff-based scan | Get changed files via `git diff`, filter to scannable types, use `--target` | See Step 1.5 for filtering logic |
| "run PMD" / "check my Apex" | PMD only | `pmd` | Apex classes and triggers |
| "lint my LWC" / "check my JavaScript" | ESLint only | `eslint` | JavaScript/TypeScript/LWC |
| "find duplicates" / "check for copy-paste" | CPD (Copy-Paste Detector) | `cpd` | Detects code clones |
| "check for vulnerabilities" / "scan libraries" | RetireJS | `retire-js` | JavaScript library CVEs |
| "deep analysis" / "data flow analysis" | SFGE (Graph Engine) | `sfge` | Requires Java 11+, 10-20min, use `--workspace "force-app"` |
| "performance analysis" / "governor limits" | ApexGuru | `apexguru` | Requires authenticated org |
| "analyze my Flows" | Flow engine | `flow` | Target: `**/*.flow-meta.xml`, requires Python 3 |
| "AppExchange security review" | AppExchange scan | `all:Security:(1,2)` | Read `<skill_dir>/references/special-behaviors.md` → AppExchange section |

**If the pattern matches above**, proceed directly to Step 3 (Build Command). Otherwise, continue to Step 1 for detailed parsing.

---

## Step 1: Parse the User's Intent

Analyze the user's request along these 7 dimensions. Any can be combined freely:

### 1.1 ENGINE — Which analysis engine(s)?

Map user keywords to `--rule-selector` values:
- PMD / Apex rules → `pmd`
- ESLint / JS/TS rules / lint → `eslint`
- Flows / Flow analysis → `flow`
- duplicates / copy-paste / CPD → `cpd`
- vulnerabilities / CVE / libraries / RetireJS → `retire-js`
- SFGE / data flow / deep analysis → `sfge`
- performance / ApexGuru → `apexguru`
- regex / pattern rules → `regex`
- all engines / everything → `all`
- Not specified / general "scan" → `Recommended` (default)

### 1.2 CATEGORY — What kind of issues?

Map user keywords to category tags:
- security / vulnerabilities / OWASP → `Security`
- performance / speed / optimization → `Performance`
- best practices / quality → `BestPractices`
- code style / formatting → `CodeStyle`
- design / complexity → `Design`
- error prone / bugs → `ErrorProne`
- documentation / comments → `Documentation`

### 1.3 SEVERITY — How critical?

**Severity levels:** 1=Critical (must fix), 2=High (should fix), 3=Moderate (recommended), 4=Low (nice to fix), 5=Info (FYI)

Map user keywords:
- "critical only" / "sev 1" → `1`
- "critical and high" / "sev 1-2" → `(1,2)`
- "moderate and above" / "sev 1-3" → `(1,2,3)`

### 1.4 SPECIFIC RULE — Named rule?

If the user mentions a specific rule by name (e.g., "ApexCRUDViolation", "no-unused-vars"):
- Map to: `--rule-selector <engine>:<ruleName>`
- If engine is ambiguous, use just the rule name: `--rule-selector <ruleName>`

**⚠️ IMPORTANT — Partial Rule Names:** The `--rule-selector` flag requires the EXACT full rule name (e.g., `@salesforce-ux/slds/no-hardcoded-values-slds2`, not `no-hardcoded-values`). It does NOT support wildcards or partial matches.

**When you are NOT 100% certain of the full rule name:**
- **Do NOT guess** — a wrong name returns 0 results and wastes a scan cycle
- Instead, **look up the rule first** using the `sf code-analyzer rules` command with grep:
  ```bash
  sf code-analyzer rules --rule-selector all 2>&1 | grep -i "USER_KEYWORD"
  ```
- Extract the full rule name from the output, then use it in your scan command
- If grep returns multiple matches, present them to the user and ask which one they meant
- If grep returns 0 matches, tell the user no rule matched their keyword

### 1.5 TARGET — What files to scan?

Map user keywords:
- Specific file/folder → `--target <path>`
- Glob pattern / "all Apex classes" → `--target **/*.cls,**/*.trigger`
- "my changes" / "diff" → Run `git diff --name-only [base]...HEAD`, filter to scannable types, pass as `--target`
- "LWC" → `--target **/lwc/**`
- "Flows" → `--target **/*.flow-meta.xml`
- Not specified → Entire workspace (omit `--target`)

**For diff filtering details:** See `<skill_dir>/references/special-behaviors.md`.

### 1.6 OUTPUT — What format?

**DEFAULT:** Always JSON. Only change if user EXPLICITLY requests another format.

**Naming:** `./code-analyzer-results-<YYYYMMDD-HHmmss>.<ext>` (timestamp via `TIMESTAMP=$(date +%Y%m%d-%H%M%S)`)

Formats: `.json` (default), `.html` (report), `.sarif` (GitHub/IDE), `.csv` (spreadsheet), `.xml`

### 1.7 COMPARISON — Delta/trend analysis?

Map user keywords:
- "new since main" → `git diff --name-only main...HEAD` → scan those files
- "new since last commit" → `git diff --name-only HEAD~1`
- "compared to develop" → `git diff --name-only develop...HEAD`

---

## Step 2: Build the Rule Selector

**Syntax:** `:` = AND, `,` = OR, `()` = grouping

**Examples:**
- Engine only: `pmd`
- Engine + category: `pmd:Security`
- Engine + severity: `pmd:2`
- Complex: `(pmd,eslint):Security:(1,2)` = (PMD or ESLint) AND Security AND (sev 1 or 2)
- Specific rule: `pmd:ApexCRUDViolation`
- All rules: `all`

**More examples:** `<skill_dir>/references/command-examples.md`

---

## Step 3: Build the Full Command

Generate timestamp: `TIMESTAMP=$(date +%Y%m%d-%H%M%S)`

Build command:
```bash
sf code-analyzer run \
  --rule-selector <selector> \
  --target <targets> \              # optional
  --output-file "./code-analyzer-results-${TIMESTAMP}.json" \  # DEFAULT: JSON
  --include-fixes \                 # always
  --workspace <path>                # optional
```

**Key decisions:**
- DEFAULT: timestamped JSON (`.json`). Only change format if user explicitly requests HTML/SARIF/CSV/XML.
- Always include `--include-fixes` (enables Step 6 auto-fix)
- Omit `--target` to scan entire workspace
- For diff-based scans: get files via `git diff --name-only`, filter to scannable types, pass as `--target`

**Special cases:** See `<skill_dir>/references/special-behaviors.md` for SFGE/ApexGuru/AppExchange/diff filtering.

---

## Step 4: Execute the Scan

**⚠️ TOOL REQUIREMENT: Use Bash tool ONLY. DO NOT use run_code_analyzer (MCP tool) or any MCP tool.**

**Rules:** Foreground only (no `run_in_background`), hardcoded filename (not `$TIMESTAMP`), timeout 1200000ms, no `sleep`, log output to timestamped file.

**Steps:**

1. Generate timestamp: `date +%Y%m%d-%H%M%S` → capture output (e.g., `20260512-143022`) **using Bash tool**
2. Tell user:
   ```
   Starting scan...
   Results: ./code-analyzer-results-20260512-143022.json
   Log:     ./code-analyzer-results-20260512-143022.log
   May take several minutes for large codebases.
   ```
3. Run command with literal timestamp in filename and `tee` to capture log (timeout: 1200000):
   
   ⚠️ **IMPORTANT:** Use the Bash tool, NOT the run_code_analyzer MCP tool.
   
   ```bash
   sf code-analyzer run --rule-selector Recommended --output-file "./code-analyzer-results-20260512-143022.json" --include-fixes 2>&1 | tee "./code-analyzer-results-20260512-143022.log"
   ```
4. After completion: Exit 0 = success. Error output → check both the log file and `<skill_dir>/references/error-handling.md`.
5. IMMEDIATELY parse results (Step 5). Do NOT ask user what they want.

---

## Step 5: Parse and Present Results

### Parsing Rules:

1. **Execute the parse script using `<skill_dir>`** — see below
2. **NEVER use `jq` to parse results** — jq one-liners WILL fail due to shell quoting issues
3. **Run it IMMEDIATELY after the scan** — do NOT ask the user "what would you like next?"

### Script Execution

All scripts are bundled in the `scripts/` subdirectory of the same directory that contains this SKILL.md file. Use the absolute path to that directory — do NOT use `./scripts/` as that resolves relative to the current working directory, not the skill directory.

```bash
node <skill_dir>/scripts/parse-results.js "./code-analyzer-results-TIMESTAMP.json"
```

⚠️ **DO NOT:**
- ❌ Invent or generate script code yourself
- ❌ Use bare relative paths like `node scripts/parse-results.js` (won't resolve from user's CWD)
- ❌ Use heredocs or inline script content
- ❌ Use `jq` as a substitute for the parse script

### How to Present Results:

**ALWAYS present a concise summary, then point to the output file for full details.**

```
## Scan Complete

**Found X violations** across Y files.

| Severity | Count |
|----------|-------|
| Critical (1) | X |
| High (2) | X |
| Moderate (3) | X |
| Low (4) | X |
| Info (5) | X |

### Top Issues
| # | Rule | Engine | Sev | File | Line |
|---|------|--------|-----|------|------|
| 1 | ApexCRUDViolation | pmd | 2 | AccountService.cls | 42 |
| 2 | ApexSOQLInjection | pmd | 1 | QueryHelper.cls | 18 |
| ... (show up to 10 most critical) |

### Top Rules by Frequency
| Rule | Engine | Count |
|------|--------|-------|
| no-var | eslint | 170 |
| ApexDoc | pmd | 165 |
| ... |

Full results: `./code-analyzer-results-20260512-143022.json`
```

### Result Presentation Rules:

- **0 violations**: "Scan complete — no violations found! Output: `<path>`"
- **1-10**: Show all violations in table
- **11-50**: Show severity counts + top 10 violations
- **50-5000**: Show counts + top 10 violations + top 10 rules + top 5 files
- **5000+**: Same as 50-5000, plus suggest narrowing scope (severity/category/folder)

**Always end with:** Output file path + next-action offers (explain rules / apply fixes)

**For large result sets:** See `<skill_dir>/references/special-behaviors.md`.

---

## Step 6: Apply Engine-Provided Fixes (Post-Scan)

After presenting results, check if violations have **engine-provided fixes** (deterministic, not AI-generated).

**Rules:** NEVER apply without confirmation. Use EXACT scripts from `<skill_dir>/scripts/`. Filter vendor files if needed, then: Discover → Apply → Summarize.

**Flow:** Filter vendor (6.1 if needed) → discover (6.2) → present (6.3) → ASK user → apply (6.4) → summarize (6.5) → present results.

### 6.1 — Check for vendor files (if needed)

If user said "fix my code" or "project source", or if top files by violation count are vendor libraries (jQuery, Bootstrap, *.min.js), run:

```bash
node "<skill_dir>/scripts/filter-violations.js" \
  "./code-analyzer-results-TIMESTAMP.json" \
  "./code-analyzer-results-TIMESTAMP-filtered.json" \
  --report
```

Present: "Excluded X vendor files (Y violations) - jQuery, Bootstrap, etc. Applying fixes to Z project files only."

Use filtered file for Step 6.3+. **See:** `<skill_dir>/references/vendor-file-handling.md` for detailed logic.

### 6.2 — Discover fixable violations

```bash
node "<skill_dir>/scripts/discover-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```

(Use filtered file from Step 6.1 if created.)

### 6.3 — Present fixable violations and ASK for confirmation

After running the discovery script, present results:

```
### Engine-Provided Fixes Available

**X of Y violations** have auto-fixes provided by the analysis engine:

| Rule | Engine | Sev | Fixable Count |
|------|--------|-----|---------------|
| no-var | eslint | 3 | 170 |
| no-hardcoded-values-slds2 | eslint | 4 | 76 |
| ... |

These are safe, deterministic fixes generated by the engines (not AI-generated).

Would you like me to apply these fixes? (yes / no / select specific rules)
```

### ⚠️ STOP HERE AND WAIT FOR USER RESPONSE.

**Even if the user originally said "scan and fix everything", you MUST still stop here and wait.** Present the table, ask the question, and WAIT for a response in the NEXT turn.

### 6.4 — Apply fixes ONLY after user confirms

**Only proceed after user says "yes", "apply", "go ahead" IN A SEPARATE RESPONSE.**

```bash
node "<skill_dir>/scripts/apply-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```

(Use filtered file if Step 6.1 created one.)

### 6.5 — After applying, ALWAYS run the summary script

⚠️ **MANDATORY**: After the apply script completes, you MUST run the summary script as your VERY NEXT action.

```bash
node "<skill_dir>/scripts/summarize-fixes.js" "./code-analyzer-results-TIMESTAMP.json"
```

Then present to the user:

```
### Engine-Provided Fixes Applied Successfully ✓

**Applied X auto-fixes across Y files.**

| Severity | Fixes Applied |
|----------|---------------|
| Critical (1) | X |
| High (2) | X |
| ... |

| Rule | Fixes Applied |
|------|---------------|
| no-var | 169 |
| ... |

Want me to re-run the scan to verify the fixes resolved the violations?
```

### 6.6 — If user declines: Skip. If selects rules: filter. If "all": run as-is.

### 6.7 — Re-scan (optional): Re-run with new timestamp, compare before/after counts.
---
## Rules / Constraints

| Constraint | Rationale |
|-----------|-----------|
| Timestamped output (JSON + log) | Prevents overwrite; enables history tracking |
| Use `tee` for logs | Keeps logs in working dir with matching timestamp |
| Never use `--format` flag | Removed in v4+; use `--output-file <path>.<ext>` instead |
| Foreground scans, 1200000ms timeout | SFGE takes 10-20min; backgrounding loses output |
| Execute scripts from `<skill_dir>/scripts/` | Never write inline scripts or heredocs |
| Never apply fixes without confirmation | User must explicitly approve code modifications |
| Check for vendor files before fixes | If 50%+ vendor (jQuery, Bootstrap), filter first |
| Run fix scripts in order | Filter (if needed) → Discover → Apply → Summarize |
| SFGE needs explicit `--workspace` | Prevents template file compilation errors |
| Look up partial rule names first | Guessing fails; use `sf code-analyzer rules` to find exact name |
| ONLY Bash tool, never MCP | run_code_analyzer MCP tool bypasses script workflow |
| Never invoke other skills for fixes | This skill owns complete workflow end-to-end |

---

## Gotchas

| Issue | Why It Happens | Solution |
|-------|---------------|----------|
| `--format` flag error | Removed in v4+ | Use `--output-file <path>.<ext>` |
| Scan returns 0 results | Invalid rule selector | Run `sf code-analyzer rules --rule-selector <selector>` to verify |
| SFGE compilation error | Template files in workspace | Set `--workspace "force-app"` |
| jq parsing fails | Shell quoting issues | Use `node "<skill_dir>/scripts/parse-results.js"` |
| Inline scripts written | LLM generates custom code | NEVER write scripts — use existing from <skill_dir>/scripts/ |
| Scan times out | Large SFGE | Increase timeout to 1200000ms |
| run_code_analyzer MCP used | LLM prefers MCP over Bash | Use Bash tool ONLY |
| Other skills invoked | LLM delegates to other skills | Use apply-fixes.js from this skill only |
| Most violations are vendor | Includes jQuery, Bootstrap, *.min.js | Run filter-violations.js before applying fixes |

---

## Output Expectations

Every scan produces: timestamped JSON file, concise summary (severity/top violations/rules/files), next-action offers. If fixes applied: summary by severity/rule, offer verification.

---

## Reference File Index

`<skill_dir>` is the absolute path to the directory containing this SKILL.md file.

### Scripts (Always execute, never read)
| File | When to use |
|------|-------------|
| `<skill_dir>/scripts/parse-results.js` | Step 5 — extract summary from scan JSON |
| `<skill_dir>/scripts/filter-violations.js` | Step 6.1 — exclude vendor files (jQuery, Bootstrap) from fixes |
| `<skill_dir>/scripts/discover-fixes.js` | Step 6.2 — identify fixable violations |
| `<skill_dir>/scripts/apply-fixes.js` | Step 6.4 — apply engine fixes after user confirms |
| `<skill_dir>/scripts/summarize-fixes.js` | Step 6.5 — summarize applied changes |

### References (Read when needed)
| File | When to read |
|------|-------------|
| `<skill_dir>/references/quick-start.md` | Command syntax templates |
| `<skill_dir>/references/flag-reference.md` | Flag docs, rule selector syntax |
| `<skill_dir>/references/error-handling.md` | Scan failure diagnosis |
| `<skill_dir>/references/engine-reference.md` | Engine capabilities, file types, rule tags |
| `<skill_dir>/references/command-examples.md` | Uncommon command scenarios |
| `<skill_dir>/references/special-behaviors.md` | SFGE/ApexGuru/AppExchange/diff/large scans |
| `<skill_dir>/references/vendor-file-handling.md` | Vendor file detection and filtering logic |

Examples in `<skill_dir>/examples/` show output structure validation and command patterns (basic/large/security scans, fix workflows).
