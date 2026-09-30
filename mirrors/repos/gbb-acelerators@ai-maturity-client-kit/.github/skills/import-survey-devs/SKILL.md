---
name: import-survey-devs
description: Imports Developer Survey Microsoft Forms exports using the existing survey-devs tooling. Use for "import survey-devs", "importar survey de devs", "developer survey import", "importar la encuesta de desarrolladores".
---

# Skill: Import Developer Survey

Use existing survey-devs tooling. Do not mix its dimensions into assessment scoring.

## Rule for dimension names

Developer Survey outputs use `DS-D2` to `DS-D8`. Forms with older `D2` style text still parse. When the Developer Survey appears beside the v2 assessment, call its dimensions `DS-D#`.

## Form languages

The survey can be built from the PT-BR, EN or ES bank. Each bank shows the answer options in its language; `survey-devs/options.json` maps every option (and older Portuguese options with dashes) back to the same canonical option before scoring, so results do not depend on the form language. Keep the exported option text as it is; never translate answers by hand.

## Procedure

Run the repository script or Make target documented under [survey-devs/](../../../survey-devs/). Keep outputs in `output/` and report respondent count, warnings, and next step.

## Cross-reference to v2

Use Developer Survey insights to contextualize v2 questions through the crosswalk in `framework.v2.json`. Do not recompute v2 scores from survey answers.
