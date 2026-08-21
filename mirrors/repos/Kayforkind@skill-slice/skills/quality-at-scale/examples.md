# quality-at-scale — examples

Medium-agnostic. Visuals are one appendix, not the default.

## GOOD — 200 API handlers (code)

- Medium: code · N: 200 · Gold: one idempotent POST handler with tests
- Axes: api_shape, error_paths, deps, sync_async
- Unit bank: 200 rows before generate
- Waves: 10 × 20 · Verify: tests + typecheck each wave
- Wave 1: 1 WEAK craft → shrink wave 2 to 10, then resume 20
- Quarantine: 4 axis-collisions → regenerated
- Done: ledger `done`, sample PASS, 200 shipped
- Why good: gold, bank, axes, calibration, medium verify, evidence

## BAD — 200 API handlers (code)

- “Generated 200 handlers” — no bank, no axes, no sample
- 140 share the same error-handling paste
- No ledger / quarantine / diff vs gold
- Rejected: count-only, no evidence

## GOOD — 100 test cases (tests)

- Gold: clear arrange/act/assert + named scenario + edge
- Axes: scenario_class, input_class, failure_mode, boundary, negative_path
- Waves: 5 × 20 · Verify: run + assertion-quality review
- 8 quarantined (happy-path twins), reworked
- Done evidence complete

## BAD — 100 test cases (tests)

- 60 happy-path variants; no failure-mode axis; negligible coverage delta
- Rejected

## GOOD — 50 doc pages (docs)

- Gold: audience tag, structure, examples, cross-refs
- Axes: audience, depth, structure, example_density, prerequisites
- Waves: 5 × 10 · Verify: Read + structural diff vs gold
- 5 quarantined (tone drift), reworked
- Done evidence complete

## BAD — 50 doc pages (docs)

- Tone drifts after page 10; duplicated structure; no diff vs gold
- Rejected

## GOOD — 1000 data rows (data)

- Gold: schema-valid row with edge + locale tags
- Axes: schema_variant, edge_case, nullness, locale, distribution
- Scalable path: schema-validated generator + Cursor verify samples
- Waves: 20 × 50 · Verify: schema + uniqueness scan
- 47 quarantined (schema violations), regenerated
- Done evidence complete

## BAD — 1000 data rows (data)

- 300 near-dupes differing only by noise; no uniqueness scan
- Rejected

## Appendix — visual floods (abbreviated)

- GOOD: 60 icons with silhouette/palette/composition axes, waves of 6, render+inspect, quarantine 4
- BAD: 200 SVGs “done” by file count; 120 share silhouette — rejected
- Lesson: collapse modes (template twins, skipped medium verify) apply to **every** medium

## GOOD — 80 Remotion Shorts variants (video) — bulk harness

- Gold: one Short PASS via `/reviewresults` (frames Read + rubric)
- Axes: hook_type, caption_density, plate_source, motion_motif, beat_pace
- Waves: 4 × 20 · After **each** wave: `/reviewresults --mode wave` on ≥10 stratified samples
- Wave 2 fail_rate 25% → STOP; fix caption template; shrink wave 3 to 10; resume
- Ledger: `wave` + `calibration` + `wave_review` each wave; final `done` with review paths
- Why good: same bar as gold inside the loop; script may generate, harness accepts

## BAD — 80 Remotion Shorts (video)

- Agent writes a batch render script; runs all 80; “reviews” one hero at the end
- 50 dark opens / caption crush; file count == 80 claimed done
- Rejected: script-and-ship + review-once-at-end = harness failure
