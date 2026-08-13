# WebP budgets for agent vision

Encode captures as **lossy WebP** before the model Reads them. Tokens track resolution; request size tracks codec — PNG walls waste latency.

## Defaults (CLI) — conserve context

| Knob | Value | When |
|------|-------|------|
| **Short (lowest) edge** | **512** px (`--short-edge`) | **Default** — identity, element overview, layout-at-a-glance, anti-slop tells |
| Quality | **80** (`--quality`) | Default encode |
| Method | **4** (Pillow) | Default encode |
| Soft size | re-encode if **> 1 MB** | Safety net |
| Contact sheet | **≤ 2×2** tiles, ~12 px gutter | Still short-edge fitted after compose |

Never upscale small assets.

## When to raise budget (detail / full layout)

Only when 512 short-edge is **not enough**:

| Need | Flag |
|------|------|
| Zone in on glyphs, inspector text, 1px seams | `--detail` (long edge **1568**) or `--max-edge 1568` |
| Dense full-screen layout audit | `--detail` or `--max-edge 1568`–`2048` |
| Still blurry after detail | tighter `--region` crop first; then `--quality 90` |

```text
# overview / identity (default)
python scripts/capture.py window --title Godot

# details / OCR / full-layout
python scripts/capture.py window --title Godot --detail
python scripts/capture.py region --x 100 --y 100 --w 800 --h 600 --max-edge 1568
```

## Agent rules

- Prefer **1–3** WebPs per review turn
- **Start at short-edge 512**; escalate to `--detail` only after a fail that needs pixels
- Prefer one **sheet** over many single icon files
- Prefer window/region over 4K/5K full desktop
- After Read + rubric, prune old timestamps if cluttered (keep last few)

Implemented in [webp_encode.py](../scripts/webp_encode.py) and [asset_sheet.py](../scripts/asset_sheet.py).
