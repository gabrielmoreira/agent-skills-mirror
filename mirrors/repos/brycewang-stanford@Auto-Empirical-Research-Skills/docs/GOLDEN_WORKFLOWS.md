# Golden Workflows

These are copy-paste starting points for the most common empirical-research jobs. Use them with the local catalog when you want to move from "which skill exists?" to "what should I ask the agent to do?"

## 1. Full DID Pipeline

Use when: policy evaluation, staggered adoption, event-study plots, or applied micro DID.

Primary skills:

- [`StatsPAI_skill`](../skills/00-Full-empirical-analysis-skill_StatsPAI/SKILL.md)
- [`Full-empirical-analysis-skill`](../skills/00.1-Full-empirical-analysis-skill_Python/SKILL.md)
- [`Full-empirical-analysis-skill-Stata`](../skills/00.2-Full-empirical-analysis-skill_Stata/SKILL.md)
- [`Full-empirical-analysis-skill-R`](../skills/00.3-Full-empirical-analysis-skill_R/SKILL.md)

Prompt:

```text
Run a full DID empirical pipeline on this project. Start by writing the data contract and sample-construction log, then produce Table 1, parallel-trends/event-study evidence, main DID estimates, modern staggered-DID alternatives if treatment timing varies, placebo checks, heterogeneity, mechanism tests, and publication-ready tables/figures. Keep every identifying assumption explicit and save a replication-ready output folder.
```

## 2. IV With Weak-Instrument Diagnostics

Use when: endogenous treatment, excluded instrument, first-stage concerns, or referee asks about weak IV.

Primary skills:

- [`StatsPAI_skill`](../skills/00-Full-empirical-analysis-skill_StatsPAI/SKILL.md)
- [`aer-identification`](../skills/50-brycewang-aer-skills/skills/aer-identification/SKILL.md)

Prompt:

```text
Audit and run the IV design. State the endogenous variable, instrument, exclusion restriction, monotonicity/compliance logic, and estimand. Produce the first stage, weak-IV diagnostics, reduced form, 2SLS/LIML/GMM alternatives, overidentification tests if available, sensitivity checks, and a referee-facing paragraph explaining the identifying assumptions and remaining threats.
```

## 3. AER Submission Preflight

Use when: AER, AER:Insights, AEJ, or top-field economics submission is close.

Primary skills:

- [`aer-workflow`](../skills/50-brycewang-aer-skills/skills/aer-workflow/SKILL.md)
- [`aer-submission`](../skills/50-brycewang-aer-skills/skills/aer-submission/SKILL.md)
- [`aer-replication`](../skills/50-brycewang-aer-skills/skills/aer-replication/SKILL.md)

Prompt:

```text
Run an AER-track submission preflight. Route through the AER workflow, then check contribution framing, identification strength, abstract length, manuscript length, tables/figures, disclosure statements, cover letter, conflicts, replication README, data/code deposit structure, and any venue-specific constraints. Return a blocking/non-blocking checklist with exact files to edit.
```

## 4. Replication Package Audit

Use when: preparing a journal deposit, openICPSR upload, referee replication, or internal reproducibility review.

Primary skills:

- [`aer-replication`](../skills/50-brycewang-aer-skills/skills/aer-replication/SKILL.md)
- [`audit-replication`](../skills/41-sticerd-eee-sewage-econometrics-check/skills/audit-replication/SKILL.md)

Prompt:

```text
Audit this replication package as if you were the journal data editor. Check whether raw data, derived data, scripts, environment files, README, codebook, random seeds, output freshness, and table/figure reproduction are complete. Produce a pass/fail table, exact commands to reproduce the paper, and a prioritized patch list.
```

## 5. Chinese Academic De-AIGC Pass

Use when: Chinese thesis, journal manuscript, grant proposal, or policy report needs lower AI-writing signal while preserving academic rigor.

Primary skills:

- [`de-aigc-skills`](../skills/48-de-AIGC-skills/SKILL.md)
- [`humanize-chinese`](../skills/49-voidborne-d-humanize-chinese/SKILL.md)

Prompt:

```text
Run a Chinese academic de-AIGC pass on this section. Diagnose the visible AI-writing patterns first, then rewrite with section-appropriate academic voice, varied sentence rhythm, concrete claims, cautious causal language, and implicit cohesion. Preserve all technical terms, citations, numbers, and empirical findings. End with a before/after issue table and a 5-dimension self-score.
```

## 6. Raw Data → Full-Text Word (`.docx`) Manuscript

Use when: you want one run to go from a dataset to a finished manuscript you can open in Word — body, tables, figures and reference list in a single file. This is the default expectation for 中文期刊 submissions, 学位论文, and any co-author who edits in track-changes.

Primary skills:

- [`paper-workflow`](../skills/69-Paper-WorkFlow/SKILL.md) — the orchestrator; Stage 9 assembles and gates the `.docx`
- [`StatsPAI_skill`](../skills/00-Full-empirical-analysis-skill_StatsPAI/SKILL.md) / [`Python`](../skills/00.1-Full-empirical-analysis-skill_Python/SKILL.md) / [`Stata`](../skills/00.2-Full-empirical-analysis-skill_Stata/SKILL.md) / [`R`](../skills/00.3-Full-empirical-analysis-skill_R/SKILL.md) — the Stage 3–4 analysis backend

Prompt:

```text
Run the full empirical-paper pipeline on this dataset and deliver a finished Word manuscript. At Stage 0 set manuscript.format = markdown and manuscript.deliverable = docx, because the deliverable is Word. Lock the design before the first estimate, pass the Method Gate, then export every table in three-line form and every figure as PNG+PDF. Draft the body with the exhibits referenced by include directive — never retype a number into the prose. At Stage 9 run scripts/assemble_manuscript_docx.py to build 09_submission/main.docx and scripts/check_deliverable_contract.py --strict to verify it, and show me the gate output. Tell me the converter it used, how many tables and figures landed in the file, and anything it could not resolve.
```

Two things to know before you run it:

- **Pick the body format up front.** Markdown → `.docx` is a high-fidelity conversion; LaTeX → `.docx` is a lossy one. Changing your mind at Stage 9 means re-laying-out the whole paper, so the question is asked at Stage 0 intake.
- **Do not convert the manuscript with a bare `pandoc main.tex -o main.docx`.** Pandoc cannot resolve `\input{results/table2}` against the workspace layout, so it drops every included table silently — the file still opens, it is just missing your results, with no error anywhere. The assembler resolves the includes itself before converting, and `check_deliverable_contract.py` re-counts tables and figures from the shipped file to catch any that went missing anyway.

`pandoc` is optional. When it is absent the assembler falls back to a dependency-free builtin writer and records which converter produced the file, so a machine without pandoc still ships a Word deliverable.
