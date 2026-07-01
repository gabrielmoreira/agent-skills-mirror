---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
argument-hint: "[component, page, or application to build]"
user-invocable: true
---

# Frontend Design

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. This client has already rejected proposals that felt templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take one real aesthetic risk you can justify.

## Ground it in the subject

If the brief does not pin down what the product or subject is, pin it yourself before designing: name one concrete subject, its audience, and the page's single job, and state your choice. If there's any information in your memory about the human's preferences, context about what they're building, or designs you've made before, use that as a hint. The subject's own world, its materials, instruments, artifacts, and vernacular, is where distinctive choices come from. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is a thesis. Open with the most characteristic thing in the subject's world, in whatever form makes sense for it: a headline, an image, an animation, a live demo, an interactive moment. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the template answer; use that only if it is truly the best option.

Typography carries the personality of the page. Pair display and body faces deliberately, not the same families you would reach for on any other project, and set a clear type scale with intentional weights, widths, and spacing. Make the type treatment itself a memorable part of the design, not a neutral delivery vehicle for the content.

Structure is information. Structural devices, numbering, eyebrows, dividers, and labels should encode something true about the content, not decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that is only appropriate if the content actually is a sequence, such as a real process or a typed timeline where order carries information the reader needs. Question whether choices like numbered markers actually make sense before incorporating them.

Leverage motion deliberately. Think about where and if animation can serve the subject: a page-load sequence, a scroll-triggered reveal, hover micro-interactions, ambient atmosphere. An orchestrated moment usually lands harder than scattered effects; choose what the direction calls for. Sometimes less is more, and extra animation can make the design feel AI-generated.

Match complexity to the vision. Maximalist directions need elaborate execution; minimal directions need precision in spacing, type, and detail. Elegance is executing the chosen vision well.

Consider written content carefully. Often a design brief may not contain real content, and it is up to you to come up with copy. Copy can make a design feel as templated as the design itself. See the section on writing below for more guidance.

## Process: brainstorm, explore, plan, critique, build, critique again

For calibration: AI-generated design right now clusters around three looks:

1. A warm cream background near `#F4F1EA` with a high-contrast serif display and a terracotta accent.
2. A near-black background with a single bright acid-green or vermilion accent.
3. A broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns.

All three are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly; the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, do not spend that freedom on one of these defaults. A human designer balances doing what they are good at with taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the user's design brief:

- **Color**: a compact token system with 4-6 named hex values.
- **Type**: typefaces for 2+ roles, such as a characterful display face used with restraint, a complementary body face, and a utility face for captions or data if needed.
- **Layout**: one-sentence layout concepts and ASCII wireframes to ideate and compare.
- **Signature**: the single unique element this page will be remembered by, embodying the brief in an appropriate way.

Then review that plan against the brief before building. If any part reads like the generic default you would produce for any similar page rather than a choice made for this specific brief, revise that part and say what changed and why. Only after confirming the relative uniqueness of the design plan should you write the code, following the revised plan exactly and deriving every color and type decision from it.

When writing the code, be careful with CSS selector specificity. It is easy to generate CSS classes that cancel each other out, especially with a type-based selector like `.section` and an element-based selector like `.cta`. This often happens with paddings and margins between sections.

Do much of this planning and iteration in your thinking, and only show ideas to the user when you have higher confidence they will delight them.

## Restraint and self-critique

Spend your boldness in one place. Let the signature element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected. Critique your own work as you build, taking screenshots if your environment supports it. Before leaving the design, remove one accessory.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand, and therefore easier to use. They are design material, not decoration. Bring the same intentionality to copy that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's side of the screen. Name things by what people control and recognize, never by how the system is built. A person manages notifications, not webhook config. Describe what something does in plain terms rather than selling it. Being specific is always better than being clever.

Use active voice as default. A control should say exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors do not apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the register conversational and tuned: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each element do exactly one job. A label labels, an example demonstrates, and nothing quietly does double duty.
