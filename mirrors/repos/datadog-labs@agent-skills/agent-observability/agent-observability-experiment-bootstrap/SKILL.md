---
name: agent-observability-experiment-bootstrap
description: Bootstrap a reproducible LLM Observability experiment through the Python ddtrace SDK or the Node dd-trace SDK. Use for experiment, dataset, evaluator, benchmark, regression, or LLM-as-a-judge scaffolding. The legacy Python invocation remains supported.
---

# LLM Observability Experiment Bootstrap

Generate one reproducible experiment artifact. The artifact evaluates a task over a versioned dataset, records outputs and evaluator metrics, carries configuration and provenance, and prints a result link or identifiers when possible.

This skill is adapter-independent. Each adapter owns a language-specific directory under `references/`; load only the selected adapter contract. The directories are intentionally symmetric even when one adapter currently has fewer supporting references.

## Invocation and compatibility

The installed directory and legacy invocation remain valid:

```text
/agent-observability-experiment-bootstrap [--purpose TEXT] [--format py|ipynb|mjs]
  [--dataset PATH | --dataset-name NAME] [--dataset-version N]
  [--project-name NAME] [--evaluator-style function|class|remote]
  [--jobs N] [--output PATH] [--task-source module:function]
  [--placeholder-task] [--app-root PATH] [--env-file PATH]
```

General options:

```text
--adapter python|node             # default: python
--format py|ipynb|mjs             # Python: py/ipynb; Node: mjs
--site SITE                      # otherwise DD_SITE or datadoghq.com
```

Do not prompt for optional defaults. Resolve a non-empty purpose from `--purpose`, the request, or a focused question. Keep the purpose as reasoning context, not a fixed taxonomy.

## Mandatory context loading

Load context in this order:

1. Parse the adapter.
2. Read exactly one adapter reference:
   - Python SDK → `references/python/python.md`
   - Node SDK → `references/node/nodejs.md`
3. For Python task generation, read only the selected provider reference under `references/python/providers/`.
4. For Python task generation, read only the selected evaluator reference under `references/python/evaluator-styles/`.

Do not load all provider, evaluator, Python, and Node references “for completeness.” The selected reference is the source of truth for syntax and API behavior.

## Adapter selection

Use Python when the application or requested artifact is Python, or when no adapter is specified. Use Node when the application is JavaScript/TypeScript and the local `dd-trace` package exposes `tracer.llmobs.experiments`.

Never mix the Python and Node SDKs in one generated artifact. Do not use private SDK modules or invent a missing symbol. If local source and an installed package disagree, report the discrepancy and generate against the selected version.

## Shared experiment model

Every adapter must represent the following concepts:

1. **Project** — resolve an explicit project name, configured service metadata, or a clearly documented generated fallback. Never silently use an unrelated project.
2. **Dataset** — records with input, optional expected output, optional metadata, and tags. Pin a remote dataset version when supplied.
3. **Task** — a deterministic adapter from record input to the application under test. Keep evaluation logic outside the task.
4. **Evaluators** — named row-level or summary-level metrics. Use deterministic checks for contracts and judges only where semantic evaluation is needed.
5. **Run state** — preserve task errors, evaluator errors, completion state, result rows, and partial failures separately.
6. **Provenance** — include purpose, adapter, skill name/version, project, dataset identity/version, task source, evaluator labels/rubrics, model/configuration, Git revision, and generation timestamp.

`expected_output` is optional and must not be synthesized from an observed production output without explicit validation. Distinguish a missing value from an intentionally empty object. Dataset tags must use the backend’s validated `key:value` form where the selected reference requires it.

## Generation workflow

### 1. Resolve purpose and project

Derive the purpose and project without guessing across product boundaries. A project is not automatically the same as an `ml_app`, service, dataset, or repository name. Record how each value was resolved.

### 2. Resolve the dataset

Support:

- inline records;
- local JSON or CSV;
- a named remote dataset and optional version; and
- an explicitly approved trace/annotation export.

For local JSON, require a top-level array, validate the selected adapter’s record shape, scrub obvious PII and credential-like values, and report affected record indices. Do not invent canonical or remote record IDs.

For CSV, preserve the runtime path and document the dependency. Use the Python CSV column contract from `references/python/python.md`; Node generation must not pretend that a Python-only CSV helper exists.

### 3. Resolve the task

Use `--task-source` when provided. Otherwise use the selected language’s bounded application discovery rules:

- Python: inspect the resolved app root and rank real callable candidates.
- Node: prefer an explicit import/module function and emit a clearly marked placeholder when absent.

Never claim that an invented import is wired. Preserve side-effect warnings for network, database, filesystem, environment, or tool calls.

### 4. Select evaluators

Select two or three evaluators based on purpose and available signals. Keep labels unique and stable.

- Accuracy: exact/near match plus a richer rule or judge when needed.
- Tool use: inspect structured tool calls; state the limitation when the task does not expose them.
- Structured output: parse and validate the schema.
- Retrieval: evaluate groundedness only when retrieved context is available.
- Regression: prefer deterministic checks and explicit thresholds.
- Exploration: include diagnostics or taxonomy metrics, not only a pass/fail score.

Evaluator failures must not become passing values. Summary evaluators must remain distinct from row evaluators.

### 5. Emit the artifact

Use the selected adapter reference for the exact generated code. Include:

- purpose and project resolution;
- dataset source and version;
- real task source or a prominent placeholder warning;
- evaluator labels and rubrics;
- configuration and provenance;
- credential instructions without literal secrets; and
- a result URL/ID placeholder and next steps.

Preserve the historical Python section ordering and evaluator/provider reference behavior when using the Python adapter.

### 6. Validate locally

Before presenting the artifact:

- Python `.py`: `python -m py_compile <path>`.
- Python `.ipynb`: parse JSON and require code/markdown cells.
- Node `.mjs`: `node --check <path>`.

For every adapter, check for private imports, literal credentials, malformed tags, missing provenance, mismatched dataset versions, fabricated IDs, and task/evaluator errors that were collapsed into false or pass.

### 7. Report completion

Use this compact structure:

```text
Generated LLM Observability experiment: <adapter>/<format>
Path: <path>
Purpose: "<purpose>"
Project: <project>
Dataset: <local path | name>, version=<version or latest>
Task: <wired source | placeholder>
Evaluators: <labels>
Provenance: generated_by=claude-code, adapter=<adapter>, skill=agent-observability-experiment-bootstrap
Validation: <commands and pass/fail>
Result link: <URL or pending until run>

Next steps:
1. Verify the task source and evaluator semantics.
2. Set the credentials required by the selected SDK.
3. Install the selected SDK and run the generated artifact.
4. Review per-row errors before treating metrics as a successful run.
```

## Safety and uncertainty

- Do not modify application source code unless explicitly asked.
- Do not write credentials into generated files or artifacts.
- Do not publish prompts, outputs, traces, datasets, or evaluations without explicit user approval.
- Do not use production data as ground truth without labeling and validation.
- Do not retry non-idempotent writes automatically unless the selected SDK explicitly supports it.
- On partial publication, preserve IDs and failed rows and provide a reconciliation path.

## Reference maintenance

Each adapter reference must identify the public source links and branch used to verify it. Re-check the reference when the SDK version changes. The Python reference uses the public `dd-trace-py` `main` branch; the Node reference uses the public `dd-trace-js` `master` branch.

Keep shared workflow guidance here and language-specific syntax in the references. If a detail is only true for one SDK, do not duplicate it in this file.

## Existing references

- `references/python/` — Python `ddtrace.llmobs` API, providers, evaluator styles, environment template, and legacy compatibility.
- `references/node/` — Node `tracer.llmobs.experiments` API and future Node-specific references.


Do not modify `dd-trace-py` or `dd-trace-js` while updating this skill.
