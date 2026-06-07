---
name: structured-doc-validate
description: Validate canonical structured YAML artifacts for schema shape, reference integrity, evidence quality, coverage, and granularity. Read-only by default; no legacy prose docs.
---

# Structured Docs Validation

Goal: audit canonical structured YAML artifacts so agents can trust, repair, or safely avoid stale project context.

## Structured Artifact API Contract

Legacy prose artifacts are deprecated. Do not create, update, or rely on `docs/agent/*.md`, scoped prose docs, or generated human-readable Markdown views. Use structured YAML as the source of truth. Root `AGENTS.md` is only harness interoperability output from workflows that explicitly produce it.

Resolved structured docs root:

Treat `docs/agent/api` as a logical layout rooted at a resolved structured docs root, not a fixed repo path.

Resolution rules:
1. Resolve `workspace_root` with `git rev-parse --show-toplevel 2>/dev/null` or fallback to `pwd`.
2. Canonicalize `workspace_root` before fingerprinting when possible (`realpath`, `pwd -P`, `Path(...).resolve()`, or equivalent).
3. `structured-doc-validate` reads repo-local only when `<workspace_root>/docs/agent/api` already exists.
4. Otherwise read the global overlay root: `~/.pi/agent/workspaces/<workspace-fingerprint>/docs/agent/api`.
5. Compute `<workspace-fingerprint>` exactly from canonical `workspace_root`: strip one leading slash/backslash, replace every slash, backslash, and colon with `-`, then wrap with `--`.
6. Example: `/data/data/com.termux/files/home/CodeProjects/pi-mono` -> `--data-data-com.termux-files-home-CodeProjects-pi-mono--`.
7. Do not create new repo-local structured docs in unadopted repos unless the user explicitly asks for repo-local adoption there.

Logical structured layout under the resolved docs root:

```text
repo/
  scopes.yaml
  repo-inventory.yaml
  project-intent.yaml
  architecture.yaml
  data-flow.yaml
  data-model.yaml
  invariants.yaml
  dependency-rules.yaml
  design-issues.yaml
  risk-register.yaml
  change-guide.yaml
  testing-strategy.yaml
  validation-baseline.yaml
  contracts.yaml
  adr.yaml
  agent-operating-guide.yaml
scopes/
  by-path/<repo-relative-path>/...
  by-domain/<slug>/...
```

Every structured artifact should conform to `../_shared/references/schemas/common.schema.json` plus its artifact-specific schema. Stable IDs include `scope:*`, `component:*`, `entity:*`, `invariant:*`, `risk:*`, `contract:*`, `flow:*`, `command:*`, `issue:*`, `adr:*`, and `testplan:*`.

## Runtime Schema Loading

When validating structured artifacts, read `../_shared/references/artifact-api.md` first. Then read only the shared skill package schemas needed for artifacts being validated:
- `../_shared/references/schemas/common.schema.json`
- `../_shared/references/schemas/<artifact-file-base>.schema.json`

Do not read all schemas unless the validation target is the whole docs root. Do not use templates. Schemas are runtime API contracts; project docs outside the shared runtime refs are maintainer aids unless the user asks about this package itself.

## Invocation

Use this skill directly or use `/validate-structured-docs` as the prompt-template shortcut.

Supported tasks:
- Validate structured docs for this repo/docs root.
- Audit docs after this diff.
- Check whether docs are granular enough for agent workflows.
- Find stale evidence or invalid refs.
- Report documentation quality without editing artifacts.

## Rules

- Read-only by default. Do not edit code or artifacts unless the user explicitly asks for repair.
- Do not read legacy prose Markdown docs.
- Resolve `<docs-root>` exactly before reading artifacts.
- If a focus is provided, read `<docs-root>/repo/scopes.yaml` first when present and select matching scope artifacts by longest path prefix or explicit domain match.
- If no focus is provided, validate repo-level artifacts first, then scoped artifacts as context budget allows.
- Prefer exact, evidence-backed findings over broad opinions.
- Broken schemas, missing shared schema coverage for canonical artifact files, parse failures, and dangling refs are errors. Fuzzy evidence, coverage, and granularity concerns are warnings unless they block safe use.
- If structured artifacts predate newer schema requirements, missing now-required fields are schema errors, not compatibility notes.
- Every finding must include artifact path, record ID when available, severity, evidence, impact, and recommended next step.
- If a validation command exists in `validation-baseline.yaml`, prefer running or recommending that command; otherwise validate by inspection and targeted shell checks.

## Four-Layer Validation Workflow

### 1. Schema validity

Check:
- YAML parses cleanly.
- Every canonical artifact file being validated has matching shared schema coverage.
- Common envelope fields exist and are consistently shaped.
- Artifact-specific top-level keys match the matching schema.
- Required arrays/items are present, including newer required fields introduced by schema evolution.
- Stable IDs use expected prefixes for artifact family.
- Status, severity, confidence, and other constrained values match schemas.
- Required refs/evidence fields are present where schemas or workflow rules require them.

Use best-effort schema validation by inspection when no validator command exists. When a JSON Schema validator is available, run it against only relevant files and include command/results.

### 2. Reference integrity

Build or inspect a canonical ID registry from artifacts read. Check:
- Every `*_ref`, `*_refs`, `depends_on`, `evidence_refs`, scope ref, contract ref, invariant ref, risk ref, issue ref, ADR ref, and artifact ref points to a known canonical ID or is explicitly external/unknown.
- Cross-scope refs have owner/consumer relationship support in `scopes.yaml` and, when API-like, `contracts.yaml`.
- Router/checklist artifacts reference owner facts instead of duplicating them.
- No record points to deleted, malformed, duplicate, or contradictory owner records.

Prefer compact missing-owner recommendations over leaving ambiguous dangling refs.

### 3. Evidence validity

For evidence-bearing records, check:
- Referenced source paths exist under repo root when repo-aware validation is possible.
- Line ranges exist and are ordered when present.
- Referenced symbols/text are plausibly present near claimed paths or ranges.
- Evidence belongs to claimed scope and owner artifact.
- Observed records have evidence; planned records use explicit planned/low-confidence markers.
- `current`/high-confidence claims are not supported only by stale, missing, or unrelated evidence.

Do not claim semantic proof. Report stale/missing evidence as actionable quality risk.

### 4. Coverage and granularity

Check:
- Changed files or high-value source areas have relevant scope or owner-artifact representation.
- Scope routing covers important paths without excessive overlap.
- Components/entities/contracts/risks are neither too broad to guide changes nor so tiny they fragment ownership.
- Repeated facts are owned once and referenced elsewhere.
- Validation/testing artifacts cover commands and risks important to the requested change.

Granularity is heuristic. Use warnings with concrete split/merge suggestions, not automatic failure, unless the docs cannot guide safe work.

## Diff-Aware Mode

When user asks to validate after a diff:
1. Inspect changed files with `git diff --name-only` or user-specified base.
2. Match changed paths to scopes from `repo/scopes.yaml` when present.
3. Read only relevant owner artifacts plus directly referenced artifacts.
4. Prioritize evidence paths, owner refs, contracts, invariants, risks, tests, and validation baseline entries touched by the diff.
5. Report undocumented changed files or stale evidence first.

## Output Format

Use concise human output. Include machine-shaped summary when useful:

```yaml
verdict: pass | pass_with_warnings | fail | blocked
schema:
  status: pass | mixed | fail | blocked
  findings: []
refs:
  status: pass | mixed | fail | blocked
  findings: []
evidence:
  status: pass | mixed | fail | blocked
  findings: []
coverage:
  status: pass | mixed | fail | blocked
  findings: []
granularity:
  status: pass | mixed | fail | blocked
  findings: []
recommendations: []
```

Finding shape:

```yaml
severity: error | warning | info
artifact_path: <path>
record_id: <id-or-null>
layer: schema | refs | evidence | coverage | granularity
problem: <concise problem>
evidence: <file/path/command observation>
impact: <why it matters for agent workflows>
recommended_next_step: <specific repair or follow-up>
```

## Verdict Rules

- `fail`: parse/schema errors, missing shared schema coverage for canonical artifacts, missing now-required fields, dangling required refs, missing required owner artifacts for selected scope, or missing evidence that makes current/high-confidence records unsafe.
- `pass_with_warnings`: schema/required refs are usable, but evidence, coverage, or granularity issues need follow-up.
- `pass`: no material issues found within inspected scope.
- `blocked`: docs root, required files, repo root, schemas, or commands cannot be accessed enough to validate.

## Follow-Up Routing

- For broken artifact shape or invalid refs: recommend `safe-change` structured-docs-only repair or `codebase-recon` consolidation.
- For missing scope coverage: recommend `codebase-recon` on the relevant path/domain focus.
- For stale source evidence after code changes: recommend `safe-change` docs update for affected owner artifacts.
- For architecture/code concerns discovered while validating docs: recommend `arch-code-review`; do not turn validation output into code review findings unless requested.

## Stop Conditions

Stop once the requested focus is validated enough to give a verdict and actionable findings. Do not exhaustively read a large repo when targeted evidence already proves the result.
