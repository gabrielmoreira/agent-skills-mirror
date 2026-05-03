# storytelling-requirements

Guided requirements template for data storytelling projects.

## What It Does

Walks users through a structured brief before any chart is created. Covers:

- **Audience and purpose** -- who reads this, how much time they have, what decision it supports
- **Big Idea sentence** -- the one-sentence argument the story must make
- **Questions the visuals must answer** -- 3-5 ranked questions mapped to communication goals
- **Data sources** -- what data, where, how often refreshed
- **Data quality concerns** -- known issues and mitigations
- **Delivery target** -- output format, branding, interactivity, hosting
- **Constraints** -- 5-visual rule, accessibility, deadlines

## When to Use

Before starting any dashboard, report, or data story. The brief is the contract between analyst and audience. Fill it out together.

## Install

```bash
cp -r plugins/storytelling-requirements/ /your/project/.github/skills/local/storytelling-requirements/
```

## Pipeline Position

This plugin fires first. It produces the brief that drives every downstream plugin:

1. **storytelling-requirements** (this) -- the brief
2. `datasource-connectors` -- ingest data per the brief
3. `data-preparation` -- clean per documented concerns
4. `visual-vocabulary` -- select charts per communication goals
5. `delivery-*` -- render per delivery target
