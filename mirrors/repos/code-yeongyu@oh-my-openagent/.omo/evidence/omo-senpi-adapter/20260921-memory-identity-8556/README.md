# Live QA — memory identity follows the session's workspace (#8556)

Date: 2026-09-21 · Branch: `fix/8556-memory-identity-session-workspace` · Driver: `probe.mjs` (this directory)

## What was tested

A session is bound under workspace A, then the same session file is re-opened by a process whose
working directory is `apps/server` (workspace B) — the shape of the reported incident, where a
shared host generation was ensured from the desktop server's directory and every session it picked
up resolved `server-<hash>`.

`probe.mjs` drives the REAL `senpi` binary twice against a built plugin bundle:

1. `senpi -p --mode json` from workspace A, scripted mock provider, one `memory create` call.
2. `senpi -p --mode json --session <that session file>` from workspace B, another `memory create`.

`--plugin-root` selects the bundle, so the same probe runs as the RED control against the bundle on
`origin/dev`:

```bash
bun .omo/evidence/omo-senpi-adapter/20260921-memory-identity-8556/probe.mjs --label fixed
bun .omo/evidence/omo-senpi-adapter/20260921-memory-identity-8556/probe.mjs --label base --plugin-root <copy of the plugin with origin/dev's extensions/omo.js>
```

Isolation: the sandbox owns `SENPI_CODING_AGENT_DIR`, `XDG_*`, and `OMO_MEMORY_HOME` under one
`mktemp` root (`createSandbox` from `packages/omo-senpi/scripts/qa/drive.mjs`); no run touches the
real agent directory, the real memory home, or any shared socket.

## What was observed

`probe-base.json` (bundle from `origin/dev`) — VERDICT FAIL:

```
PASS run A bound identity A :: status=0 served=project-d7fe390e
PASS reattach from workspace B exits clean :: status=0
PASS no memory identity conflict after reattach :: absent
FAIL reattached system prompt carries identity A :: sentinel=false
FAIL memory tool after reattach answers with identity A :: served=undefined subject=undefined
PASS identity B never served :: identityB=server-114623f1
```

`probe-fixed.json` (this branch's bundle) — VERDICT PASS:

```
PASS run A bound identity A :: status=0 served=project-98a78d34
PASS reattach from workspace B exits clean :: status=0
PASS no memory identity conflict after reattach :: absent
PASS reattached system prompt carries identity A :: sentinel=true
PASS memory tool after reattach answers with identity A :: served=project-98a78d34 subject=probe write after reattach from workspace B
PASS identity B never served :: identityB=server-38250d18
```

The identity the memory tool served is read from its own write notice, because a headless `-p`
session routes storage to a transient run root (#7765) rather than to `agents/<id>` directly.

The conflict-text check is informational here: `--mode json` has no notification surface, so the
error text never reaches stdout. On the base bundle the conflict shows up as its actual consequence
— after the reattach the session carries no memory block and the memory tool serves nothing. On this
branch the same reattach keeps identity A and the tool writes into it.

## Why it is enough

The two runs reproduce the reported sequence at the real harness: bind under one workspace, reattach
from another, and ask the memory tool who it is. The base bundle loses memory at that point; the
built bundle on this branch keeps identity A and commits into it. The unit side covers what a live
`-p` probe cannot reach on its own — a shared host serving a session whose cwd differs from the host
process cwd — in `packages/omo-senpi/src/components/memory/identity-rebind.test.ts`.

## What was omitted

Nothing secret-bearing is stored here: the logs are mock-provider JSONL from a sandbox with a dummy
`omo-mock` API key. Sandbox roots live under the system temp directory and were removed after the
run, so the paths inside the JSON reports no longer exist.
