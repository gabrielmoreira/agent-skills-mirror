---
name: deepshow
description: Complete or continue a DeepShow creation from source materials to PageStory, rendered HTML, and independent review by orchestrating the four deepshow-* Skills. Use when the user wants the full creation journey or wants DeepShow to determine and continue from the current stage.
---

# DeepShow

DeepShow is centered on showing. It helps users show what needs to be shown and show it better.

Guide the creation journey while leaving each stage's creative judgment to its owning Skill. Inspect the conversation and existing artifacts, begin at the earliest unfinished stage, and continue without recreating correct work.

For a new creation, follow this order:

1. Invoke `deepshow-storycreator` to create `pagestory.md`.
2. Invoke `deepshow-storyauditor` to review PageStory independently.
3. Once PageStory is ready, invoke `deepshow-pagecreator` to create the rendered artifact.
4. Invoke `deepshow-pageauditor` to review the rendered result independently.

Before each stage, read the corresponding `../deepshow-*/SKILL.md` completely and follow it. If the platform supports nested Skill invocation, invoke it directly; otherwise reading and following the file is the invocation.

Respect every user decision required by the active Skill. Present an Auditor's judgment before any revision. If the user accepts a finding, return to the corresponding Creator with the current artifact as the baseline, then continue forward. Never simulate acceptance.

Resume from current work:

- With source materials but no PageStory, start with StoryCreator.
- With PageStory but no rendered page, start with StoryAuditor unless the current conversation already establishes readiness or the user asks for StoryCreator or PageCreator.
- With a rendered page, start with PageAuditor unless accepted findings or the user's request call for PageCreator revision.
- When the user names a stage Skill, honor that narrower request.

Do not duplicate stage criteria, create orchestration state, or add artifacts beyond those the Creator Skills require. Finish each turn with the current stage, what was completed, and the next user decision or stage.
