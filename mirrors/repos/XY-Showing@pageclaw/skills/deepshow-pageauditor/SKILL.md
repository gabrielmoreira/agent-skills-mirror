---
name: deepshow-pageauditor
description: Independently judge whether a rendered DeepShow Scroll Page or HTML slide Deck shows what its PageStory needs to show and shows it well. Use after page creation or before asking PageCreator to revise an existing artifact.
---

# DeepShow PageAuditor

Independently judge whether the rendered page shows what the PageStory needs to show and shows it well. Review before editing.

Use `index.html`, `pagestory.md` when available, the explicit or inferred Render Target, and the effective visual direction from the conversation or design document. Read the matching file in `../shared/render-targets/`. Without PageStory, review only the rendered experience and state that fidelity was not evaluated.

Prefer inspection in a user-visible browser: use the Agent App's built-in browser when available; otherwise invoke `computer-use` with the user's default browser. Fall back to another rendering capability only when neither is available. If rendered inspection is unavailable, label the review as source-only and do not claim visual validation.

Judge the artifact holistically through three connected views, not as a checklist:

- **Showing Fidelity:** Does the page preserve PageStory's facts, meaning, certainty, attribution, relationships, emphasis, and material content? Check evidence-bearing visuals as well as visible copy and metadata. Treat an omission as a problem only when it changes meaning or priority, or could mislead.
- **Showing Quality:** Do hierarchy, composition, typography, density, imagery, rhythm, and visual language give the material appropriate prominence, clarity, coherence, and character? Does the page feel specific to this PageStory rather than like a generic template?
- **Rendered Experience:** Does the artifact work in its actual Render Target? Inspect relevant narrow and wide Scroll Page views or every Deck slide at its target ratio, and exercise meaningful navigation, links, focus, and controls.

A page may be flat, dense, exploratory, sequential, or multi-purpose when that suits what it shows. Preserve effective choices; do not reward decoration, demand a single journey, or manufacture findings.

The page is ready when a careful viewer can perceive and understand everything the PageStory intends to communicate, and the rendered experience helps rather than interferes with that showing.

Respond in chat by default. Lead with a one-sentence overall judgment and next step, then report only the smallest high-leverage set of findings with evidence, impact, and ownership: StoryCreator for a PageStory defect, PageCreator for a rendering defect, and the user only when ownership is genuinely unclear. Do not score or create `page-audit.md` unless the user explicitly asks.

Do not edit while forming or presenting the independent review. If the user accepts findings or asks to apply them, read `../deepshow-pagecreator/SKILL.md` and follow its revision contract using the existing page, PageStory, and current conversation.
