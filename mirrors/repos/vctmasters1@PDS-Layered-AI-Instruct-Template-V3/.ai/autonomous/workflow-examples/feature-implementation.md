# Workflow Example — Feature Implementation

**Status**: Scaffold reference walkthrough
**Workflow key**: `feature-implementation` (referenced from [`autonomy-config.yaml`](../autonomy-config.yaml) `workflows:` block)
**Scope**: A single feature, single module, ≤20 files, ≤25 agent steps.

> This is a **worked example**, not a script. The orchestrator does not execute markdown — it reads the table below as a hint for agent ordering when the user's goal matches the template.

---

## Contents

| Section | Purpose |
|---|---|
| [When to Use](#when-to-use) | Match signals for this template |
| [Pre-conditions](#pre-conditions-verified-by-orchestratormd-pre-flight) | What pre-flight checks |
| [Step Sequence](#step-sequence) | Planned agent ordering |
| [Worked Example](#worked-example) | Concrete trace |
| [Failure Variations](#failure-variations) | What can go wrong |
| [Extension Checklist](#extension-checklist) | How to add new workflows |
| [See Also](#see-also) | Related files |

---

## When to Use

Pick this workflow when the user's goal is, roughly:

> *"Add **X** to **<module>**, with tests."*

Concrete signals:

- A specific module path is identifiable (`api/`, `gui/`, `db/`, …).
- The change introduces new behaviour, not a refactor of existing behaviour.
- Tests don't already exist for the new behaviour.
- No DB schema changes, no new external service, no new credential.

If any signal is missing, fall back to ad-hoc orchestration (let `pds-pipe-super` plan from scratch).

---

## Pre-conditions (verified by [`orchestrator.md`](../orchestrator.md) pre-flight)

- `autonomy-config.yaml.enabled == true`
- No `.ai/PAUSE`
- Branch state is clean OR `pds-man-versioncontrol` confirms the working branch is appropriate
- Module exists and has `<module>/.ai/instruct.md`
- Queue capacity available

---

## Step Sequence

Each row is a **planned** agent invocation. Approval gates apply per `human_approval.mode`. Failures halt at `failure_streak == 3`.

| # | Agent | Purpose | Halt-on |
|---|---|---|---|
| 0 | *(orchestrator)* | Pre-flight, allocate `goal_id`, lock scope via `pds-man-versioncontrol` | any pre-flight failure |
| 1 | `pds-meta-router` | Resolve `scope_path`, `scope_authority_file`, governance refs | unresolved scope |
| 2 | `pds-pipe-super` | Plan worker stages within scope; produce step list | refuses to plan |
| 3 | `pds-man-naming` | Consult for new identifiers (file names, function names, endpoint paths) | naming conflict |
| 4 | `pds-pipe-scaffolder` | Produce structured plan (no final code) | plan rejected |
| 5 | `pds-pipe-generator` | Produce final code from approved scaffold | generator BLOCK |
| 6 | `pds-pipe-validator` | Static + convention checks against scope rules | validator BLOCK |
| 7 | `pds-pipe-tester` | Generate tests for the new code | tester BLOCK |
| 8 | `pds-pipe-validator` | Re-run validation against generator + tester output | validator BLOCK |
| 9 | `pds-pipe-reviewer` | Final instruction-drift + architectural review | reviewer BLOCK |
| 10 | `pds-pipe-cleanup` | Archive any superseded files | unsafe deletion attempt |
| 11 | `pds-man-versioncontrol` | Release scope lock; emit branch/PR guidance | merge gate failure |
| 12 | `pds-meta-observer` | Emit run digest (steps, files, tokens, anomalies) | n/a |

Total: 12 planned hand-offs, well under the default `max_steps: 25`. The remaining budget is reserved for retries within `failure_streak`.

---

## Worked Example

**User goal**:

> `/ai-autonomous-start "Add a /healthz endpoint to api/ that returns {status:'ok'} with a unit test."`

**Run trace** (abridged; full step log lives at `.ai/logs/autonomous-2026-05-29.jsonl`):

| Step | Agent | Outcome | Notes |
|---|---|---|---|
| 0 | orchestrator | preflight_passed | `goal_id=01HZX9K3M7…`, lock `api/` |
| 1 | pds-meta-router | success | `scope_path=api/`, authority `api/.ai/instruct.md` |
| 2 | pds-pipe-super | success | Plan: scaffold → generate → validate → test → validate → review → cleanup |
| 3 | pds-man-naming | success | Endpoint path `/healthz` approved; handler `health_check` registered |
| 4 | pds-pipe-scaffolder | success | Plan JSON: 1 new file `api/healthz.py`, 1 new test `api/tests/test_healthz.py` |
| 5 | pds-pipe-generator | success | Wrote `api/healthz.py` (12 LOC) |
| 6 | pds-pipe-validator | success | 0 blockers, 1 warning (missing module-level export) |
| 7 | pds-pipe-tester | success | Wrote `api/tests/test_healthz.py` (1 test, asserts 200 + body) |
| 8 | pds-pipe-validator | success | All warnings resolved by tester pass |
| 9 | pds-pipe-reviewer | success | No instruction drift detected |
| 10 | pds-pipe-cleanup | success | Nothing to archive |
| 11 | pds-man-versioncontrol | success | Lock released; PR template emitted to terminal |
| 12 | pds-meta-observer | success | Digest: 2 files, ~18.4k tokens, 1m46s wall, 0 anomalies |

**Queue final row**:

```json
{
  "goal_id": "01HZX9K3M7QF2VABCDE0123456",
  "status": "completed",
  "step_index": 12,
  "files_modified": ["api/healthz.py", "api/tests/test_healthz.py"],
  "stop_reason": null
}
```

---

## Failure Variations

| Variant | What changes |
|---|---|
| Validator finds 2 blockers at step 6 | `failure_streak: 1` → re-invoke `pds-pipe-generator` with feedback. If 3 consecutive blockers → halt `aborted` |
| Naming conflict at step 3 | Halt `awaiting_approval`; user picks an alternate name; resume |
| User denies approval at step 5 | Halt `denied`; row terminal; user restarts with refined goal |
| `.ai/PAUSE` appears between steps 7 and 8 | Halt `paused_sentinel` at next iteration; tester output preserved; resumable |
| Scope authority `api/.ai/instruct.md` edited mid-run | Heartbeat detects drift → halt `scope_drift`; user re-runs goal |

---

## Extension Checklist

To add a new workflow file under `.ai/autonomous/workflow-examples/`:

1. Pick a kebab-case key (e.g., `bugfix-with-tests`).
2. Copy this file as a starting template.
3. Adjust the **When to Use** signals to be unambiguous.
4. Edit the **Step Sequence** table to reflect the actual agent ordering.
5. Register the key under [`autonomy-config.yaml`](../autonomy-config.yaml) `workflows:`.
6. Add a row to [`AGENTS.md`](../../../AGENTS.md) "How to Enable Autonomous Layer" if it changes the operator surface.
7. Open a `/ai-reflect` entry justifying the addition; the curator reviews.

Workflow files are **not** authoritative — they are hints. The orchestrator is always free to fall back to ad-hoc planning if the run diverges from the template.

---

## See Also

- [`../orchestrator.md`](../orchestrator.md) — the loop that consumes this hint
- [`../autonomy-config.yaml`](../autonomy-config.yaml) — `workflows:` registry
- [`../safety-guardrails.md`](../safety-guardrails.md) — what can halt this run
- [`../task-queue.md`](../task-queue.md) — where the goal row lives
