# Worked example — the stopwatch

The icon this pipeline was built around, from a real app.

| file | what it is |
|---|---|
| `still.png` | 512px RGBA still, `gpt-image-2.5-sunburst` |
| `timer.webp` | the finished loop — 288px, 122 frames @ 24fps, true alpha |
| `contact_sheet.png` | `verify` output: five frames on light and dark |

Reproducing it:

```bash
python -m iconloop --out out still \
  --prompt "a 3D stopwatch icon in sage green and cream, soft matte plastic, \
rounded friendly proportions, small feet and a top button"

python -m iconloop --out out animate \
  --motion "the stopwatch rocks gently side to side while its hand sweeps \
steadily clockwise"

python -m iconloop --out out matte
python -m iconloop --out out encode --sweep
python -m iconloop --out out encode --size 288 --name timer
python -m iconloop --out out verify
```

## What `verify` reports on the shipped file

```
[ok] motion      122 frames, mean step 7.25, 110/121 moving
[ok] loop seam   seam 2.04 against a mean step of 7.25
[ok] timer.webp  122 frames, 122 alpha chunks, VP8X 0x12, 1273 partial-alpha px
```

The seam being well under a normal frame step is the `end_image` trick working:
the loop closes without a visible hitch.

## What went wrong the first time

This asset originally shipped at **41 frames / 8fps** — sampled down from the
24fps render purely to keep the file under 400KB. It looked broken on device,
and the frame rate was the reason. The second icon in the same set was worse
still: its motion was a slow eased bob, and ease-in-out at 8fps hangs visibly
at each turnaround.

That is why `encode` defaults to the source rate and warns when you drop below
it. The size saving is real; it is just rarely worth it.
