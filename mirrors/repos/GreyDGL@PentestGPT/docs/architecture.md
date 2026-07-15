# PentestGPT architecture

Status: 2026-07-12

This is the internal source of truth for the current repository shape. The root `README.md` is the
public project page and is intentionally being revised separately.

## Repository family

```text
PentestGPT_Project/
├── PentestGPT/          # framework, legacy interactive client, and tool image
├── UnifedAgentWrapper/  # canonical unified-agent package
└── xbow-benchmark/      # reference-only benchmark harness and historical results
```

The three directories are independent Git repositories. The XBOW checkout is retained as a
reference corpus only; the product CLI, runtime, and CI do not depend on it. Benchmark logic and
result archives must not be added here.

## Maintained runtime

`pentestgpt_agent/` is the autonomous framework. It is a nested uv project with its own lockfile and
environment. The loop deliberately has only two LLM roles:

```text
RunSnapshot -> Supervisor -> compile_plan -> one TaskLease
                                             |
TraceStore <- EpisodeRunner <- Executor <----+
     |                              |
     +---- compile_execution -------+
                    |
               MemoryKernel
```

- The Supervisor chooses one task or proposes completion.
- The Executor performs one leased task and returns a typed result.
- Both roles use fresh provider sessions and `FULL_ACCESS`. The deployment environment is the
  isolation boundary; PentestGPT does not maintain a second tool or filesystem sandbox.
- Deterministic code owns scope validation, leases, evidence provenance, retries, revisions, and
  canonical state.
- SQLite is canonical memory. Provider transcripts are diagnostic traces, not memory.
- There is no always-on judge, RAG service, speculative backlog, or parallel scheduler.

`pentestgpt_legacy/` is the maintained human-driven implementation of the USENIX 2024 workflow. It
has its own lightweight provider clients and does not use `unified_agent`.

## Why unified-agent remains useful

The external `UnifedAgentWrapper` is a real seam with two production adapters: Claude Code and
Codex. PentestGPT depends on its small interface for:

- provider selection, model, effort, workspace, and permission configuration;
- structured-output invocation;
- normalized command, tool, file, session, usage, cost, and terminal events;
- shared task rendering and provider error handling.

Removing that module would duplicate provider SDK churn inside `pentestgpt_agent.trace` and
`pentestgpt_agent.trial`. It therefore earns its place as a deep module. PentestGPT policy must stay
outside it: task kinds, memory, evidence, scope, scheduling, and completion belong to this repo.

The dependency is pinned to a commit of the public package in `pentestgpt_agent/pyproject.toml`, and
`tests/test_dependency.py` verifies that the nested project imports the installed dependency rather
than the repository-root copy.

## Root unified_agent copy

The root `unified_agent/` is an older, drifted compatibility copy. No maintained PentestGPT runtime
imports it:

- `pentestgpt_agent` uses the external package;
- `pentestgpt_legacy` uses its own provider clients;
- only root packaging, its duplicate tests, and the current tool-image health check retain it.

Do not develop features in this copy. Removing it is desirable, but it is a separate public-package
cleanup because the root wheel currently exports the package and the Docker image copies it. That
cleanup must update the root package metadata, Docker health tests, lockfile, and public README in
one deliberate change.

## Deep modules

| Module | Interface | Hidden implementation |
|---|---|---|
| `PentestLoop` | `run(RunSpec) -> RunSnapshot` | recovery ordering, retries, episode identity, failure settlement |
| `MemoryKernel` | create/open/snapshot and atomic commits | SQLite schema, transactions, revisions, leases, dependency liveness |
| `compile_plan` | decision + snapshot -> valid plan | scope, dependency, phase, completion, and size validation |
| `compile_execution` | result + lease + trace -> valid execution | exact receipt matching, evidence fallback, identity, recovery rules |
| `EpisodeRunner` | one typed episode -> normalized result | provider invocation and durable append-only trace files |
| external `UnifiedAgent` | one task over Claude or Codex | SDK differences, native options, event normalization |

These interfaces are the preferred test surfaces. New provider behavior belongs behind
`UnifiedAgent`; new canonical-state behavior belongs behind the Memory Kernel or compilers.

## Memory and retrieval

Stored state is complete and retrieval is bounded. The Supervisor receives the open working set,
recent closed work, required basis/dependency context, selected observations, history counts, and
recent diagnostics. The Executor receives one task, explicit basis, same-task evidence, and a retry
diagnostic. A future retriever may select canonical IDs, but it must not replace SQLite or turn
summaries into evidence.

The current controller weakness is convergence, not database capacity: long runs can lose compact
coverage information and revisit completed surfaces. The next design slice should improve the
deterministic strategy projection and duplicate/branch policy before adding another agent or RAG.

## Runtime and benchmark ownership

- Local framework development runs from `pentestgpt_agent/`.
- The root Docker image supplies pentest tools, provider CLIs, legacy code, and persisted auth. It
  does not currently bake in the maintained framework.
- The sibling `xbow-benchmark` checkout is a historical/reference artifact, not a supported runtime
  or verification path. PentestGPT owns no XBOW runner.
- HTB execution happens only on the authorized remote attack box described in the parent project
  guide, never directly from the development Mac.

## Current design priorities

1. Preserve the two-role loop and deterministic memory authority.
2. Improve Supervisor coverage retrieval and convergence using saved-trace replay tests.
3. Keep both roles fully enabled inside a restricted deployment environment.
4. Remove the root `unified_agent` compatibility copy in a coordinated public-package cleanup.
5. Add a goal-specific verifier only when non-CTF completion semantics require it.
