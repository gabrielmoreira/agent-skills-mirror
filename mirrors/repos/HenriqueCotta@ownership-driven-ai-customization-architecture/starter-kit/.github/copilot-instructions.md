# Repository Baseline

Prefer explicit behavior and readable boundaries, and keep the repository coherent as those behaviors evolve.

Keep changes scoped, but do not leave clear downstream drift behind when the follow-through is small and certain.

Default closure policy: reconcile small and certain downstream follow-through in the current pass. Carry broader, riskier, or less certain follow-through forward explicitly.

## Follow-Through Triggers

When a change shifts behavior or expectations that other surfaces encode, review those downstream surfaces for drift.
