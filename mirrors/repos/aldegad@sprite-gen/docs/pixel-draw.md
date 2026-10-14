# `sprite-gen pixel-draw` — Claude Opus draws pixel art as a pixel grid

> **Experimental.** The verb, its flags and its report may change between versions, and the quality of what a model draws
> varies from run to run: expect to compare candidates, re-draw, or touch up `grid.txt` by hand. The numbers below come from a
> small set of measured runs, not from a benchmark.

> Owns: `sprite-gen pixel-draw`: the inputs, the safe area of a sprite or icon, the run folder and `report.json`, gates G1–G8 and what they take from sprite-gen, the row repair, the one redraw, the pick between candidates, Message Batches and `--resume`, re-rendering an edited `grid.txt` · Index: [docs/README.md](README.md)

The model does not paint an image that is then shrunk to a grid. It writes the grid itself: a
palette of keys and, per frame, one line of keys per pixel row. Code checks every answer, asks for
broken rows again one at a time, renders the frames and, among candidates that pass, has one
vision call pick. `grid.txt` — the palette and the rows — is the truth of a run; every PNG is
derived from it and can be derived again.

Use it for a single small asset: an item icon, a prop, a monster, a character still, four facing
directions, a draft walk cycle, a grass or water tile. It was measured on `claude-opus-5-5` on
2026-10-12 (250 drawings of 12 subjects at 16–48 px, judged by a vision model against the same
subjects made with GPT images shrunk by sprite-gen's own functions):

- single assets at 32 px and below came out shippable, and beat the shrunk GPT images at 16 px and
  on characters, where one-pixel details (eyes, a belt, a glint) are placed on the grid from the
  start instead of being averaged away;
- 48 px held up (7 of 8 shippable) but is the edge of what was measured; past 48 px, painterly
  styles, or a character from a picture the user gave, use [`gen`](gen.md) and
  [pixel-unfake](pixel-unfake.md) instead;
- a walk cycle keeps the body consistent but the legs barely change sides between the two contact
  frames: it is a draft for a touch-up, and the run says so (G6 warning). A real loop belongs to the
  [video → loop pipeline](video-pipeline.md);
- a fixed palette (`pico8`) was kept every time, at a visible cost in material rendering;
- dense small-pattern tiles (cobblestones) sometimes spent every token thinking and wrote nothing,
  at effort xhigh only.

It runs on `ANTHROPIC_API_KEY` and **every call is billed per call** against that key; the run
says so on stderr before the first request leaves, and `report.json` adds up what it cost.

## Quick start

```bash
export ANTHROPIC_API_KEY=<your Claude Console key>

# one sprite, 32x32, two candidates, the vision pick
sprite-gen pixel-draw --out-dir runs/slime \
  --subject "A green slime monster: a glossy jelly blob with two black eyes and a white highlight, front view."

# an inventory icon at 16 px, PICO-8 colours only
sprite-gen pixel-draw --out-dir runs/potion --kind icon --size 16 --palette pico8 \
  --subject "An inventory icon of a red health potion: a round glass flask with a cork stopper."

# four directions in one call (say what each frame is in the subject)
sprite-gen pixel-draw --out-dir runs/knight-4dir --frames down,up,left,right \
  --subject "A small RPG knight, standing idle: down = facing the viewer, up = back turned, left and right = profiles."

# a walk cycle draft
sprite-gen pixel-draw --out-dir runs/knight-walk --frames walk1,walk2,walk3,walk4 --walk-cycle \
  --subject "A small RPG knight, side view facing right, walking."

# a repeating tile, twenty of them at half price: --batch
sprite-gen pixel-draw --out-dir runs/grass --kind tile --batch \
  --subject "A top-down grass ground tile: short green grass with a few lighter blades and small darker tufts."
```

On success the report is printed on stdout and written to `<out-dir>/report.json`; the picked
candidate's files are at the top of the run folder.

## Inputs

| Flag | Values (default) | What it does |
|---|---|---|
| `--subject TEXT` | words | What to draw. For several frames, say what each one is (the frame names are listed for the model, their meaning comes from your words). |
| `--spec FILE` | JSON object | `subject`, `size`, `kind`, `frames`, `walk_cycle`, `palette` instead of the flags. A key given both in the file and as a flag takes the flag, said on one stderr line ([run contract](run-contract.md#1-pipeline-stages)). |
| `--size N` | 8–48 (32) | Canvas side in pixels; every frame is N×N, a sprite's or icon's body about the size of the [safe area](#the-safe-area) (26×26 at 32). Measured best at 32 or less. |
| `--kind` | `sprite`, `icon`, `tile` (`sprite`) | Sprites and icons have a transparent background, a dark outline and a margin around the body; a tile fills every pixel and repeats seamlessly. |
| `--frames a,b,…` | 1–4 names (one frame named after `--kind`) | Frames drawn **in one call**, so they share one palette and one design. Names are letters, digits, `_` and `-`. |
| `--walk-cycle` | flag | The four frames are contact, passing, contact, passing: the prompt says so and G6 checks the legs change sides. |
| `--palette` | `free[:N]` (`free:16`), `pico8`, `#RRGGBB,…`, or a file | A free palette allows at most N colours; a fixed one allows only its colours. A file is JSON (a list, or `{"colors": [...]}`) or one colour per line (`RRGGBB` or `#RRGGBB`, `;` comments — Lospec's `.hex`). |
| `--candidates K` | 1–6 (2) | Answers drawn for the request, each on its own; one is picked (G7). |
| `--effort` | `medium`, `high`, `xhigh` (`high`) | Thinking effort of each drawing. |
| `--format` | `chargrid`, `json` (`chargrid`) | How the model writes the grid. `grid.txt` is a character grid either way. |
| `--batch` | flag | Draw through Message Batches at half price and wait for the batch (below). |
| `--batch-wait S` | seconds (3600) | How long to wait for one batch before the run ends unfinished; `--resume` collects it later. `0` submits and returns. |
| `--max-tokens N` | 1024–128000 (32000 for one frame, 64000 for more) | Output cap of each drawing, thinking included. |
| `--pick` | `vision`, `human` (`vision`) | Who picks among candidates that passed. |
| `--out-dir DIR` | a new or empty folder | The run folder. |
| `--resume` | flag | Continue the run in `--out-dir` from its `request.json` (below). |
| `--grid FILE` | a `grid.txt` | Check and render an edited grid; no model call (below). |

## What a run does

For each candidate, independently (in parallel, or in one batch):

1. **Draw** at `--effort`, with the prompt built from the inputs: the subject, the canvas, the frames
   (and the walk cycle), the palette rule, the kind's background, [safe area](#the-safe-area) and
   style rules, and the exact output format.
2. **G1 parse.** The answer is read strictly ([below](#gates)). A row one key too long or short, a
   key that is not in the palette, rows missing at the end — those rows go back to the model on
   their own, each with the rows above and below and a column ruler, and it answers
   `ROW <frame> <n>: <row>` lines that code splices in (effort medium, about $0.01 and six seconds
   each). Two rounds at most.
3. **Redraw, once.** An answer still broken after its repairs, or broken beyond its rows (no block,
   a broken palette, a frame missing, too many rows), is drawn again at the same effort. An answer
   that spent all `--max-tokens` thinking and wrote nothing is drawn again **one effort lower**
   (xhigh → high → medium → low). A candidate is drawn at most twice in all.
4. **G2–G6 and G8** on the pixels. G2, G3 and G6 fail the candidate; G4, G5, the walk check and G8
   (a frame past the physical cap, feet off the floor row) warn; G8 also notes a frame past the safe
   area within the cap in an info line, which asks for nothing. G3, G4, G5 and G8 are judgments
   sprite-gen already makes elsewhere, asked rather than copied ([below](#what-it-takes-from-sprite-gen)).
5. **G7 pick.** Of two or more candidates that passed, one vision call (`claude-opus-5-5`, effort
   low, structured output) looks at all of them on one sheet, shuffled under letters, scores each and
   names the best; with `--pick human` nobody picks and the candidates wait for a person. One that
   passed alone is the pick.

A refusal is reported as it came and that candidate is not drawn again. Nothing falls back to
another model, provider or effort beyond the one lowered redraw.

## The safe area

A pixel artist drawing a 32×32 sprite does not fill the cell: the body sits in about 26×26, and a
raised sword, a cast or an effect may go past it. sprite-gen keeps the same reserve around every cell it
lays out — [`prepare`](run-contract.md)'s safe margin, 9.4% of the side, floored — and `pixel-draw` takes
its numbers from there instead of keeping its own:

| Canvas | Margin | Safe area | Floor row (counted from 1) | Physical cap |
|---|---|---|---|---|
| 8–10 | 0 | the whole canvas | the last row | the canvas |
| 16 | 1 | 14×14 | 15 | 16×15 |
| 24 | 2 | 20×20 | 22 | 24×22 |
| 32 | 3 | 26×26 | 29 | 32×29 |
| 48 | 4 | 40×40 | 44 | 48×44 |

The safe area is a target for the body's average size, not a wall. The prompt of a sprite or an icon
says it in rows and columns the model can count: the body about the size of the safe area; a pose or a
detail that needs the room — a raised weapon, a long blade, an effect, a wide stance — may reach past it
into the margin, up to the canvas edge, the four corner pixels kept transparent; and for a sprite, the
feet on the floor row, the safe area's bottom row, in every frame. That is the row `prepare`'s fit
grounds a frame on, so a sprite drawn here stands where sprite-gen's other sprites of the same cell size
stand. (`gen --layout-guide` draws its floor line one margin further in: that is room for an image
model's still to bob into once a video moves it, and a grid drawn here is the frame itself.)

G8 checks it ([below](#gates)) with the judgment sprite-gen already makes when it snaps a picture to
pixels — one function, `safe_area_fit` in [`frames/extract.py`](../sprite_gen/frames/extract.py), whose
rule is written once, in [pixel-unfake.md](pixel-unfake.md#pixel_unfake-mode): G8 hands it each frame's
opaque box, the canvas as the cell. It never fails a candidate. G8 also warns when a sprite's feet are off
the floor row: the body box — the rows and columns holding at least a quarter as many opaque pixels as
the fullest one, which a blade, a strand or a spark does not — ending above or below it (a sprite that
flies or floats is told the same floor and gets the same warning). G6 compares the frames inside the
safe area: a weapon raised or an effect thrown into the margin in one frame leaves the figure's height
and floor as they were. `--grid` measures a grid by its own size, each side on its own when it is not
square. A tile has no margin: it fills every pixel and repeats.

Measured on `claude-opus-5-5` at effort high, one candidate, on 2026-10-13 — seven drawings: a knight
and a wizard standing, walking and attacking at 32 px, the knight standing at 16 px. Every one kept its
body inside the safe area, stood on the floor row in every frame and left the canvas edge clear; a
blade, a staff and a spark reached one or two pixels into the margin. Under the earlier prompt, which
asked to fill the canvas, the same knight (2026-10-12) stood 29–31 px tall with its boots two rows
below the floor row, and one of its walks put the plume on the canvas edge. One wizard walk drew its
two passing frames alike and failed G6, as walk drafts do. Those seven were drawn when the prompt still
asked for only a thin detail in the margin and the canvas edge clear; the wording that lets a pose go
past the safe area has not been measured yet.

## Gates

| Gate | Checks | On failure |
|---|---|---|
| G1 parse | One block; palette lines `<key> #RRGGBB` (`.` is transparent and nothing else); the frames asked for, each exactly N rows of N palette keys | Row issues → row repair (two rounds), then one redraw; anything else → one redraw. Recovered by code and recorded: a single frame written without its `FRAME` line or under another name, frames in another order, the fence tagged otherwise, no `END` line |
| G2 palette | Opaque colours used ≤ the limit; a fixed palette's colours only | fails |
| G3 alpha | Each frame's background by the judgment `gen` reads a generated raw by (`alpha_verdict`, [gen.md](gen.md#transparent-output--strategy-per-provider)): `real-alpha` is at least 5 % of the pixels and half the one-pixel border alpha 0, `no-alpha` none. Sprite/icon: `real-alpha`, something drawn, four transparent corners. Tile: `no-alpha` | fails |
| G4 tile seam | Each tile frame's join along x and along y, by the measure `background-tile` reports (`inspect_tile`, [asset-tools.md](asset-tools.md#repeating-tiles)): the wrap edge against the tile's own neighbours | warns where it says `needs-review`, with its reasons — a local measure, never proof that the tile repeats cleanly; look at `tiled-3x3.png` |
| G5 stray pixels | Lone pixels of a sprite/icon by the judgment the matte cleanup erases them by (`isolated_dots`, [chroma-alpha.md](chroma-alpha.md#chromamode-ycbcr--chrominance-plane-matting-opt-in)): opaque, with no opaque pixel among their eight neighbours — a pixel touching another only at a corner, as in a diagonal stroke, is joined | warns |
| G6 frames | Same bottom row in every frame, heights within one pixel, no two frames the same; a sprite's or icon's rows are measured inside the [safe area](#the-safe-area), so a staff raised or a spark into the margin in one frame is not a taller figure (the margin is G8's). With `--walk-cycle`: the contact frames differ by at least 40% of the mean contact↔passing difference | fails; the walk check warns ("weak leg alternation — touch up the legs") |
| G8 safe area | Sprite/icon: each frame's opaque box against the [safe area](#the-safe-area) and the physical cap, by the pixel snap's own judgment (`safe_area_fit`, [pixel-unfake.md](pixel-unfake.md#pixel_unfake-mode)); a sprite's body box ending on the floor row | never fails: past the physical cap, and feet off the floor row, warn; past the safe area within the cap is an info line (`info`), which asks for nothing. Below 11 px the margin is 0: the safe area and the cap are the canvas |
| G7 pick | Two or more passed: the vision pick (or a person) | a pick that fails ends the run `pick_failed`, candidates kept |

## What it takes from sprite-gen

`pixel-draw` is a new way to make a picture, not a new set of rules for one. Where sprite-gen already
answers a question the verb asks, it asks that function; a part that is its own says why.

| Part | Taken from | Owner of the rule |
|---|---|---|
| The safe area's numbers (margin, floor row) | `prepare`'s cell normalisation (`gen.prepare.normalize_cell`) | [run-contract.md](run-contract.md) |
| G3 transparent background | `gen.chroma.alpha_verdict`, which `classify_raw_alpha` reads a raw by | [gen.md](gen.md#transparent-output--strategy-per-provider) |
| G4 tile seam | `background.tile.inspect_tile`, `background-tile`'s join measure | [asset-tools.md](asset-tools.md#repeating-tiles) |
| G5 stray pixels | `frames.extract.isolated_dots`, the YCbCr matte cleanup's lone pixels | [chroma-alpha.md](chroma-alpha.md#chromamode-ycbcr--chrominance-plane-matting-opt-in) |
| G8 safe area | `frames.extract.safe_area_fit`, the pixel snap's judgment; a frame's opaque box, `frames.extract.solid_alpha_bbox` | [pixel-unfake.md](pixel-unfake.md#pixel_unfake-mode) |
| `--spec` and a flag with the same key | `gen.base.flags_over_spec`, `prepare --request`'s answer: the flag wins, said on one line | [run-contract.md](run-contract.md#1-pipeline-stages) |
| A call sent again, and the wait | `gen.retry`, every direct provider call's rule | [gen.md](gen.md#a-refused-request-sent-again) |
| A palette colour read and written | `util.hexcolor` | — |
| `run(**kwargs)` | `util.cli_kwargs.namespace_from_kwargs` | — |
| `anim.gif` | `util.gif_utils.save_clean_gif` | — |
| The pick sheet's checker | `qa.preview.checker`, the contact sheets' | — |
| The billing line, the printed report | `gen.base.announce_api_billing`, `gen.base.print_json` | [gen.md](gen.md) |
| The refusal line | `gen.refusal` (`CONTENT_POLICY`) | [gen.md](gen.md#direct-openai-calls-and-authentication) |
| What ends a call unanswered, and its words; a refusal's body | `gen.xai` (`NO_ANSWER`, `no_answer_reason`, `error_body`) | — |

Its own, because nothing in sprite-gen does it: the grid and its parse (G1), the row repair, the palette
rules (`--palette`), `frame-<name>.png`'s encoder (its bytes depend on the pixels alone, which Pillow's
do not), G2's count against the rule, G6 (one pixel of height across a drawn set — `extract`'s size
check is for a frame the matte broke, under 35 % or over 275 % of the median frame's area), the walk check (the
video path's legs read a filmed cycle's steps, not whether two drawn contact frames swap legs), the
3×3 tiling, the vision pick, Message Batches and `--resume` (`video-resume` asks xAI again by request
id; a batch is collected, and every answered call read back), and the cost in `report.json`.

## The run folder

```
<out-dir>/
  request.json            the resolved request (what --resume reads)
  report.json             everything below, and what it cost
  grid.txt                the picked candidate's grid: the truth, editable, diffable
  palette.json            its keys and colours, the rule, the colours used
  frame-<name>.png        each frame at its own size, byte for byte reproducible
  preview-x<s>.png        the frames side by side, nearest-neighbour ×s (about 256 px a frame)
  tiled-3x3.png           a tile repeated 3×3 (×s)
  anim.gif                two or more frames, 150 ms each (×s)
  candidates/c1/…         the same files for every candidate whose grid parsed whole
  calls/<id>.json         every model call: prompt, answer, thinking summary, usage, request id
  batches/<id>.json       every batch submitted, the moment it was
  pick-sheet.png          the sheet the vision pick looked at
```

The top-level files are the picked candidate's, copied. With `--pick human`, or when nothing
passed, there are none: the candidates are under `candidates/`.

`frame-<name>.png` is written by sprite-gen's own encoder (stored deflate blocks): its bytes depend
on the pixels alone, so the same `grid.txt` gives the same file on any machine and any Pillow or
zlib build. The previews, the tiling and the GIF are views for the eye.

### `report.json`

| Field | |
|---|---|
| `status` | `ok`, `failed` (no candidate passed), `refused` (every candidate refused), `pick_failed`, `unfinished` (a batch not collected yet) |
| `request` | the resolved inputs (`palette` with its rule and colours) |
| `chosen`, `files`, `warnings`, `info` | the picked candidate, its top-level files, its warnings (worth a look, maybe a redraw) and its info lines (nothing to do) |
| `pick` | `by` (`vision` / `only` / `human`), `best`, and for the vision pick its `labels`, `sheet` and `verdict` |
| `candidates[]` | per candidate: `status`, `reason`, `effort` of the answer kept, `generations` (call ids), `redraws` (after which call, why, at which effort), `repairs` (rows asked, answered, still broken), `G1` (issues and what was recovered), `gates` (G2–G6 and G8 with their measures), `warnings`, `info`, `files` |
| `calls[]` | per call: `id` (`c1-gen1`, `c1-gen1-fix1`, `pick`), `purpose`, `mode` (`realtime` / `batch`), `model`, `effort`, `max_tokens`, `request_id`, `message_id`, `batch_id`, `stop_reason`, `stop_details`, `usage` (as the API reported it), `thinking_tokens`, `cost_usd`, `seconds`, and for a failed call `error` and `billed` |
| `batches[]` | per batch: `id`, `custom_ids`, `submitted_at`, `collected`, `ended_at`, `waited_seconds` |
| `usage`, `cost_usd`, `seconds` | totals over the calls, and the run's wall time |

`cost_usd` is each call's usage at the published price (below), Message Batches at half. It is
what the calls cost by the API's own usage counts, not a console bill. Which price each token is
billed at is one function, `anthropic_api.billed_tokens`: input, output, cache reads, and cache
writes by their lifetime (`usage.cache_creation`'s five-minute and one-hour counts; a reply that
does not split them wrote for five minutes), each count as the reply gave it — a caller pricing
the calls at rates of its own reads the same split.

## Failures

The run ends non-zero with one line on stderr, and the report says the rest:

- **No candidate passed** — `pixel-draw: no candidate passed the gates (c1: <reason>; c2: …)`.
- **Every candidate refused** — `pixel-draw: refused by the provider's content policy
  (stop_reason=refusal category=<category>); every candidate was refused` (the
  [refusal marker](gen.md#direct-openai-calls-and-authentication) callers already read).
- **A call failed** — a request the API refused before answering in a way Anthropic documents as a
  request not taken (429 but its spend cap, 500, 529 overloaded) made nothing and is asked again
  twice, each wait said on stderr ([a refused request sent again](gen.md#a-refused-request-sent-again)).
  Anything else — a 400, a rejected key, a 502, 503 or 504, a stream that broke after it began
  (what was written may be billed) — ends that candidate with the API's line (the key masked) and
  is not asked again.
- **A batch not collected** — `unfinished`, below.

## Message Batches and `--resume`

`--batch` sends the drawings through Message Batches, which bill half and may take up to 24 hours
(most finish within one). The row repairs and the pick stay realtime: they cost about a cent and
would add a batch wait each. The batch is recorded in `batches/<id>.json` the moment it is
submitted.

If it has not ended within `--batch-wait`, the run ends `unfinished`, naming the batch and the
command that collects it:

```bash
sprite-gen pixel-draw --out-dir runs/grass --resume
```

`--resume` reads the request from `request.json` (generation flags are refused with it), reads every
call already answered back from `calls/` instead of asking it again, collects a batch already
submitted instead of submitting it again, and carries on. A call that ended in an error, and a
realtime call that was cut off mid-answer, are asked again. A `calls/` record built from another
request than the one in `request.json` stops the run rather than being reused.

## Editing `grid.txt` — `--grid`

```bash
sprite-gen pixel-draw --grid runs/slime/grid.txt --out-dir runs/slime-edit [--kind sprite] [--palette free:16] [--walk-cycle]
```

Reads a character grid (the frames and size are what it holds), runs G1 (no repair: an issue is
reported with its frame and row) and G2–G6 and G8 — the safe area of the grid's own size — and writes
the same files and a report with no calls.
Pass the `--kind`, `--palette` and `--walk-cycle` the grid was drawn under; the run's
`request.json` has them.

## Model, effort and price

| | Value | Source |
|---|---|---|
| Model | `claude-opus-5-5` | Models API `GET /v1/models/claude-opus-5-5`, 2026-10-12: output cap 128,000 tokens |
| Thinking | `{type: adaptive, display: summarized}` | the only mode the model takes (`disabled` and a token budget are 400s); the summary keeps the stream alive and is kept in `calls/` |
| Effort | `output_config.effort`, always sent | the model's own default is `medium`, so the run never leaves it implicit |
| Price | $4 input, $20 output per million tokens; thinking is billed as output; Message Batches half | platform.claude.com pricing, 2026-10-12 |

Measured at 32 px on one candidate (median, realtime): effort high $0.17 and about 80 seconds,
xhigh $0.59 and 2–5 minutes, medium $0.10 and about 50 seconds; judged quality hardly moved between
them, which is why high is the default. Medium and high break the grid more often (a quarter or
more of answers at 32 px, against a sixth at xhigh) — the row repair fixed 21 of 29 broken answers on its
own. xhigh alone ended five times with nothing written at the token cap.

A run of this verb, 2026-10-12, at 32 px, effort high, two candidates and the vision pick: a
sprite $0.39 in 104 seconds, an icon $0.31 in 79, a tile $0.21 in 56, a four-frame walk cycle $0.96
in 274. One drawing of a single frame cost $0.09–0.20, a row repair $0.01–0.02 and the pick about
$0.01.

The transport is raw HTTPS over urllib, as for the other providers: the runtime dependency surface
stays Pillow and NumPy ([SECURITY.md](../SECURITY.md)).
