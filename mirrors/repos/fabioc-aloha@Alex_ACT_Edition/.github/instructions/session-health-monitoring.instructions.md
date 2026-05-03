---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Monitor session health, manage context window, and ensure continuity across sessions"
application: "Always active — unconscious monitoring of session state and context capacity"
applyTo: "**"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Session Health Monitoring

Always-active unconscious behavior. Monitor context usage and ensure graceful session transitions.

## Context Window Awareness

### What I Cannot See

- Exact token count of current session
- Remaining context window capacity
- VS Code doesn't expose session metrics programmatically

### Proxy Heuristics

| Signal | Interpretation |
|--------|----------------|
| ~4 characters | ≈ 1 token |
| Large file read (500+ lines) | ~2,000-5,000 tokens |
| Base64 image in response | ~10,000-50,000 tokens |
| Semantic search results | ~500-2,000 tokens |
| Terminal output (unfiltered) | Variable, often 1,000+ tokens |

### High-Token-Cost Operations

| Operation | Est. Cost | Mitigation |
|-----------|-----------|------------|
| **Image generation display** | 10K-50K tokens | Write to file, report path only — NEVER embed base64 |
| **Full file reads** | 2K-5K tokens | Use line ranges, read in chunks |
| **Unfiltered terminal output** | 1K+ tokens | Use `Select-Object -First 20`, redirect to file |
| **Multiple semantic searches** | 500-2K each | Batch related searches, use grep for known patterns |
| **Large code generation** | Variable | Generate to file, not inline |

## Session Memory Pattern

### When to Create Session Memory

- At session start for complex multi-session tasks
- Before known high-cost operations
- When switching major topics mid-session
- At user request

### Session Memory Template

Write session notes to `/memories/session/[descriptive-name].md` with: Status (Active/Concluded), Progress Summary, Next Steps, Key Decisions, Files Modified. Session memory is conversation-scoped.

## Warning Signs

### Context Pressure Indicators

| Signal | Action |
|--------|--------|
| Forgetting early conversation context | Update session memory, suggest new session |
| Responses truncating unexpectedly | Reduce output verbosity, offload to files |
| Repeated clarification of established facts | Context may be dropping off |
| User mentions "you forgot" or "we discussed" | Acknowledge, re-read session memory |

### Proactive Checkpoints

- **After 6+ exchanges**: Consider updating session memory
- **Before image work**: Warn about token cost, confirm approach
- **After major milestone**: Summarize progress to session memory
- **If unsure about capacity**: Offer to start fresh session with handoff

## Graceful Handoff Pattern

When approaching session limits or switching to new session:

1. **Update session memory** with current state
2. **List completed work** clearly
3. **Document next steps** explicitly
4. **Note any pending decisions** that need user input
5. **Suggest**: "New session can read `/memories/session/[file].md` to continue"

## Integration with Existing Patterns

- Works alongside `emotional-intelligence.instructions.md` (session health includes user state)
- Complements `alex-identity-integration.instructions.md` (4+ hour boundary awareness)
- Supports `memory-curation.instructions.md` (token efficiency in memory files)
