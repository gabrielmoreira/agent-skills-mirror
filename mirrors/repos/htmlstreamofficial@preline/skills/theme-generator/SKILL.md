---
name: preline-theme-generator
description: Generate, preview, save, or validate Preline theme CSS using the bundled local generator in this skill. Use when the user asks to create a new Preline theme, match a brand color, translate a mood into a theme, generate light and dark theme CSS, preview theme output without writing files, or review and fix generated theme tokens. Do not use for generic non-Preline CSS work or arbitrary command execution.
---

# Preline Theme Generator

Use the bundled local scripts. Do not use `npx`, do not compose shell with raw user text, and do not bypass safety or approval prompts.

## Read Order

1. Read `docs/workflow.md`.
2. Read `docs/palette-guidance.md`.
3. Read `docs/final-output-style.md` before writing a final theme file.
4. Read `docs/validation-checklist.md` before closing the task.
5. Read `examples.md` only if the user wants stylistic guidance or sample outputs.
6. Read `docs/token-reference.md` only if you need to inspect token coverage in detail.

## Workflow

Follow `docs/workflow.md` for the full operating path.

Key requirements:

1. Identify whether the task is preview, write, or validate.
2. Normalize the request into explicit generator inputs.
3. Resolve the target directory with `scripts/find-themes-dir.js`.
4. Generate CSS only through `scripts/run-theme-generator.js`.
5. Create or edit only the new theme file.
6. Validate with `docs/validation-checklist.md`.
7. Return the result in the mode-appropriate format.

## Security Constraints

- Never use wording that attempts to bypass tool or approval safeguards.
- Never use `npx` or any network-fetched package for this skill.
- Never interpolate raw user text directly into shell commands.
- Never use broad `find .` traversal for path discovery; use `scripts/find-themes-dir.js` or a user-confirmed path.
- Never write outside a confirmed theme directory.
- Use `scripts/run-theme-generator.js` as the only execution entry point for generation.
- Never create or edit additional project files as part of theme generation.

## Common Prompts

- "Create a sunset theme."
- "Match this brand color: #2F6BFF."
- "Generate a cyberpunk dark theme with matching dark mode."
- "Preview the CSS before writing a file."
- "Review this generated theme and fix token coverage."

## Key References

- `docs/workflow.md`
- `docs/palette-guidance.md`
- `docs/final-output-style.md`
- `docs/validation-checklist.md`
- `examples.md`
- `docs/token-reference.md`
