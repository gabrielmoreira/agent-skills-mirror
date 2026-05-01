# Agent Workflow Rules

## Planning
For any task that touches more than 3 files or involves architectural decisions:
1. Enter plan mode first
2. Present implementation plan
3. Wait for explicit "proceed" or "go ahead"
4. Execute step by step

## Subagent Usage
Use Task tool (subagents) for:
- Parallel file exploration
- Background long-running operations
- Independent research tasks

Provide subagents with:
- Clear, specific objective
- Relevant file paths
- Success criteria

Avoid subagents for:
- Simple single-file reads
- Sequential dependent operations

## Context Management
- Always read files before editing
- Compact at task boundaries, not mid-work
- Summarize complex explorations

## Quality Gates
After ANY code edit, before marking complete:
1. Run lint: `npm run lint`
2. Run typecheck: `npm run typecheck`
3. Run related tests: `npm test -- --related`

## Session Wrap-Up
On "/wrap-up" command:
1. Review all changes made this session
2. Check for uncommitted changes
3. Verify tests pass
4. Update LEARNED.md with new patterns
5. Create session summary

## Self-Correction Loop
When user corrects me:
1. Acknowledge the correction
2. Propose addition to LEARNED.md
3. Apply after approval
