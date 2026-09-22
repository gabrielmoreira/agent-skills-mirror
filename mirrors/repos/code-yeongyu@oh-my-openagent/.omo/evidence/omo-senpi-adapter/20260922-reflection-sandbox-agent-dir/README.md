# Reflection sandbox uses the engine's agent directory (omo#8595)

Branch `fix/reflection-sandbox-agent-dir-8595`, base `dev` @ `8e411f323`. Evidence directory resolved with
`.agents/skills/senpi-qa/scripts/resolve-evidence-dir.mjs --slug 20260922-reflection-sandbox-agent-dir`.

## What was tested

| Surface | Command | Proves |
|---|---|---|
| Failing-first unit proof | `bun test packages/omo-senpi/src/components/memory/{identity-runtime,wiring-runtime}.test.ts` | the child's agent dir was neither propagated from the engine nor pinned into the child environment (`RED-agent-dir-propagation.txt`), and a stale event context threw straight into the launch path (`RED-stale-context.txt`) |
| Same tests after the change | same command | grant and pin name one directory, an inherited value loses, and a disposed context falls back (`GREEN-agent-dir-propagation.txt`) |
| Package suite | `bun test packages/omo-senpi` | no adjacent regression (`package-suite.txt`) |
| Typecheck | `bunx tsgo --noEmit -p packages/omo-senpi/tsconfig.json` | exit 0 |
| **Real seatbelt surface** | `bun .omo/evidence/omo-senpi-adapter/20260922-reflection-sandbox-agent-dir/sandbox-auth-probe.mjs` | the production wiring renders the sandbox, `/usr/bin/sandbox-exec` runs the child for real, and the child performs the exact `mkdir <auth.json>.lock` the credential store performs (`live-sandbox-auth-probe.json`) |
| Live adapter driver | `SENPI_BIN="$(command -v senpi)" node packages/omo-senpi/scripts/qa/drive.mjs` | a real senpi session loads the plugin with an isolated agent dir (`qa-drive-live.json`); harness precondition in `qa-drive-self-test.txt` |
| Plugin bundle freshness | `node packages/omo-senpi/plugin/scripts/build-extension.mjs [--check]` inside `node:24-bookworm` + bun 1.4.2 | the committed bundle matches a CI-toolchain rebuild (`bundle-regen-linux.log`) |

## What was observed

**Failing first.** Four assertions failed on `dev` for the intended reason: `childEnv.OMO_CODING_AGENT_DIR`
was `undefined`; an inherited stale directory survived into the child; `resolveAgentDir` never reached the
identity runtime, with or without `agentDir` on the context. A fifth failure followed from the host's getter
contract - `agentDir` throws once its runner is stale - and escaped into the launch path until the read was
guarded. After the change: 10 passed, 0 failed in those two files; 3717 passed / 32 skipped / 0 failed for
the package; typecheck exit 0.

**Real surface.** With the engine reporting agent dir `…/engine-agent-dir` and the parent leaking
`…/decoy-agent-dir` in all three agent-dir variables:

- the rendered child ran under `/usr/bin/sandbox-exec` (`sandboxed: true`),
- all three variables reached the child as the engine's directory (`pinsEngineDir: true`),
- the credential lock succeeded inside the granted directory (`PINNED_LOCK=ok`),
- the same lock was denied in the decoy directory (`DECOY_LOCK=denied`) - no second home is granted,
- the control run, identical except that the pin is stripped, reproduced the reported defect exactly:
  `PINNED_LOCK=denied`, which is the `EPERM ... auth.json.lock` in the issue.

**Live driver.** `result: PASS`, `ultraworkInjected: true`, `providedSenpiCodingAgentDir: IGNORED`, sandbox
agent dir under a per-run temp root. `realSenpiChangedPaths: []` and `realOmoChangedPaths: []` - no path in
either real home changed. `realSenpiUntouched` / `realOmoUntouched` report `false` because the certification
walk fails CLOSED when it cannot establish directory identity
(`certificationErrors: DIRECTORY_IDENTITY_UNAVAILABLE`), not because a change was seen; the changed-path
lists are the positive evidence and they are empty.

**Bundle.** `omo.js` is the only regenerated artifact that changed (marker line plus the inlined change);
`omo-task.js`, `omo-member.js`, `memory-run-supervisor.mjs`, `omo-init-deep-advisor.js` and
`runtime/agent-toolkit-sdk/sdk.js` came back byte-identical. Both `--check`s passed inside the container
(`EXT_CHECK_OK`, `INSTALL_CHECK_OK`).

## Why it is enough

The defect is a path mismatch that only becomes visible when a sandboxed child performs a write the profile
does not allow. The probe exercises exactly that write, through the production wiring, under the real
kernel-enforced profile, and its control shows the pre-fix outcome on the same machine in the same run - so
the evidence covers both directions instead of asserting the fixed one. The unit tests pin the contract that
produced it (grant equals pin, inherited values lose, a disposed context degrades instead of throwing), and
the package suite plus typecheck cover the blast radius inside the adapter.

Residual risk: Linux hosts render `--bind` instead of a seatbelt profile, and the probe's live half only ran
on darwin; the rendered-args assertions in `identity-runtime.test.ts` cover the bwrap branch and CI runs the
package suite on ubuntu. A brand whose env prefix is neither `OMO`, `SENPI` nor `PI` and that also inherits
its own agent-dir variable would still win over the pin - out of scope here, and impossible for this
distribution.

## What was omitted

No end-to-end model-backed reflection run: it needs live provider credentials, and its failing step is the
credential lock the probe already drives directly. No token, credential, environment dump, host name or
absolute home path is recorded in this directory; the probe writes only into a per-run temp root.

## Cleanup receipt

- `sandbox-auth-probe.mjs` removes its own temp root at the end and reports `remains: false`
  (see the tail of `live-sandbox-auth-probe.json`).
- First probe iteration's leftover temp root removed by hand; re-listing the pattern returns
  `No such file or directory`.
- The live driver removed its own `omo-senpi-qa-*` sandbox; no process matching `[o]mo-senpi-qa` survives.
  Four older `omo-senpi-qa-*` roots from 23:45-23:50 predate this run and belong to another session, so they
  were left alone.
- The bundle rebuild ran in `docker run --rm`; no container or image state remains beyond the pulled
  `node:24-bookworm` base.
