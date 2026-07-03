# #11383 Capability Prompt Path Evidence

## Scope

- The `INBOX` `triage` subaction now fetches fresh cross-channel messages,
  calls `InboxService.triage`, and persists classifier results instead of only
  reading the existing queue.
- The inbox action description/routing hints now distinguish triage as the
  optimized-prompt classifier path.
- `inbox-triage-capability.scenario.ts` seeds scenario-scoped message adapters,
  adds an organic "triage my inbox" turn, requires a `purpose:
  "inbox_triage"` model call, and asserts one persisted triage row per seeded
  message.
- `plugins/plugin-inbox/test/inbox-action.test.ts` covers fresh-message
  classification, already-triaged filtering, and fail-closed classifier errors.
- The runtime preserves trajectory context across planned action execution, and
  SQL trajectory serialization keeps empty step objects parseable so later
  model-call writes are not collapsed to a stale one-step `steps_json` blob.

## Local validation

- `bun run --cwd plugins/plugin-inbox test -- test/inbox-action.test.ts`
- `bun run --cwd packages/core test -- src/features/trajectories/TrajectoriesService.test.ts src/runtime/__tests__/execute-planned-tool-call.test.ts src/__tests__/trajectory-context.test.ts src/runtime/__tests__/secret-swap-egress.test.ts src/runtime/__tests__/pii-swap-egress.test.ts src/__tests__/streaming-runtime-hooks.test.ts`
- `bun run --cwd packages/scenario-runner test -- src/final-checks/index.test.ts src/native-export.test.ts`
- `bunx biome check packages/core/src/features/trajectories/TrajectoriesService.ts packages/core/src/features/trajectories/TrajectoriesService.test.ts packages/core/src/features/trajectories/index.ts packages/core/src/runtime/execute-planned-tool-call.ts packages/core/src/runtime/__tests__/execute-planned-tool-call.test.ts packages/core/src/trajectory-utils.ts packages/scenario-runner/src/runtime-factory.ts packages/scenario-runner/src/executor.ts packages/scenario-runner/src/final-checks/index.ts packages/scenario-runner/src/final-checks/index.test.ts plugins/plugin-inbox/src/actions/inbox.ts plugins/plugin-inbox/test/inbox-action.test.ts`
- `git diff --check`
- `bun run verify`
- `ELIZA_SCENARIO_PGLITE_DIR=/tmp/eliza-11383-evidence-pglite env -u SCENARIO_USE_LLM_PROXY -u SCENARIO_LLM_PROXY_STRICT bun --conditions eliza-source --tsconfig-override tsconfig.json packages/scenario-runner/src/cli.ts run plugins/plugin-personal-assistant/test/scenarios --lane live-only --scenario inbox-triage-capability --report .github/issue-evidence/11383-capability-prompt-path/live-inbox-triage-capability-report.json --run-dir .github/issue-evidence/11383-capability-prompt-path/live-inbox-triage-capability-run --export-native .github/issue-evidence/11383-capability-prompt-path/live-inbox-triage-capability-native.jsonl`

## Evidence

- `live-inbox-triage-capability-report.json` passed all final checks, including
  `modelCallOccurred` for `purpose: "inbox_triage"`.
- `live-inbox-triage-capability-native.jsonl` contains 12 passed native export
  rows from 4 trajectory files; the manifest records run id
  `005fee18-d856-44a5-9fa4-1e3b588098a5`.
- Manual SQL inspection of `/tmp/eliza-11383-evidence-pglite` found the triage
  turn trajectory `9a6669e8-a8f7-4f73-b4f8-8788fdd31a52` with `step_count =
  28`, `llm_call_count = 10`, and one `purpose: "inbox_triage"` call on the
  classifier prompt at step 27.
- UI screenshots/video: N/A - no user-facing UI changed.
