---
name: openmotion-sale-promo
description: >-
  OpenMotion — Turn one sale offer into a punchy 10 or 15 second promo video: the occasion, the
  discount, the old price struck through as the new price lands, the promo code with its real
  deadline, and a call to action. Use when someone asks for a Black Friday, Cyber Monday, holiday,
  flash-sale or clearance video, a discount reveal, a was/now price drop or a promo-code ad.
  Produces an editable HyperFrames project and MP4 in 9:16, 4:5, 1:1 or 16:9.
---

# OpenMotion · Sale Promo

An OpenMotion Skill. The advertiser's brand is the hero: its name leads the film and its colour can
replace the accent. The end card carries a small "Made with OpenMotion" sign-off; leave it on unless
the user asks for `--no-credit`.

Give one offer, get a sale spot people can act on:

1. **`offer.json`** — the product, its regular price, the discount, the code, the deadline and the call to action.
2. **An editable HyperFrames project** generated from that file (five beats, 10 or 15 s) and its **MP4**.

A promo that shows a wrong price is worse than no promo. The script derives the sale price, the
percentage and the saving from the regular price, so they can never disagree; spend the effort on
getting the offer facts right.

## Look

One continuous world instead of slides: the product photo stays on screen for the whole film (slow
push-in, then it reframes into a card and opens back out), a diagonal sale tape scrolls the offer from
first frame to last, a circular badge keeps spinning, and display type (Anton, shipped with the Skill
under the SIL Open Font License) rises through line masks. Use a real, well-lit product photo on a clean
backdrop with empty space in the lower third; a weak photo makes a weak film.

## 1. Collect the offer

Ask for, or read from the user's page: brand name, occasion, product name and photo, regular price,
**one** of percent off / amount off / sale price, currency, promo code, the real end date and time with
its time zone, call to action and short URL. Use the user's own product photo. If they have none, ask
before generating one with `openmotion_media_use` (discover providers and model IDs) then
`openmotion_assets_use`; get consent before any paid generation. Never invent a discount, a code or a
deadline.

One video carries one offer. Two offers make two videos: run the script once per row.

## 2. Write offer.json and check it

Use the [schema](references/schema.md), then:

```sh
node scripts/build.mjs --check offer.json
```

The check refuses: no price or more than one way to state the discount, a sale price at or above the
regular price, a code that is not 3–16 capital letters or digits, a missing deadline or one that is
already past `postDate`, a missing photo file, and text too long to fit. It prints the computed prices;
read them back to the user.

## 3. Generate and render

```sh
node scripts/build.mjs offer.json out/ [--aspect 9:16] [--duration 10] [--no-credit]
cd out && npx hyperframes check && npx hyperframes render -o promo.mp4
```

| Beat | 10 s | What happens |
| --- | --- | --- |
| Hook | 0–1.7 s | The occasion rises word by word over the full-frame photo |
| Discount | 1.7–4.0 s | "40% OFF" (or "$50 OFF" for low prices) fills the frame over a darker veil |
| Price | 4.0–7.0 s | The photo reframes into a card; the regular price is struck through first, then the sale price counts down; a discount tag pops |
| Code | 7.0–8.6 s | The code in a dashed chip and the deadline beside the card, held still |
| Call to action | 8.6–10 s | The photo opens back to full frame; occasion, button, URL, sign-off |

15 s stretches every beat. Default is 9:16 (1080×1920) because sale ads run as vertical video;
`--aspect` writes 4:5, 1:1 or 16:9 from the same data. `theme` picks a palette (`black-friday`,
`cyber-monday`, `holiday`, `new-year`, `light`) and `brand.accent` overrides its accent. `labels`
translates the fixed words ("OFF", "Use code", "Save") for other languages; prices follow `locale`.

The film has no soundtrack. Add the user's licensed music in the editor and land the discount beat on
a strong hit. The generator uses the GSAP and Geist font installed with OpenMotion; when this Skill is
installed on its own, set `OPENMOTION_HOME` to the OpenMotion checkout or run `npm install gsap`.

In OpenMotion, import or open `out/` as a project and continue through the usual editor preview and
export. Updating an existing managed project uses the shared project-edit contract with its current
revision; do not write around version protection.

## 4. Review

Walk [references/review.md](references/review.md) from a contact sheet and stills at each beat. Report
what you checked; do not self-certify that it "looks good".

## Provenance

The offer arc (hook → discount → was/now → code and deadline → call to action), computing every number
from the regular price, and "strike first, then land the new price" follow the MIT-licensed
[promo-video](https://github.com/iart-ai/ecommerce-video-skills/tree/main/skills/promo-video) Skill by
iart.ai (Copyright (c) 2026 iart.ai). That Skill targets Remotion; this one is rewritten for
OpenMotion's HTML compositions in our own words and code. This Skill is Apache-2.0, like the rest of the
repository.
