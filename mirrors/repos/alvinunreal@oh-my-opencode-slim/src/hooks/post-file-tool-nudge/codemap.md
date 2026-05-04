# src/hooks/post-file-tool-nudge/

## Responsibility

Detect recent file interaction (`Read`/`Write`) and queue a one-shot workflow reminder that is injected on the next system prompt transform without mutating tool execution output.

## Design

- Factory `createPostFileToolNudgeHook(options?)` emits three handlers:
  - `tool.execute.after`
  - `experimental.chat.system.transform`
  - `event`
- A per-instance in-memory `pendingSessionIds: Set<string>` tracks sessions that recently ran file tools.
- `FILE_TOOLS` is the canonical set `{ 'Read', 'read', 'Write', 'write' }`.
- Injection is optional per session via `options.shouldInject?: (sessionID) => boolean`.
- Cleanup path handles both `session.deleted` payload shapes (`properties.sessionID` and `properties.info.id`).

## Flow
1. `tool.execute.after`: if tool is file tool and has `sessionID`, add it to `pendingSessionIds`.
2. `experimental.chat.system.transform`: if session has pending marker, remove it and append `POST_FILE_TOOL_NUDGE` (`PHASE_REMINDER_TEXT`) to `output.system`.
3. Optional `shouldInject` gate can consume without injecting.
4. Additional `Read`/`Write` events before the same transform collapse to one reminder due to set semantics.
5. `session.deleted` event removes stale session IDs from the set.

## Integration

- Registered via `src/hooks/index.ts` and activated in plugin lifecycle registration.
- Mutates `output.system` only, ensuring persisted file tool outputs remain untouched.
- Consumed by orchestrator session flows that need anti-pattern mitigation (`inspect/edit` loops).
