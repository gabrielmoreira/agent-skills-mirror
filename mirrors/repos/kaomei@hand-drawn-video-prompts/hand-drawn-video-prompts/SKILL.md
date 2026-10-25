---
name: hand-drawn-video-prompts
description: Use when a user provides a Chinese voiceover script and needs copy-ready vertical B-roll prompts or an assembled 9:16 video in a modern Q-version hand-drawn crayon style.
---

# Hand-Drawn Video Prompts

Turn a Chinese voiceover script into executable 9:16 B-roll shots. Depending on the requested mode, provide copy-ready prompts or continue through the available video, voiceover, caption, timeline, and export workflow.

The default visual language is modern Q-version hand-drawn crayon illustration on a fixed warm-white canvas, `#F8F6EF`.

## Modes

- **Prompt mode:** output shot breakdowns, Nano Banana/Flow prompts, and Chinese on-image keywords without calling media-generation or export tools.
- **Complete-video mode:** when the user explicitly asks for a complete video, read [references/automation-workflow.md](references/automation-workflow.md) and use the currently available video, voiceover, transcription/caption, timeline, and export tools.

If the user supplies a full script and asks to make a video without specifying a mode, use complete-video mode. If they ask only for prompts, use prompt mode.

## Non-negotiable visual rules

- Use vertical 9:16 composition and a solid warm-white canvas with exact base color `#F8F6EF`.
- Allow only extremely subtle, low-contrast paper grain. Never use black, gray-brown, beige gradients, colored backgrounds, vignettes, or drifting background colors.
- Use thick imperfect black hand-drawn lines, sunflower yellow, cobalt blue, and tomato red.
- Keep people natural and restrained in Q-version proportions. Do not use giant heads, tiny bodies, bulging eyes, photorealistic faces, 3D rendering, cyber HUDs, or vintage newspaper styling.
- Use two to four readable visual groups and leave generous upper and lower breathing room.
- Keep subtitles out of the generated artwork's lower area.

## Chinese keyword mode

By default, place the requested short Chinese keyword directly on the paper or beside the relevant object:

- Use two to eight Chinese characters in small, clear hand-drawn lettering.
- Keep the text in a top or side safe area, never in the bottom subtitle area.
- Keep the text block under 10–12% of the frame height.
- Do not use sticky notes, label cards, stickers, rounded text boxes, title panels, or isolated white cards.
- In video prompts, keep the lettering fixed and legible. Do not let it rotate, melt, run, or morph.
- For long text, dates, amounts, company names, and exact claims, use a deterministic subtitle or graphic layer instead.

When text accuracy is uncertain, provide both a recommended text version and a text-free safe version.

## Entity accuracy

When flags, companies, logos, or public figures appear, create an explicit entity anchor and state the accuracy boundary:

- **Flags:** specify the country, official structure, colors, proportions, and key symbols. Never substitute a similar flag or a random colored banner. Use a reference image or original asset overlay when exactness matters.
- **Companies and logos:** use industry, product, device, and brand-color cues. Do not ask the model to recreate an exact logo from memory. Use a supplied original logo as a reference or post-production layer when necessary.
- **Public figures:** use a clearly non-photorealistic Q-version caricature with identity cues such as hairstyle, glasses, clothing, pose, and props. Do not bypass safety restrictions or create realistic face clones.
- **Numbers and dates:** reserve exact figures for deterministic text layers whenever possible.

Always include an entity accuracy note in the output.

## Workflow

1. Estimate the narration duration. Default to one semantic shot every 4–6 seconds.
2. Split on argument turns, causal changes, examples, and conclusions rather than punctuation alone.
3. Give each shot one clear visual metaphor.
4. Write a complete, self-contained template for every shot; do not rely on “same as above.”
5. Run the quality check below before delivering.

## Required output template

```text
Shot 01
Source narration:
Suggested duration:
Visual metaphor:
Chinese on-image keyword:

[Flow image prompt]
<complete, self-contained English prompt>

[Flow image-to-video prompt]
<complete, self-contained English prompt>

[Entity accuracy note]
<reference-image or deterministic-layer guidance>
```

## Prompt requirements

Every image prompt must independently state: vertical 9:16; solid warm-white canvas, exact base color `#F8F6EF`; concrete people and objects; an executable action; the visual metaphor; spatial relationships; thick black hand-drawn lines; the three-color palette; a subject group occupying roughly 60–70% of the width; and upper/lower breathing room.

Every image-to-video prompt should default to about five seconds and use the supplied finished still as the final composition. For Flow First + Last, state that the blank warm-white paper is the First Frame and the finished still is the Last Frame. Use a locked camera, rigid paper cutouts, tactile paper stop-motion, no camera drift/zoom/parallax, no lip sync, no added characters/logos, and no audio.

## Quality check

- Every shot has one core meaning, a reasonable duration, and all required fields.
- Every prompt is self-contained and consistent in aspect ratio, exact background color, linework, and palette.
- Exact numbers, dates, logos, flags, and long text are marked for deterministic treatment.
- Public figures are handled as non-photorealistic Q-version illustrations without safety bypasses.
- No API configuration, complex version management, or unnecessary confirmation gates are added to prompt mode.

中文参考：[SKILL.zh-CN.md](SKILL.zh-CN.md)
