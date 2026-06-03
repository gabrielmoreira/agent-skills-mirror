---
name: coding_skill
description: Inspect, edit, test, refactor, and validate project code inside the configured project directory. Use when the task involves source search, code reading, bug fixes, implementation changes, syntax checks, automated tests, file moves, or refactors.
---

# Coding Skill (Primary Playbook)

This `SKILL.md` is the default guide for common coding tasks.
Focus on reliable tool usage and verifiable code changes.
Load `references/*` only when needed.

## 1) Scope and Boundary

- This skill covers generic coding work: discover, read, edit, refactor, and validate code.
- This skill is tool-centric. Keep guidance about product/domain-specific implementation out of the main flow.
- All coding-tool paths are resolved under `project_dir`. Paths outside `project_dir` are invalid.
- Use minimal edits first; escalate to broad rewrites only when partial edits are unstable.
- Do not introduce hardcoded secrets, machine-specific absolute paths, or environment-specific install commands in generated code.

## 2) Zero-Context Execution Flow (Default)

When repository context is limited, use this fixed sequence:

1. `search_code` to locate files/snippets.
2. Run quick environment preflight for path/tool consistency:
   - confirm `project_dir`-relative target paths
   - avoid bare `pip`; prefer interpreter-scoped install commands when needed
3. `read_code` to load exact edit context.
4. Apply smallest safe edit (`replace_in_file` or `update_code`).
5. For Python edits:
   - If you used `write_code`: syntax is already validated (pre-write check). Do NOT call `syntax_check` in the same tool call — the file won't exist yet when parallel tools run. Only use `syntax_check` separately for `replace_in_file` / `update_code` edits.
   - `python -m py_compile <changed_file>.py` (optional, for import-level validation; on Windows you may also use `py -3 -m py_compile`)
6. If syntax fails, patch the failing region with local edits first (`replace_in_file` / `update_code`), then re-run checks.
7. Re-read changed region (`read_code`) when ambiguity/count errors occurred.
8. Report changed files, validations, and unresolved risks.

Prefer not to skip to later steps when an earlier step fails.

## 3) Tool Contract (Default)

### 3.1 `search_code`

Purpose: text/regex discovery in project files. Returns `file:line:col: matched_text` for each match.

**Important**: This tool only returns the matching line text, NOT full function/class definitions or surrounding code. To read the full implementation of a matched symbol, use `read_code` with the file path and line range from search results.

Required:
- `query` (string)

Common optional:
- `path` (default `"."`)
- `file_glob` (default `"**/*"`)
- `use_regex` (default `false`)
- `max_results` (default `200`, range `1-1000`)

Example:

```json
{
  "query": "class Workflow",
  "path": "agentclaw",
  "file_glob": "**/*.py"
}
```

### 3.2 `read_code`

Purpose: read file content by line range or Python symbol.

Required:
- `path`

Optional:
- `start_line`, `end_line`
- `symbol` (Python only)
- `symbol_type` (`auto|function|class`)

Examples:

```json
{
  "path": "agentclaw/graph/workflow.py",
  "start_line": 60,
  "end_line": 180
}
```

```json
{
  "path": "agentclaw/node/llm.py",
  "symbol": "_build_messages",
  "symbol_type": "function"
}
```

### 3.3 `syntax_check`

Purpose: language-aware syntax diagnostics.

Required:
- `path`

Optional:
- `language` override (`py|js|ts|json|yaml|toml`)
- `context_lines` (default `3`, range `0-8`)
- `include_source_context` (default `true`)

Example:

```json
{"path":"agentclaw/node/llm.py"}
```

When to use:
- immediately after editing Python/JS/TS/JSON/YAML/TOML files
- before `py_compile`/register/runtime checks

When NOT to use:
- for semantic/runtime logic debugging (it is syntax-focused)
- as a replacement for import/runtime validation

Common failure shapes -> next action:
- `path_not_found` / `Not a file`
  - align path with `project_dir`, then retry same check
- `PY_SYNTAX_ERROR` / syntax diagnostics with line+col
  - patch failing region via `replace_in_file` or `update_code`, then re-run `syntax_check`
- checker unavailable (`node`, `tsc`, `PyYAML`, `tomli`)
  - report dependency gap and continue with partial validation

Output format:
- Human-readable block first (error message, source context with `>` marker, smart HINT), followed by structured JSON.
- HINT line detects common root causes:
  - `HTML entities (&quot; &gt; &#x27;)` → use `write_code` instead of `write_file` to auto-sanitize.
  - `double-escaped sequences (\\\\n)` → use literal multi-line content or single `\\n`.
- `ok=true` + `status=success`: syntax pass with no flagged risk pattern.
- `ok=true` + `status=warning`: syntax pass but `risk_diagnostics` is non-empty.
  - treat as unresolved risk and patch before claiming completion.
- `ok=false` + `diagnostics`: syntax failure; repair same region first.

### 3.4 `update_code`

Purpose: regex-based code update with automatic syntax validation.

Required:
- `path`
- `pattern` (Python regex)
- `replacement`

Optional:
- `dry_run` (default `false`)

Features:
- Uses Python regex with re.MULTILINE flag
- Automatically validates syntax after update (Python/JSON files)
- Returns syntax warnings without blocking write (allows incremental fixes)

Example:

```json
{
  "path": "agentclaw/node/llm.py",
  "pattern": "def\\s+old_name\\(",
  "replacement": "def new_name(",
  "dry_run": true
}
```

When to use:
- Pattern-based refactoring across code
- Renaming functions/variables with regex
- Updating repeated code patterns

When NOT to use:
- Exact text replacement (use `replace_in_file`)
- Large block rewrites (use `write_code`)

Result includes:
- `syntax_warning`: line number and error if syntax check fails (does not block write)
- `preview`: affected code lines
- `replacements`: number of matches replaced

### 3.5 `replace_in_file`

Purpose: deterministic single-file snippet replacement.

Required:
- `path`, `old_text`, `new_text`

Optional:
- `replace_all` (default `false`)
- `expected_replacements`
- `occurrence_index` (1-based)

Notes:
- old_text and new_text are matched/written LITERALLY — no escape sequence processing (`\\n` means literal backslash-n). Use real multi-line strings for actual newlines.

Rules:
- Use this for small exact replacements, not broad transformations.
- If multiple matches and `replace_all=false`, set `occurrence_index` to disambiguate.
- `expected_replacements` should only be set when match count is deterministic.
- If `expected_replacements` mismatches, re-read file and recalculate before retrying.

Example:

```json
{
  "path": "workflows/nl2sql.py",
  "old_text": "Workflow(\"nl2sql\")",
  "new_text": "Workflow(id=\"nl2sql\", name=\"NL2SQL\")"
}
```

### 3.6 `write_file`

Purpose: create/overwrite a full file when partial edit is inefficient.

**Note**: For source code files (.py, .js, .ts, .json, etc.), prefer `write_code` (section 3.8) — it auto-sanitizes HTML entities and runs pre-write syntax checks.

Required:
- `path` (relative project path)
- `content` (raw source text)

Rules:
- Content is written LITERALLY as-is — no escape sequence processing (`\\n` becomes literal backslash-n, not a newline). Use real multi-line content for actual newlines.
- Use `write_file` for new files or full rewrites only.
- For existing files, prefer `replace_in_file` / `update_code`; only use `write_file` overwrite when intentional.
- If an existing file was already written once in this task, do not keep rewriting it with `write_file`; switch to local patch tools for follow-up fixes.
- Do not pass source text into `path`.
- Keep `content` as raw code; do not pre-escape triple quotes into the final file.
- Always re-read the file after `write_file` before registration/runtime checks.
- If writing Python code, run `syntax_check` + `python -m py_compile` immediately after `write_file`.
- If syntax fails after `write_file`, do not rewrite whole file first; repair failing region with targeted edits.

Example:

```json
{
  "path": "workflows/new_agent.py",
  "content": "from agentclaw import Workflow\n..."
}
```

When to use:
- creating a new file
- full overwrite only when partial edits are clearly unstable

When NOT to use:
- one-line or small region fixes (prefer `replace_in_file` / `update_code`)
- first attempt for syntax error repair on an existing file

Common failure shapes -> next action:
- `content_too_large`
  - split into smaller deterministic edits
- post-write syntax error
  - run local patch loop on failing lines; do not jump to another full rewrite
- path confusion after write
  - re-list and re-read file with `project_dir`-relative path, then validate again

### 3.7 Safe Coding Patterns (Avoid Syntax Errors)

When generating code with complex strings or nested structures, use segmented writing to prevent syntax errors.

#### Rule 1: Segmented Writing Strategy

For new files with complex content:
1. Write basic structure (imports, class/function signatures)
2. Run `syntax_check` to validate
3. Add simple logic and core functionality
4. Run `syntax_check` to validate
5. Add complex content (long strings, nested structures)
6. Run `syntax_check` + `py_compile` to validate

#### Rule 2: Complex String Handling

For code containing long prompts or multi-line strings:
1. Use separate constant definitions for complex strings
2. Keep string nesting simple (avoid mixing f-strings with triple quotes)
3. Use `textwrap.dedent` for indentation handling when needed
4. Validate after each addition

#### Rule 3: Incremental Validation

After each `write_file` or significant edit:
1. If `write_code` was used: syntax is already validated — skip `syntax_check` (do NOT call it in the same tool batch as `write_code`; the file won't exist yet).
2. If `replace_in_file` / `update_code` was used: run `syntax_check` in a **separate** tool call.
3. If syntax passes, run `py_compile` for Python files.
4. Fix any issues with local edits before adding more content.
5. Only proceed to next content addition after validation passes.

This approach reduces syntax error rates and makes fixes more targeted.

### 3.8 `write_code` (Preferred for source code)

Purpose: write source code files with automatic sanitization and pre-write validation.
**Use this instead of `write_file` for any source code** (.py, .js, .ts, .json, etc.).

Required:
- `path` (relative project path)
- `content` (source code)

Optional:
- `overwrite_existing` (default `false`)

Auto-sanitization:
- HTML entities (`&quot;` → `"`, `&#x27;` → `'`, `&gt;` → `>`, `&amp;` → `&`) are auto-decoded
- Double-escaped newlines (`\\n` literal) trigger a warning in the response

Pre-write checks:
- Python files: `compile()` check before writing; rejects invalid syntax without touching file
- JSON files: `json.loads()` check before writing

Result contract:
- `[OK]` with file stats on success; includes `note=html_entities_auto_fixed` if sanitization was applied
- `[SYNTAX_ERROR]` with line context and smart HINT if pre-write check fails — file NOT written
- `[Error]` on parameter/path validation failure

Example:

```json
{
  "path": "workflows/nl2sql.py",
  "content": "from agentclaw import Workflow\n\nworkflow = Workflow(id=\"nl2sql\")\n",
  "overwrite_existing": true
}
```

When to use:
- any new code file creation
- full overwrite of source code when partial edits are unstable
- when model output may contain HTML entity encoding

When NOT to use:
- non-code files (configs, logs, binary) — use `write_file`
- small edits to existing files — use `replace_in_file` / `update_code`

### 3.9 `lookup_api`

Purpose: introspect installed Python packages to discover correct import paths, constructor signatures, and methods.
Use this when you are **unsure of the correct import or API** for any installed library.

Required:
- `module` (e.g. `"agentclaw"`, `"agentclaw.node"`)

Optional:
- `symbol` (e.g. `"LLMNode"`, `"Workflow"`) — omit to list all exported names
- `include_methods` (default `false`) — list public methods of a class

Examples:

```json
{"module": "agentclaw"}
```
→ Lists all classes, functions, and other exports of the module.

```json
{"module": "agentclaw", "symbol": "LLMNode", "include_methods": true}
```
→ Returns: import paths (shortest + source), constructor signature, description, and public methods.

When to use:
- before writing `import` statements for unfamiliar packages
- when `search_code` cannot find the symbol (because it is in an installed package, not project code)
- to verify constructor arguments before generating code

When NOT to use:
- for project-local code (use `search_code` + `read_code` instead)
- for non-Python packages

## 4) Tool Selection Strategy

- `replace_in_file`: first choice for small deterministic edits.
- `update_code(anchor)`: bounded block insertion/replacement with explicit anchors.
- `update_code(regex)`: repetitive pattern refactors.
- `replace_in_files`: broad mechanical rename/namespace updates.
- `write_code`: **preferred** for creating new code files or full rewrites (auto-sanitizes, pre-validates).
- `write_file`: non-code files or when `write_code` is not appropriate.
- `lookup_api`: verify imports and constructor signatures before generating code for installed packages.
- For precise single-target edits, prefer:
  1. `replace_in_file` + `occurrence_index` / `expected_replacements`
  2. `update_code(exact)` + `expected_count=1`
  3. avoid unbounded `replace_all=true` unless scope guards are set.

## 5) Failure Recovery Loop (Default)

1. Classify failure first: path, parameter, count, ambiguity, or checker environment.
2. Fix the same failing tool call before switching to unrelated tools.
3. Re-read local context before retry when mismatch/ambiguity appears.
4. Retry with corrected args.
5. After two same-shape failures, switch strategy and explain the switch.
6. For syntax failures after code edits, prefer local patch loops before full-file rewrite.

### 5.1 Error-Code Repair Playbook (Default)

Map structured failures to deterministic next actions:

- `error_class=path_not_found`
  - Action: verify `project_dir`-relative path with `search_code`/`read_code`, then retry same tool.
- `error_class=parameter_validation`
  - Action: correct required args for current mode/tool, retry immediately.
- `error_class=ambiguous_match`
  - Action: set `occurrence_index` or narrow match anchors/text.
- `error_class=replacement_scope_too_large`
  - Action: narrow scope first; only then set explicit replacement caps.
- `error_class=syntax_error` or `SYNTAX_ERROR` diagnostics
  - Action: patch failing region with local edit tools, then re-run `syntax_check` + `py_compile`.
- checker unavailable errors
  - Action: report missing dependency and keep status `partial` if this blocks required validation.

Common patterns:

- `path_not_found` / `Not a file`
  - Re-discover path with `search_code`; confirm relative path under `project_dir`.
- `parameter_validation` / missing fields
  - Correct required mode fields and retry same tool immediately.
- `expected_count` / `expected_replacements` mismatch
  - File changed or match pattern drifted; re-read and recompute.
- ambiguous match
  - provide `occurrence_index` or explicit ambiguity override.
- replacement scope too large
  - narrow `old_text`/anchors, or set explicit `max_replacements` / `max_total_replacements` after verifying match count.
- checker unavailable (`node`, `tsc`, `PyYAML`, `tomli`)
  - report dependency gap and treat validation as partial.
- syntax/compile failure after write
  - run targeted fix on failing lines with `replace_in_file`/`update_code`;
  - only do full rewrite when local fixes failed repeatedly.

## 6) Structured Outcome Contract (Default)

When using MCP coding tools, consume structured fields first, not prose keywords:

- success hints:
  - `ok=true`
  - `changed` / `replacements` present as expected
  - for `syntax_check`, require `status=success` (not `warning`) before claiming clean pass
- failure hints:
  - `error_class`
  - `missing_fields`
  - `suggested_fix`
  - explicit `[ERROR] ...` prefix

Required behavior:

1. If `error_class=parameter_validation`, fix arguments and retry the same tool.
2. If result is `dry_run=true`, do not claim the edit is applied.
3. If replacement/count guard fails, re-read target region before retry.
4. In final report, bind each claimed change to a concrete successful tool call.
5. If `syntax_check` returns `risk_diagnostics`, include them in risks or fix them before marking `completed`.

## 7) Validation Standard

For code-change tasks:

1. `syntax_check` for changed files when supported.
2. `py_compile` for changed Python files.
3. If changed files include `workflows/*.py`, confirm bootstrap import wiring in `server.py` (direct import or via `workflows/__init__.py`).
4. Re-run focused checks when previous step failed.

Do not report full completion without validation evidence.

### 7.1 Workflow Tooling Pattern (Recommended)

For workflow-local tools in generated workflow files:

1. Prefer `@workflow.tool` as the default registration path.
2. Use `workflow.register_toolkit(...)` only when cross-workflow reuse/pluginization is explicitly required.
3. If migrating old examples (`ToolKit()` + `workflow.use(toolkit)`), keep behavior equivalent and avoid unrelated rewrites.

## 8) Anti-Hardcoding Rules (Default)

- Never write credentials/tokens/passwords directly into source files.
- Avoid absolute host-specific paths (for example `/home/<user>/...`) in code and scripts.
- Prefer config/env-based values and explicit input parameters.
- If dependency installation is required, do not emit bare `pip install ...` by default.
  - prefer `<python_executable> -m pip ...` or project-selected package manager strategy.

## 8.1 Import Validity Check (Recommended for generated code)

- Do not invent module paths or symbol names from memory.
- Before final `write_code`/`write_file` for framework code, verify:
  - imported module path exists in the local repository/runtime;
  - imported symbols are actually exported.
- **For installed packages**: use `lookup_api(module="<pkg>", symbol="<name>")` to get correct import paths and constructor signatures.
- **For project-local code**: use `search_code`/`read_code` to confirm local definitions before writing.
- If registration/preflight reports import blockers, fix imports first, then continue to syntax/runtime validation.

## 9) Completion Contract

Final result should include:

1. `changed_files`
2. `operations` (tools actually used)
3. `validation` (`syntax_check`, `py_compile`, or explicit limitations)
4. `status` (`completed` / `partial` / `blocked`)
5. `next_step` (if not completed)

## 10) Reference Policy

Read references only when needed.
Read only when task requires coordination between `coding_skill` and `agent_creator`:

- `references/agent_workflow_coding_notes.md`
