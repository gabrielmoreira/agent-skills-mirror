---
name: repository-investigation
description: Investigate an unfamiliar repository before changing it. Use this whenever a coding task spans multiple modules, asks for architecture or root-cause analysis, names behavior whose implementation location is unknown, or risks editing before enough evidence is gathered.
---

# Repository investigation

Build a focused evidence map before proposing or applying a change. The purpose is to make the first edit land on the real ownership boundary instead of the first matching string.

## Workflow

1. Restate the observable behavior, constraint, and desired outcome in one short internal goal.
2. Discover repository instructions and the build/runtime entry points.
3. Search for identifiers, routes, events, configuration keys, and tests before opening large files.
4. Trace one complete path from input to state transition or side effect and then to its consumer.
5. Identify persistence, concurrency, authentication, cancellation, and error boundaries that affect the change.
6. Inspect relevant history only when current code leaves an architectural decision unexplained.
7. Record a compact evidence map: owning files, data flow, invariants, existing tests, and unresolved assumptions.
8. Use the evidence map to decide whether the task is simple enough to act directly or needs an explicit plan.

## Investigation discipline

- Prefer targeted search and line ranges over recursively loading whole source trees.
- Distinguish an interface or prompt claim from a production call site that actually uses it.
- Verify both writers and readers of persisted or streamed state.
- For asynchronous behavior, locate lifecycle ownership, queue semantics, cancellation, reconnect, and recovery.
- For security-sensitive behavior, trace authenticated identity all the way to the resource and side effect.
- Treat generated files, build output, vendored dependencies, and comments as secondary evidence unless they are the runtime source of truth.

## Output to the running task

Keep the result concise and actionable:

- operative request and constraints;
- ownership/data-flow map with paths;
- invariants the implementation must preserve;
- tests and commands that can prove the result;
- assumptions that require user input or runtime evidence.

Do not turn the investigation into a generic repository summary. Stop when the evidence is sufficient to make the next decision safely.
