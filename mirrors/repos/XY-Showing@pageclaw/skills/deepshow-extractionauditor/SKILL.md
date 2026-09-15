---
name: deepshow-extractionauditor
description: Independently review whether a pagestory.md faithfully restores one source document’s information, relationships, and intended uses. Use after deepshow-storyextractor when extraction loss, misreading, or unclear recovered structure needs correction.
---

# DeepShow ExtractionAuditor

Review a PageStory against its single source document, rendered pages when needed, and its referenced assets. This review checks extraction quality; StoryAuditor separately judges whether a PageStory serves the user’s later presentation goal.

Read the source directly and form an independent judgment before editing. Check whether its information has been retained faithfully, including secondary material, numerical and symbolic content, formulas, attribution, links, resources, and their correspondence. Distinguish an issue already present in the source from one introduced during extraction.

Check that relationships conveyed by placement, columns, pagination, hierarchy, grouping, connections, and text-image combinations remain understandable in Markdown. Faithful contextual repair, reconnected text, reformatted tables, and explained diagrams are appropriate when they make the source independently readable. Flag a change only when it loses meaning, makes a relationship unclear, or introduces meaning the source does not support.

Judge whether examples, exercises, templates, promotional copy, resources, images, tables, and formulas still serve their source roles. Meaningful repetition, short phrases, and placeholders may need to remain. Choose the suitable Markdown treatment for an image or graphic based on the information and use it carries; neither verbatim image retention nor text conversion is universal.

Respond in chat by default. Lead with `Ready to use` or `Return to StoryExtractor`, give the smallest material finding set with enough source evidence to locate it, and state the next action. Report material findings when present, without manufacturing issues. Provide scores or save an audit file only when the user explicitly asks.

Keep the review read-only. Once the user accepts a finding or authorizes correction, read `../deepshow-storyextractor/SKILL.md` and revise the existing PageStory and assets under that contract, preserving unaffected content. Finish when the PageStory and its referenced assets preserve the source’s information, relationships, and uses well enough for a reader to understand them without the original layout.
