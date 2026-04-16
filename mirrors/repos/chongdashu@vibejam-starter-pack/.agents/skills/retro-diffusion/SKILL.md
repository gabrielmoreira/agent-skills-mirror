---
name: retro-diffusion
description: "Use Retro Diffusion for pixel-art image generation, img2img edits, spritesheets, and animation experiments such as platformer walk cycles, turnarounds, and action sheets from reference images."
metadata:
  short-description: "Retro Diffusion image and animation workflows."
---

# Retro Diffusion

Use this skill when the user wants to generate pixel-art images or animation sheets through Retro Diffusion, especially when the task involves reference-image-driven character work like side-view platformer walks, turnarounds, or action cycles.

## Philosophy: Match The Style To The Asset Contract

Retro Diffusion does not expose a provider-agnostic model marketplace like fal. The important control is the `prompt_style`, and each style implies a specific asset contract:

- some styles are general image models
- some are spritesheet-oriented
- some are fixed-size animation generators
- some require an input frame and work best only from neutral poses

The right way to use Retro Diffusion is:

- choose the style that matches the asset shape you want
- respect the style's size contract
- pass a clean RGB reference when using `input_image`
- treat cost checks and output capture as first-class workflow steps

**Before generating, ask:**
- Are we making a single image, a spritesheet, or an animation?
- Is this a freeform prompt, a reference-driven edit, or a starting-frame animation?
- Does the selected `prompt_style` impose a fixed frame size?
- Do we want a GIF preview, a PNG spritesheet, or both?

**Core principles**:
1. **Style first, prompt second**: in Retro Diffusion, `prompt_style` is the mode selector, not just a flavor tweak.
2. **Respect size contracts**: `animation__four_angle_walking` is a `48x48` workflow, `animation__8_dir_rotation` is `80x80`, and advanced animations should match the starting frame size.
3. **Reference cleanliness matters**: `input_image` should be RGB with no transparency, and the prompt should describe the reference rather than assume the API will infer everything.
4. **Capture the sheet, not just the preview**: for sprite work, prefer `return_spritesheet: true` so downstream analysis stays deterministic.
5. **Prompt shorter than you think**: for advanced animations, keep prompts extremely terse. The service expands action text internally, and long prompts can fail server-side even when your raw prompt looks reasonable.
6. **Treat completion as artifact-based, not CLI-message-based**: a run can succeed even if the local wrapper times out, drops the final response, or never prints a clean completion message.

## What This Skill Provides

- A portable Retro Diffusion harness bundled with the skill for:
  - text-to-image
  - img2img-style runs via `input_image`
  - multi-reference runs via `reference_images`
  - fixed-style animation and spritesheet generation
- A generic inference runner that:
  - sends requests to `POST https://api.retrodiffusion.ai/v1/inferences`
  - supports cost-only checks via `check_cost: true`
  - writes normalized run manifests and decoded outputs
- A batch runner for repeatable experiment configs
- Model/style presets for commonly useful Retro Diffusion modes:
  - `rd-pro-platformer`
  - `rd-pro-edit`
  - `rd-pro-spritesheet`
  - `rd-fast-character-turnaround`
  - `rd-plus-character-turnaround`
  - `animation-four-angle-walking`
  - `animation-8-dir-rotation`
  - `animation-walking-and-idle`
  - `rd-advanced-animation-walking`
  - `rd-advanced-animation-idle`
  - `rd-advanced-animation-attack`

## Working With Retro Diffusion

### API Shape

- Endpoint: `POST https://api.retrodiffusion.ai/v1/inferences`
- Auth header: `X-RD-Token: YOUR_API_KEY`

Outputs can include:

- `base64_images`
- `output_urls`
- `balance_cost`
- `remaining_balance`

Important operational rule:

- do not assume a run failed just because the terminal process returned no final success line
- Retro Diffusion runs can complete while the local caller reports an indeterminate state
- before retrying, check the intended output folder for:
  - new image artifacts
  - run metadata JSON
  - file modification times newer than the run start
- only classify a run as failed after artifact verification, not from missing stdout alone

Animations normally come back as transparent GIFs. Add `return_spritesheet: true` when you want a PNG sheet instead.

### Reference And Animation Guidance

For `input_image`:

- convert to RGB first
- remove transparency
- do not include the `data:image/png;base64,` prefix
- mention what the reference is in the prompt
- prefer an explicit prepared RGB reference image over silent RGBA-to-black conversion

For side-view platformer walks:

- prefer `rd_advanced_animation__walking` first when you already have a neutral starting frame
- keep `width` and `height` equal to that starting frame
- use `frames_duration` deliberately instead of taking the default
- ask for in-place locomotion if you want extractable frames instead of a traveling character
- if a large anchor behaves inconsistently, prepare a compact square reference first and retry
- successful advanced-walking runs returned transparent spritesheet PNGs rather than GIFs when `return_spritesheet: true` was set

For multi-direction walking presets:

- `animation__four_angle_walking` and `animation__walking_and_idle` are `48x48` workflows
- they are useful for broad exploration, but not as clean for direct comparison against an existing `64x64` anchor

For eight-direction turnaround experiments:

- try `animation__8_dir_rotation` first when you want a one-shot directional sheet
- remember it is fixed at `80x80`
- treat it as the first experiment, not guaranteed directional truth
- if `animation__8_dir_rotation` returns server errors or weak directions, fall back immediately to a staged `rd_pro__edit` workflow
- a dependable staged fallback is:
  - cardinals first from the isometric anchor
  - diagonals second using the same anchor plus the cardinal sheet as `reference_images`

### Prompting Guidance

Prompt like animation direction, not concept art copy:

- who the character is
- facing direction
- intended motion
- what must remain stable
- what should not happen

Good Retro Diffusion prompt components for character animation:

- identity: compact adventurer, same costume colors, same silhouette and proportions
- facing: side-facing, profile view, facing right
- motion: walk cycle in place, readable step rhythm, alternating arm swing
- stability: keep silhouette and costume consistent frame to frame
- exclusions: no camera movement, no perspective rotation, no extra props, no background

For advanced animation prompts in particular:

- prefer one or two short sentences
- avoid long descriptive prose
- avoid repeating identity details more than necessary
- keep the full prompt comfortably below `300` characters when possible

Important live-use nuance:

- "shorter" is not the same as "better"
- once you have a run that preserves character identity well, do not aggressively simplify the prompt unless you know which clauses are safe to remove
- keep the non-negotiable guardrails that lock the output:
  - facing / camera orientation such as `side-facing`
  - identity preservation such as `same costume and silhouette`
  - action disambiguation such as `bow-butt melee attack`
  - cleanup constraints such as `no background clutter`
- removing those guardrails can cause Retro Diffusion to drift into a different move family entirely, even when the starting frame and references are correct

## Scripts

- `scripts/retro_inference_run.py`
  - one Retro Diffusion run
  - image, edit, or animation/spritesheet
  - supports cost-only mode
- `scripts/retro_experiment_matrix.py`
  - run a JSON-defined experiment batch
  - useful for cross-comparing Retro Diffusion styles on the same source sprite
- `scripts/prepare_reference_image.py`
  - prepare explicit RGB reference inputs from local PNGs
  - flatten transparency to a chosen matte
  - optionally resize to a target square with nearest-neighbor scaling

## Portable Workflow

Keep project-specific artifacts in the user's working project, not inside the skill directory.

Good default layout:

- checked-in experiment contracts under a path such as `experiments/retro-diffusion/configs/`
- generated outputs under a project-owned `outputs/`, `artifacts/`, or asset-staging directory
- human-readable prompts, notes, and learnings next to the experiment docs if the project uses them

The important rule is:

- the skill provides scripts, references, and presets
- the user's project decides where prompts, configs, manifests, and generated images live

## Run Verification Workflow

When a Retro Diffusion run appears to stall, timeout, or return an ambiguous result:

1. Record the intended output directory before starting the run.
2. Launch the run once.
3. If the wrapper does not report clean completion, inspect the output directory before doing anything else.
4. Check for:
   - expected output filenames
   - non-empty PNG / GIF artifacts
   - run JSON or response JSON written by the harness
   - timestamps newer than the invocation time
5. If artifacts exist, treat the run as completed and assess quality from the returned sheet.
6. Only retry when:
   - no new artifacts were produced, or
   - the returned artifact is explicitly corrupt / incomplete for the task.

Practical rule:

- ambiguous transport state is not the same as model failure
- verify files first, retry second

## Anti-Patterns To Avoid

❌ **Anti-pattern: comparing incompatible animation styles as if they were the same task**
Why bad: a fixed `48x48` four-angle walker and a reference-driven advanced walking sheet are not equivalent outputs.
Better: compare them as different Retro Diffusion strategies, not as the same contract.

❌ **Anti-pattern: feeding transparent RGBA sprites directly into `input_image`**
Why bad: the docs say `input_image` should be RGB with no transparency.
Better: convert the input to RGB first and keep the subject on a clean flat background.

❌ **Anti-pattern: asking for “walk animation” without saying whether you want a GIF or spritesheet**
Why bad: you may get a preview format that is harder to analyze downstream.
Better: request `return_spritesheet: true` when the goal is extraction or frame comparison.

❌ **Anti-pattern: using verbose prompts with advanced animation modes**
Why bad: the backend may internally expand the action text and hit a hidden `500`-character validation limit.
Better: keep advanced-animation prompts minimal and literal.

❌ **Anti-pattern: over-simplifying a prompt after a good run**
Why bad: deleting "extra words" often deletes the exact identity and motion constraints that were keeping the model on-style.
Better: shorten carefully, but preserve the clauses that lock facing, silhouette, action type, and background behavior.

❌ **Anti-pattern: retrying immediately because the wrapper did not print a clean success message**
Why bad: Retro Diffusion may already have produced the output sheet, and an unnecessary retry wastes time, money, and confuses source-of-truth selection.
Better: inspect the target output directory and run artifacts first, then decide whether a second run is actually needed.

❌ **Anti-pattern: assuming the reference image alone will preserve style**
Why bad: `animation__any_animation` can still drift into the wrong move family or add inconsistent effects if the prompt stops reinforcing orientation and action semantics.
Better: pair the starting frame and references with a compact but explicit prompt that preserves orientation, identity, and action read.

❌ **Anti-pattern: assuming a larger isometric anchor will work better**
Why bad: larger references can be less stable than compact prepared anchors, especially in advanced animation modes.
Better: downscale the approved anchor to a compact square first, then try advanced walking.

❌ **Anti-pattern: trusting `animation__8_dir_rotation` as the canonical turnaround path**
Why bad: it can fail server-side or produce weak directional separation even at the documented `80x80` size.
Better: keep it as a cheap first probe only, and rely on staged `rd_pro__edit` when you need a dependable turnaround workflow.

❌ **Anti-pattern: ignoring the built-in frame-size contracts**
Why bad: some styles silently clamp or ignore your requested size.
Better: choose the style because its size/output format fits the task.

❌ **Anti-pattern: treating Retro Diffusion as a general-purpose video model**
Why bad: this API is about pixel-art image and animation sheet generation, not free-camera video.
Better: use it for sprite-native outputs and compare those against video-derived workflows later.

## Variation Guidance

**IMPORTANT**: Do not converge on one Retro Diffusion mode for every sprite task.

- vary between `RD_PRO`, `RD_FAST`, and advanced animation styles based on the asset contract
- vary `frames_duration` deliberately for short attack vs longer walk tests
- vary whether a run returns GIF preview or spritesheet based on the downstream need
- do not assume the best prompt for platformer walking is also the best prompt for turnarounds or idles

## References

- API and style notes: `references/api-and-styles.md`
- Animation strategy notes: `references/animation-workflows.md`
- Presets: `assets/model-presets.json`
- Prompt starters: `assets/prompt-profiles/`

## Remember

Retro Diffusion is strongest when you meet it on its own terms:

- pick the correct built-in style
- feed it a clean reference
- ask for the exact sprite artifact you need
- keep advanced-animation prompts brutally short
- prefer staged `RD Pro Edit` for dependable isometric turnaround work
- and track the result like an experiment, not a one-off prompt
