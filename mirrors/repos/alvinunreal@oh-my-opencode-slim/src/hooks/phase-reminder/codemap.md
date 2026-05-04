# src/hooks/phase-reminder/

## Responsibility

Keep orchestrator guidance aligned over long turns by prepending a phase reminder to the latest user message text before the next LLM request.

## Design

- `PHASE_REMINDER` constant is composed from `PHASE_REMINDER_TEXT` (`config/constants.ts`).
- `createPhaseReminderHook()` returns a single `experimental.chat.messages.transform` handler.
- Message filtering is role/agent-aware:
  - locates the latest `'user'` role in `output.messages`,
  - only mutates if no explicit agent or `agent === 'orchestrator'`,
  - no-op for internal control messages containing `SLIM_INTERNAL_INITIATOR_MARKER`.
- Mutation target is the first `text` part in that message; replacement is an in-place prefix.
- Uses `SLIM_INTERNAL_INITIATOR_MARKER` from `../../utils` to avoid feedback loops.

## Flow

1. On transform, scan backward through `messages` for last `info.role === 'user'`.
2. If agent is non-orchestrator, return.
3. Locate first part where `type === 'text'`.
4. If marker exists, return.
5. Prefix `part.text` with `PHASE_REMINDER + '\n\n---\n\n'`.

## Integration

- Registered through `src/hooks/index.ts` and plugin-level hook wiring in `src/index.ts`.
- Consumes `experimental.chat.messages.transform` and mutates the outgoing `messages` payload only.
- Does not depend on stateful services; no network or client APIs are required.
