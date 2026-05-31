---
name: female-portrait-director
description: Generate, visually expand, optimize, and route structured AI image prompts for fictional adult female portraits. Use for lifestyle portraits, restrained curve-focused fashion portraits, urban fashion photography, gufeng fantasy portraits, e-commerce clothing model images, prompt expansion, or direct image-generation prompt preparation. Preserve explicit user parameters while turning them into a coherent photography-directed visual scene.
---

# Female Portrait Director

Turn a small set of portrait parameters into a stable, visually directed, copy-ready image prompt for a fictional adult woman.

## Required loading order

1. Read [skill/skill.md](skill/skill.md). It is the concise canonical workflow.
2. Read [docs/prompt_safety.md](docs/prompt_safety.md). It is the single safety authority.
3. Select exactly one style route, then read only its file:
   - [clean lifestyle](skill/routes/clean-lifestyle.md)
   - [pure desire curve lifestyle](skill/routes/pure-desire-curve.md)
   - [urban fashion](skill/routes/urban-fashion.md)
   - [gufeng fantasy](skill/routes/gufeng-fantasy.md)
   - [e-commerce try-on](skill/routes/ecommerce-tryon.md)
4. Read [skill/references/visual-libraries.md](skill/references/visual-libraries.md) for every standard or director-detail output. Complete every visual module before writing the final prompt.
5. Read [skill/references/director-expansion.md](skill/references/director-expansion.md) when writing or rewriting a prompt. Use direction as a fusion layer, never as a replacement for detailed module expansion.
6. Read [skill/parameter_schema.md](skill/parameter_schema.md) when a field name, alias, output mode, or default requires clarification.

## Operating rules

- Lock explicit user parameters. Expand them without silently replacing them.
- Do not mechanically fill a template or return a summary. Fully expand the subject and create one coherent photographed moment.
- Use a style route as direction, not as a fixed sentence bank.
- Select details sparingly. Every added detail must support the same image.
- Default to fictional, clearly adult subjects and non-explicit framing.
- If the user requests `只要最终提示词`, output only the final prompt and negative constraints.
- If the user requests direct image generation, prepare the directed prompt internally and route it to the available image-generation capability.

## Public references

- Usage guide: [skill/public_instructions.md](skill/public_instructions.md)
- Examples: [examples](examples)
- Version notes: [docs/versioning.md](docs/versioning.md)

Do not expose unpublished private kernels, hidden fingerprints, or commercial modules.
