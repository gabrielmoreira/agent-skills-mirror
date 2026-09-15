---
name: paper2html
description: Use when turning an academic paper PDF/arXiv/OpenReview page/local LaTeX source into a single-file Chinese HTML deep-reading page, especially when the user wants a Cheat-Sheet style explanation, KaTeX formulas, figure/table evidence, validation, or a publishable research page.
---

# Paper2HTML

## Overview

Create one self-contained Chinese `index.html` that lets the reader understand the paper without reopening the PDF. Open with a compact, source-faithful story, then deliver a clear Cheat-Sheet page with evidence boundaries, KaTeX formulas, complete figure coverage, reviewer-level analysis, and no decorative complexity.

Every completed page ends its substantive analysis with all seven MIT **Other Discussion Roles**. Each role shows the original English prompt verbatim and a source-grounded Chinese response.

Use scripts first. Keep this skill as workflow and quality gates, not a long prompt.

## Scripted Path

```bash
cd /path/to/paper2html

# 1) Create workspace, notes, and starter index.html
python scripts/bootstrap_paper2html.py \
  --title "Paper Title" \
  --slug paper-slug \
  --out /path/to/output/paper-slug-html-YYYYMMDD \
  --arxiv 2504.07952 \
  --github https://github.com/org/repo \
  --publish-to topic/series/paper-slug

# 2) Inventory TeX/source when available
python scripts/tex_inventory.py \
  /path/to/output/source/unpacked \
  --out /path/to/output/notes/tex-inventory.md \
  --json /path/to/output/notes/tex-inventory.json

# 3) Optimize figures and create data URIs for single-file HTML
python scripts/optimize_paper_images.py \
  paper_figures/*.pdf paper_figures/*.png \
  --out-dir /path/to/output/assets/optimized \
  --width 1600 \
  --data-uri-json /path/to/output/assets/data-uris.json

# 4) Optional: ask Gemini for a visual draft on a copy
scripts/gemini_frontend_pass.sh \
  /path/to/output/index.html \
  --reference /path/to/good-reference.html \
  --timeout 240

# Inspect the Gemini request without making a model call
scripts/gemini_frontend_pass.sh /path/to/output/index.html --dry-run

# 5) Validate the completed page
scripts/validate_paper_html.sh /path/to/output/index.html --public

# 6) Optional publication through a compatible research-page importer
PAPER2HTML_BLOG_ROOT=/path/to/blog \
PAPER2HTML_PUBLIC_BASE_URL=https://example.com/research \
scripts/publish_paper2html.sh \
  /path/to/output/index.html \
  --to topic/series/paper-slug \
  --title "Paper Title" \
  --description "One sentence summary" \
  --tags "paper-reading,agent" \
  --ship
```

## Workflow

1. **Freeze the source boundary**
   - Treat user input as a locator for one paper, then look for public adjacent artifacts: arXiv source/PDF, OpenReview, proceedings, project page, GitHub, appendix, dataset cards, and model cards.
   - Run `bootstrap_paper2html.py` when starting from a known title, arXiv id, or GitHub repository. Otherwise manually create the same `notes/source-boundary.md`.
   - Separate reading sources from public evidence sources. Public pages must not expose local paths, private filenames, review metadata, private prompts, or run logs.
   - If public publishing is requested and no public paper source exists, generate private HTML only.

2. **Extract the material**
   - Prefer TeX/source packages over PDF-only reading. Run `tex_inventory.py` when source exists.
   - Build a material pack covering metadata, outline, claims, notation, equations, algorithms, experiments, appendix details, and public links.
   - Use PDF rendering for visual verification and figure/table placement. `pdftotext` is only an auxiliary index.
   - Record every discovered paper figure in `notes/figure-table-map.md`. For each item, capture its source/page, original caption, what the visual itself shows, and either the exact `data-figure` basename used in HTML or an explicit waiver reason.
   - Include every paper figure by default. Figures that do not fit the main narrative go in a `完整图谱 / Figure Gallery` appendix section.
   - Extract reproducibility details: datasets, splits, models, baselines, metrics, prompts, tool/prover/solver versions, decoding, timeouts, retries, and appendix-only settings.

3. **Ground against the human knowledge boundary**
   - Before writing, complete `notes/grounding-anchor.md` using public sources beyond the focal paper's related-work section.
   - Record: the prior human knowledge boundary with `solved / partially solved / unsolved` status and public links; the paper's real contribution relative to that boundary; and a short writing anchor showing which sections establish the contribution versus repeat source-faithful background.
   - If a claim rests only on model memory, mark it as unverified. Do not manufacture novelty for incremental work; for surveys, describe the organizational contribution.
   - The grounding anchor is an internal working note. Public links used from it must also appear in `Reference / Evidence`.

4. **Write the page**
   - Use `assets/cheatsheet-template.html` as the visual skeleton and organize the page around the grounding anchor's real-contribution statement, not the paper's narrative order alone.
   - Use the fixed section order unless the paper requires a small adjustment: `先讲一个故事`, `故事与技术如何对应`, `先给结论`, `研究动机`, `数学表示及建模`, `算法流程/方法`, `实验设计`, `实验结果`, `我的评论`, `One More Thing`, `Other Discussion Roles / 其他讨论角色`, `Reference / Evidence`.
   - Open with a compact protagonist/system, goal, obstacle, insufficient obvious explanation, and the paper's turning point. Prefer a sourced discovery or experiment; otherwise label the opening as a thought experiment or teaching analogy. Never invent author dialogue, motivation, chronology, or results.
   - Follow the story with a short bridge mapping its actors and conflict to the paper's actual concepts, method, and evidence, clearly distinguishing analogy from source fact.
   - Add a short version note near the top with reading basis and retrieval date, without local paths.
   - Bind each major claim to evidence and state boundaries when evidence does not support a stronger conclusion.
   - Use Chinese by default; keep paper terms, model names, datasets, commands, and identifiers in English.
   - Use KaTeX for all math. Inline math uses `\(...\)` or `$...$`; block math uses `$$...$$` or `\[...\]`.
   - Captions may claim only what the displayed figure/table itself shows. Put broader interpretation in a nearby callout.
   - Mark every included paper figure as `<figure data-figure="basename.ext">`.
   - `One More Thing` is for bounded research insight, not unsupported extrapolation.
   - Read `references/other-discussion-roles.md` and follow its rendering contract. The discussion-role section is mandatory, is the final substantive section, and may be followed only by `Reference / Evidence`.
   - Include all seven roles exactly once and in source order: `Scientific Peer Reviewer`, `Archaeologist`, `Academic Researcher`, `Industry Practitioner`, `Hacker`, `Private Investigator`, `Social Impact Assessor`.
   - Preserve every role's complete English prompt and exact `data-discussion-role` marker. Responses must perform the prompt rather than summarize it, distinguish facts from hypotheses, and never fabricate newer papers, author history, implementation runs, product facts, or impact claims.
   - Do not contact authors or any external person without explicit user approval, even though the preserved Private Investigator prompt mentions contact.

5. **Use the optional Gemini visual pass carefully**
   - `gemini_frontend_pass.sh` writes `index.gemini-draft.html`; it must never edit the source HTML.
   - Gemini may improve hierarchy, spacing, typography, callouts, responsive behavior, and component composition. It is not a factual source.
   - The script attaches the source boundary, material pack, TeX inventory, figure map, and grounding anchor when present. It requires preservation of role markers, verbatim prompts, figure markers, and evidence boundaries.
   - The primary agent must review and selectively merge useful visual changes back into `index.html`.

6. **Validate**
   - Run `scripts/validate_paper_html.sh <index.html>` from this skill.
   - It checks placeholders, public-path leaks, all seven role markers and verbatim prompts, response substance, final-section order, figure inventory/waiver coverage, KaTeX rendering, desktop/mobile screenshots, and mobile horizontal overflow.
   - Treat skipped browser checks as partial verification, not a full pass.
   - Deliver user-visible artifacts through the active collaboration channel when supported, and report the validation result.

7. **Publish**
   - The optional publisher requires a target repository with a compatible `pnpm research:publish` command and `PAPER2HTML_BLOG_ROOT`.
   - Use `--check` for import plus local validation without commit/push.
   - `--ship` validates, imports, formats, checks, commits, pushes, watches deployment, and verifies the public URL. Use it only when the user explicitly requested those history and remote changes.
   - The target repository owns staging, commit, and deployment behavior.

## Template

- `assets/cheatsheet-template.html` is the fixed visual skeleton. Copy it into the output directory, then fill content and embed images.
- Keep the template restrained and reading-focused. Do not turn paper pages into marketing landing pages.
