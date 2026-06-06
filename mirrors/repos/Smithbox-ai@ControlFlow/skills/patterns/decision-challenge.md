# Decision Challenge

Use this pattern once for a high-risk or non-trivial decision whose failure would materially change architecture, scope, recovery, security, or user-visible behavior.

## Trigger

Apply when at least one is true:

- evidence supports multiple materially different designs
- a decision is difficult to reverse
- a critical assumption has weak or indirect evidence
- the chosen path crosses a shared contract or broad ownership boundary

Skip for trivial choices, established repository conventions, or decisions already independently reviewed.

## Bounded Challenge

1. State the proposed decision and supporting evidence.
2. State the strongest plausible failure mode or counterargument.
3. Compare one simpler or safer alternative.
4. Decide `KEEP`, `REVISE`, or `REJECT` and record the reason.

Stop after one challenge unless new evidence materially changes the decision. Use existing ControlFlow review routes when independent review is required. Do not invoke external agents, cross-model CLIs, or hidden autonomous loops.
