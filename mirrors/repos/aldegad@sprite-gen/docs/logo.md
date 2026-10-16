# `sprite-gen logo` — typography from a mood image

> Owns: `sprite-gen logo`: a title logo, wordmark or title lettering drawn by the model inside the picture it belongs to, then lifted out of it as a transparent PNG — the three steps, the files and the report, the text check and its refusals, the key choice, the logo matte and its known limit · Index: [docs/README.md](README.md)

Lettering asked for on its own comes back as a font with an effect laid over it. Asked
for inside the picture it belongs to — a game's title screen, a poster — the model draws it
as part of that world: its letterforms, materials and light come from the scene. So a logo
is made in three steps:

1. **mood** — a title screen (16:9) or poster (2:3) in the brief's style with the title
   lettered in it. The text check reads it back; a title the model dropped or misspelt is
   refused here, before the next image is bought.
2. **lettering** — that picture attached as the reference of an image edit that asks for
   only its lettering, with the same letterforms, materials, colours, outlines, glows and
   effects, on a flat chroma key.
3. **matte** — the key removed by the logo matte (soft glows and partial alpha kept, no key
   hue left), trimmed to the lettering with a 2 px margin. The logo's text is read again on a
   plain backdrop; letters that differ from the text asked are refused.

Nothing in this path draws a font. A step that cannot be done fails and says why; it is
never replaced by rendered text or by another provider.

```bash
sprite-gen logo --provider codex --text "STARFALL" --style "painted fantasy" --out-dir logo/
sprite-gen logo --provider codex --text "Iron Lantern" --subtitle "Chapter One" --style "16-bit pixel art" --out-dir logo/
sprite-gen logo --provider codex --text "별빛 기사" --language Korean --style "painted fantasy" --out-dir logo/
sprite-gen logo --provider codex --text "STARFALL" --mood title-screen.png --out-dir logo/   # start from a picture you have
sprite-gen logo --provider codex --text "STARFALL" --lettering logo/lettering.png --out-dir logo/  # cut again, nothing generated
```

| Option | Meaning |
|---|---|
| `--text` | the title the logo spells; empty is refused before anything is bought |
| `--subtitle` | an optional short line, lettered smaller with the title and checked with it |
| `--style`, `--scene` | style words, and what the mood image shows besides the title |
| `--composition` | `title-screen` (16:9, default) or `poster` (2:3); `--aspect-ratio` overrides the ratio (codex ignores ratios: the prompt says it) |
| `--language` | the script the lettering is in (`Korean`, `Japanese`, …) |
| `--mood PATH` | start from a picture with the title already in it (a title screen you have, a candidate you picked): step 1 is not generated, its text is still read |
| `--lettering PATH` | a lettering image already on a key is cut again (after a matte change, or for a lettering drawn elsewhere): nothing is generated; the logo's text is still read |
| `--chroma-key` | `auto` (default), `magenta` or `green` — [below](#which-key) |
| `--provider`, `--model`, `--quality`, `--resolution` | as `gen`, for both images and both text checks ([gen](gen.md)) |
| `--out-dir`, `--report` | where the files go; the report defaults to `<out-dir>/logo.report.json` |

## Files

| File | What it is |
|---|---|
| `mood.png` | step 1: the picture with the title in it (or a copy of `--mood`) |
| `lettering.png` | step 2: the lettering alone on the key, as the model drew it |
| `logo.png` | step 3: the transparent logo, trimmed; written only when its text reads as asked (or could not be checked, below) |
| `logo.rejected.png` | the cut of a logo whose text did not read as asked, kept aside for a look |
| `logo.preview.png` | the logo on a dark and on a light backdrop, side by side: where a halo or a hard edge would show |
| `logo.report.json` | the report |

A run removes an earlier run's `lettering.png`, `logo*.png` from its folder first, so a
file there is always this run's (an input named with `--mood` or `--lettering` is kept).

## The report

`kind: sprite-gen-logo-report`, with `status`: `ok`; `unverified` (the logo was made but
its text could not be checked); `refused` (with `refused_at`: `mood-check`, `matte` or
`logo-check`, and `reason`); `failed` (a step failed: a provider refusal, a timeout). Then:

- `text`, `subtitle`, `language`, `style`, `scene`, `composition`, `provider` and how it was
  resolved (`provider_resolved_from`, `provider_fallback`, as `gen`);
- `steps.mood` (`source`: `generated`, `given` or `none`; the prompt sent), `steps.key`,
  `steps.lettering` (the prompt, the reference, `raw_alpha`), `steps.matte` (the matte's own
  numbers, below) and `steps.trim` (`bbox` in the lettering image, sizes, `pad_px`);
- `logo`: `size`, `alpha` (`opaque_pct`, `partial_pct`, `empty_pct` of the trimmed logo and
  `visible_opaque_share`) and `key_hue_left` (visible pixels whose colour still carries the
  key's hue — 0 is the aim);
- `text_check.mood` and `text_check.logo` (below);
- `calls`: every call in order — `mood`, `mood-check`, `lettering`, `logo-check` — with its
  provider, model, `auth_source`, `transport`, `elapsed_seconds` for the images, and `route`:
  `subscription` (a codex ChatGPT login, a Grok login) or `per-call` (a codex API-key login,
  `XAI_API_KEY`, `OPENAI_API_KEY`; each said on stderr before its request leaves, as every
  metered call in sprite-gen is);
- `warnings`.

## The text check

The provider that drew the images reads them back, once each, through the same vision call
the facing check uses (`inspect_image`; codex `exec` read-only and ephemeral, or the xAI or
OpenAI Responses API on the same credential). It is asked to return the lines of text as
spelled, without being told what they should say. Both checks compare by one rule
(`logo.normalize`), what the text spells:

- **kept** — every letter and digit, and every mark written on one: an accent, a vowel
  sign, a virama, a nukta, a tone mark, a voiced mark. `किला` read as `कला` (the vowel sign
  `ि` gone) is a mismatch, and so is `Café` read as `CAFE`. An accent counts on a capital
  too: for lettering in capitals that go without their accents (as Greek capitals do), give
  the title that way. Hangul is compared by its syllables, so `별` written as jamo is `별`;
- **folded away** — case, compatibility forms (full-width letters, ligatures, `Ⅳ` and
  `IV`), the characters drawn as nothing (joiners, variation selectors), enclosing marks (a
  keycap), and spaces, punctuation and symbols, with any mark written on them. So `Hero's
  Quest` matches `HERO’S QUEST!` and `I O N` matches `ION`.

The subtitle may be read before or after the title. The verdict is one of:

| Verdict | At the mood image | At the logo |
|---|---|---|
| `match` | go on to the lettering | publish `logo.png`, `status: ok` |
| `mismatch`, `no-text` | refused: the lettering is not bought | refused: the cut is kept as `logo.rejected.png` |
| `unverified` (the call failed, or its answer was not the JSON asked for) | a warning; go on | `logo.png` is published with `status: unverified` and a warning: look at the preview |

A model that reads stylised lettering can misread it; a refusal names what was read, so a
person can judge, and `--mood` or `--lettering` starts again from the files already made.

## Which key

The lettering keeps the mood image's colours, and the matte needs a key no letter is made
of. The mood check also returns the box round the title, and `--chroma-key auto` scores the
two keys on the colours inside it (`logo_matte.choose_key`, the whole image when no box came
back): a pixel already in a key's hue (a pink letter on magenta) counts hard against that
key, and every other colour scores how long its mix with the key keeps the key's hue — which
is how long a glow of that colour keeps its fade ([the known limit](#known-limit)). A cyan
or yellow glow keeps green's hue to about 85 % coverage and magenta's to about half; an
orange one the other way; a white or cream glow keeps either. Magenta wins a tie.
`steps.key` records the key, `source` (`auto`, `explicit`, or `border` for `--lettering`),
`region` and both keys' scores. Name the key yourself when you know the lettering better.

## The logo matte

`sprite_gen.frames.logo_matte`. The sprite matte behind `cutout` and `extract` ramps
coverage over a short chroma distance, which suits a sprite's one-pixel edge: on a white
glow it is opaque half way to white, keeping the pink mix of glow and key (a halo), and cuts
the last fifth of the fade to nothing (a hard edge). The logo matte instead explains each
pixel as `alpha × colour + (1 − alpha) × background` and writes the colour with the key's
share taken out:

- the **background** is the key as painted, a quadratic surface fitted to the key's pixels,
  so a vignette stays background; its noise is measured there. The border band must be at
  least half key, or the image is refused (`the lettering image's border is not the … key`);
- a pixel far from the key in chroma and without the key's hue is the lettering's own
  material: opaque, as drawn — except a rim pixel that is a mix of the key with the colour
  just inside it, which is a letter's antialiased edge;
- every other pixel is a mix. Next to a letter, a pixel that lies on the line from the key
  to one of the letters' own colours (learned where a letter meets the key) — a letter's
  antialiased edge — takes its coverage by projection, in the letter's colour; any other
  mix — a glow — takes the least coverage any colour could have, which is exact for the
  bright, saturated colours glows are and never leaves the key's hue in the colour;
- a glow's last trace, under the noise of one pixel, is measured on the mean of its faint
  neighbours, so it fades out instead of ending in an edge;
- coverage under 3/255, isolated faint specks, and faint coverage on the picture's outer
  4 px (a generated picture's edge often carries a seam a few levels off the key) are
  cleared, and transparent pixels carry no colour.

`steps.matte` reports the background (`mean`, `spread`, `sigma`, `border_key_pct`), and the
pixel counts: `solid_px`, `edge_px` (where the palette was learned), `blend_px` (explained by
a letter colour), `unmix_px` (glow), `faint_px`, `partial_px`, `specks_cleared_px`,
`frame_seam_cleared_px`, `palette_size`. A lettering image that came back with its own
transparent background (codex sometimes answers an edit with alpha) is kept on that alpha
(`method: native-alpha`); a key painted as a transparency checkerboard is refused.

### Known limit

The dense part of a glow, past the coverage where its mix with the key still shows the
key's hue, cannot be told from a letter of that mixed colour by its pixels, and is kept
opaque in it: a cyan glow pooled in an O's counter on magenta (past about half coverage), or
the ring round a small gold sparkle's white core on green (past about three quarters: a
faint olive cast on a light backdrop). On the key whose hue the glow shares more it keeps
its fade (`tests/frames/test_logo_matte.py` holds both sides): that is what
`--chroma-key auto` weighs, after the letters' own colours — a letter in the key's hue would
be lost entirely, so it counts more. When `logo.preview.png` shows such a ring where a glow
is dense, cut the same lettering on the other key's terms by generating it again with
`--chroma-key` (or accept the ring: at full size it sits inside the glow's brightest part).

## Cost

Four calls a logo — two images and two text checks — on the provider named. On a
subscription (codex ChatGPT login, Grok login) nothing is billed per call; `calls[].route`
says which route each ran on. `--mood` saves the first image, `--lettering` both. Nothing is
sent again on its own: a refusal is said and the run ends.

## Related

- [gen](gen.md) — the image calls, providers and their credentials
- [sheet-slicing](sheet-slicing.md) — `cutout`, the uniform-background cut for sprites
- [curation](curation.md) — a view to pick between logo candidates (`unpack-atlas --pngs-dir`)
