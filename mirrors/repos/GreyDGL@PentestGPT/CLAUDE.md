# Claude guide

Internal instructions for Claude Code in this repository. Read
[`docs/architecture.md`](docs/architecture.md) before architecture work. The root `README.md` is the
public project page and must not be edited unless the user explicitly requests that separate review.

## Active project map

- `pentestgpt_agent/` — maintained autonomous Supervisor/Executor framework; nested uv project.
- `pentestgpt_legacy/` — maintained human-driven USEN-2024-style client.
- `../UnifedAgentWrapper/` — canonical `unified-agent` package used by the framework.
- `../xbow-benchmark/` — reference-only benchmark harness and historical results; it is not a
  supported `pentestgpt-agent` CLI, CI, or runtime integration.
- `unified_agent/` — obsolete compatibility copy retained by root packaging/Docker only. Do not add
  features here or confuse it with the framework dependency.

The old fixed-stage `pentestgpt/` package and the previous ledger-centered
Instructor/Executor/Judge implementation are gone. Historical reports may still name them.

## Runtime contract

- The Supervisor and Executor both use `SandboxPolicy.FULL_ACCESS`; deployment isolation is the
  security boundary.
- Each episode is fresh. SQLite and exact trace receipts—not provider conversation history—are
  memory.
- Deterministic code owns scope, plan validation, leases, evidence, retries, completion bases, and
  revisions.
- Provider action and file activity is logged but is not an audit failure.
- Keep the core at two LLM roles. Do not add an always-on judge, RAG layer, or scheduler without
  trace evidence that the current deterministic seam cannot solve the problem.

## Commands

Framework work runs inside the nested project:

```bash
cd pentestgpt_agent
uv sync --extra claude          # or codex / all
uv run python -m pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv lock --check
uv build
```

From the repository root:

```bash
make run TARGET=http://127.0.0.1:8000 BACKEND=claude
make check
make ci
make docker-build
make docker-login
make docker-auth-status
```

The root Docker image does not currently contain `pentestgpt_agent`; treat `make docker-run` as
pending runtime wiring. The sibling XBOW checkout is retained only as a reference and is not a
product verification path.

## Documentation map

- `docs/architecture.md` — current repository and module decisions.
- `pentestgpt_agent/CONTEXT.md` — domain language and invariants.
- `pentestgpt_agent/README.md` — framework development and operation.
- `docs/docker-dev-plan.md` — current Docker/auth status and known gap.
- `PENTESTGPT_AGENT_NEW_*` — compact historical migration/qualification records.
- `pentestgpt_agent/HTB_ENIGMA_QUALIFICATION_20260712.md` — failed remote qualification evidence.

## Editing rules

- Preserve unrelated and concurrent worktree changes. Never restore or modify files merely because
  they appear as changes you did not create.
- Do not edit the root public `README.md` during internal documentation cleanup.
- Do not put benchmark runners or generated result archives back into this repository.
- Keep application imports as `unified_agent`; change dependency source configuration rather than
  copying the wrapper into `pentestgpt_agent`.
- Add focused replay or interface-level tests for behavior changes before live runs.
- Never expose provider credentials, VPN files, HTB tokens, flags, or raw sensitive traces.
