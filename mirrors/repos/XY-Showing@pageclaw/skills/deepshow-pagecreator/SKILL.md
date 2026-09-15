---
name: deepshow-pagecreator
description: Turn an existing PageStory into, or revise, a static HTML Scroll Page or slide Deck through DeepShow's complete design, planning, build, and quality process.
---

# DeepShow PageCreator

Help the user better show what the PageStory needs to show by designing and creating its rendered page. Use an existing `pagestory.md`, the matching Render Target, visual references or preferences when available, and, for a revision, the existing HTML and assets plus accepted feedback. Produce `index.html` and only the assets the result needs.

If no PageStory exists, hand the task to `deepshow-storycreator`. Do not invent one or substitute sample content.

Read the matching file in `../shared/render-targets/`. Infer an evident Render Target and tell the user which one you are using. Ask only when the target is materially ambiguous.

## Understand What Must Be Shown

The PageStory governs the page's facts, meaning, certainty, attribution, emphasis, relationships, and intended assets. It is not a literal HTML outline. Faithful rendering may summarize, group, split, reorder, or emphasize material, derive navigation and neutral interface copy, and promote important material when that helps show it better. Preserve the PageStory's meaning; do not add facts, strengthen claims, change attribution, or hide material content.

PageStory headings are authoring structure, not mandatory visible labels. Design the information architecture for the chosen medium. Avoid duplicated headings, repeated introductions, and mechanically turning every Markdown section into a page section. A PageStory scene is not automatically a slide.

Judge the artifact holistically: what would make this PageStory work as a good page in this medium?

## Resolve the Creative Direction

For a new artifact, make consequential layout and visual choices explicit before designing. Use direction or delegation the user has already provided. Otherwise, invite optional reference websites or screenshots and offer a few meaningfully different, PageStory-specific directions covering both layout and visual language. Wait for the user's choice. Ask only what would materially change the result; when the user delegates, choose and state the direction.

When a visual reference is supplied, inspect its layout, typography, color, density, surfaces, motion, and interaction when possible. Explain and record the principles worth adapting and what should not be copied. A visual reference influences presentation only; it is not a content source.

## Design and Plan

For every new page, complete the design and implementation plan before building:

1. Create `assets/<name>-design.md` from the PageStory, Render Target, reference analysis, and confirmed creative direction. Record the showing hierarchy: what should be immediately visible, what explains or supports it, and what remains available for exploration.
2. Run the complete bundled `ui-ux-pro-max --design-system` process. Use its HTML/CSS-relevant design intelligence to define the information architecture, layout, palette, typography, spacing, surfaces, motion, and interaction. Append its Design System and an executable Aesthetic Implementation to the design document.
3. Invoke the bundled `writing-plans` Skill and save the executable plan as `assets/<name>-impl.md`.

Read each invoked Skill completely and follow it. The PageStory, Render Target, and confirmed user direction take precedence when specialist guidance conflicts with the artifact. Treat `ui-ux-pro-max` as the page's design foundation, not as a template to copy mechanically. Do not start implementation until both process files exist.

## Build or Revise

Build `index.html` and the assets it actually needs by executing the implementation plan. If the implementation materially departs from the plan, update the plan so it continues to describe the artifact.

When revising, treat the current HTML and assets as the baseline. Preserve effective content and design decisions, apply accepted feedback at the layer where the defect exists, and do not rewrite the PageStory to accommodate a layout problem. Repeat design or planning work only when the requested revision materially changes the structure or creative direction.

## Complete the Internal Quality Loop

After a new page is functionally complete:

1. Invoke the bundled `polish` Skill and apply its relevant improvements.
2. Invoke the bundled technical `audit` Skill and fix validated material findings.

Run every quality pass against the real rendered artifact, not source code alone. Both Skills use bundled `impeccable` preparation; follow that complete path rather than replacing it with a superficial visual check. Invoke `quieter` when the result is visually too aggressive. Invoke `critique` when meaningful design-quality concerns remain after polish and audit. Apply validated material improvements from every quality pass actually invoked. These internal passes improve the created artifact; they do not replace an independent `deepshow-pageauditor` review.

For a revision, repeat only the quality work relevant to the changed surface, then verify the complete artifact still holds together.

## Verify and Finish

Inspect the real rendered artifact for its Render Target. Confirm that the page opens, required assets and links resolve, PageStory content is present and faithful, and the experience works at relevant viewport sizes or slide aspect ratio. Exercise keyboard navigation and interactions when present, and keep focus and reading states usable. If rendering tools are unavailable, state the limitation rather than claiming visual verification.

Stop when the page deliberately expresses everything the PageStory needs to show in the chosen medium, and no evident content, design, interaction, or implementation problem interferes with that expression.

Finish in chat with the paths to `index.html`, the design document, and the implementation plan; the chosen direction; the quality passes and checks actually completed; and any material limitation. Recommend `deepshow-pageauditor` when an independent review would help.
