# Experiment design

Read this when running independent authors, comparing complete authoring time, or judging screenshots. Use only the evidence needed for the current claim.

## Author comparisons

- Freeze the source revision, task, runtime, required instructions and starting input (if any). Record model/reasoning settings when available and say when they are unknown. Keep each author's context independent. Describe the intended difference between arms; hold other conditions comparable.
- Use a separate subagent for each author task. For generated `prompts.json`, preserve the task and record any experiment appendix, such as an optional mode or an attempt budget, before dispatch. Keep source projects and active runtimes read-only. Follow the repository's model-selection instructions.
- Discovery tasks may run concurrently. For speed comparisons, prefer serial runs without competing parent rendering/tests, and alternate run order when repeating. A parallel one-off measures a workload under contention, not an isolated version speed difference.
- Preserve the first draft, every failed attempt, edits and the final artifact. If the budget interrupts normal recovery, retain the last verified usable result and label the final experiment state separately. A cap that prevents restoring a prior good draft is not evidence that ordinary delivery cannot recover.
- A repair trial with a supplied JSON tests recovery, not fresh prompt-to-diagram generation. Independent authors may choose different abstractions; audit against source facts before comparing outcomes. Use same-JSON cross-rendering to isolate runtime effects where useful.
- One pair provides a case observation. Use contrasting complete inputs or another project before generalizing a benefit; reserve broader fresh generation for claims that require it.

## Whole-process timing

- Record task dispatch, work start before initial reads, first JSON, first verified usable result, visual review and final delivery/report timestamps. Include source reading, authoring, repairs, failed commands and necessary review in elapsed time.
- Record CLI durations and known waits separately. Leave unclassified time unknown; do not call it pure model reasoning or subtract it merely because a run was slow. Existing trace collection does not automatically provide these timings.
- Compare similar delivered outcomes. Report failed/unfinished tasks and their costs separately. A small render-time change deserves another optimization round only when it creates meaningful cumulative cost in the real authoring path.

## Semantic and visual comparison

- Keep raw inputs, source snapshots and runtime identities immutable. For same-input comparisons, use identical JSON; identify any benchmark normalization and the checks it omits. For placement experiments, list allowed position/spacing changes and separately record source-backed semantic corrections.
- Audit relationship endpoints, directions, conditions, ownership, labels, source facts and completeness. First/final counts alone cannot establish accuracy. Judge proposed moves on the entire graph, including exception and return paths.
- Match CSS viewport, theme, style, motion, zoom, detail mode and scroll position. Wait for rendering to settle and inspect the actual images. The `shots.mjs` helper supplies a light-theme comparison; add relevant dark/detail states when the affected behavior requires them.
- Use fixed-viewport top and scrolled captures for first-screen visibility, floating controls and occlusion claims. Full-page captures can change floating-control relationships; corroborate suspected overlap in the live viewport and, when needed, element bounds.
- Read the diagram as a user: follow conditions to endpoints, distinguish crossings from junctions, read labels and assess overview and balance. Capture failures are missing evidence. Gate success, fewer bends and shorter routes each answer only part of this review.

Keep these records in the existing round directory and journal. Reuse unchanged evidence with its revision and limitations instead of repeating an entire suite or inventing a separate scoring system.
