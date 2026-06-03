---
name: agent_creator
description: Create or modify AgentClaw workflows and agents from natural-language requirements. Use when changing workflow architecture, nodes, prompts, persona, routing, tool/skill configuration, runtime behavior, validation gates, registration, or project wiring.
---

# Agent Creator (Lean Playbook)

This file is the default workflow-building guide.
Read this file first. Route into `references/*` when the task pattern calls for it.

## 0) Default Mode (Important)

Use **Lean Mode** by default:

1. Keep to the shortest executable path.
2. Prefer local patch fixes over full-file rewrites.
3. Validate after each Python edit.
4. Prefer not to continue to the next gate while the current gate is failing.
5. Report `completed` / `partial` / `blocked` truthfully.

Keep the build lean, but do not skip a pattern reference when the request clearly matches it. The right reference is part of the shortest reliable path.

## 0.1) Reference Routing (Pattern Library)

Use references as early design aids, not last-resort repair manuals.

Before designing or coding, scan the user request for domain patterns:

| If the request mentions... | Read before design | Use it to choose... |
| --- | --- | --- |
| SQL, NL2SQL, database Q&A, table, column, schema, analytics, dashboard data, log audit, compliance/audit report, scheduled data report | `references/nl2sql.md` | tool-based exploration vs. process-based workflow, schema discovery, SQL validation, execution/report gates |

If no pattern matches, stay in this file and load references only when a concrete missing detail blocks progress.

## 0.2) Agent Construction Mental Model

A good AgentClaw workflow is not just code that runs; it is a small evidence pipeline that turns user intent into safe action.

Design the workflow in layers:

1. **Input contract**: define what the user supplies and what output they expect.
2. **Evidence/discovery**: gather facts the agent should not guess: files, schemas, APIs, current state, configs, and user rules.
3. **Reasoning/generation**: use `LLMNode` for interpretation, synthesis, SQL/code/report drafting, natural-language explanation, and ambiguous mapping.
4. **Validation/gating**: use deterministic checks before execution, mutation, file writing, scheduling, or final claims.
5. **Action/output**: execute only validated actions; write files or call APIs in small deterministic nodes.
6. **Final response**: tell the user what happened, what was verified, and what remains blocked.

Prefer this split:
- deterministic nodes collect, normalize, compute, validate, persist, and call APIs;
- `LLMNode` handles judgment, language, synthesis, uncertainty, and human-facing narrative;
- use `agent_style="agentic"` when the workflow benefits from flexible tool-driven exploration.

## 1) Scope

This skill covers:
- agent/workflow inspection and iteration
- prompt and persona updates
- node prompt, routing, tool/skill configuration changes
- workflow design
- workflow file edits
- bootstrap wiring
- registration and runtime validation
- runtime behavior fixes

Low-level edit mechanics belong to `coding_skill`.
For coding tool usage (`search_code`, `read_code`, `syntax_check`, `replace_in_file`, `update_code`, `write_file`, etc.), **always consult `coding_skill` first**:
- `read_skill_file(skill_name="coding_skill")` — tool contracts, edit strategies, validation standards

### 1.1 Design the Evidence Flow

Before designing or coding any workflow, identify the facts the agent needs in order to act safely and accurately.

Use this as a construction habit for all task types, not only database tasks:

1. Separate **known inputs** from **facts that must be discovered at runtime**.
2. When the agent depends on external facts (schemas, APIs, files, project structure, business rules, credentials, current state, or third-party contracts), design an explicit discovery step or ask the user for the source.
3. Treat unknown domain facts as part of the workflow design, not as blanks to fill from model memory.
4. For tasks where wrong facts can produce invalid output, place a validation gate before execution or final reporting.
5. Prefer a slightly longer evidence-backed workflow over a short workflow that can only succeed by guessing.

Common evidence gates:
- Code/project agents: inspect files and verified APIs before editing.
- API agents: inspect OpenAPI/docs/sample responses before calling or generating clients.
- Data agents: inspect schema/data contracts before generating queries or reports.
- Automation agents: inspect current state before changing resources.

## 2) Minimal Build Loop (Default)

1. Inspect existing workflow files and bootstrap entry (`server.py`, `workflows/*`, `agent.py`).
2. Align path bases from runtime context (`cwd`, `project_dir`, `skill_tools_working_dir`, `coding_tools_project_dir`).
3. Identify task-specific evidence requirements:
   - What facts must be known before the agent can act?
   - Can the workflow discover those facts at runtime?
   - What validation gate prevents fabricated or stale facts from reaching execution?
4. Verify local API facts before coding:
   - `agentclaw/__init__.py`
   - `agentclaw/node/__init__.py`
5. Implement with valid local APIs only; do not guess imports or symbols.
6. After each Python edit:
   - If you used `write_code`, syntax is already validated by the pre-write check. Call `syntax_check` separately only for files edited with `replace_in_file` or `update_code`.
   - `python -m py_compile ...` can be used for import-level validation. On Windows, `py -3 -m py_compile` is also acceptable.
7. **Pre-registration validation** (must pass before registration):
   - Verify the workflow file can be imported without errors:
     `shell(command="python -c \"import importlib.util; spec = importlib.util.spec_from_file_location('_check', '<file_path>'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\"")`
   - This catches missing dependencies, undefined variables, syntax errors, and invalid imports.
   - If import fails, fix the issue first: install packages via the shell tool, fix code, or add delayed imports, then re-validate.
   - Import validation must pass before registration.
8. Register workflow via HTTP API (hot-register):
   - `POST /_internal/admin/workflows/register-file` with `{"file_path": "workflows/my_workflow.py", "force_replace": true}`.
   - Use the local-only `internal_url` from the relay config as `{BASE_URL}`. The `/_internal/` relay auto-injects auth server-side, so no manual Bearer token or key is needed.
   - Hot-register executes `exec_module()` on the file, so any module-level import error will fail registration.
   - Verify registration by checking that `registered_workflow_ids` contains the expected workflow ID.
   - API details: `read_skill_file(skill_name="agentclaw_api", file_name="references/workflow_admin.md")`
9. Verify workflow discovery:
   - `GET /_internal/admin/workflows` returns `{"workflows": [...]}`.
   - Confirm the registered workflow ID appears in the list.
10. **After successful registration**, ensure bootstrap wiring:
   - Add `import workflows.my_workflow` in `server.py`, or import it via `workflows/__init__.py`, so the workflow loads after server restart.
   - Add this import only after registration succeeds. Registration is the primary mechanism; the bootstrap import is for persistence across restarts.
11. Validate runtime using **streaming mode** to avoid timeouts:
   - `shell(command="curl -s -N -X POST {BASE_URL}/_internal/api/workflow/run -H 'Content-Type: application/json' -d '{\"workflow_id\": \"my_workflow\", \"inputs\": {...}, \"response_mode\": \"streaming\"}'", timeout=300)`
   - Streaming mode returns SSE events line by line. `event: workflow_finished` indicates success; `event: error` indicates failure.
   - For simple workflows, blocking mode is acceptable: use `response_mode: "blocking"` with `timeout=300` in the shell tool.
   - API details: `read_skill_file(skill_name="agentclaw_api", file_name="references/workflow.md")`
12. Report results with evidence.

### 2.1 Simple Workflow Default

For simple workflows (single-node or short linear flows), default to:

1. `agent_style="default"`
2. `enable_builtin_tools=False`

Only enable `agentic` mode or broad builtin tools when the task needs multi-step tool orchestration, such as dynamic code execution, external API/browser operations, or complex planning.

### 2.1.1 Builtin Skills and Builtin Tools Tradeoff

Treat `enable_builtin_skills` and `enable_builtin_tools` as capability switches, not defaults for every workflow.

#### `enable_builtin_skills=True`

What it provides:
- Injects built-in skill guidance such as `agent_creator`, `coding_skill`, and API usage playbooks when relevant.
- Helps the model follow project conventions, validated workflow patterns, tool contracts, and registration/validation gates.
- Useful when the agent itself needs to create, inspect, modify, debug, or validate AgentClaw project artifacts.

Costs:
- Adds skill descriptions and protocols to the prompt, increasing token usage.
- Can make simple agents more verbose or over-cautious if the task does not need project-building guidance.
- Skill quality and relevance matter; irrelevant skills can distract the agent.

Use when:
- The workflow is a builder, developer assistant, code assistant, workflow maintainer, prompt/config editor, or debugging agent.
- The agent should know AgentClaw conventions, project APIs, validation gates, or reusable construction patterns.
- The task benefits from reading task-specific playbooks before acting.

Avoid or keep off when:
- The workflow is a simple fixed-purpose Q&A, classifier, summarizer, extractor, or report formatter.
- The agent does not need to inspect or modify project structure, workflows, prompts, tools, or code.

#### `enable_builtin_tools=True`

What it provides:
- Exposes built-in tools for planning, file operations, code reading/editing, shell execution, and project interaction, depending on runtime configuration.
- Enables flexible agentic exploration and repair loops when combined with `agent_style="agentic"`.
- Lets the agent gather missing evidence from the real project/runtime instead of guessing.

Costs:
- Increases prompt size because tool schemas are included.
- Adds latency and token usage through multi-turn tool calls and tool results.
- Expands the action surface; risky tools may require confirmation and careful validation.
- Depends on tool descriptions and result quality. Poor tool results can mislead the agent.

Use when:
- The agent must inspect files, run commands, edit code, call APIs, operate the browser/computer, or interact with the project environment.
- The task is exploratory, open-ended, repair-oriented, or requires runtime evidence before acting.
- You are building an agentic developer/ops assistant rather than a deterministic business workflow.

Avoid or keep off when:
- The workflow has a known deterministic sequence and does not need runtime exploration.
- The agent should only transform provided input into output.
- Low latency, predictable cost, strict permissions, or small context size matters more than flexibility.

#### Recommended combinations

1. Simple LLM task:
   - `agent_style="default"`
   - `enable_builtin_skills=False`
   - `enable_builtin_tools=False`
2. Project-building or workflow-maintenance agent:
   - `agent_style="agentic"`
   - `enable_builtin_skills=True`
   - `enable_builtin_tools=True`
3. Domain agent with custom tools only:
   - `agent_style="agentic"` only if flexible tool choice is needed
   - `enable_builtin_skills=False`
   - `enable_builtin_tools=False`
   - pass explicit `tools=[...]` instead
4. Reliable scheduled/report workflow:
   - prefer deterministic custom nodes plus targeted `LLMNode` report generation
   - keep broad builtin tools off unless the workflow truly needs dynamic runtime exploration

### 2.1.2 Agentic Mode Tradeoff

Use `agent_style="agentic"` as a deliberate architecture choice, not as a default escape hatch.

Strengths:
- Flexible: the model can decide which tools to call and adapt to incomplete or changing information.
- Easy to implement: one small agentic node plus clear tool descriptions can replace a large hand-wired workflow.
- Strong capability: tool use plus iterative reasoning often works better than a rigid path for open-ended, exploratory, or messy tasks.

Costs:
- Tool-dependent: quality depends heavily on tool coverage, tool descriptions, and tool result shape.
- Slower: multi-turn model/tool loops add latency and can hit workflow timeouts.
- Higher token usage: tool definitions, tool results, intermediate turns, and repeated context all increase token consumption.

Prefer agentic mode when exploration and adaptability matter more than predictable latency and cost. Prefer a deterministic or gated process when the task has a known sequence, strict validation requirements, scheduled execution, or high-volume usage.

When using `agent_style="agentic"`, recommend setting the workflow execution timeout to `240` seconds unless the user asks for a different value. Agentic runs may include multiple model/tool turns, and `240s` is the preferred default balance for demos and normal tasks.

### 2.1.3 Domain Pattern Selection

Before coding, choose which pattern the task needs:

1. **Direct generation**: enough facts are already present in user input or state; a simple `LLMNode` is acceptable.
2. **Tool-driven exploration**: facts must be gathered dynamically with tools; use `agent_style="agentic"` with an explicit tool-use protocol.
3. **Gated process**: wrong facts can cause invalid actions; use deterministic discovery/validation nodes before generation or execution.

Favor gated processes for database agents, API mutation agents, infrastructure agents, filesystem mutation agents, scheduler agents, payment agents, permission agents, and report-generation agents.

For NL2SQL / SQL / database Q&A / analytics agents, read `references/nl2sql.md` before designing or coding so the workflow starts from schema evidence and SQL validation rather than a one-step SQL guess.

### 2.1.4 Data, Audit, and Report Agents

For log audit, data analysis, monitoring summary, scheduled report, compliance report, or incident report agents, keep a clear split between evidence collection and report authorship.

Target shape:

```text
discover_contract
  -> collect_data
  -> normalize_and_compute
  -> generate_report
  -> write_report?      if file output is required
  -> format_response
```

Construction guidance:
1. `discover_contract` is deterministic and inspects the real source contract: database schema, table columns, API response shape, log format, file headers, or user-provided spec.
2. `collect_data` queries only fields proven by `discover_contract`. If several timestamp/status/user fields are possible, discover the actual columns first and build the query from confirmed fields.
3. `normalize_and_compute` is a good place for counts, time windows, top-N lists, structured evidence, and explicit labels such as `keyword_match` or `rule_match`.
4. Let `LLMNode` produce the human-facing report from structured evidence. Reports, summaries, risk explanations, recommendations, and Markdown narratives belong in `generate_report` by default.
5. If a Markdown/file report is required, have `generate_report` produce `report_markdown`, then use a small deterministic `write_report` node to write that exact content to disk.
6. Category/risk rules are strongest when they come from the user, source metadata, or explicit configuration. If no rules are provided, surface uncertainty in the LLM report instead of presenting keyword matches as verified business conclusions.
7. A clean final file puts `workflow.publish()` last, after helper functions, custom nodes, edges/routers, and report-writing nodes are defined.

Common failure shapes to avoid:
- A single custom node that queries data, classifies risks, generates recommendations, writes Markdown, and returns success.
- Hardcoded candidate field lists without schema filtering.
- Pure keyword matching presented as an intelligent audit conclusion.
- Claiming report generation is validated when runtime failed, output directory is missing, schema discovery failed, or no report file was produced.

### 2.2 Tool Registration — Two Patterns

There are exactly **two** patterns for registering tools. Choose one per workflow:

**Pattern A: `@workflow.tool` (recommended for most cases)**

```python
workflow = Workflow(id="my_wf", name="My Workflow", ...)

@workflow.tool
def query_db(sql: str, limit: int = 100, **kwargs):
    """Execute SQL query.

    Args:
        sql: The SQL query string
        limit: Max rows to return
    """
    import psycopg2  # delayed import
    conn = psycopg2.connect(host=os.getenv("DB_HOST", "localhost"), ...)
    ...

workflow.add_node(LLMNode(id="agent", tools=["query_db"], ...))
workflow.publish()
```

**Pattern B: `ToolKit()` + `@toolkit.tool` (for shared/reusable toolkits)**

```python
toolkit = ToolKit()

@toolkit.tool
def query_db(sql: str, limit: int = 100, **kwargs):
    """Execute SQL query.

    Args:
        sql: The SQL query string
        limit: Max rows to return
    """
    import psycopg2  # delayed import
    conn = psycopg2.connect(host=os.getenv("DB_HOST", "localhost"), ...)
    ...

workflow = Workflow(id="my_wf", name="My Workflow", ...)
workflow.register_toolkit(toolkit)
workflow.add_node(LLMNode(id="agent", tools=["query_db"], ...))
workflow.publish()
```

**Rules**:
1. `@workflow.tool` — define Workflow first, then decorate functions. Tools auto-attach.
2. `ToolKit` pattern — define `toolkit = ToolKit()` first, decorate with `@toolkit.tool`, then call `workflow.register_toolkit(toolkit)` after creating the Workflow.
3. `register_toolkit()` accepts only a `ToolKit` instance. Passing a bare function raises `TypeError`.
4. The standalone `@tool` decorator (from `agentclaw import tool`) only marks a function — it requires `toolkit.register(fn)` to attach. Prefer `@toolkit.tool` or `@workflow.tool` instead.
5. Third-party imports used by tools must be **delayed** (inside function body), so the file can be loaded even if the dependency is not yet installed.
6. Tool documentation is auto-extracted from function signatures and Google-style docstrings.

workflow = Workflow(id="my_wf", name="My Workflow", ...)
workflow.register_toolkit(toolkit)
workflow.publish()
```

### 2.3 Inputs Schema Requirement

When defining `user_input` parameter, `inputs` schema is **mandatory**:

```python
workflow = Workflow(
    id="nl2sql",
    name="NL2SQL",
    user_input="user_query",  # parameter name
    inputs={"user_query": {"type": "string"}}  # schema definition (key must match user_input)
)
```

**Rules**:
1. `inputs` key must match `user_input` value
2. Type must be specified: `{"type": "string"}` or `str` (shorthand)
3. Missing `inputs` causes registration failure

**Shorthand**:
```python
inputs={"user_query": str}  # equivalent to {"type": "string"}
```

### 2.4 Node Selection

**LLMNode** - Primary node for LLM-based tasks:
- LLM reasoning and generation
- Tool calling with `agent_style="agentic"`
- Example: NL2SQL, code generation, Q&A
- When creating an `LLMNode`, do not specify `model_id` by default; let it inherit the workflow/system default model unless the user explicitly asks for a specific model.

**HumanNode** - Human approval or input gates

**CustomNode** - Custom logic and data transformation

### 2.5 Workflow Wiring Canonical Pattern

Use the repository-native wiring pattern:

1. `workflow = Workflow(id="...", name="...", ...)`
2. define nodes (`workflow.add_node(...)` or decorators)
3. connect start: `workflow.add_edge("__start__", "<first_node>")`
4. connect intermediate edges: `workflow.add_edge("a", "b")`
5. end edge is optional:
   - explicit: `workflow.add_edge("<last_node>", "__end__")`
   - implicit: no outgoing edge on last node also ends execution
6. publish: `workflow.publish()`

### 2.6 Package Installation

When a workflow depends on third-party packages (e.g. `psycopg2-binary`, `requests`, `pandas`):

1. **Always use the `shell` tool** to install packages. The shell tool automatically activates the project venv (injects `VIRTUAL_ENV` and venv `PATH`), so `pip install` runs inside the correct environment.
2. **Use the `shell` tool** for `pip install` — the shell tool handles venv activation automatically, avoiding PEP 668 environment errors.
3. Install **before** writing workflow code that imports the package.

**Example**:
```
shell(command="pip install psycopg2-binary")
```

**Rules**:
1. Install packages one at a time or as a single `pip install pkg1 pkg2` command via the shell tool
2. Verify installation success from the shell tool output before proceeding
3. Use `-binary` variants when available (e.g. `psycopg2-binary` instead of `psycopg2`) to avoid build dependencies
4. Third-party package imports should use delayed imports inside function bodies (see §2.2)

Use only verified AgentClaw APIs:

1. **Workflow construction**: `Workflow(id="...", name="...", inputs=..., user_input="...")`
2. **Node management**: `workflow.add_node(node_instance)`
3. **Edge connection**: `workflow.add_edge(from_node, to_node)`
4. **Routing**: `workflow.add_router(after="...", routes={...}, condition=...)`
5. **Publishing**: `workflow.publish()`
6. **Node classes**: `LLMNode`, `HumanNode`, `MCPNode`, `CustomNode`
7. **Decorators**: `@workflow.node(id)`, `@workflow.tool`

Before using any API, verify it exists in `agentclaw/__init__.py` or `agentclaw/node/__init__.py`.

## 3) API Fact Rule (No Fabricated Imports)

Before final write/register, confirm imports in local repo runtime:

1. Prefer root imports:
   - `from agentclaw import Workflow, LLMNode, ...`
2. If submodule imports are used, verify both module path and exported symbol.
3. If uncertain, use `search_code` / `read_code` first.

Always verify module paths in local repo runtime before use.

### 3.1) API Verification Checklist

Before generating workflow code, execute this verification sequence:

1. **Read API fact sources**:
   - `read_code(path="agentclaw/__init__.py")`
   - `read_code(path="agentclaw/node/__init__.py")`

2. **Verify each class**:
   - Use `search_code` to confirm class exists
   - Confirm import path is correct

3. **Verify each method**:
   - Confirm method signature and parameters
   - Only use verified methods

4. **Record verification**:
   - Before code generation, list all APIs to be used
   - Confirm each API is verified and exists

Only proceed with code generation after all APIs are verified.

## 4) Path Rule (No Hardcoded Paths)

1. Avoid hardcoded machine-specific absolute paths.
2. Resolve path errors using current runtime path bases first.
3. If `path_not_found` appears, fix path base mismatch before retrying downstream steps.

## 5) Edit Rule (Patch-First)

1. Existing file fix: patch local failing region first.
2. Full-file rewrite: only when local fixes repeatedly fail or structure is corrupted.
3. Syntax must pass before proceeding to register/runtime checks.
4. For an existing file, avoid repeated `write_file` loops; prefer `replace_in_file` / `update_code` for second and later edits in the same task.

## 6) Validation Gates

Execute gates in strict order. Each gate must pass before proceeding to the next.

### Gate 1: Syntax Validation
- **Tool**: `syntax_check(path=...)`
- **Pass criteria**: `ok=true`
- **On failure**:
  1. Read `error_code` and `candidate_fixes` from tool output
  2. Use `replace_in_file` or `update_code` for local fix
  3. Re-run `syntax_check`
  4. Must pass before proceeding to Gate 2

### Gate 2: Compilation Validation
- **Tool**: `python -m py_compile <file>`
- **Pass criteria**: exit code 0
- **On failure**:
  1. Analyze compilation error message
  2. Apply local fix
  3. Re-compile
  4. Must pass before proceeding to Gate 3

### Gate 3: Registration Validation
- **Tool call**: `python(file="scripts/register_workflow.py", skill_name="agent_creator", args=["<file_path>"])`
- **Path rule**: `skill_name="agent_creator"` tells the python tool to resolve `file` relative to the agent_creator skill directory. Always pass `skill_name`.
- **Pass criteria**: `register_ok=true` in JSON output
- **On failure**:
  1. Read `issues[].code` from output
  2. Fix each issue by priority
  3. Re-run script
  4. Must pass before proceeding to Gate 4

### Gate 4: Runtime Validation
- **Tool call**: `python(file="scripts/validate_workflow.py", skill_name="agent_creator", args=["<workflow_id>", "--inputs", "{...}"])`
- **Path rule**: same as Gate 3; always pass `skill_name="agent_creator"`.
- **Pass criteria**: `all_ok=true` in JSON output
- **On failure**:
  1. Check `register_ok`, `run_ok`, `api_ok` fields
  2. Locate failure step
  3. Fix and re-validate
  4. Must pass to report `completed`

### Gate Execution Rules
1. Execute gates in order (1 → 2 → 3 → 4)
2. Each gate must pass before advancing
3. All gates must pass to report `completed` status
4. Each gate must pass before advancing to the next

## 7) Structured Result Interpretation

For `register_workflow.py` and `validate_workflow.py` script output, read structured JSON fields first:

- registration: `register_ok`, `error_class`, `issues[].code`, `bootstrap_sync`
- runtime: `ok`, `all_ok`, `runtime_access_ok`, `register_ok`, `run_ok`, `api_ok`, `root_cause_hint`

Prefer structured fields over prose text when judging success.

## 8) Anti-Hardcoding

1. Read secrets/tokens/passwords from environment variables.
2. Prefer config/env values over in-source constants.
3. Avoid environment-specific install guidance by default.

## 9) Output Contract

Final report should include:

1. `changed_files`
2. `design_summary`
3. `validation` (`py_compile`, bootstrap, register, runtime)
4. `evidence` (tool outcome facts)
5. `status` (`completed` / `partial` / `blocked`)
6. `next_step`

### 9.1) Status Determination Rules

**completed** - Report only when ALL criteria met:
1. ✅ Gate 1 (syntax_check): `ok=true`
2. ✅ Gate 2 (py_compile): exit code 0
3. ✅ Gate 3 (register_workflow.py): `register_ok=true`
4. ✅ Gate 4 (validate_workflow.py): `all_ok=true`
5. ✅ All modified files listed
6. ✅ Validation evidence provided

**partial** - Report when:
1. Gates 1-2 pass but Gates 3-4 fail
2. Code generated but validation incomplete
3. Known issues exist but basic functionality works

**blocked** - Report when:
1. Gate 1 (syntax) fails repeatedly
2. Path issues cannot be resolved
3. API verification fails with no alternative
4. User input required to proceed

Report status accurately with supporting evidence.

## 10) On-Demand References

Read only the minimum required file:

- `references/nl2sql.md`: NL2SQL / SQL / database Q&A agent patterns, including tool-based and process-based designs
