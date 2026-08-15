---
name: svg-quality-audit
description: >-
  Audits a folder of SVGs for XML integrity, executable-script risk, and visual
  quality via Chrome headless render plus a free vision-language model. Use when
  asked to analyze, check, or audit SVG quality, or before shipping a generated
  SVG batch. Not for creating or restyling SVGs (use svg-creator). Never claim
  visual quality from XML structure alone.
version: 1.0.1
---

# SVG quality audit

## When to Use
- User wants a quality read on a collection of SVGs.
- Before committing / shipping a generated SVG batch (pairs with the project's vision-verify-before-ship rule).
- Diagnosing "why do these render wrong / look like sludge".

## Prerequisites
- **Target folder:** the SVG directory the user named. Do not assume a private vault path.
- **Project rules:** if the repo has SVG shipping rules, read those first.
- **Vision gap:** many agents cannot judge binary PNGs by reading pixels. Render each sample SVG → PNG (Chrome headless is reliable) and score the PNG with a vision-language model (OpenRouter free vision or local Ollama). Do not claim visual quality from XML structure alone.

## Procedure

**Phase 1 — Structural scan (100% of files, fast, no render needed).**
1. Run `scripts/structure_scan.py <dir>`.
2. Review the output: valid-XML count, drawable-shape distribution, gradient/filter/text/image counts, and defect buckets. Pure stdlib, no deps.

**Phase 2 — Render sample (only what you'll vision-judge).**
1. Run `scripts/render_vision_judge.py --render-only <dir> <out>`.
2. This renders each SVG to a 400×400 PNG with a checkerboard (transparency) backdrop via Chrome headless. Resumable.

**Phase 3 — Vision judge (the ONLY way to catch visual defects structure misses).**
1. Run `scripts/render_vision_judge.py --judge <out>`.
2. Scores each PNG 1–10 with a strict rubric (`SCORE:` / `FLAGS:` / `WHY:`) via the free VLM. Resumable, per-call timeout, 429 backoff, incremental JSON. Run large passes in the background.

**Working recipe:**
- **OpenRouter free vision:** list live free vision models via `GET https://openrouter.ai/api/v1/models` and pick one with image input. Pass the key via env `OPENROUTER_API_KEY`. Never print the key. Never read a redacted placeholder from a local config and treat it as live.
- **Local Ollama:** a local vision-capable model is fine for small samples; flaky for large batches under VRAM pressure.
- Load `references/free-vision-endpoints.md` when configuring VLM endpoints.

**Defect taxonomy:**
- Load `references/svg-defect-taxonomy.md` for per-defect counts, example files, and recovery one-liners.
- **Escape-bug (dominant):** literal `\n` / `\t` / `\"` where real newlines / quotes belong (JSON / `repr()` serialization bug). ~735 recover by un-escaping; Chrome already renders them. NOT corruption.
- **JSON-LD `<script>` is BENIGN.** `type="application/ld+json"` = schema.org metadata. The "65% have `<script>`" alarm is false — 0 executable JS. ALWAYS separate `application/ld+json` from `text/javascript` / `application/javascript`.
- **LLM-junk-after-`</svg>`:** model commentary leaked after the close tag. Renders but must be trimmed for a clean library.
- **Duplicate attributes** (e.g. two `opacity=`), **mismatched tags**, **undefined entities** — invalid XML, fix required.
- **Structure ≠ visual quality:** a file can be valid XML yet score 3 ("empty / basic shapes"). Vision is mandatory for a real quality verdict.

## Pitfalls
- ElementTree's strict parser over-flags: "invalid token at line 1 col 38" is almost always the escape-bug, NOT corruption. Test un-escape recovery before declaring a file dead.
- Do NOT claim "done / shipped" from structure alone — render + vision a stratified sample first (vision-verify-before-ship rule).
- agy/* generation needs heavy handholding or it emits low-quality / near-duplicate sludge — if you regenerate fixes via Jules / agy, over-specify the brief (subject, palette, shape budget, no `Math.random()`, no template recycling).
- Free VLM tiers are rate-limited; loop with 429 backoff and run large passes in the background.
- The escape-bug un-escape is a **no-op on clean files** (verified: 186 clean files stayed valid after the replace) — safe to apply across the whole set.

## Verification
- Confirm `scripts/structure_scan.py` outputs valid-XML count and defect buckets.
- Confirm `scripts/render_vision_judge.py --render-only` generates 400×400 PNGs in the output directory.
- Confirm `scripts/render_vision_judge.py --judge` outputs `SCORE:`, `FLAGS:`, and `WHY:` for the rendered PNGs.
- Ensure no file is declared "dead" without testing un-escape recovery for the escape-bug.
- Ensure no executable JS is falsely flagged from JSON-LD `<script>` tags.
