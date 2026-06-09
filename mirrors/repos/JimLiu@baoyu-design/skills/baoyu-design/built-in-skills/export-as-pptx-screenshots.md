---
name: "export-as-pptx-screenshots"
description: "Export as PPTX (screenshots)\nFlat images — pixel-perfect but not editable"
---
# Screenshot PPTX Export

Export an HTML slide deck to a `.pptx` as full-bleed PNG images. Pixel-perfect, not editable. One `gen_pptx` tool call.

## Steps

1. Surface/preview the deck per your selected harness reference.
2. Call `gen_pptx`:

```jsonc
{
  "mode": "screenshots",
  "width": 1920, "height": 1080,
  "slides": [
    { "showJs": "goToSlide(0)", "selector": "body" },  // selector unused in screenshot mode but required
    { "showJs": "goToSlide(1)", "selector": "body" }
  ],
  "hideSelectors": [".nav", ".progress"],
  // No resetTransformSelector in screenshot mode — the iframe is locked to
  // width × height for capture, so the deck's own responsive scaling fills it.
  "filename": "my-deck"
}
```

`slides[].delay` defaults to 600ms — bump if transitions are slower.

### If the deck uses the `<deck-stage>` starter component

- `slides[N].showJs`: `"document.querySelector('deck-stage').goTo(N)"` — 0-indexed, so slide 1 is `goTo(0)`.
- `hideSelectors` is unnecessary — the overlay and tap-zones live in shadow DOM and aren't captured.

## Validation

Same flags as editable mode, except `reset_selector_miss` and `slide_size_mismatch` won't fire — the iframe is locked to width × height instead of fiddling with the deck's wrapper. Watch for `duplicate_adjacent` (showJs didn't navigate).

Speaker notes from `#speaker-notes` are attached automatically. Page reloads after.
