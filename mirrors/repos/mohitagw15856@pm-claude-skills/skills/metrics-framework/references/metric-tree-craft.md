# Metric Trees That Drive Decisions (Not Dashboards)

A metrics framework is a causal argument: "these inputs, which teams can move, produce that output, which the business needs." Most frameworks fail by being taxonomies instead of trees — lists of things worth watching, connected to nothing.

## Building the tree

1. **Root: one North Star** — the value-exchange metric: it counts units of *delivered customer value* that correlate with revenue (messages sent, reports shared, orders fulfilled — not revenue itself, which lags, and not signups, which precede value). Test: if the North Star doubles, is the business unambiguously healthier? If you can imagine it doubling while the business rots (hello, "time in app"), pick again.
2. **Branches: the 3-5 input metrics** — each must be (a) causally upstream of the root — you can tell the story of *how* moving it moves the North Star, (b) movable by a nameable team, (c) leading, not lagging. "Activation rate", "weekly habit rate", "expansion trigger rate" — each owned, each with a current baseline.
3. **Leaves: the per-team operational metrics** — what a squad actually optimises sprint-to-sprint, laddering to one branch. A leaf that ladders to no branch is a hobby.

## Guardrails: the metric's conscience

Every input metric gets a paired guardrail — the thing you must NOT degrade while pushing it: activation ↔ week-4 retention (don't inflate day-1 with dark patterns) · items-per-session ↔ refund rate · pipeline created ↔ close rate. A framework without guardrails is a Goodhart machine: it will be gamed, honestly and enthusiastically.

## Definitions or death

Each metric ships with: exact definition (the query logic in prose), owner, refresh cadence, current baseline, and the dashboard link. Two teams with two definitions of "active" will fight for a quarter before discovering it's a data dictionary problem. The framework document IS the dictionary.

## Review rhythm

Metrics rot: features change what actions mean, gaming accretes, strategy shifts. The framework names its review date (quarterly) and its amendment rule (who can change a definition, and what happens to historical comparability when they do — annotate, never silently rewrite history).
