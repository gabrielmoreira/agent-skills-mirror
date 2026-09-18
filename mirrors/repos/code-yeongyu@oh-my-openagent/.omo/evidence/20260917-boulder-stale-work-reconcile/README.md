# QA - stale boulder work reconcile (#8413)

## WHAT WAS TESTED

The two ulw-execute read paths that were wired to `reconcileStaleWorks`, driven in process against
the record observed in a real install (`work_id: omo-agent-toolkit-eval-sdk-20260913`, one
`senpi:` session, `status: "active"`, no `updated_at`, no `started_at`, extra `ulw_loop_session`
and `mode` fields) placed beside a sibling work that completed normally in the same file:

1. **Senpi surface** - `components/ulw-execute-continuation/boulder-eligibility.ts`
   `findContinuableBoulderWork(projectDir, "<a different session>")`, the call the component makes
   on user input and on `agent_settled`.
2. **Resume** - `selectActiveWork(projectDir, workId)`.
3. **OpenCode surface** - `hooks/ulw-execute` `createUlwExecuteHook(...)["chat.message"]` with the
   real `/ulw-execute` template text, once with two stale works (the hook lists them) and once with
   one stale work (the hook resumes it).
4. **Healthy work** - the same senpi read path after the transcript's mtime is moved to 5 minutes
   ago.

The project, the agent home and the session transcript were created under a temp root, with
`OMO_CODING_AGENT_DIR` and `HOME` pointed at it; the transcript was written at
`<agentDir>/sessions/<encoded project cwd>/2026-09-13T06-51-23-701Z_<sessionId>.jsonl` with its
mtime set 41 hours back, which is the layout and the age of the real record.

Captured output: [`qa-ulw-execute-read-paths.txt`](./qa-ulw-execute-read-paths.txt).

## WHAT WAS OBSERVED

| Step | Result |
|------|--------|
| Senpi read path, 41h-old transcript | `active` -> `paused` with `stale_since`; `session_ids`, `mode` and `ulw_loop_session` unchanged; the `completed` sibling untouched |
| Resume (`selectActiveWork`) | `paused` -> `active`, `stale_since` gone |
| OpenCode hook, two stale works | both demoted to `paused` with the same `stale_since`; the hook still lists both as resume options |
| OpenCode hook, one stale work | repaired and then resumed by the new session in the same turn: `active` with `opencode:ses_qa8413b` appended |
| Senpi read path, 5-minute-old transcript | `.omo/boulder.json` byte-identical afterwards (no write) |

Isolation receipts: `resolveAgentSessionsDirectory` returned the isolated sessions directory
(`isolated sessions dir: true`); `shasum ~/.omo/agent/settings.json` is identical before and after a
full QA run, and the real sessions directory entry count is unchanged. The temp root is removed by
the driver at the end (`cleanup: removed $TMPDIR/qa-8413-...`).

## WHY IT IS ENOUGH

The failure in #8413 is a state transition that never happened, so the proof has to be the file on
disk before and after the code that reads it - which is what the tables show, through the real
consumer functions rather than through the reconcile API. Both wired surfaces are exercised, in the
listing and the resuming route, and the no-op case is proved by byte equality rather than by a
status read. The unit matrix in `packages/boulder-state/src/stale-work.test.ts` covers the rest:
the threshold boundary, a 31-day gap, a session id that can never resolve to a transcript
(`senpi:unknown`) beside a fresh unrelated one, missing transcript with and without timestamps,
`completed` records, absent and unreadable boulder files, and both resume paths.

## WHAT WAS OMITTED

No live `senpi` or `opencode` binary was driven: the change is a state transition inside a shared
core package plus two call sites, and the drivers here call those call sites directly. The senpi
plugin bundles under `packages/omo-senpi/plugin/extensions/` are generated artifacts rebuilt by
`bun run build:senpi-plugin` in the release flow and are not part of this change. No secret-bearing
output was captured; absolute home paths are written as `~`.
