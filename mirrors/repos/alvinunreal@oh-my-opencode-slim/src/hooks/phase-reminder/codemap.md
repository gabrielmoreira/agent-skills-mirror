# src/hooks/phase-reminder/

## Responsibility
Orchestrates phase reminder injection into user messages, ensuring workflow guidance is appended without mutating the original message content or affecting UI display.

## Design

### Core Abstraction
- **Hook Factory**: `createPhaseReminderHook()` returns an OpenCode experimental chat message transformer hook
- **Non-Mutating Strategy**: Appends phase reminder as a separate message part rather than modifying user-authored text
- **Targeted Injection**: Only anchors onto orchestrator-authored user messages (per-message eligibility)

### Key Components
- `PHASE_REMINDER` constant (imported from `../../config/constants`)
- `SLIM_INTERNAL_INITIATOR_MARKER` constant (imported from `../../utils`)
- Message part type checking and injection logic

### Design Patterns
- **Observer Pattern**: Intercepts and transforms messages before API transmission without altering source
- **Guard Clauses**: Multiple preconditions prevent unnecessary processing:
  - Empty message check
  - User message existence check
  - Per-message orchestrator agent check
  - Duplicate injection prevention
  - Internal initiator marker check

## Flow

1. **Hook Invocation**: OpenCode calls the `experimental.chat.messages.transform` hook before sending messages to API
2. **Session Selection**: Finds the latest user message and uses its session identity as the eligibility scope
3. **Forward Scan**: Scans messages from oldest to newest within that session view
4. **Eligibility Check**: Skips non-orchestrator messages, session mismatches, internal-initiator parts, and messages without usable text
5. **Single Anchor Selection**: The first eligible message becomes the anchor
6. **Idempotent Injection**: Appends the tagged phase reminder only if the anchor does not already carry it, then stops scanning
7. **Stable Carry**: Later eligible messages receive no reminder, keeping exactly one anchored copy per view
8. **Re-Anchor on Prefix Rewrite**: If compaction, trimming, or a fork removes the anchor from the visible prefix, the next first eligible message becomes the anchor for the rewritten view
9. **Transmission**: Messages proceed to API with the anchored reminder (not visible in UI)

## Integration

### Dependencies
- **Config**: `PHASE_REMINDER` constant from `../../config/constants`
- **Utils**: `SLIM_INTERNAL_INITIATOR_MARKER` from `../../utils`
- **Types**: `MessageWithParts` type from `../types`

### Consumers
- **OpenCode**: Registers the hook via plugin initialization
- **Orchestrator Agent**: Orchestrator-authored user messages receive the anchored phase reminder
- **API Layer**: Receives messages with injected reminders (UI remains unaffected)

### Context
- **Execution Timing**: Runs right before API transmission (post-UI rendering)
- **Scope**: Anchors onto orchestrator-authored user messages (per-message eligibility); persists across agent switches
- **Persistence**: Reminder is appended as a separate message part, preserving original content
