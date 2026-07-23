# Research Productivity Skills

This collection vendors 5 practical agent skills for everyday research work:
paper discovery, open-access retrieval, and literature synthesis.
It is intended as a compact productivity layer around the empirical-research
skills already in AERS.

> **Deduplication note (2026-07-22).** This collection originally vendored 18
> skills, 13 of which were byte-identical copies of skills also vendored in
> [`skills/67-econfin-workflow-toolkit/`](../67-econfin-workflow-toolkit/).
> Duplicate names produce double triggers for agents that load both
> collections, so the copies here were removed and `67-econfin-workflow-toolkit`
> is now the single canonical home for: `agent-browser`, `arxiv`,
> `chinese-quote-converter`, `command-development`, `do-agent`, `fix-chinese`,
> `markitdown`, `marp-export`, `marp-slides-creator`, `md-to-docx`,
> `skill-creator`, `web-access`, `web-research`.

## What Is Included

| Area | Skills | Use when you need to... |
|---|---|---|
| Academic discovery | [`academic-paper-search`](academic-paper-search/SKILL.md), [`nber-working-papers-api`](nber-working-papers-api/SKILL.md), [`unpaywall-api`](unpaywall-api/SKILL.md) | Search papers, retrieve metadata, locate working papers, find legal open-access full text |
| Literature synthesis | [`literature-survey-generator`](literature-survey-generator/SKILL.md), [`five-questions`](five-questions/SKILL.md) | Build cited research reports, generate literature surveys, analyze empirical economics papers through the five-question framework |

For browser automation, file conversion, slide production, Chinese text
cleanup, and skill/command authoring, see
[`skills/67-econfin-workflow-toolkit/`](../67-econfin-workflow-toolkit/).

## How To Choose

- Start with `academic-paper-search` for broad paper discovery, then use
  `unpaywall-api` when the key problem is finding a legal full-text copy.
- Use `five-questions` when the input is an empirical economics paper and the
  desired output is a structured Chinese methodological reading report.
- Use `literature-survey-generator` when the desired output is a full survey
  draft rather than a search result list.

## Licensing Notes

This is a mixed-origin collection. Check each skill folder and upstream project
before redistribution or commercial reuse. The collection intentionally does not
vendor the proprietary Anthropic document-office skills (`docx`/`pdf`/`pptx`/`xlsx`)
or the general-purpose UI design skills (`frontend-design`, `ui-ux-pro-max`);
install those from their authorized source instead of copying them into this
repository.
