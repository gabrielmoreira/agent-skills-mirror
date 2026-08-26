# Eval Results: maplibre-cartography

Canonical results table for this skill. One row per eval test; baseline is the model's
answer with the skill omitted (`--var injectSkill=false`), with-skill is the same prompt
with the skill injected. See `evals/prompts/maplibre-cartography.yaml`.

Run: 2026-07-03 · model `cerebras:gpt-oss-120b` · judge `cerebras:gpt-oss-120b` (CI default) rejudged by Claude Sonnet 5

| #   | Test                                           | Type         | Baseline (no skill)                                                               | With skill                                                            |
| --- | ---------------------------------------------- | ------------ | --------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Route shields on the open OpenMapTiles stack   | Explicit     | FAIL — invents a `road_shield_1..10` scheme                                       | PASS — names `us-interstate_2` / `{network}_{ref_length}`             |
| 2   | Point symbols camouflaged on aerial imagery    | Implicit     | FAIL — halo/outline/background-shape advice only, never a saturated distinct fill | PASS — saturated accent fill (e.g. amber/teal/magenta) plus dark halo |
| 3   | Lowering road opacity to calm roads on imagery | Anti-pattern | FAIL — endorses lowering opacity                                                  | PASS — opaque and desaturated; hierarchy carried in width and value   |
| 4   | flyTo camera animation (out of scope)          | Negative     | PASS                                                                              | PASS                                                                  |

**Result: baseline 3 FAIL + 1 correct negative / with-skill 4/4 PASS — launch bar cleared.**
