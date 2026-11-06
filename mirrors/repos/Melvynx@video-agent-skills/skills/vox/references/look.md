# The look: Codex layers

Every layer is one Codex image. The prompt is always three parts:

```text
<subject>[ <CHROMA> for a cut-out]
Style: <STYLE>
```

## STYLE (always, word for word)

```text
Vox explainer documentary collage, handmade analog paper cut-out look. Warm aged off-white paper with visible fibers and grain, torn paper edges with white fibrous rims, black-and-white halftone engraved photo cut-outs with a thin white scissor-cut border, subtle soft drop shadows between paper layers, muted vintage palette (dusty sky blue, cream, sepia, ink black, one warm yellow). Crisp, high detail, flat front-facing lighting, editorial magazine quality. Absolutely no text, no letters, no numbers, no logo, no watermark.
```

The style sentence is the only place "Vox" appears, as a look. The subject never names Vox, never asks for a logo, a brand or readable words: the image model would write them.

## CHROMA (cut-outs only)

```text
Isolated on a perfectly flat pure chroma green background (#00FF00), even color, no gradient, no shadow on the green, nothing else in the frame, generous green margin around the subject.
```

## Kinds

| kind | ratio | what | after Codex |
|---|---|---|---|
| `plate` | 9:16 (16:9 for a wide video) | the full-frame background, kept whole | copied to `layers/` |
| `cutout` | 2:3 (tall subject), 3:2 (wide subject), 1:1 | one object on green | chroma cut to `layers/<name>.png` |

Say the ratio in the subject for a plate ("Full-frame vertical background plate"). One object per cut-out: two birds = two layers (and two wing poses of one bird = two layers, the page swaps them to make it flap).

## Subjects that work

Write them concrete: what, seen how, made of what. "As a black-and-white halftone engraved photograph cut out with scissors, thin white paper border following its silhouette" turns any object into a Vox cut-out.

```json
[
 {"name": "plate-sky", "kind": "plate", "ar": "9:16", "subject": "Full-frame vertical background plate: a dusty pale-blue sky made of layered torn paper sheets, a few soft torn white paper clouds near the top and bottom edges, light paper grain, the center of the frame left empty and calm for a subject to be placed later. Low horizon of torn sepia paper hills at the very bottom."},
 {"name": "plate-paper", "kind": "plate", "ar": "9:16", "subject": "Full-frame vertical background plate: one plain sheet of aged cream off-white paper, visible fibers, faint fold lines, very subtle vignette, nothing else."},
 {"name": "plate-map", "kind": "plate", "ar": "9:16", "subject": "Full-frame vertical collage scene: a vintage engraved map of France on aged paper (coastline and rivers only, no labels), a hand-drawn red route line, torn yellow paper strip accents, soft shadows."},
 {"name": "eiffel", "kind": "cutout", "ar": "2:3", "subject": "The Eiffel Tower in Paris, full height, as a black-and-white halftone engraved photograph cut out with scissors, thin white paper border following its silhouette, slightly rough cut edges, vertical, centered."},
 {"name": "roofs", "kind": "cutout", "ar": "3:2", "subject": "A wide row of Parisian Haussmann building rooftops with zinc mansard roofs, chimney pots and small dormer windows, seen from the front at roof level, as a black-and-white halftone engraved photograph cut out with a thin white scissor border, flat bottom edge."},
 {"name": "news-a", "kind": "cutout", "ar": "2:3", "subject": "One old nineteenth-century French newspaper front page, yellowed aged newsprint, a big bold masthead band rendered only as an abstract black bar, dense narrow columns of tiny illegible grey type texture (no readable letters), one engraved halftone illustration of a crowd in the middle column, slightly creased, cut out with a thin white scissor border, flat, straight on."},
 {"name": "cloud-a", "kind": "cutout", "ar": "3:2", "subject": "One fluffy cloud shape torn out of thick white paper, fibrous torn edges, slight paper texture and soft shading, centered."},
 {"name": "gull-up", "kind": "cutout", "ar": "1:1", "subject": "One flying seagull seen from the side with both wings raised high, black-and-white halftone engraved photo cut-out with a thin white scissor border, centered."},
 {"name": "gull-down", "kind": "cutout", "ar": "1:1", "subject": "One flying seagull seen from the side with both wings lowered down, black-and-white halftone engraved photo cut-out with a thin white scissor border, centered."},
 {"name": "note", "kind": "cutout", "ar": "3:2", "subject": "One slightly crumpled blue paper banknote in the style of a euro bill (engraved window and bridge motif), printed paper texture, no readable numbers or words, seen at a slight angle, centered."},
 {"name": "strip", "kind": "cutout", "ar": "3:2", "subject": "One long horizontal strip of torn cream off-white paper, about five times wider than tall, fibrous torn edges top and bottom, faint paper grain, perfectly empty surface, centered."}
]
```

Color is for accents only: a yellow strip, a red line, a blue note. People and buildings stay black-and-white halftone.

## The Codex job (one per layer, 3 at a time, in the background)

```bash
mkdir -p <dir>/raw
codex exec --skip-git-repo-check -s workspace-write -C "$PWD" \
  --output-last-message <dir>/raw/<name>.txt \
  "Use your built-in image_gen tool to generate exactly one raster image for the prompt below, in a <ar> aspect ratio. Do not edit any file. Do not ask questions. No SVG, no HTML, no placeholder.
When done, reply with exactly this line:
IMAGE_PATH: <absolute path of the generated image>

Image prompt:
<subject>[ <CHROMA>]
Style: <STYLE>" \
  < /dev/null > <dir>/raw/<name>.log 2>&1
```

Always `< /dev/null`: without it `codex exec` waits for input forever. When it ends, read `raw/<name>.txt`, copy `IMAGE_PATH` to `raw/<name>.png`. No `IMAGE_PATH`: the newest file in `~/.codex/generated_images/` made after the job started (`ls -t ~/.codex/generated_images/*/* | head -3`). Nothing there: show the end of the `.log` (a usage limit, or `codex login` needed) and run it once more.

A plate whose ratio came out wrong: crop it to the frame, never stretch it:

```bash
ffmpeg -v error -y -i raw/<name>.png -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" layers/<name>.png
```

## The chroma cut (cut-outs)

```bash
ffmpeg -v error -y -i raw/<name>.png -vf "colorkey=0x00FF00:0.30:0.10,despill=type=green:mix=0.6:expand=0,format=rgba" layers/<name>.png
```

`colorkey` removes the green, `despill` takes the green tint off the edges. A fringe still visible on red: raise the similarity (`0.30` to `0.36`). The object turns transparent in places (a green part in it): lower it to `0.24`.
