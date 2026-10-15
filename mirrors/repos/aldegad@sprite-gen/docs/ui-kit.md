# `ui-kit` — one painted sheet to nine-slice UI elements

> Owns: The UI kit layout guide, splitting a transparent UI kit sheet into elements, writing a kit whole into a new directory, fitting the layout to a drawing that drifted from it, required and missing elements, nine-slice insets, content padding and fills · Index: [docs/README.md](README.md)

A game UI kit is one transparent image with every part of a game's menus and HUD on it: a panel, a button and its pressed state, a card frame, two bar frames and a timer badge, and on the taller sheet the two bars' fills, an item slot, a counter plate, a lit and an unlit dot, and a touch joystick's base and knob. `gen --layout-guide ui-kit` asks the image model to draw each element in a fixed box. `ui-kit` cuts the sheet along those boxes, measures where each element may stretch, and writes one PNG per element with a JSON report. [`game-pack`](game-pack.md#version-2-images-tiles-and-ui) reads that report. The seven frames are the kit; the taller sheet's other eight elements are optional, so a sheet that leaves one of them out still makes a kit, without it ([missing elements](#missing-elements)).

## Generate the sheet

```bash
sprite-gen gen --provider openai --quality high --transparent --aspect-ratio 2:3 \
  --layout-guide ui-kit --prompt-file uikit-prompt.txt --out uikit.png
```

`--layout-guide ui-kit` draws the [layout](#layout) as a guide image, attaches it after any `--ref`, and adds a paragraph to the prompt that names every box and what to draw in it. The caller's prompt describes the style: material, palette, trim, mood. It does not need to list the elements or their positions. The guide asks for straight, even edges between corner ornaments, empty element centres, bare fills of one colour along their length, dots and joystick parts as circles with nothing square around them, no text and empty space between elements, because only those can be sliced.

The sheet's shape chooses the layout. `--aspect-ratio 2:3` draws the whole kit; `--aspect-ratio 1:1` (or no ratio) draws the seven frames alone, the layout every square sheet has had. Every provider that takes a ratio takes both.

The guide is an attached image, so `--transparent` keys the sheet out of a magenta background by default ([gen](gen.md#transparent-output--strategy-per-provider)). A model sometimes paints the grey and white checkerboard that editors show behind transparent pixels instead of that background. Keying the checkerboard would erase the sheet, so `gen` refuses it before keying, with its own reason (`chroma: the background is a painted transparency checkerboard …`). Generate the sheet again.

## Layout

The guide and the splitter read one table (`sprite_gen.frames.ui_kit.LAYOUT`). Boxes are in pixels of a sheet 1024 px wide: 1024 × 1024 for the square sheet, 1024 × 1536 for the 2:3 sheet. They scale with the sheet's size, and neighbouring boxes are 48 px apart. The square sheet holds the first seven elements. The 2:3 sheet holds the same seven at the same places and the other eight in a band below them. `ui-kit` reads a sheet's shape to know which: square or 2:3, each within 1 %; any other shape is refused. So a square sheet drawn before the 2:3 sheet existed is cut, measured and packed exactly as before.

| Element | Sheet | Box (x, y, w, h) | Stretch | Padding | What to draw |
|---|---|---|---|---|---|
| `panel` | both | 48, 48, 576, 400 | `xy` | measured | a large frame with an empty centre |
| `button` | both | 672, 48, 304, 128 | `xy` | measured | a wide button, normal state |
| `button_pressed` | both | 672, 224, 304, 128 | `xy` | measured | the same button, pressed |
| `card` | both | 704, 400, 272, 576 | `xy` | measured | a tall card frame with an empty centre |
| `hp_bar_frame` | both | 48, 496, 608, 112 | `x` | measured | an empty horizontal health bar frame |
| `xp_bar_frame` | both | 48, 656, 608, 112 | `x` | measured | an empty horizontal experience bar frame |
| `timer_badge` | both | 48, 816, 160, 160 | `none` | measured | a small round badge with an empty centre |
| `hp_bar_fill` | 2:3 | 48, 1024, 608, 64 | `x` | `0` | the health bar's fill alone, a bare strip of colour ([fills](#fills)) |
| `xp_bar_fill` | 2:3 | 48, 1136, 608, 64 | `x` | `0` | the experience bar's fill alone, the same kind of strip |
| `slot` | 2:3 | 48, 1248, 192, 192 | `xy` | measured | a square item slot frame with an empty centre |
| `badge` | 2:3 | 288, 1248, 176, 112 | `xy` | measured | a small counter plate with an empty centre |
| `pip_on` | 2:3 | 512, 1248, 96, 96 (circle) | `none` | `0` | a small round indicator dot, lit |
| `pip_off` | 2:3 | 512, 1392, 96, 96 (circle) | `none` | `0` | the same dot unlit |
| `joystick_base` | 2:3 | 704, 1024, 272, 272 (circle) | `none` | `0` | a round touch joystick base |
| `joystick_knob` | 2:3 | 768, 1344, 144, 144 (circle) | `none` | `0` | the joystick's round knob |

`stretch` is how a game may resize the element: `xy` as a nine-slice, `x` in width only (a three-slice), `none` not at all. Round parts (`timer_badge`, the pips, the joystick base and knob) are `none`, so they are only ever drawn at their own proportions. `stretch` belongs to the layout, not to the measurement; so does whether padding is measured: an element that holds no content (a fill, a pip, a joystick part) gets a padding of `0` on every side. The two pips have boxes of one size, so a row of dots can swap one for the other in place. The seven elements on both sheets are required, and the eight on the 2:3 sheet alone are optional ([missing elements](#missing-elements)).

The guide draws the pips and the joystick base and knob as the circles their boxes hold, and asks for them as circles with nothing square around them. A model may still draw a round part on a square plate that fills its box, so the splitter checks: when more than a quarter of the area outside the ellipse a round part's cut holds (the ellipse touching the cut's four sides) is opaque, at alpha 128 or more, the report is `needs-review` with `<element>: its corners are filled`. Regenerate the sheet; a plate behind a dot or a joystick shows as a square in the game. The timer badge keeps the square sheet's box and is not checked, so square sheets cut as they always have.

## Split the sheet

```bash
sprite-gen ui-kit --sheet uikit.png --out-dir ui/
```

The command writes `ui/<element>.png` for every element the sheet's layout holds (but a [missing](#missing-elements) one) and `ui/ui-kit.json`. Options:

* `--alpha-floor N` (default `64`, `0` turns it off) and `--alpha-edge N` (default `2`): the [alpha cleanup](#alpha-cleanup) that runs before anything is cut.
* `--report PATH`: write the JSON report elsewhere (default `<out-dir>/ui-kit.json`); it must end in `.json`, and outside `--out-dir` it must be a path that does not exist yet. Each element's `file` in it then leads from the report's directory to the PNG in `--out-dir`.

A kit is written whole into a new directory. `--out-dir` must not exist yet, or be an empty directory; one that holds anything, an earlier kit or any other file, is refused with its name and what it holds, and left as it was. Write each kit into a directory of its own, or remove the old one first. The command never changes the sheet, and a refused sheet writes nothing.

The kit (every element PNG, and the report when it is in `--out-dir`) is written into a hidden directory beside `--out-dir`, `.<name>.ui-kit-<random>`, which then takes `--out-dir`'s name in one rename. A report outside `--out-dir` is written to a hidden temp file beside it first and given its own name after the rename, in a step that fails when that name has been taken, so no run replaces another's report.

One step publishes the kit: that rename, or with the report outside `--out-dir`, the step that gives the report its name. A run that fails, or is stopped with Ctrl-C, before that step removes everything it made: the kit, the directories it created, its hidden directory and temp file; an empty `--out-dir` it was given is left empty. Stopped after that step, the command still exits with the interruption, but the kit is published: the run removes nothing but its temp file, and the whole kit and its report stay. So `--out-dir` holds either nothing or the whole kit, never part of one, and a report never names a PNG that is not there. When two runs write into one new `--out-dir`, the one whose kit lands second is refused and removes its own; the same holds for two runs and one outside report.

A run that is killed, rather than failing, cannot clean up after itself:

* It can leave its hidden `.<name>.ui-kit-<random>` directory beside `--out-dir`, or a hidden `.<report>.<random>.tmp` file beside an outside report, and the directories it created; remove them. Under `--out-dir`'s own name it never leaves anything but the whole kit.
* With the report outside `--out-dir`, a run killed between the rename and the step that publishes the kit leaves the whole kit in `--out-dir` and no report. Remove the directory and run again.
* On Windows, a rename takes no existing directory's name, not even an empty one's, so an empty `--out-dir` is removed just before the rename (a run that fails puts it back). A run killed at that moment leaves no `--out-dir`.
* A run that is interrupted again while it is removing what it made (for example, a second Ctrl-C during that clean-up) cannot finish the clean-up either. It can leave the same things a killed run leaves: its hidden staging directory or hidden report temp file beside the output, the directories it created, with an outside report the whole kit without its report, and on Windows no `--out-dir`. It never leaves part of a kit under `--out-dir`'s own name: `--out-dir` holds nothing or the whole kit.

The steps of the cut:

1. **Alpha cleanup.** Faint haze between elements would join them, so it is cleared first (below).
2. **Parts.** Pixels with alpha above zero form 8-connected parts. A part smaller than 16 pixels is dropped and counted.
3. **Assignment.** Each part goes to the box that contains its centroid, with every box widened by half the gap (24 px at 1024). When that leaves a box empty, the layout is [fitted to the drawing](#a-drawing-that-drifted-from-the-layout) and the parts are assigned again. A part whose centroid lies in no widened box is reported under `unassigned`; it makes the report `needs-review` when it has at least 16 pixels.
4. **Crop.** An element is the bounding box of its box's parts, so ornaments that reach past the box stay whole. A box with no part fails the command when its element is required (the sheet has to be generated again), and leaves its element out when it is optional ([missing elements](#missing-elements)).
5. **Insets** and **padding** are measured on the cropped element (below).

### A drawing that drifted from the layout

An image model may draw the layout a little off. The whole drawing can come out a few percent shorter than the guide, and then the lower an element is, the farther it sits above its box, until its centroid lies in the widened box above its own: that box holds two elements, and the element's own box none. So, when a box is left empty:

1. **Fit.** Along x and along y, take the scale and offset that move the layout's box centres closest (least squares) to the centres of what the boxes hold (the bounding box of each box's parts). Along an axis on which every box that holds parts is centred on one line, take an offset alone.
2. **Assign again.** Move every box by the fit, its position and its size, and its widening by half the gap with it, and assign the parts to the moved boxes.
3. Repeat from the new assignment until it comes out the same, at most 8 rounds. Fewer than 3 boxes that hold parts, or a scale that is not positive, end it without a fit.
4. **Keep it or not.** The fitted assignment replaces the layout's own when it leaves fewer required boxes empty, or as many and fewer boxes in all.

A sheet whose every box holds its element is never fitted, so it is cut exactly as before. A kept fit is in the report as `layout_fit`, and each element's `box` is then its fitted box. The tests draw a 2:3 sheet 7 % shorter than its guide, from the top edge down. Assigned to the layout's own boxes, three boxes are left empty (`badge`, `pip_off` and `joystick_knob`), two hold two elements each, and the upper fill lies in no box; the fitted boxes find all fifteen elements whole.

## Missing elements

The seven frames are the kit, and each is required: `panel`, `button`, `button_pressed`, `card`, `hp_bar_frame`, `xp_bar_frame` and `timer_badge`. When a frame's box is empty, after the fit, `ui-kit` writes nothing and fails with `<element>: its box holds no element; generate the sheet again`, or, for several, `panel, card: their boxes hold no element; generate the sheet again`.

The eight elements of the 2:3 band are optional: the two fills, the slot, the badge, the two dots and the joystick base and knob. When one's box is empty, the kit is made without it:

* It has no PNG and no entry in `elements`. The report names it under `missing`, in layout order. A 2:3 report always has `missing` (`[]` when nothing is missing); a square report has none, as before, since a square sheet's elements are all required.
* The command exits `0`, and its line ends with `; missing, left out of the kit: pip_off`.
* A missing element is not a measurement to review: `status` and `review_reasons` are about the elements that are there.
* [`game-pack`](game-pack.md#version-2-manifest) packs the elements the report has, so a missing element has no `ui.nine_slice` entry, and a game falls back for exactly that part. A game that needs both dots, or both joystick parts, falls back for both when one of them is missing.

The whole kit is drawn in one image call, so a model that leaves one box of the band empty costs that element, not the kit. Generate the sheet again to get it.

## Insets

Insets are measured only along the axes the layout lets the element stretch; the others are `0`. Along x (columns; y is the same with rows):

1. Colours are taken premultiplied by alpha, with alpha as a fourth channel, in 8-bit units.
2. The reference band is the middle fifth of the columns (from 40 % to 60 % of the width). The reference column is the per-row median over that band.
3. A pixel deviates when its largest channel difference from the reference column, in its row, exceeds twice the largest difference found in the reference band in that row, plus 8.
4. A column with no deviating pixel is plain. The stretch band is the run of plain columns that contains the reference band.
5. `left` is the band's first column plus a 2 px margin, and `right` is the distance from the band's end to the right edge plus 2 px; a side with no deviating column at all gets `0`. An inset never reaches into the reference band.

So every column with an ornament, a cap, a border line or their anti-aliased edge lies inside a fixed slice, and the stretched middle holds only columns that look like the middle of the element. Two cases make the report `needs-review`, naming the element and the axis: an ornament that reaches the reference band (the band could not grow on that side), and a reference band that is not uniform itself, so an ornament probably sits in the middle of an edge (in some row its largest difference exceeds both 64 and four times the median over the rows). A frame with an ornament in the middle of an edge cannot be nine-sliced; regenerate it.

## Padding

Padding places the content (text, a card's contents, a bar's fill, a badge's digits, a slot's icon). It is measured for the elements the [layout](#layout) marks `measured`; the others get `0` on every side. On the element's middle five rows, take the per-column median. The interior is the run of columns around the centre that continues while each step to the next column changes no channel by more than 16 and every column stays within 96 of the centre (the median of the central 5 × 5 pixels): a smooth gradient on a button face stays interior, a border's sharp edge ends it. The same on the middle five columns gives the interior rows. A pixel counts as interior when every channel lies within 16 of the range those two runs cover; when a corner of the rectangle is not interior (a round badge, an ornament reaching inward), the rectangle shrinks evenly toward the centre until all four corners are. Each padding is the distance from an element edge to that rectangle, plus 2 px. A content area narrower or shorter than a quarter of its element makes the report `needs-review`: the centre was probably not empty.

## Fills

`hp_bar_fill` and `xp_bar_fill` go inside `hp_bar_frame` and `xp_bar_frame`: in the frame's content rectangle, the rectangle its [padding](#padding) leaves (`x = padding.left`, `y = padding.top`, `w = size.w - padding.left - padding.right`, `h = size.h - padding.top - padding.bottom`, in the frame's pixels). The image model draws a fill at its own size, so its report entry says how it fits:

```json
"hp_bar_fill": {
  "...": "...",
  "stretch": "x",
  "insets": { "left": 14, "right": 14, "top": 0, "bottom": 0 },
  "padding": { "left": 0, "right": 0, "top": 0, "bottom": 0 },
  "inside": { "element": "hp_bar_frame", "rect": { "x": 46, "y": 30, "w": 520, "h": 52 }, "scale": 0.928571 }
}
```

* `inside.element` is the frame and `inside.rect` its content rectangle.
* `inside.scale` (`rect.h / size.h`, rounded to six decimals) resizes the fill, ends and insets with it, to exactly the rectangle's height. Never resize a fill by a second factor for its width: it is a three-slice, so its ends keep their shape and its middle stretches.
* Drawn `rect.w` wide at `rect.x`, `rect.y` from the frame's top-left corner, a full fill covers the content rectangle to the pixel and never reaches past it. A fraction `f` of a bar is the fill drawn `f × rect.w` wide from the rectangle's left edge. Below its two ends' width (`insets.left + insets.right`, times `scale`), a three-slice cannot shrink: show its left part instead.
* When the two ends, scaled, are at least as wide as the content rectangle, a full bar would overflow it, and the report is `needs-review` naming the fill and its frame.

[`game-pack`](game-pack.md#version-2-manifest) does this sizing for you: it stores each fill at its frame's content rectangle.

## Alpha cleanup

Transparent sheets from image models often carry a faint alpha haze: barely visible pixels around and between the drawn objects. The cleanup is shared by `ui-kit` and [`slice-sheet --alpha-floor`](sheet-slicing.md#transparent-sheets) (`sprite_gen.frames.alpha_floor.clear_haze`).

* A pixel at or above the floor (`--alpha-floor`) is solid. A pixel above zero and below the floor is faint.
* A faint pixel within `--alpha-edge` pixels (8-connected, so diagonals count) of a solid pixel is part of an object's anti-aliased edge and is kept unchanged.
* Every other faint pixel is haze and becomes fully transparent (`0, 0, 0, 0`). A pixel that was already fully transparent is left as it was.

Solid pixels and edge pixels are never changed, so a stroke stays whole as long as some of its pixels reach the floor. A stroke drawn entirely below the floor is indistinguishable from haze and is removed: lower the floor for very faint art. The report measures instead of asserting: it counts what actually changed.

| Field | Meaning |
|---|---|
| `floor`, `edge_px` | the settings |
| `pixels` | pixels in the image |
| `faint_fraction_before`, `faint_fraction_after` | share of all pixels with alpha from 1 to `floor - 1`, before and after |
| `haze_fraction_before`, `haze_fraction_after` | share of all pixels that are faint and farther than `edge_px` from a solid pixel |
| `cleared_pixels` | pixels made transparent |
| `changed_solid_pixels`, `changed_edge_pixels` | solid and kept-edge pixels whose value changed; `0` unless the cleanup is wrong |

## Report

`ui-kit.json`:

```json
{
  "kind": "sprite-gen-ui-kit",
  "version": 1,
  "sheet": "/abs/path/uikit.png",
  "sheet_size": [1024, 1024],
  "status": "pass",
  "review_reasons": [],
  "alpha_cleanup": { "floor": 64, "edge_px": 2, "...": "..." },
  "dropped_parts": 3,
  "unassigned": [],
  "elements": {
    "panel": {
      "file": "panel.png",
      "box": { "x": 48, "y": 48, "w": 576, "h": 400 },
      "rect": { "x": 52, "y": 50, "w": 570, "h": 396 },
      "size": { "w": 570, "h": 396 },
      "stretch": "xy",
      "insets": { "left": 112, "right": 110, "top": 92, "bottom": 90 },
      "padding": { "left": 40, "right": 40, "top": 38, "bottom": 38 },
      "parts": 1
    }
  }
}
```

`box` is the layout box scaled to this sheet (its fitted box when the report has `layout_fit`) and `rect` the element's bounding box, both in sheet pixels. A fill also has [`inside`](#fills); no other element has it. `file` is the element PNG's path from the report's own directory, with `/` separators: `panel.png` when the report is in `--out-dir` (the default), `../elements/panel.png` for `--out-dir elements --report reports/kit.json`. A reader joins it to the report's directory, as [`game-pack`](game-pack.md#version-2-request) does, so a report and its elements move together. `size`, `insets` and `padding` are in pixels of the element PNG. Elements appear in layout order. `status` is `needs-review` when any `review_reasons` apply; the PNGs are written either way, so the elements can be inspected.

A 2:3 report also has `missing`, the optional elements whose boxes were empty, in layout order ([missing elements](#missing-elements)). When the layout was [fitted to the drawing](#a-drawing-that-drifted-from-the-layout), the report has `layout_fit`, after `missing` and before `elements`; for a synthetic 1024 × 1536 sheet drawn 7 % shorter than its guide:

```json
"layout_fit": { "scale": { "x": 0.9969, "y": 0.9301 }, "offset": { "x": -0.2, "y": 0.0 } }
```

A layout box at (x, y, w, h), scaled to the sheet, was fitted to (x · scale.x + offset.x, y · scale.y + offset.y, w · scale.x, h · scale.y). `offset` is in sheet pixels, rounded to a tenth; `scale` is rounded to four decimals.

Like every measurement here, `pass` means the numbers found nothing to flag. Look at the elements stretched to a few sizes before shipping them.

## Python API

* `sprite_gen.frames.ui_kit.split_ui_kit(image, *, alpha_floor=64, alpha_edge=2) -> (elements, report)`: the elements as images by name, and the report as written to its default place, `<out-dir>/ui-kit.json` (each `file` is `<element>.png`), without `sheet`. A missing optional element is in neither; a `ValueError` when a required box is empty.
* `sprite_gen.frames.ui_kit.report_file(report, png) -> str` and `element_path(report, file) -> Path`: the `file` a report at `report` gives an element PNG, and the PNG a report's `file` names.
* `sprite_gen.frames.ui_kit.measure_insets(image, stretch) -> (insets, notes)` and `measure_padding(image) -> (padding, notes)`: the measures above on one element image, with the review notes they raise.
* `sprite_gen.frames.ui_kit.content_rect(record)` and `fit_inside(fill, frame, name) -> (inside, note)`: an element record's content rectangle, and a fill's `inside` with its review note.
* `sprite_gen.frames.ui_kit.sheet_layout(size) -> (reference_size, slots)`: the layout a sheet of that size holds; a `ValueError` for a shape that is neither square nor 2:3. Each slot's `optional` says whether a sheet may leave it out.
* `sprite_gen.frames.ui_kit.boxes(size)`, `draw_guide(path, size)` and `guide_text(size)`: the boxes a sheet of that size holds, the guide image and its prompt paragraph (`size` defaults to the square sheet).
* `sprite_gen.frames.alpha_floor.clear_haze(image, *, floor=64, edge=2) -> (image, report)`.
