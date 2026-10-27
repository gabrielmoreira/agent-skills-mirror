# Video → sprite pipeline (engine SSoT)

> Owns: Pipeline B engine contract: state canvas, keyed frames, true-period and one-shot cycles, strip/GIF/WebP, the batch, a set's sheet, a walk or run's stop · Index: [docs/README.md](README.md)

One still becomes a whole motion set: the still is padded into the canvas a state
needs, Grok Imagine animates it in place, the clip is keyed frame by frame, and one
seamless cycle is cut out as a strip, a transparent GIF and a WebP — every stage
measured and reported, nothing recovered silently.

```
still ──video-canvas──▶ canvas.png ──video──▶ clip.mp4 ──video-frames──▶ keyed/*.png ──video-loop──▶ strip · gif · webp ──video-cycle-align──▶ one cycle length (a set)
                    │                     ▲                                                       └── video-set runs all four per (direction, state), then aligns each walk or run across its directions
                    └──video-prompt──▶ your agent's video MCP (ZCRE)
```

| Verb | Module | In → out |
|---|---|---|
| `sprite-gen video-canvas` | `sprite_gen/video/canvas.py` | still → padded still (state canvas) + report |
| `sprite-gen video` | `sprite_gen/gen/video.py` ([gen](video.md)) | still + prompt → mp4 + report |
| `sprite-gen video-prompt` | `sprite_gen/video/clip_prompt.py` | (direction, state) → the prompt `video-set` sends, for a clip made by a video MCP on your agent ([below](#a-clip-from-a-video-mcp-on-your-agent--zcre)) |
| `sprite-gen video-frames` | `sprite_gen/video/frames.py` | mp4 → `raw/`, `keyed/` RGBA frames (`keyed.refused/` when refused) + report |
| `sprite-gen video-loop` | `sprite_gen/video/loop.py` | keyed frames → `cycle/`, `<name>.strip.png` + `.strip.json`, `<name>.gif`, `<name>.webp` + report |
| `sprite-gen video-set` | `sprite_gen/video/batch.py` | bases × states → one folder per item, `set.report.json`, `table.md` |
| `sprite-gen video-cycle-align` | `sprite_gen/video/align.py` | the loop directories of one walk or run, one per direction → one cycle length, each loop turned to start on a foot strike, + report ([loop repair](loop-repair.md) section 4) |
| `sprite-gen video-sway` | `sprite_gen/video/sway.py` | a loop directory + an ellipse -> the strip, GIF and WebP with that region swaying with the body (old name `video-follow`) ([section 6](#6-the-sway-layer--video-sway)) |
| `sprite-gen video-sway-inspect` | `sprite_gen/video/sway_inspect.py` | a loop directory + the ellipses `video-sway` takes -> a record of where each is carried in every cell and what the move changes there, and two boards of every cell; the loop directory is only read ([section 6](#inspecting-a-sway--video-sway-inspect)) |
| `sprite-gen video-set-sheet` | `sprite_gen/video/set_sheet.py` | the loop directories of one set, each with its `--view` → one sheet: a row per direction in compass order, one cell size, one ground line, every row as cut, + a record and an optional centre picture; the loop directories are only read ([section 7](#7-one-sheet-for-a-set--video-set-sheet)) |
| `sprite-gen video-stop` | `sprite_gen/video/stop.py` | keyed frames + a walk or run loop → one-shot stop strip (`loop: false`, `hold_last: true`), GIF, WebP, report ([section 8](#8-a-walk-or-run-that-stops--video-stop)) |

## 1. Canvas — the input frame decides the output frame

Grok Imagine keeps the input image's framing and **ignores `aspect_ratio` on
image-to-video**. So the canvas
is a property of the motion state, owned by one table (`STATE_CANVAS`).

A still cropped
at the crown gets only the quarter — pass `--headroom 0.26` or more for an overhead swing.

`--shape tall|wide|square` overrides the row; `--headroom` / `--lead` / `--trail` tune the room
(`--trail` is the empty fraction of the width kept behind the subject, for a weapon drawn
back before the strike); `--facing left` mirrors the wide layout. A still whose corners are not one flat colour
is refused — a non-flat background cannot be extended without guessing.

**`--fit tight` adds no room.** It is the framing for a fixed body height at a low
clip resolution: the room above makes the subject a small part of the clip, and a
`--body-height` target then has to upscale it. A motion that leaves the frame is clipped: pair it
with `video-frames --allow-subject-edge-contact`.

**The canvas owns key normalization.** Image models paint "`#00FF00`" a little
differently every run and the video model reproduces
the input colour almost exactly. So when
the flat corners are a green/magenta key at *any* brightness (`--key auto`, the
default; `--key green|magenta` to insist, refused when the corners are not that
family), the still's background is repainted to the **exact declared key** and the
padding is that same pure key. A corner that survives the matte fails loud
(the still is not on a key the engine can cut). `--key white` keeps the old behaviour: no
chroma key, the padding is the corner colour.

## 2. Clip — `sprite-gen video`

For loops, prompt for **in-place, evenly paced, returns-to-start** motion on a flat
chroma fill ("walks in place on a treadmill", "hop … return to the exact starting
stance … same height every time"). `video-set` carries those templates
(`MOTION_TEXT` / `VIEW_TEXT`). They describe the gait "for this body type" and never
name limbs.

There are two three-quarter views, `front_diagonal` and `back_diagonal`: turned to the
right, the way an isometric game's character walks down and up to the right (turned over, they face
left; a character with an item on one side has them drawn facing left instead, see
[handedness](#handedness--an-item-on-one-side)).

A caller's own motion paragraph (`build_prompt(motion=...)`) gets the same `HOLD_TEXT` sentence
after it, once: a request interpreter writes its motion before the still
exists and cannot know where the other hand's item is drawn, so it writes the choreography and
the engine says what stays put.

`build_prompt(direction, state, character, facing, motion=...)` takes a caller's own motion
paragraph — whole sentences about the subject, such as a request interpreter writes per
request — in place of the built-in state sentence. The frame, camera, background and design
rules stay the engine's, and an attack keeps its `HOLD_TEXT` sentence after the paragraph. A
walk or run gets `GAIT_HOLD_TEXT` for its view after the paragraph instead: it stays in place as
if on a treadmill and keeps facing the viewer, away from the viewer or `{facing}` the whole time,
so a caller describes the gait (a sneak, a march, a lazy stroll) and the engine keeps it on the
spot.

**A front or back walk starts mid-step.** `video-set` does this before
the canvas (`--walk-start redraw`, the default): one `sprite-gen gen --ref <base>` call per front or
back walk, on the base's own key, kept as `walk-start.png` with its report and reused while the
prompt and base are the same; a base on no chroma key is refused with `--walk-start as-given`, which
films from the base itself. Side and diagonal walks, and every other state, film from the base.

### A body that is not a person — `--body-plan`

`video-set --body-plan`, `video-prompt --body-plan`, `gen --direction --body-plan`, `prepare
--body-plan` and
`build_prompt(body_plan=...)`, `walk_start_prompt(body_plan=...)`, `still_view_text(body_plan=...)`,
`gen.still_prompt(body_plan=...)` name what the subject stands on (`sprite_gen/video/body_plan.py`):
`biped` (the default), `quadruped` or `legless` for the character, or one `<figure>=<plan>` per figure
of a scene (`--body-plan "the man=biped" --body-plan "the horse=quadruped"`). Any other body gets:

| Sentence | for a body that is not one biped |
|---|---|
| attack | `ATTACK_TEXT_ANY_BODY`: the same timed strike "with what it is already holding, or with its own body if it holds nothing", then `HOLD_TEXT_ANY_BODY["attack"]`: anything it holds stays held the same way, a part the strike does not use stays where it is drawn, no hand counted. Which part strikes (a bite, a head-butt, a forefoot) is not guessed: a caller who knows says it with `--motion`, which gets `HOLD_TEXT_ANY_BODY` after it |

Only the biped sentences were measured on clips; the others say no part the body lacks and are not
yet measured. An app
that draws the still itself with `still_view_text` and films with `build_prompt` passes the same
`body_plan` to both: the clip starts from that still.

#### The sheet rows — `prepare --body-plan`

The run records the plan in `sprite-request.json` as `body_plan` (absent without one), and a run
prepared again from that request keeps it.
A request's own `action` is its own words and is
never rewritten.

### A clip from a video MCP on your agent — ZCRE

sprite-gen never calls a video MCP. When your own agent (Claude, Codex) has one connected — ZCRE's
remote MCP (`https://mcp.zcre.ai/mcp`, signed in with your own ZCRE account, paid from your own
credits, under ZCRE's terms) — the agent makes the clip with that MCP's tools and sprite-gen does the
rest, stage by stage, with the verbs `video-set` runs: `video-prompt` prints the prompt `video-set`
would send, `video-frames` and `video-loop` cut each mp4 the agent saved, and for a walk or run cut in
two or more directions `video-cycle-align` gives them one cycle length, each turned to start on a
foot strike ([loop repair](loop-repair.md) section 4). `video-set` itself is not run on this route, so
what it does for a set happens only when you run it. What crosses the boundary is a PNG, a prompt and
an mp4.

```bash
sprite-gen video-canvas --still still.png --state walk --facing right --out item/canvas.png --report item/canvas.report.json
sprite-gen video-prompt --direction side --state walk --facing right --no-last-frame --json > item/prompt.json
# the agent, with its ZCRE tools and grok-imagine-video-1.5: prepare_upload for item/canvas.png and the
# transfer it describes, query_zcre upload to confirm it, query_zcre quote with prompt.json's prompt and
# duration, the credits shown to the user and approved, create_generation with that quote, query_zcre
# status until it succeeds, the output saved as item/clip.mp4
sprite-gen video-frames --clip item/clip.mp4 --out-dir item/frames --spill auto --reference item/canvas.png
sprite-gen video-loop --frames-dir item/frames/keyed --out-dir item/loop --fps <fps in item/frames/frames.report.json> --state walk --cycle auto --anchor motion-auto --facing right --name side-walk
# a set, once the walk is cut in every direction (each as above, in its own folder):
sprite-gen video-cycle-align --loop-dir front/loop --loop-dir side/loop --loop-dir back/loop --view front --view side@right --view back --report walk.cycle-align.json
```

A walk or run is cut with `--anchor motion-auto`. A clip on this route has no end frame to bring it
back to its first frame's size, and `motion-auto` is the anchor that measures the size over the clip
and holds it before the cycle search
([section 4](#4-loop--period-first-seam-second-then-the-gait-floor)); `video-loop`'s own default for a
walk or run, `body`, does not. A jump takes no `--anchor`: `motion-auto` is refused for a state that
is not a walk or run. `--fps` is the frames report's own, never a number written in by hand.

The set stage is the same step `video-set` runs after its loops are cut (`--align-cycles auto`, its
default): one `--loop-dir` per direction of the same walk or run, one `--view` each in the same
order, so that every loop starts as the same own foot lands wherever its view can tell the feet
apart. A frame that falls between two source frames is made by RIFE, and the command fails where one
is needed and RIFE is not installed; `--between nearest` makes none. A loop whose view cannot
tell its feet apart — or tells them apart by too small a margin (`foot_why` `low-margin`) — starts
on its larger strike and is listed under the report's `unnamed_feet` with its two strike frames in
`cycle/`: look at the first, say which own foot lands there, and run the same alignment again with
`--foot <loop>=left|right` — that loop alone turns to start on the set's foot
(`start_foot_source: "given"`).
Every aligned loop's report row (and its `strip.json`, under `cycle_align`) records its beat
(`beat`): how far the frames the alignment moved off their own time jolt the legs, in beats; under
`--between auto` a frame RIFE could not make cleanly is made again at another fraction of its two
source frames, or its jolt is shared by the frames beside it, where the nearer source frame would
break the beat; where nothing keeps it, the loop is named in the warnings. A loop whose `--view` is
`back` or `back_diagonal` is also read for stepping the same foot twice in a row (`same_foot`),
named in the warnings with whether any other cut of its clip would alternate; `--same-foot refuse`
stops the set before anything is rewritten instead (both are explained in
[loop repair](loop-repair.md) section 4).

`video-prompt --json` also gives the duration (the state's own, as `video-set`), whether the clip
ends on the canvas (`last_frame`), the loop cut (`cycle`) and the canvas, clip, frames and loop
commands with placeholders; a front or back walk adds `start_still`, the mid-step redraw `video-set`
makes before its canvas (`sprite-gen gen --ref`, your image provider). `--character`, `--motion`, `--model` and `--body-plan` reach the
prompt as they reach `build_prompt`. What the ZCRE route supports:

| | Through ZCRE's MCP |
|---|---|
| Model | `grok-imagine-video-1.5` (Grok Imagine Pro), image-to-video only. There is no Lite model there, so `LITE_WALK_TEXT` never applies. |
| End frame | None. `--no-last-frame` refuses what `video-set` films pinned — idle, attack, a walk or run in a diagonal (`pins_last_frame`). `--unpinned` films one anyway, with a warning: the prompt asks for an evenly paced repeat (an attack for one strike), the loop is searched instead of cut whole, and it may not close. Walk, run and jump from the side, front and back are the route. |
| Resolution | 480p, 720p, 1080p. The clip keeps the canvas's ratio. |
| Side facing | `video-set`'s facing observation is not run on this route; check the still faces `--facing`. |

### Handedness — an item on one side

A watch on one wrist, a pin on one side of the head, a bag on one shoulder: a right-facing view turned
over puts the item on the other side. Mirroring stays the default — five views make eight directions —
because drawing the left-facing views costs as much again. For a character whose item must stay put,
draw them instead, and say where the item is.

**The item, once.** `--handed "<item>=<left|right> [body part]"` names an item and the character's own
side it is on (`handedness.parse`; repeatable): `"the black smartwatch=left wrist"`. The engine works
out where that side is in each view (`handedness.placement`).

**The still.** `sprite-gen gen --direction <view> [--facing right|left] --handed …` adds the engine's
view sentence (`still_view_text`, the one a diagonal or front still is drawn with) and, per item, the
handedness sentence (`handedness.text`): the item is on the own left wrist only and the right wrist has
none; where that wrist is in this view (at the picture's right, on the far side); and that these
sentences decide the side whatever an attached picture shows. A side or diagonal view needs `--facing`,
a front or back view takes none. With `--handed`, `--facing-fix mirror` is refused and `regen` never
falls back to mirroring a still-opposite retry: a mirror moves the item. Do not attach a picture whose
item is on the other side — a mirrored still, or a side picture drawn the wrong way: check it with
`handed-check` first. A front or back picture, where the item's side is plain, is the safe reference.

A clip keeps what its first frame shows and makes up what it hides. For a walk or run with an item on
the far arm, draw the side still **mid-stride with both arms in view**, and say the pose in your
prompt — the engine's sentence says where the item shows, not how the character stands:

> caught in the middle of a walking stride: the far arm swings forward, its forearm and hand out in
> front of the chest, clear of the body's outline, with the watch on that wrist in plain sight; the
> near arm swings back past the body and shows whole

`video-prompt --json` names this under `still_needs` (and on stderr), and `video-set` under each
item's `still_needs`, whenever a walk or run has an item on the far wrist or hand of a side view.

No sentence holds an arm still: the arms swing with the walk. The other arm is said bare, never as a
list of what it must not wear — a clip prompt that lists that draws it there.

**Left-facing views, drawn.** `video-set --facing right,left` films every side and diagonal view both
ways, each from its own still: `--base side@right=E.png --base side@left=W.png --base
front_diagonal@right=SE.png --base front_diagonal@left=SW.png …` (front and back once, as before). A
turned view with no still for one facing is refused, naming the `gen --direction … --facing …` call
that draws it — the engine never turns one over for the other.

**The check.** `sprite-gen handed-check --strip <loop>.strip.png --direction <view> [--facing …]
[--state walk] --handed … --marker '#RRGGBB'` (or `--image`, `--frames-dir`) finds the item by a saturated colour
nothing else on the character has — a watch's screen — and checks every frame.

`--strap '#RRGGBB' --zone TOP,BOTTOM` adds the item's band seen without its marker: pixels of that
colour in those rows of the body (fractions of its height), eroded so outlines drop out, wider and
taller than 1.6 % of the body height and away from every marker blob, are another place the item
shows. It is opt-in because dark colours are common — outlines, a hat, motion smear on the legs — and
the zone is the character's wrist height. `--board` draws every frame with its blobs ringed (green as
expected, red not) and bands boxed, for what pixels cannot judge: an unmarked item, an item hidden on
the wrong hand. The exit code is 1 on a failure.

## 3. Frames — extract, key, check the edges

`ffmpeg` extracts every frame; the clip's real fps is recorded (never assumed).

Choose the key
away from the subject's hues ([chroma-alpha.md](chroma-alpha.md)).

The report also carries per-frame alpha coverage and an **edge-contact check**, read after the
specks are gone: any opaque pixel in the top/left/right 4-pixel bands is contact. Each contact pixel is
classified by its *raw* colour and the piece of the keyed frame it is in (its opaque pixels, corners
joining them, as the specks are read): the declared key's hue family in a piece with nothing else in
it is **`residual`** (background the matte did not erase); anything else is **`subject`** — a
key-tinted pixel joined to the subject included. The two
defects fail with different messages: residual-only contact points at `video-canvas`
(normalize the base still and regenerate); subject contact means the model framed too
tight and points at a taller/wider canvas. When both occur the message names both.
`residual` can also be reported on the antialiased fringe where a subject genuinely
touches the edge (a key-tinted blend pixel with low alpha), so a "framed too tight"
message with a small residual count is still a framing problem, not a key problem.
`--allow-edge-contact` turns the whole check off. `--allow-subject-edge-contact`
accepts only the subject at the edge — the clipping a `--fit tight` canvas chooses —
and still fails a frame where the key alone reaches the edge, which is a keying defect
whatever the framing.

**A drawing cut by its own frame**. A bust or half-length drawing runs off the frame
itself (its sleeve is cut off at the left, its hair at the top). In every frame of its clip the
subject touches those edges, and no taller or wider canvas gives it room there. The new default, `edge_policy: "border"`,
reads the drawing's own border on the clip's first frame (keyed, its specks erased). A side (top,
left or right) is a border side when the subject's pixels on that side's outermost row or column
cover at least 2 % of the side's length (`BORDER_MIN_FRACTION`, 0.02). A strand's tip grazing the
edge covers less than that; a drawing cut there covers far more. A pixel that is only near the
edge, inside the 4-pixel band but not on the outermost line, does not make a border. This reading is implemented by `frames.extract.own_border` using `FRAME_SIDES` and `BORDER_MIN_FRACTION`. The Breathe layer's `pixel` mode uses the same function when wording its refusal of a frame pushed past a border side ([breathing](breathing.md)).

Subject contact on a border side is accepted in every frame, wherever it is along that side.
Subject contact on any other side is still the clip framed too tight and refused, with the same
message as before. Example: a bust cut at the top and left whose hand leaves the right is
refused. The numbers in a refusal message (top / left / right px of the worst frame) are now the
pixels the border does not take, side by side. So a caller that reads those numbers to choose a
taller or wider canvas reads the side that needs room, not the border sides.

Leftover key background is still refused, with one exception: the body's rim the matte cut
loose. A thin outline drawn with the key's colour blended into it carries the key's hue, so the
matte erases most of it and can leave a few pixels at the edge between strands of hair, on their
own; read by colour they are residual. A key-only (residual) piece is accepted only when all of
these hold: it is on a border side; the same frame's subject reaches that side's band; the whole
piece holds fewer than 8 pixels (`SPECK_MIN_PX`, the speck size); and every pixel of the piece
lies within 10 px of the frame's body (`RIM_REACH`). Distance is counted as a square: each way
and diagonally one pixel is 1. The body is the frame's largest piece that holds a pixel off the
key's colour, as the speck pass reads the largest piece as the body. The whole piece counts, in
the band and out of it: an 8-pixel piece with 4 of its pixels in the band is refused. A corner pixel lies in two bands; it is accepted only when both sides
accept it.

When a side is read as the border, `video-frames`
prints one line on stderr naming the sides and pointing at `edge_border` in the report. Known limit: on a side that is already a border side, a hand that
newly leaves the frame there is accepted, because by position it cannot be told from the sleeve
moving along the edge.

**What a refused run leaves**. Now `keyed/` exists only after a run
that passed. The frames are keyed in a hidden working folder beside it, renamed `keyed/` when
the run passes, and left as `keyed.refused/` when it is refused (by the edge check, or by a
frame keyed to 0 % transparency). A refused run leaves no `keyed/`, not even an earlier run's:
the earlier one is removed when the run starts reading the clip. A pass removes
`keyed.refused/`. The report (`frames.report.json`, or `--report`) is written either way. A run stopped by an argument error (an unknown flag
value, a missing clip) touches nothing.

## 3a. Spill — key colour the model painted into the subject

A video model does not only leave the key around the subject; it paints it *onto* the
subject — a green sheen across polished metal, a tint on a pale surface. Those pixels are
opaque, often many pixels in from the edge, and form patches far larger than the chroma
engine's trapped-spill cap (clusters up to 0.5 % of the subject). The engine leaves a large
key-tinted patch alone on purpose, because in a still it is usually the subject's own
key-coloured material. In a clip it usually is not.

The still the clip was made from settles it. `video-frames --spill` takes:

| Mode | What is corrected |
|---|---|
| `small` (default) | only small key-tinted clusters — the still pipeline's rule, byte-identical output |
| `full` | key-tinted clusters of any size, including faint tints (colour only: alpha is unchanged) |
| `auto` | keys `--reference` (the still) with the same matte and counts its interior key-hued pixels at the same threshold used by `full`; a share ≤ 0.5 % means the still has no key-coloured material of its own → `full`, otherwise `small` |

`video-set` passes `--spill auto` with each item's `canvas.png` as the reference (override
with `--spill small|full`), so a green-free character loses the reflections while a
character that *is* green keeps its colour. Tiny accents or dark, edge-only material can fall below that reference test; use `--spill small` when preserving those is essential.

### Edges: `--decontam`

`--spill` fixes key colour painted into the subject; strands and outlines at its edge are a different problem: H.264 4:2:0 chroma mixes the key into anything one to three pixels wide, leaving an olive rim on red hair or turning it orange under despill. `video-frames` and `video-set` default to `--decontam auto`, which re-explains each edge pixel as a blend of the local key background with colours the subject owns and writes that colour at the pixel's observed luma. Where `auto` cannot run (a white key, or a subject with no interior deeper than 6 px) and under `--alpha-mode brightness`, it leaves frames exactly as keyed and records the reason in the report. On stderr, `video-frames` prints a one-line warning (and `video-set` lists it under `warnings`) when `auto` did not run on any frame, skipped frames, found key-coloured subject material, or kept edge pixels beside a small key-coloured part as the matte keyed them.

Pass `--decontam off` to keep the matte as it is. Method, guards and measurements: [chroma-alpha.md](chroma-alpha.md#decontam--give-the-edge-the-subjects-own-colour-back).

## 3b. Canvas shape for raised limbs and wide costumes

`video-set` picks the canvas from the state row alone. Two things that are not a jump or
an attack still leave a 1:1 frame: limbs raised in a celebration, and a costume that is
wider than the body (a skirt, a veil, a held object). Both fail `video-frames`'s
edge-contact check — the clip was made, the frames were cut, and the run stops at the
gate. The state table now routes `cheer`, `wave` and `celebrate` to the wide canvas, and
`video-set --shape wide` forces it for every state of a batch when the costume is the
reason.

## Video Processing Pipeline and Terminal Gate

```bash
sprite-gen video-canvas --still still.png --state death --out canvas.png
sprite-gen video-prompt --direction side --state death > prompt.txt
sprite-gen video --image canvas.png --prompt-file prompt.txt --duration 3 --resolution 480p --out clip.mp4
sprite-gen video-frames --clip clip.mp4 --out-dir frames --spill auto --reference canvas.png
sprite-gen video-loop --frames-dir frames/keyed --fps 24 --state death --cycle once --out-dir out
```

In the sequence above, replace 24 with the `fps` value from `frames.report.json`. For batch operations, `sprite-gen video-set --end-frame` takes `ITEM=PATH` (e.g., `--end-frame side-death=final.png`). With no seam gate or wrap correction, nonloop insists on `--anchor none` and `--fit state`, with no optional override to anchor. See [states-and-frames.md](states-and-frames.md) for the state table.

This provides a conservative geometric screen; inspect semantic pose visually.

In `sprite-gen video`, `--image` is the start frame and `--last-frame` is the end frame. Unpinned execution is the default when omitting terminal canvas arguments. Nonloop clip cache identity includes end image SHA256; a changed end pin cache rejects until user explicitly `--force` regenerates.

## 4. Loop — period first, seam second, then the gait floor

`--min-len/--max-len` override the window — on every path that
sets a cut's length, the gait fallback, `--steps` and the one-shot failover included; a cut outside
them fails rather than being written.

See [loop review](loop-review.md)
for the visual review contract and manual overrides.

**The fundamental period: recorded, never cut on the pixels' word.** A motion that repeats every
P frames repeats every 2P as well, and 2P can be the better repeat: a clip drawn on twos (a new
drawing every other frame) whose cycle is an odd number of frames shows each cycle half a drawing
off the one before, so the profile dips deeper two cycles on than one, and the minimum taken above
is two cycles. Played alone that loop is clean; resampled to the length of a set whose other loops
hold one cycle ([loop repair](loop-repair.md) section 4) it walks at twice their speed.

The engine does not cut it shorter. Half a gait cycle on, the legs are back in place with near and
far swapped; where the two legs are drawn alike (one colour of trousers, white fur) that one step
and a true cycle half a drawing late are **the same picture**. So
`video-loop` cuts the period it always cut, and only **records** what a half or a third of it shows
(`cycle.fundamental`, `sprite_gen/video/period.py`).

**The size is held before the search or cut** (`--size-hold auto`, the default). A walk or run clip filmed from its first frame only often grows or shrinks as it plays, so the frame one cycle after the first is not the first's size and the loop pops at the wrap. Under `--size-hold auto`, a walk or run cut automatically with `--anchor motion-auto` (before the cycle search) or cut by hand with `--cycle fixed` under any anchor (before the cut is read, over the whole clip) is held at its first frame's size. When a clip's height changes by 1 % or more over the clip, read one cycle on, frames are scaled back to the first frame's size about their feet. Where the size is held and the feet climb or sink by 1 % of the first frame's height or more over the clip, frames are also shifted so their feet stand on the first frame's row. This stops a receding walk's jump at the wrap from moving into place: the motion anchor's fine search corrects a climb within 28 rows over the cut but leaves the cut uncorrected when feet climb further than that, and the body anchor moves frames sideways only.

The cut's seam and step count are measured on the held frames. A fixed cut is held only where the cut itself shows the change, comparing each frame of the cut with the frame one cycle of the cut's length later, or, where the clip ends before that frame, with the frame one cycle earlier, and feet are moved only where the cut shows them move. Where the cut does not show the change, it is cut as filmed, and the report says why. The report records `size_hold` with `padding_ltrb`, records `size_hold.feet` when size is held, and also records `size_hold.cut_frames` on a held fixed cut. Fixed cuts with `--anchor motion` record the shifted target boxes in `size_hold.anchor_regions`. Automatic searches under `--anchor body`, `feet`, or `none`, `--cycle pinned`, and cuts of states that are not a walk or run are not held. `video-loop-repair` restores a held fixed cut from its source frames by holding them again by those moves (a report without them, from 3.1.0, is not restored).

Passing `--size-hold off` on a fixed cut keeps the filmed frames pixel for pixel and records `size_hold: {"applied": false, "why": "--size-hold off"}`. Under `--anchor motion-auto`, `--size-hold off` searches the filmed frames first, but if the first search finds no cycle, the gait fallback still scales back a size change of 3 % or more with feet left where filmed and searches again.

**A lead-in is left out of the search** (walk and run, `--cycle auto` or `periodic`). A video
model may reframe a small subject in a clip's first frames: the body grows (or shrinks) by a third
or more in under half a second, then walks at its new size. What it finds, and what it refuses, is said in the clip's own frame numbers:
every `start` and `context_pair_range` in the report's `cycle`, refused candidates too, so a cut
taken again from them (`--cycle fixed --start`) is the frames they name. A cut the caller names (`fixed`, `pinned`) is the caller's frames, lead-in or not.

Gates, all fail loud: no period (profile flat, below the recorded `periodicity_min`), loop seam ratio above `--seam-max` (2.0), GIF/WebP reopened and checked (frame count, `loop=0`, transparent corners, no RGB under alpha 0 in the WebP). On every walk or run loop that plays round, the step gate reads cells between drawings and refuses the loop when its largest step that is not a pixel's jitter, divided by the mean of the other steps, exceeds `STEP_RATIO_MAX` (2.5); a step is a pixel's jitter when aligning its drawing with the previous drawing takes at most `STEP_JITTER_PX` (1.5) pixels of the frames as filmed, measured by coverage so colour has no effect, and the step with that move taken back is within 2.5 of the mean. A fixed cut of a walk or run reads clip foot crossings to judge the cut, refusing an odd step count that would swap legs at the wrap. Both checks are lifted by `--seam-max` past 2.5; see `docs/loop-repair.md` section 3, "The step gate". Every walk or run loop gated by its seam ratio (not a pinned clip) is also refused when the top of its silhouette (the head, or a part held above it) jumps into the loop's first frame more than `--seam-pop-max` times its median step (default 10; `jolt.seam_pop.pop`, read on the loop as it plays); a top that cannot be read is not refused (`seam_pop_gate` says `unreadable`). `--seam-max` does not lift this gate; `--seam-pop-max off` turns it off, leaving a warning line as before; see `docs/loop-repair.md` section 3, "The seam pop gate".

See [loop repair](loop-repair.md).

**Held drawings: recorded on every loop.** A video model may film a walk at 12 drawings a second
inside a 24 fps clip, each drawing shown for two frames ("on twos", or three: "on threes"). Nothing is refused here: played at its own rate a held loop is ordinary
limited animation. It matters when `video-cycle-align` stretches it ([loop repair](loop-repair.md)
section 4, "Held drawings").

**Every cut's feet: recorded on every walk.** `video-loop` reads every cut of the cut's length the
clip holds (after any lead-in), each as the loop it would make, on the keyed frames of every walk or
run it cuts, and records it as `clip_feet` in `strip.json` and its report: `length`, `cuts`,
`same_foot` (how many step the same foot twice), `alternate`, `unread`, `seam_in_step` (cuts whose
seam falls inside a step, counted apart), and `same_foot_at` (the first clip frame of each that
does). This is recorded whatever the view; `video-cycle-align` reads it only where the view reads
the feet (back and back_diagonal; [loop repair](loop-repair.md) section 4, "Same foot twice").

### One-shot actions — `--cycle auto|periodic|one-shot`

A video model asked to jump "over and over" sometimes jumps once and stands for the
rest of the clip. That is not a period, and the periodicity gate says so. For states
that *are* single actions by nature (`jump`, `attack`, unknown states; never `walk`,
`run`, `idle`) `auto` then runs a second, different detector instead of failing.

The failover is explicit: `cycle.kind = "one-shot"` and `periodic_attempt` preserve
both decisions. The strip sidecar carries `kind` and `loop: false`, so scene loaders
play it once on a trigger. GIF/WebP previews still loop, and the same seam and
animation gates apply. `--cycle periodic` refuses a weak periodic candidate;
`--cycle one-shot` forces return detection. Stationary clips, jitter and actions
without an observed return fail loud. A walk or run refused by the
`--anchor motion-auto` search names the windows it measured and refused, best first
([loop review](loop-review.md), "The gait fallback"). `--cycle fixed --start N --length L` skips detection and cuts exactly
those frames — for a clip that holds too few repeats for the periodicity gate but whose
cycle is known. It is an explicit
instruction, not a failover: the report says `kind = "fixed"`, and the seam gate still
applies.

Every `video-loop` refusal that writes `status = "failed"` (selection, the motion anchor, the
jump repair, the jolt gate, the pin gate, the seam gate, a strip with no body to crop, and a
GIF or WebP that could not be written or failed its verification) now removes what an earlier
cut handed over in the output folder: `cycle/`, `<name>.strip.png`, `<name>.strip.json`,
`<name>.gif`, `<name>.webp`, and `cycle.source/` and `follow.source.png`, which a later
alignment and follow-through keep beside them. A cut the
refused run had already written (a strip with no body, the pin and seam gates, the GIF and
WebP) is kept as `cycle.refused/`, to look at. The next cut that passes removes it; a refusal that comes before
the cut removes an earlier one. An argument error touches nothing.

`--cycle pinned` is for a clip pinned to end on its first frame (`video --last-frame` set to
the start image). The cycle is every frame but the last, which re-renders the first, so the
wrap plays like the step into that last frame. Where the pinned frame redraws the first, `--wrap-blend auto` (the default) takes the first frame's drawing back over the last half second, a redraw only, recorded as `wrap_blend`. Passing `--wrap-blend off` cuts as filmed, but [the seam bridge](loop-repair.md#the-seam-bridge-a-loop-that-is-not-a-walk-whose-wrap-jumps) can still make frames round the wrap of a loop that is not a walk or run; for such a loop, pass `--repair off --wrap-blend off` for the earlier bytes. See [loop repair](loop-repair.md#6-the-redrawn-wrap-a-pinned-clip-whose-last-frame-the-model-drew-again) for the gating and blending rules.

`--cycle once-return` is for a clip pinned to end on its first frame that plays once (`video-set
--play once-return`, [play modes](#play-modes)). It keeps every frame, the last too, so the strip
starts and ends on the first pose and a game plays it once and goes on from the pose it started in.

Outputs:

- `cycle/frame-NNN.png` — the cycle frames, RGB under alpha 0 scrubbed, detached specks
  below 1 % of the body erased.
- `<name>.strip.png` + `<name>.strip.json` — a horizontal strip (union-cropped with 8 transparent
  columns on each side even where the subject reaches the frame's side edge, **no bottom
  pad** so feet meet the floor, bottom-aligned, ≤ 64 cells **and ≤ 32 000 px wide** because
  Chrome refuses images near 32 767 px — the cap is on pixels, so a 650 px cell allows 49
  cells and the meta says `subsampled`; ≤ 520 px tall) with `frames · w · h · body_h · delay_ms ·
  cycle_frames · cycle_seconds`. `body_h` is the **standing height** — the tallest frame whose feet touch the floor. Scale a jump strip — whose cells include
  air room — by `body_h`, not `h`, and it reads the same size as a walk strip;
  `--body-height N` does that scaling in the pipeline so every state comes out at the same
  character size (`--strip-height` stays the cap). `delay_ms = cycle_seconds / frames`, so a
  24 fps clip yields 41.67 ms cells; render at 24 fps to keep one cell per frame
  (a 30 fps render of 24 fps cells is a 5:4 pulldown and judders).
- **Cells** are scaled with their coverage and their colour taken apart (`resize_cell`; a cell
  at its own size is copied as it is). Coverage keeps LANCZOS's edge, held between the least and
  the most coverage of the source pixels the colour mixes from, so nothing spills outside the
  silhouette and nothing opens inside it. Colour is a Hamming mix of premultiplied colour, a
  filter with no negative lobe, so every pixel's colour is a mix of the colours under it. Each
  channel therefore stays within the colours under it, but the key hue's excess (green:
  `G - max(R, B)`) does not: a colour led by red mixed with one led by blue is led by neither as
  far, so a cell can carry a little more key hue than any source pixel under it. Every filter
  that mixes colours does this, in a cell and again wherever the cell is scaled later; the
  resample knows no key and caps nothing (`tests/video/test_strip_resample.py`). The one
  operation that compares a cell with the key bar, source restoration, handles it itself
  ([loop-comparison.md](loop-comparison.md#what-a-restored-cell-is)). The
  GIF and WebP are cut from these cells. The function lives in `sprite_gen/util/resample.py`
  and is the resample of every place that scaled a keyed picture with LANCZOS: a row frame fitted to its cell and the twin
  beside a pixel-unfake frame (`extract`), a sliced sheet's figures (`slice-sheet`) and a
  scene's layers (`scene-render`) go through it too. Its twin for an affine map,
  `transform_cell`, does the same for the places that moved, scaled, rotated or sheared a keyed
  picture with BICUBIC: the gait fallback's scaled-back frames (`video-loop`, "The gait
  fallback" in [loop-review.md](loop-review.md)) and a curated transform on a smooth row
  (`curation.apply_transform`). Coverage keeps BICUBIC's edge, held to the coverage of the
  2 x 2 source pixels the colour mixes from, and colour is a BILINEAR mix of premultiplied
  colour. A pixel row's curated transform samples NEAREST
  and is untouched. The scene GIF's ffmpeg downscale stays LANCZOS: it scales opaque composited
  frames, where nothing is divided by a low coverage.
- `<name>.gif` — `n_out` frames evenly across the cycle, 1-bit alpha, disposal 2, `loop=0`. `--n-out` and
  `--gif-fps` still override; `--strip-height` caps the cell/strip/GIF height. Scaling up
  requires an explicit `--body-height` target and still respects that cap.
- `<name>.webp` — same frames, lossless, `img2webp -exact`.

## 5. Set — the batch

`sprite-gen video-set --base side=side.png --base front=front.png --states idle,walk,run,jump,attack --out-dir set/`
runs canvas → video → frames → loop for every (direction, state). The xAI team quota
is **2 requests per second**: starts are
staggered (`--start-gap 2`); each clip runs once. Clip length
is each state's own default (3 s, attack 2 s) unless `--duration` sets one for all, and an
attack or idle clip is pinned to end on its canvas and cut whole (`--cycle pinned`). States use differently shaped canvases (square, tall, wide),
so the same character films at different pixel heights; `--body-height N` gives every state's loop the
same standing-height target and keeps the character one size across the set. At a low
`--resolution`, `--fit tight` frames every item without room so that target is reached by
scaling down rather than up, and lets the subject reach the frame edge. Items
are idempotent (an existing clip is reused unless `--force`); one failure stops only
its item and is listed in `table.md` with its stage and error. Exit code is non-zero
when any item failed.

A front or back walk films from its base redrawn mid-step (`--walk-start redraw`, default; one
image generation each, `--still-provider` picks the provider; see §2). See [loop repair](loop-repair.md) section 4.

### Play modes

`--play` gives how a motion plays as a value of the request, and `--motion` gives the
motion's own words, so a motion the engine has no state for — a punch, typing at a desk, a block — is
filmed under a name of your own. The modes and the presets are `sprite_gen/video/play.py`.

```bash
sprite-gen video-set --base side=side.png --base front=front.png --states idle,punch,type_at_desk,slash \
  --play punch=once-return --motion "punch=It throws one straight punch with its front fist and pulls it back." \
  --play type_at_desk=loop --motion "type_at_desk=It sits at a desk and types on a keyboard." \
  --play slash=lifetime --motion "slash=A white crescent arcs from left to right." --out-dir set/
```

| `--play` | the clip | the prompt asks for | the cut (`video-loop --cycle`) | `strip.json` |
|---|---|---|---|---|
| `loop` | as the state is filmed: an idle or attack pinned to its first frame, a walk or run pinned in a diagonal view, any other unpinned | an evenly paced repeat, or the return to the first pose where pinned | `pinned` for an idle or attack, otherwise `periodic` | `loop: true` |
| `once-return` | pinned to end on its first frame | one action, then the first pose again (after your text: `It does this once, then returns to the exact pose of the first frame.`) | `once-return`: the whole clip, its last frame too, gated by the pin | `loop: false`, `hold_last: false`, `returns: true`; the first and last cells are the first pose |
| `once-hold` | unpinned (`--end-frame ITEM=PATH` pins a terminal pose) | one action, its last pose held still for 0.4 s | `once`: the first settled pose whose drawing is not its first, a change inside an unchanged body outline included (a terminal state's by its own body geometry) | `loop: false`, `hold_last: true` |
| `lifetime` | framed as an effect and pinned to an empty black frame | an effect that appears and is gone | `lifetime` | `loop: false`, `blend: add` |

`STATE=…` applies to every view of that state and `ITEM=…` (`side-punch=…`) to one item, whose own
value wins over its state's.

Named states are presets. Without `--play` every state is filmed, prompted and cut: `effect`
as a lifetime, the six terminal states (`death`, `fall`, `land`, `cast`, `hurt_hold`, `transform`) as a
once-hold and every other state as a loop, each with its own sentence, canvas row and cut. A state of one nature plays only that mode — `effect`
a lifetime, a terminal state a once-hold, a cyclic state (`idle`, `walk`, `run`, `talk`, `blink`,
`breathe`) a loop — and another motion is filmed under a name of its own. A named state's sentence is
used in its preset mode, and the attack's (one strike, then a recovery to the exact starting stance) in
once-return as well: the same prompt and the same pinned clip, cut whole and played once. In any other
mode, and for a word the engine does not name, the mode's own sentence names the motion (`performs the
'punch' action once in place, then returns to the exact starting stance.`) unless `--motion` gives one.

A mode the request names is the cut's: a `loop` asked for is searched as a loop (`periodic`) and
refused when it does not repeat, never failed over to a single play the way a preset's `auto` cut of a
`jump` or of an unnamed state may be ([one-shot actions](#one-shot-actions----cycle-autoperiodicone-shot)).
The canvas row is the state's (a motion of your own films on the square default; `--shape` widens
every canvas of the set), except that a lifetime is framed as an effect whatever its name.

`video-prompt --play MODE` does the same for a clip made elsewhere: the record's `play`, `last_frame`,
`cycle` and commands follow the mode. A source with no end frame films a once-return only with
`--unpinned`, as a searched return (`--cycle one-shot`: rest, action, rest; `loop: false`), and
refuses a lifetime.

Not measured on a clip model: the sentences for a motion of your own (`PLAY_TEXT`, `RETURN_TEXT`).
The once-return template is the one an attack is filmed with (`ACTION_COMMON_TEXT`).

## 6. The Sway layer — `video-sway`

A clip model draws a walk's body moving, but a soft part hanging off it (a chest, a belly, a pouch on a strap) mostly moves with the body as one piece, even when the prompt asks it to bounce. The Sway layer puts that sway back on a cut loop: a soft part of a looping body sways with the body's own motion, moving an ellipse of the strip as a damped mass on the body's bob, after `video-cycle-align`.

`video-sway` replaces `video-follow` (in Python: `sprite_gen.video.sway`, `sway_loop`, `sway_offsets`). The old names (`video-follow`, `video-follow-inspect`, `sprite_gen.video.follow`, `follow_loop`, `follow_offsets`, `sprite_gen.video.follow_inspect`) still run, produce the same files, and print their old name in messages. The loop's record of a sway is read under the key `sway` or `follow`. This release still writes it under `follow`, the strip as cut is still `follow.source.png`, and inspection still writes `follow-inspect.json`, `follow-inspect.source.png`, and `follow-inspect.moved.png` with the same keys, so tools that read those names keep working. Moving written names to `sway` is a later change made together with the tools that read them.

```bash
sprite-gen video-sway --loop-dir set/front-walk/loop --region 136,164,60,50 [--region ...] \
  [--gain 2.5] [--on-fold refuse|lower] [--freq 2.4] [--zeta 0.6] [--board follow.png] \
  [--read-on <sha256>] [--stretch-floor D] [--gain-across G]
sprite-gen video-sway --frames set/front-idle/loop/cycle --out swayed --region cx,cy,rx,ry[,flat] [--fps F] \
  [--breathe breathed/breathe.json [--lag 0.15]] [--reference FRAME.png] [--gain G] [--gain-across G] [--on-fold ...] [--stretch-floor D]
```

- **The region** is an ellipse over the part in the strip's first cell, in cell pixels
  (`cx,cy,rx,ry`; repeatable). It is carried with the body's bob from cell to cell. Somebody has
  to say where it is — the engine does not find it: look at the first cell (or ask a vision model
  for the four numbers once per direction; a mirrored direction takes the mirror's region).
- **The motion** is the body's own: how far each cell's body lies from the first cell's, up and
  down and side to side. `--freq` (2.4 Hz) and `--zeta`
  (0.6) set the part; `--gain` (2.5) scales the physical answer and nothing else. On a front
  walk with a 12 px bob in a 600 px body that is a move of about ±5 px; `--gain 1` is the mass as
  measured, `0` gives back the strip as it was.
- **Only the region moves.** Inside it every pixel is moved by the offset times a weight that is 1
  at the centre and 0 at the rim (cos²), sampled as premultiplied bilinear colour; outside it no
  pixel changes. A move so large that the weight's slope folds the picture over
  (offset × π / (2 · radius) ≥ 1) is refused: lower `--gain` or give the region larger radii.
  A cell in which every region's offset is 0 is copied byte for byte, including colour under clear pixels; this holds for every sway, including `--gain 0`. A move clears that colour.
- **`--on-fold lower`** lowers the gain for you instead of refusing, region by region. No region goes under 1, the
  mass as measured: one that would have to is **held** — it does not move at all, so a
  follow-through is never quietly weaker than the motion it answers — and named, on stderr and in
  the record. The default stays `refuse`; a strip that does not fold is the same under either.
- **What it writes**: the strip, GIF and WebP over the loop's own (both animations re-opened and
  checked as `video-loop` checks them).
  `cycle/` is left as cut. The strip as it was is kept as `follow.source.png`; running
  `video-sway` again reads from it, so a second run never moves a moved strip. `--board` writes the cells before and after where the part
  sits lowest and highest, on white.
- **Order**: after `video-cycle-align`. An alignment rebuilds the strip from the cut, removes
  `follow.source.png` and the `follow` record, and says so (`follow_cleared` in its loop row); a
  new cut with `video-loop` removes them too. Run `video-sway` again after either — with
  `--read-on` where the regions were read on the cut (below).
- A one-shot (`kind: one-shot`) is refused: the follow-through is a loop's steady state.

#### Regions read on the cut, followed on the aligned loop — `--read-on`

The regions are where somebody looked: in the first cell of the strip they were read on. An
alignment turns a loop to start on a foot strike, so its first cell is another; given the same
regions, `video-sway` reads the motion again from that cell 0 and the regions land on another
place of the body, and a stretched loop moves them by a motion read anew. `--read-on <sha256>`
names the strip they were read on — its file's sha256, as cut, before any follow-through (64
lowercase hexadecimal digits; anything else is refused before anything is read):

- **`no-match`**, refused: neither — another clip, another cut, a strip nothing here was cut or
  aligned from. Locate the regions again on this strip.

#### A least area each move leaves — `--stretch-floor D`

The fold rule keeps a region from folding, and so lets the region's steepest pixel take nearly
nothing of the source: a line there is drawn across many pixels. `--stretch-floor D` (0 to under
1) asks every region's move to leave each pixel at least D of its area. On a loop aligned from the
cut, give `--read-on` too: the floor is then read on the cut's motion, so a turned loop is lowered,
held or refused as the cut is.

#### A cycle's frames at their own size: `--frames <folder> --out <new folder>`

A loop's strip holds at most 64 cells and 32,000 px across, so a cycle of large frames is cut down to fit it. The strip stays the delivery format; `video-sway --frames <folder> --out <new folder> [--fps F]` sways the full cycle before that cut.

- **The frames** are PNGs in name order, all one size, from a `video-loop` `cycle/` folder or the output of `sprite-gen breathe`. Regions are given in frame pixels. `--frames` and `--loop-dir` are alternatives, and one is required.
- **The output** contains the moved frames under their original names, with `sway.json` beside them. The output must be new or empty, and may not be equal to, inside, or containing the frames folder (compared as real paths); unequal frame sizes are refused before anything is made. A failed run leaves nothing, and the frames folder is only read.
- **The time** comes from `--fps` or, for a whole `video-loop` `cycle/`, from the loop's strip meta. A conflicting `--fps` is refused. Other frames folders need `--fps` unless `--breathe` supplies the drive. `--read-on` is refused with `--frames`; `--frames` requires `--out`; `--out` and `--fps` are refused with `--loop-dir`.
- **The record** in `sway.json` has `frames`, `frame_ms` (null on the breath), and the same record as the loop's `follow`, with `source` naming the frames folder. Body motion is read at the frames' full size: frames reduced first give other offsets, and on large frames reading can take minutes. The old name `video-follow --frames ...` writes the same bytes.

#### On the breath: `--breathe <breathe.json>`

On a breathing idle the body moves only a pixel or two while the head stays still; the outline turns that into whole-pixel steps, and the damped mass answers those steps, so the part barely moves at its default settings or sways to the steps when pushed further. `--breathe <breathe.json>` drives the part from the Breathe layer's breath instead.

- **The record** is the `breathe.json` written beside breathed frames; it supplies config, phases and `resolved.anatomy`. Its config's `inhale` is the in-breath share; a record without it reads as the default 0.40. Its config's `start_cell` and `loop_cells` say which cells of which loop the frames are; a record without them reads as the loop itself from its first cell. Only `mode: smooth` is accepted; a pixel breath is refused because its travelling wave moves the first cell. The config must pass the Breathe layer's checks, the phases are recomputed at the record's share, start cell and loop cells and must match the record (so `breath_peaks` phases written at another share are accepted when they match), and `frames`, the phase count and the swayed cell count must agree. A hand-written record is checked the same way and can state the in-breath share of a breath made elsewhere.
- **The drive** uses the Breathe layer's own breath curve at the record's in-breath share. The part follows the chest's rise late, by `--lag` of a breath, and is moved by `gain` times the gap between the chest's lift and that late lift, against the chest's rise in the record's `chest_dir`; 0 points straight up, so that offset points straight down.
- **The rest**: the first cell, rests between breaths and the close have zero offset. Each cell's ellipse is still carried by the body's outline.
- **The lag** is a share of one breath, above 0 and below `1/π`; default 0.15. A longer lag reaches further and peaks later; reach depends on lag rather than breath length.
- **A stretch of a loop** is a breathed row whose record carries `loop_cells` and `start_cell`: a way out of the loop or a way in, breathed on the loop's beat. The stretch's cell i is offset exactly as the loop's cell (start_cell + i) mod loop_cells is, from the stretch's first cell on. The fold rule (`--on-fold`) and `--stretch-floor` read the loop's whole breath, every phase of the loop, not only the phases the stretch carries, so a stretch moves by the same gain as its loop and the seams between them do not jump. The record's `reach_px`, its `fold` block and the floor's `least_cell` are then the loop's; `least_cell` is a cell of the loop.
- **The reference frame**: `--reference FRAME.png` names the frame the regions were read on when it is not the first of the frames, normally the loop set's first cell; the regions are carried from it, as on the loop's own cells. `body_px` and `body_worn_px` come from it, `body_bob_px` spans it too, and `sway.json` records `reference` with the file's `path` and `sha256`. A frame of another size than the frames is refused. Without it the regions are read on the first frame.
- **The settings and record** use a default `--gain` of 1 on the breath, against 2.5 on body motion. `--freq` and `--zeta` are refused with `--breathe`; `--fps` is refused with `--breathe --frames`; `--lag` requires `--breathe`; `--reference` is refused with `--loop-dir`. The record's `drive` carries `kind: breath`, `breathe_sha256`, `lag`, `lift_px`, `heading_deg`, `inhale`, `start_cell`, `loop_cells`, and `breaths` or `breath_peaks` in place of `freq_hz`, `zeta` and `harmonics`. Its way is `common-lay/breath-late/cos2-bilinear/1`. `--loop-dir` also accepts this drive when its strip has one cell per phase.

```bash
sprite-gen breathe <cycle> <breathed> --mode smooth --breaths 2
sprite-gen video-sway --frames <breathed> --out <swayed> --breathe <breathed>/breathe.json --region <cx,cy,rx,ry>
sprite-gen breathe way-out/ way-out-breathed/ --mode smooth --breaths 2 --loop-cells 96 --start-cell 40 --reference loop/frame-000.png
sprite-gen video-sway --frames way-out-breathed --out way-out-swayed --breathe way-out-breathed/breathe.json --reference loop/frame-000.png --region <cx,cy,rx,ry>
```

#### A region moved whole, and across apart from down: `cx,cy,rx,ry,flat`, `--gain-across G`

`--region cx,cy,rx,ry[,flat]` gives a region an optional fifth number, `flat`, from 0 to 0.9: the share of the way from centre to rim that moves in full; over the rest of the way the weight falls from 1 to 0 by cos². A large region weighted by cos² alone presses its outer part inward; one flat region can move the part whole instead of laying many small circles over it.

The fold rule and `--stretch-floor` read the radius left after the flat centre, the smaller radius x `(1 - flat)`, and the record's `fold.regions[i].radius_px` is that reduced radius. A `flat` of 0, or one left out, gives the four-number region's strip, record and inspection byte for byte. Values outside the range are refused.

`--gain-across G` sets the gain across on its own, and `--gain` then sets the gain down; without it, across uses `--gain`. When `--on-fold lower` or the floor lowers a region's gain, its across move falls in the same proportion. `--gain 0` with a non-zero `--gain-across` is refused. The record carries `gain_across`, the across gain the strip's `gain` moved by, and carries `gain_across_requested` only when given.

### Inspecting a sway — `video-sway-inspect`

The ellipse is given in the first cell, where somebody looked. Into every other cell it is carried by the body's motion, and there nobody looked: an arm that swings across a chest is inside the chest's ellipse in those cells and moves with it, and so does a sleeve of the chest's own colour, which no count of colours finds. The Sway layer does not read what a pixel belongs to. `video-sway-inspect` (old name `video-follow-inspect`) writes what somebody needs in order to look, and moves nothing:

```bash
sprite-gen video-sway-inspect --loop-dir set/front-run/loop --region 136,164,60,50 [--region …] \
  [--gain 2.5] [--on-fold refuse|lower] [--freq 2.4] [--zeta 0.6] [--read-on <sha256>] [--stretch-floor D] \
  [--breathe <breathe.json> [--lag 0.15]] [--gain-across G] --out-dir inspect/front-run [--scale 2] [--columns 8]
```

- It takes `--breathe`, `--lag`, `--gain-across` and flat regions as `video-sway` does, and stays on a loop directory without `--frames`.
- **What is inside an ellipse is not read.** Every region is written `ownership: "unknown"` in
  every cell, the first included, from its centre to its rim; no cell is marked or held on a
  guess. `solid_px` counts the body's silhouette under the ellipse (alpha ≥ 128), not whose
  pixels they are. Saying which cells hold the part alone is for a person or a model that looks
  at the board of the cells as cut, and for a second reader apart from the first.
  `video-sway` takes no such list: it moves every cell.
- `follow-inspect.source.png` has the cells as cut;
  `follow-inspect.moved.png` has them as `video-sway` would write them, laid and ringed alike.
  They are two files so that whoever says what is inside an ellipse can be given the cells as cut
  alone, without the answer beside them.

## 7. One sheet for a set — `video-set-sheet`

Each direction of a set is cut on its own, and a strip is the union of its own cycle's bodies: a side
walk's cell is wider than a front one's, a direction with a long ear taller. Laid side by side as they
are — a 3×3 board, a sheet for a game engine — the directions stand at different heights and the board
shows it as it plays. `video-set-sheet` lays them on one sheet that a board or an engine can place as it
is:

```bash
sprite-gen video-set-sheet --loop-dir S/loop --view front --loop-dir W/loop --view side@left \
  --loop-dir N/loop --view back --loop-dir E/loop --view side@right --center base.png --out-dir walk-set --name walk
```

- **Rows.** One per direction given, in the compass order **S, SW, W, NW, N, NE, E, SE** — clockwise from
  the viewer, the order a character turns in — whatever order the loops are given in. `--view` names the
  row, as `video-cycle-align` takes it: `front` S, `back` N, `side@right` E, `side@left` W,
  `front_diagonal@right` SE, `front_diagonal@left` SW, `back_diagonal@right` NE, `back_diagonal@left` NW
  (`@left` faces the screen's left). A strip turned over to face the other way is a direction like any
  other. A direction given twice, a front or back view with a side (its picture turned over is not a
  compass direction) and a count of `--view` other than the loops' are refused before anything is written.
- **The centre picture** (`--center`): a transparent still — the set's base, the picture a board shows in
  its middle. A
  still with no transparent background is refused (cut it off first: `sprite-gen cutout`), and so are
  rows without `body_h` beside one.
- **Lengths.** Loops of different lengths, in frames or in frame time, are laid all the same, one frame
  a column and the shorter rows' last cells empty; the record says `same_length: false` and a warning line
  names each direction's length. `video-cycle-align` gives a set one cycle length.

## 8. A walk or run that stops — `video-stop`

A game character that stops running jumps from a running frame straight to its standing picture. Frames made between them (RIFE in-betweens) are the wrong tool: as [loop repair](loop-repair.md) notes, RIFE smears a changed appearance, and where two drawings are too far apart for the flow, legs come out as one shape of fill; a running frame and a separately drawn standing picture are both. Every walk or run clip filmed from a still (image to video) already holds a filmed "stand → set off" at its start: the body stands, sets off, and runs into the gait the loop is cut from. Played backwards from the frame where the clip reaches the loop, that start is the body running into the standing still — filmed frames, no frame made between two others, ending on the clip's first frame, the still as filmed. `video-stop` cuts this as a one-shot clip beside the loop: a strip, its sidecar (`loop: false`, `hold_last: true`), a GIF, a WebP and a report. Played backwards, motion runs backwards (a cape, a planted foot), which is a cost to look at. This example cuts a run's stop and plays it twice as fast:

```bash
sprite-gen video-stop --frames-dir run/frames/keyed --loop run/loop/run.strip.json --out-dir run/stop --speed 2
```

- **Speed and the frame cap.** `--speed 2` plays every other frame (still kept last); `--max-frames N` (at least 2) spaces N frames evenly from the first to the still. Each frame is shown one clip tick (`--fps` defaults to the loop's `source_cut` fps, else 24). Strips wider than 32,000 px are refused; pass `--max-frames` or `--speed 2`.

The outputs are `<name>.strip.png`, `<name>.strip.json`, `<name>.gif` (plays once), `<name>.webp` (plays once), and `<name>.stop.report.json` (or `--report PATH`).

## Related

- [docs/README.md](README.md) — documentation index
