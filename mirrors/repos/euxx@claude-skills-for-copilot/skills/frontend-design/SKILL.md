---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
argument-hint: "[component, page, or application to build]"
user-invocable: true
---

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliche or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there is any information in your memory about the client's preferences or context about what they are building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from - a design for a toy for girls aged 8-11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that is truly the best option.

Typography carries the personality of the page. You do not need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:

- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, and labels encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that is only appropriate if the content actually is a sequence, such as a stepped process or a timeline. Before adding numbered markers, check that the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment - one page-load sequence or one reveal - lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action, such as opening, expanding, or confirming, is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it is up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the section on writing below for more guidance.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:

1. A warm cream background near `#F4F1EA` with a high-contrast serif display and a terracotta or warm-clay accent, often near `#D97757`.
2. A near-black background with a single bright acid-green or vermilion accent.
3. A broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns.
4. The SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow such as `rgba(0,0,0,.1)` under each, and gradient washes as decoration.
5. Template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots; labels built as `WORD - fragment`; tinted near-black such as `#0B0B0B` or `#111` standing in for black; a monospace face for small data labels; or an arrow appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly - the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, do not spend that freedom on one of these defaults. As with a hired human designer, there is often a careful balance between doing what you are good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.

- **Color**: describe the core base palette as 4-6 named hex values.
- **Type**: the typefaces and their roles.
- **Layout**: a layout concept using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance: left aligned, center aligned, or justified.
- **Principles**: the high-level guidance for what makes this page unique.

Then review that plan against the brief before building. If any part reads like the generic default you would produce for any similar page rather than a choice made for this specific brief, revise that part, say what changed and why, and only then write the code. Follow the revised plan and derive every color and type decision from it.

When writing the code, be careful with CSS selector specificity. It is easy to generate CSS classes that cancel each other out, especially with a type-based selector like `.section` and an element-based selector like `.cta`. This can happen often with padding and margin between sections.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, and built with harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it. Before leaving the design, remove one accessory.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors do not apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.
