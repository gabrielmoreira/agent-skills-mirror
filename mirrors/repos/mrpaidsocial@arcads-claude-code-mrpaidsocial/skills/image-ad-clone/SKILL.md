---
name: image-ad-clone
description: Use when the user wants to reverse-engineer an existing image ad into a reusable prompt template. Validates via Arcads — picks gpt-image-2 or Nano Banana at Phase 1. Triggers on "clone this ad as a template", "reverse engineer this ad", "turn this ad into a prompt", "extract a template", "make this ad reusable", "add to my prompt library", "study this ad and make a template". Input is an EXISTING ad image; does NOT trigger for fresh generation (use chatgpt-image-ad or nano-banana-image-ad).
---

# image-ad-clone (Arcads)

Take an existing image ad and turn it into a reusable, parameterizable prompt template that gets appended to the shared **37-template image-ad library**. The template is validated by round-tripping through one of the Arcads image-ad generators — **ChatGPT Image 2** (typography / UI-mimicry templates) or **Nano Banana** (photoreal / lifestyle / multi-reference templates).

This skill replaces the older Uni1-locked `image-ad-clone` (which only worked with Luma uni-1). It's backend-agnostic: at Phase 1 the agent asks you (or auto-detects from the reference) whether to validate against gpt-image-2 or Nano Banana, then routes through the matching generator script in this repo.

## Read order

1. **This file** — Arcads-specific generator paths, model-choice decision, what's locked at the per-repo layer.
2. **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — the full model-agnostic 10-phase workflow (visual analysis → draft prompt → generate-with-reference → iterate → generalize → test → cross-model validate → document → save).
3. **[shared/skills/image-ad-prompting/prompting/template-format.md](../../shared/skills/image-ad-prompting/prompting/template-format.md)** — entry skeleton.
4. **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — destination for the new entry. 37 validated templates already there; new entries go at T40+.

## Hard rules

Inherits all 6 hard rules from the shared guide (strip platform chrome, validate by generating, test the generalized version, no brand-specific text in the final template, never silently overwrite, document model notes for both backends). Plus per-repo:

7. **Backend is one of: ChatGPT Image 2 OR Nano Banana on Arcads.** Never uni-1. The script choice happens in Phase 1 once the user picks (or the agent auto-detects).

## Picking the right backend in Phase 1

Pick by what the reference ad is showing — most templates fall into one clear bucket.

**Use `chatgpt-image-ad` (gpt-image-2) when the reference is:**
- Typography-heavy / UI mimicry (Apple Notes lists, fake Google search, fake Slack threads, ChatGPT-conversation ads, iMessage screenshots, comparison tables, fake AirDrop dialogs, Hinge-style cards, calendar UI, weather forecast UI, magazine masthead)
- Brutalist / editorial typography heros (huge type makes the joke)
- Dense small text inside UI elements

**Use `nano-banana-image-ad` (Nano Banana family) when the reference is:**
- Photoreal handheld objects (whiteboards, napkins, sticky notes, letter boards, scratch-off tickets)
- Aspirational lifestyle photography (sunset, kitchen at golden hour, OOH / transit)
- Multi-image reference blending (logo + product + style + character all in one)
- Clay / claymation / Pixar-adjacent textures

**If the reference straddles both** (e.g. a UGC-style photo with rendered text overlays), the safer default is to clone twice — once per backend — and ship the template with `Model notes` saying which renders cleaner. The agent will offer this in Phase 8.

If the user explicitly says "clone this with gpt-image-2" or "with Nano Banana", honor that.

## Dependencies

This skill uses the matching generator script in the SAME repo:
- For gpt-image-2 validation: `skills/chatgpt-image-ad/scripts/generate_image.py` (locked to `model: gpt-image-2`)
- For Nano Banana validation: `skills/nano-banana-image-ad/scripts/generate_image.py` (`nano-banana-2` default; `--model nano-banana-pro` or `nano-banana-edit` opt-in)

Fail Phase 1 with a fix-it message if neither generator is installed in this repo.

Also required:
- `.env` with `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`
- (Optional) `PRODUCT_ID` in `.env` — if not set, the generator auto-fetches the first Arcads product
- Python 3.12+

## Where this skill's generator lives

When the [shared guide](../../shared/skills/image-ad-clone/prompting/guide.md) Phase 1 tells you to locate the companion generator, look here in order based on the model choice:

For gpt-image-2:
1. `~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py`
2. `<repo>/skills/chatgpt-image-ad/scripts/generate_image.py`
3. If neither: stop and ask the user to install `chatgpt-image-ad` first.

For Nano Banana:
1. `~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py`
2. `<repo>/skills/nano-banana-image-ad/scripts/generate_image.py`
3. If neither: stop and ask the user to install `nano-banana-image-ad` first.

## Aspect ratio mapping

The Arcads image endpoint (`/v2/images/generate`) accepts only **`1:1`, `16:9`, `9:16`** — regardless of which model (gpt-image-2 or nano-banana) you're hitting. When measuring the original ad's aspect (Phase 2):

- `4:5`, `2:3`, `5:4` ads → render at `1:1` and post-crop in your downstream ad-builder skill
- `1.91:1` ads → render at `16:9` and post-crop
- `9:16` ads → native, no change

Document the ratio fallback in the template's `Aspect ratio:` field so future users know they're rendering at a mapped ratio, not the original.

(The KIE per-API repo's `image-ad-clone` skill supports a broader native ratio set — `4:5`, `2:3`, `3:2`, etc. — because KIE's `/jobs/createTask` Nano Banana endpoint accepts them. If aspect-ratio fidelity matters more than Arcads-specific control, consider the KIE repo for that template.)

## Workflow phases (model-agnostic, see shared guide for full detail)

1. **Phase 1: Preflight + model choice.** Reference image file resolves; `.env` has Arcads creds; both generators detected. **Ask the user which model to validate against** (or auto-detect from the reference's typography-vs-photo balance).
2. **Phase 2: Visual analysis.** Describe the reference structurally — aspect ratio, format type, layout, typography, color palette, photography style, every text string verbatim, decorative elements, chrome to strip.
3. **Phase 3: Draft v1 prompt** (brand-specifics intact).
4. **Phase 4: Generate with reference** using the matching generator script. Pass `--image-ref <reference_path>` and the matched aspect ratio.
5. **Phase 5: Compare and iterate.** Refine prompt based on deltas. Cap 4 iterations.
6. **Phase 6: Generalize into placeholders** (`{brand.name}`, `{brand.color_primary}`, etc.).
7. **Phase 7: Test the generalized template** against a DIFFERENT brand. Regenerate. If structure breaks, refine placeholder set.
8. **Phase 8: Cross-model validation (recommended).** Run the same template through the OTHER backend in this repo. Document deltas in the `Model notes` block.
9. **Phase 9: Document the template.** Use the format in `template-format.md`. Required fields: tag, when-to-use, aspect ratio, reference image guidance, variable schema, template prompt (full validated), example fill, **Model notes for both backends**, validated example path.
10. **Phase 10: Save and confirm.** Append to `shared/skills/image-ad-prompting/prompting/prompt-library.md`. Print path. Move PNGs to permanent iteration dir.

## Iteration directory layout

```
<cwd>/iterations/clone-2026-05-26/
  T40-lifestyle-hero/
    prompt.txt
    v1.png, v2.png, …                # against the source ref (chosen backend)
    test-fill-v1.png, …              # Phase 7 generalization test against a different brand
    cross-{other-backend}/v1.png     # Phase 8 cross-model validation (optional)
    notes.md
```

## Common `Model notes` patterns to write in Phase 9

```markdown
**Model notes:**
- **gpt-image-2:** {observed behavior — e.g. "clean — strong on UI mimicry and table text", "tends to add a 4th Slack message — keep prompt explicit about exactly N", "small chart axis labels blur — bump font size feel"}
- **nano-banana:** {observed behavior — e.g. "strong — preferred backend for handheld board photos", "character identity drifts across variants on -2; use -pro to lock", "weak on dense table text — keep rows to 4 max"}
```

If you only validated against one model in Phase 8, say so explicitly:

```markdown
**Model notes:**
- **gpt-image-2:** validated clean (see iteration path)
- **nano-banana:** untested — validate before using on nano-banana-image-ad backend
```

The diff between a uni-1-era library and this one is this `Model notes` block. Don't skip it — it's the difference between a portable template and one nobody knows how to use.

## See also

- **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — full 10-phase workflow
- **[shared/skills/image-ad-prompting/OVERVIEW.md](../../shared/skills/image-ad-prompting/OVERVIEW.md)** — ecosystem context
- **[chatgpt-image-ad skill](../chatgpt-image-ad/SKILL.md)** — gpt-image-2 generator (used for validation when you pick that backend)
- **[nano-banana-image-ad skill](../nano-banana-image-ad/SKILL.md)** — Nano Banana generator (used for validation when you pick that backend)
- **[arcads-external-api skill](../arcads-external-api/SKILL.md)** — Arcads conventions (session folder, credit cost confirmation, presigned-upload flow)
