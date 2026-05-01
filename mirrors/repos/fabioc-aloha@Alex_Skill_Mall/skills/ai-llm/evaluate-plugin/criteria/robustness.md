---
id: robustness
name: Robustness & Edge Cases
---

# Robustness & Edge Cases

Evaluates whether the plugin performs reliably under adverse, unexpected, or
stress conditions — not just clean, expected inputs.

> **Industry reference:** HELM (Stanford), OpenAI evals, DeepMind evaluation rubrics  
> **Why it matters:** Plugins run across different LLMs (Claude, GPT, etc.) and users
> will provide malformed, adversarial, or unexpected inputs. A plugin that only works
> on the happy path is a liability.

## What to look for

- **Adversarial inputs** — Does the plugin handle intentionally malformed, empty, or hostile input?
- **Large/extreme inputs** — What happens with very large files, deeply nested structures, or long conversations?
- **Retry/loop prevention** — Does the plugin guard against infinite loops, unbounded retries, or runaway execution?
- **Missing dependencies** — What happens if an expected tool, file, or service is unavailable?
- **Concurrent/reentrancy** — If invoked multiple times, does the plugin handle state safely?
- **External dependency management** — If the plugin depends on external services (MCP servers, APIs, sibling plugins, npm packages), are dependencies documented, version-pinned where appropriate, and handled gracefully when unavailable?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | Handles adversarial inputs proportional to risk. Guards against loops. Explicit timeout/limit where relevant. External dependencies documented with graceful fallback when unavailable. Tested under realistic stress conditions. |
| **4** | Most edge cases covered. Has retry limits. Handles missing dependencies. External services have documented setup and at least a warning when unavailable. |
| **3** | Works for expected inputs. Some resilience, but untested on extreme cases. External dependencies may be mentioned but no fallback behavior is defined. |
| **2** | Fragile. Likely to fail on unexpected inputs or different LLMs. No retry limits. Undocumented external dependencies that silently fail. |
| **1** | Breaks on non-trivial inputs. No consideration of robustness. |

## What a 5 looks like

- "Maximum 3 retry attempts before aborting with an error message"
- "If input exceeds 10,000 lines, process in batches of 1,000"
- "If the tool call times out after 30 seconds, report the timeout and continue"
- "If the user provides an empty file list, ask for clarification rather than failing silently"

> **Proportionality:** Scale robustness expectations to the plugin's risk profile.
> A read-only status display where the worst failure is blank output needs far less
> robustness scaffolding than a plugin that modifies files or calls external APIs.
> Do not penalize for missing guards against extreme hypotheticals when the
> failure mode is benign.

> **External dependencies:** Plugins that depend on MCP servers, external APIs,
> sibling plugins, or runtime packages (npm, pip) should document these
> dependencies clearly and define what happens when they are unavailable.
> A plugin that silently fails because an MCP server is unreachable should
> score lower than one that checks availability and provides a helpful error.
> Score this proportionally — a single optional dependency is less critical
> than a core dependency that blocks all functionality.

## Scoring examples

### Score 5 — deep-review

```markdown
## Phase 1: Gather Context

If no changes are detected:
  - Inform the user and suggest alternatives (check a different branch, specify files)

If the diff is very large (>2000 lines):
  - Split into logical groups and review each separately
  - Note in the synthesis that the review was split
```

Why it scores 5: Handles extreme inputs (very large diffs) with explicit
splitting strategy. Covers empty input (no changes detected) with helpful
alternatives. Instructions are model-agnostic with no LLM-specific syntax.

### Score 2 — hello-skills

```markdown
Greet the user warmly... enclose the message in ASCII art.
```

Why it scores 2: No consideration of edge cases (what if user provides no name?
what if name contains special characters?). No retry limits, no input
validation. Will behave inconsistently across different LLMs.
