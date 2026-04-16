# Retro Diffusion Animation Workflows

## Which Style To Use

### Use `rd_advanced_animation__walking` when:

- you already have a single approved starting frame
- you want a same-character walk cycle from that frame
- you want to preserve a specific side-view or pose family
- you want to compare the result against other model families starting from the same anchor

This is the best first choice for:

- a single approved idle frame -> side walk cycle
- a compact isometric diagonal anchor -> walk cycle study

Operational note:

- `rd_advanced_animation__walking` worked well from prepared `64x64` anchors
- the same branch was unstable or unusable from a larger `256x256` isometric anchor
- keep prompts very short or the backend can fail with an action-length validation error

### Use `animation__four_angle_walking` when:

- you want Retro Diffusion's built-in multi-direction walking format
- you are willing to work in `48x48`
- you want a broad “how does RD solve walking by itself?” comparison

Do not treat it as a direct apples-to-apples comparison against a `64x64` anchor workflow.

### Use `animation__walking_and_idle` when:

- you want both walk and idle in one style family
- you are exploring a compact `48x48` character set

### Use `animation__8_dir_rotation` when:

- you want a built-in eight-direction rotation sheet
- your target is `80x80`
- you are exploring turnaround quality rather than strict adherence to an existing gameplay anchor

Operational note:

- treat this as a probe, not the main workflow
- it returned server-side `500` errors in live testing even at `80x80`
- if that happens, switch to staged `rd_pro__edit` immediately

### Use staged `rd_pro__edit` when:

- the built-in 8-direction mode fails or collapses directions
- you need a more dependable isometric turnaround path
- you already have one approved isometric anchor

Recommended staged path:

- generate isometric cardinals from the anchor
- then generate isometric diagonals using the same anchor plus the cardinal output as a reference image

## Prompting For Side Walks

Good prompt structure:

- identify the character
- restate the reference
- describe the action as in-place
- lock the camera/facing
- request readable limbs
- exclude camera rotation and background drift

Example direction:

`Same character as the reference image: compact pixel-art adventurer with the same costume and proportions. Create a clean side-facing walk cycle in place, facing right, with readable alternating arm swing and leg stride. Keep the character identity, profile view, costume, and silhouette stable across frames. No camera rotation, no turn toward the viewer, no extra props, no background.`

Practical shorter version:

`Character side walk in place, facing right. Keep the same costume, silhouette, and stable side profile. No travel, no camera move, no background.`

Important caution:

- do not interpret "shorter prompt" as "remove the important constraints"
- if a longer prompt produces a style-consistent run, preserve the clauses that explicitly lock:
  - side/profile orientation
  - same costume / silhouette
  - exact move family
  - no background clutter
- reducing a prompt to something like `quick jab, centered` may make it shorter, but it also removes the guards that keep the result aligned with the reference character and intended action

## Common Failure Modes

- **Perspective drift**: the character rotates toward 3/4 view during the cycle
- **Travel instead of loop**: the whole character moves sideways instead of walking in place
- **Identity softening**: face, costume, or silhouette lose the original anchor
- **Unreadable limb overlap**: arms or legs merge into a muddy cluster
- **Wrong artifact format**: GIF returned when you needed a spritesheet
- **Action-length validation failure**: advanced animation requests fail because the backend-expanded action string exceeds the service limit
- **Large-anchor instability**: a bigger isometric reference behaves worse than a compact prepared one
- **One-shot turnaround server failure**: `animation__8_dir_rotation` errors before producing anything useful

## Practical Defaults

For side-view walk-cycle studies from an approved anchor:

- style: `rd_advanced_animation__walking`
- width: `64`
- height: `64`
- frames_duration: `8`
- return_spritesheet: `true`
- num_images: `1`
- prompt: very short, literal, and action-focused

For isometric diagonal walk studies:

- style: `rd_advanced_animation__walking`
- prepared anchor: `64x64`
- width: `64`
- height: `64`
- frames_duration: `8`
- return_spritesheet: `true`

For isometric 8-turn studies:

- probe: `animation__8_dir_rotation` at `80x80`
- dependable fallback: staged `rd_pro__edit`

For `animation__any_animation` from an approved anchor:

- keep the prompt short, but do not drop the identity guardrails
- include orientation, action type, and style-preservation language explicitly
- keep a richer reference set if the first run is holding character consistency well
- if a second "simplified" run loses consistency, treat that as prompt underconstraint rather than as evidence that the references failed

This keeps the run close to the shipped anchor while still giving enough motion beats for curation later.

## Output Verification Before Retry

Retro Diffusion animation runs can produce a valid sheet even when the local caller does not surface a clean completion response.

Use this rule every time:

1. Start the run and note the expected output directory.
2. If the process appears hung, incomplete, or exits without a clear final message, do not immediately rerun.
3. First inspect the output directory for:
   - returned spritesheet PNGs
   - returned GIFs
   - run JSON / metadata files
   - fresh modification times
4. If the expected artifacts exist, review the sheet that came back and continue from that result.
5. Retry only if the run produced no usable artifact or the artifact is explicitly wrong for the requested contract.

Why this matters:

- false negatives waste generation budget
- duplicate reruns muddy which result is the real source of truth
- later curation gets harder if you accidentally replace a good run because the wrapper looked incomplete
