# Trace signals

Read `<round>/<type>.trace.txt` with the subagent's report and actual diagram. These are hypotheses, not verdicts: confirm them against source facts and the failing input, and retain contributing factors or uncertainty. Apply the main Skill's product requirements and adjustable-rule policy before deciding what to repair.

| Signal in the trace | Likely cause | Check |
|---|---|---|
| The final candidate changed or dropped nodes, edges or lanes | Lost meaning or a source-backed correction | Use `collect.mjs` "lost" signals, then compare source facts, conditions and ownership; distinguish correction from removing real content to pass |
| A draft without route controls fails crossing, corridor, through-node or label checks | Possible layout defect or authored placement constraint | Inspect node placement, dimensions and canvas first; render a scratch copy at `standard` to inspect routes, keeping the original failure |
| A crossing or corridor failure, then side pins, then `explicit-pin-conflict`, then a restructure | Placement, routing or a misleading repair hint | Test the proposed pins on the original input; check for a legal route before concluding none exists |
| The same code survives a focused repair | Incomplete repair evidence, a new instance or an unsuitable rule | Inspect the identified element and actual harm, then reproduce the advertised fix |
| Width or gap values oscillate across runs, such as `gapX` 64, 108, 72 | Missing target information or interacting constraints | Check whether the rule is appropriate and whether the suggested size can satisfy the other constraints |
| The agent writes `meta.viewBox` after a width message | Unclear canvas advice or an unsuitable fit requirement | Inspect actual readability, explicit geometry and accepted scrolling before suggesting a canvas change |
| The agent renders a scratch copy at `standard`, reads renderer source or greps references for a rule | Missing evidence, hard-to-find guidance or normal investigation | Read why the detour was necessary; improve the diagnostic or required read only for a demonstrated gap |
| `[truncated N chars]` on a read of a reference | Content exceeds this tool's output budget | Check the actual read and shorten or restructure the necessary material |
| Two or more subagents list the same unclear point | Instruction usability problem | Test whether clearer guidance reduces misunderstanding or rework |
| A rerun is blocked by stale evidence or output paths | Delivery friction | Give the exact command in the message |
| A pass on the first run | Machine acceptance only | Audit source meaning and inspect the complete diagram |
| A clear, accurate diagram repeatedly fails a style or geometry heuristic | An overbroad acceptance rule | Identify the intended harm; compare a narrower rule or advisory diagnostic on contrasting cases |
| Two selected routes get shorter but other routes become harder to follow | Local placement optimization harms the whole graph | Compare all relationships, labels, overview and repair cost before adopting the move |

## Root causes found so far

These historical cases illustrate possible causes. Check the current revision before treating their dimensions, diagnoses or fixes as current behavior.

- Workflow same-lane neighbours were placed 8px apart, leaving little route space. Automatic drafts failed on crossings and shared corridors, and agents removed lanes and nodes. Unpinned drafts now use a 32px corridor and may take offset tracks; absolute route pins retain their existing geometry contract.
- Dataflow flows across several stages turned at their midpoint, inside a middle stage's node. Agents deleted nodes. They now turn in the nearest clear gap.
- Dataflow ignored perpendicular pinned sides, so agents hand-wrote `via` points.
- Sequence canvases stayed 920px wide whatever the participant labels needed, and the message suggested widening `viewBox`, which the readability budget forbids.
- Workflow diagnostics named edges by an internal sort order, so agents edited the wrong edge.
- Architecture candidate selection ignored the number of bends, and legends reserved width at a smaller font than they rendered.
- A compile-time text floor applied to tags, which `browser-check` exempts: a self-inflicted false failure, found two rounds late because the affected test file was not run.

## Previously rejected experiments

Retain these negative results as context. Revisit only with a different supported hypothesis; they are not universal bans on the approach.

- Routing Workflow edges by role and span order: more crossings than the canonical order.
- Ripping up and replanning conflicting Workflow routes after the first pass: it traded crossings for shared corridors and made no draft pass.
- Shrinking or removing content automatically to fit a budget: it hides the accuracy loss this skill exists to prevent.
