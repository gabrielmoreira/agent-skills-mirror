# Writing Sprint Goals That Steer

A sprint goal is a decision-making tool for the *middle* of the sprint: when new work appears on day 4, the goal answers "does this serve it?" Goals that can't answer that question are decoration.

## The three tests

1. **Outcome, not inventory.** "Ship stories X, Y, Z" is a list wearing a goal costume. "A new user can go signup → first report without help" is a goal — stories serve it, and cutting one doesn't automatically fail it.
2. **Scoreable pass/fail on the last day.** If reasonable people could argue about whether you hit it, sharpen it now. Numbers help; demos help more ("we demo the flow live to support").
3. **One goal.** Two goals = permission to fail one quietly. If the sprint genuinely serves two masters (feature + debt), name the primary and cap the secondary ("goal: checkout flow; plus ≤20% capacity on migration prep").

## Good/bad pairs

| Weak | Steering |
|---|---|
| "Complete the API tickets" | "Partners can integrate v2 end-to-end using only the docs" |
| "Improve onboarding" | "Activation-blocking steps drop from 9 to 5, measured in the funnel" |
| "Work on performance" | "P95 dashboard load under 2s on the demo dataset" |
| "Migration + new filters + bugs" | "Migration cutover-ready (primary); filters only if capacity remains" |

## Mid-sprint use (the actual point)

- New request arrives → "does it serve the goal?" No → next sprint, or it explicitly displaces named stories.
- Story in trouble on day 6 → "is it load-bearing for the goal?" Yes → swarm it. No → drop it *now* and say so.
- At standup, "are we on track?" means the goal, not the burndown.
