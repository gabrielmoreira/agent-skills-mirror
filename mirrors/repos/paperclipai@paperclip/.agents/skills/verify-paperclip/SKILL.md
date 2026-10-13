---
name: verify-paperclip
description: Launch an isolated Paperclip instance, drive its real web UI or CLI using the existing feature-map recipes, capture evidence, and clean up owned processes. Use to verify user-facing Paperclip behavior.
---

# Verify Paperclip

Read the [map contract](../../../maps/README.md), then use the
[feature map](../../../maps/feature-map/README.md) to select user verification
recipes. For API/agent access, read the same-named
[agent access companion](../../../maps/agent-access-map/README.md) and use the
actual permitted agent identity, target and work mode. Follow existing API/runner/MCP
fixtures for access proof; a board request does not prove agent access. Report
recipe or access drift with evidence; map updates belong to
[maintain-verification-skill](../maintain-verification-skill/SKILL.md).
Read [development instructions](../../../doc/DEVELOPING.md) for current commands.

## Launch

Run from the repository root with Node 24.11+, Python 3, `lsof`, and dependencies
installed with `pnpm install --frozen-lockfile`. Browser driving uses the existing
`@playwright/test` dependency. If Chromium is unavailable, run
`node node_modules/@playwright/test/cli.js install chromium`, or select an installed
browser with `PAPERCLIP_PLAYWRIGHT_CHANNEL=chrome`.

Create separate, unique data and evidence directories. Keep the evidence outside
the data directory:

```sh
VERIFY_DATA_DIR=$(mktemp -d "${TMPDIR:-/tmp}/paperclip-verify-XXXXXX")
VERIFY_EVIDENCE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/paperclip-proof-XXXXXX")
python3 .agents/skills/verify-paperclip/scripts/launch.py \
  --data-dir "$VERIFY_DATA_DIR" --evidence-dir "$VERIFY_EVIDENCE_DIR"
```

Keep this command in a foreground terminal/session. The helper runs the supported
`onboard --yes --bind loopback --no-install-service --run` command, with isolated
embedded PostgreSQL, a free loopback port, no inherited instance routing or cwd
`.env`, and no automatic browser opening. It records `launch.json` in the evidence
directory. Source startup builds its required shared/plugin packages and migrates
the empty database; readiness can take longer on the first run.

This path starts an empty instance without model credentials. Create company and
agent state through the journey being checked. A UI check that stops before model
execution does not prove an agent run. For a preconfigured company/CEO and live
model work, use the documented [test-drive](../../../doc/DEVELOPING.md#one-command-isolated-manual-test-drive)
command with an authorized environment-backed credential and `--no-browser`.
Record its printed data directory, URL, runtime PID and commit before driving;
never use a fake credential to claim provider verification.

For Paperclip-managed reusable services, follow
[dev-workspace run/verify/fix](../paperclip-dev-workspace-run-verify-fix/SKILL.md)
instead of launching a second server. Its cloned-data/login requirements differ
from this empty local instance.

## Doctor

After startup, and again after any surprising behavior, run:

```sh
python3 .agents/skills/verify-paperclip/scripts/doctor.py \
  --evidence-dir "$VERIFY_EVIDENCE_DIR"
```

This read-only check compares the recorded launcher, runtime PID, port owner,
process cwd, configuration, served Git commit, health/bootstrap readiness, root
HTML response, and company-list access. It writes `doctor.json` or exits nonzero.
Do not trust a root 200 or CLI doctor output alone. The CLI doctor checks whether
the port is available before startup; it is not proof of a running server's
ownership. Browser readiness still requires the expected visible page. Reset or
relaunch a wedged browser even when the process health passes.

## Drive

Use accessible roles, labels, and placeholders from the latest page state.
Existing Playwright specs in `tests/e2e/` supply recipes and selectors; their
configured servers and fixtures are separate from this live instance. Run a named
suite through its own configuration only when that is the evidence needed.

The executable onboarding smoke drives `onboarding.md` / `web-wizard`: open
`/onboarding` in the disposable self-hosted instance,
enter a unique organization name, choose Continue, reach the agent-name field,
reopen `/<company-prefix>/onboarding`, reload, and corroborate the saved company
through read-only API checks:

```sh
node .agents/skills/verify-paperclip/scripts/onboarding-smoke.mjs \
  --evidence-dir "$VERIFY_EVIDENCE_DIR"
```

This covers company creation and setup resumption, with no mocked responses or
provider calls. Hiring, first task execution, and the alternate CLI entry remain
separate journeys. The script requires an empty instance and refuses a non-owned
or non-loopback target. For other features, reuse the owned URL and follow the
map's entry points. Company routes normally require the selected company's
`issuePrefix`, for example `/<PREFIX>/goals`; use current navigation rather than
guessing resource URLs. The unprefixed `/onboarding` route starts naming; use the
company-prefixed onboarding route to resume its agent setup. Check relevant
experimental gates and actor permissions.

For CLI checks, discover exact flags with
`node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts <command> --help`, then
select the disposable data directory/API/company explicitly. API reads can
corroborate UI writes; API-created state does not prove a creation UI.

## Evidence

Record feature file, sub-feature and entry-point ID, commit/dirty state, owned URL,
company/user, flags, runtime/harness, live versus simulated dependencies, command,
exit code, expected and observed behavior, and evidence links. Report each entry
as passed, failed, blocked with its prerequisite, or not run.

The smoke saves before/after/reload screenshots, visible-page text, a Playwright
trace, and `result.json` with company ID and API corroboration. On failure it
retains the trace, visible state, and failure result; rerun doctor before retrying.
Preserve launch output and relevant application logs without secrets. Reopen or
reload changed state and verify persistence/continuation, not just a success toast.
One passing sub-feature does not certify the entire feature family or other
surfaces. A full maintenance pass must exercise every mapped feature or report
incomplete coverage.

For Paperclip-assigned work, attach important proof through
[the artifact workflow](../../../doc/AGENT-ARTIFACTS.md). Keep runtime results in
the evidence directory or issue, not in the map; `coverage.json` describes
documentation coverage rather than live test health.

## Cleanup

Close the browser context you created (the smoke does this in `finally`). Stop the owned runtime with:

```sh
python3 .agents/skills/verify-paperclip/scripts/stop.py \
  --evidence-dir "$VERIFY_EVIDENCE_DIR"
```

The helper verifies the runtime's port, cwd, and launch ancestry before sending
SIGTERM to that PID, then waits for runtime exit and checks that its HTTP
listener and embedded database have stopped. Signaling the runtime PID lets the server drain before stopping
PostgreSQL; a terminal group interrupt can reach the database first. Do this after
failed drives as well as successful runs. If startup fails before a runtime record
exists, stop only the foreground session you created and inspect its recorded data
directory for residue. Never kill by process name or stop another checkout's server.

Verify the recorded HTTP port has no listener and the owned runtime PID has
exited. Embedded PostgreSQL should stop with the server; inspect only the recorded
data directory if shutdown is incomplete. Retain the data directory for diagnosis
until no owned process uses it; remove only that exact temporary directory when
it is no longer useful. Never delete the evidence directory during teardown.
Confirm screenshots, trace, `result.json`, `launch.json`, and `doctor.json` still
exist after shutdown. A failed launch leaves its evidence intact.

## Helpers

All helper invocations are shown above. `launch.py`, `doctor.py`, and `stop.py` use Python's
standard library and the repo CLI; `onboarding-smoke.mjs` uses the repo's existing
Playwright dependency. They introduce no new package dependency or test framework.

## Helper safety check

Run the standard-library ownership test before changing launch/doctor/stop helpers:

```sh
python3 -m unittest discover -s .agents/skills/verify-paperclip/tests -v
```

It starts an owned fixture in another temporary checkout and confirms that both
doctor and stop reject its claimed port/PID without stopping the server. A second
fixture closes its listener before exiting and proves that cleanup waits for
runtime exit. These checks do
not qualify Paperclip startup, database readiness, or onboarding.
