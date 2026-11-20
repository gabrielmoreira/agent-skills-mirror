---
name: openmotion-sale-carousel
description: >-
  OpenMotion — Turn 3 to 7 sale products into one carousel video: a title card, one card per product
  with its photo, the regular price struck through, the sale price and a discount badge, then a grid of
  every pick with the code and a call to action. Use when someone asks for a gift guide, a "deals under
  $X" or "top picks" video, a multi-product Black Friday or holiday sale reel, or a product roundup.
  Produces an editable HyperFrames project and MP4 in 9:16, 4:5, 1:1 or 16:9.
---

# OpenMotion · Sale Carousel

An OpenMotion Skill. The shop's brand leads the film and its colour can replace the accent; the end
card carries a small "Made with OpenMotion" sign-off (`--no-credit` removes it).

Give a short list of products, get one reel that walks through them: 1.5 s title, 1.8 s per product,
2.9 s end shot (12.8 s for five products, 16.2 s for seven). Every price on screen is computed from the
regular price and the discount, so a batch of cards never shows a mistyped number.

## Look

A coverflow, not slides: the focused product card sits forward and large while its neighbours turn away in 3D and dim; each switch swings the whole row, the old price is struck and the discount tag pops. At the end every card fans into an arc above the code and call to action. Outlined title text drifts behind. Display type is Anton, shipped with the Skill (SIL OFL).

## 1. Collect the products

Ask for 3–7 products with a real photo, name, regular price and **one** of percent off / amount off /
sale price each, plus the occasion, a title ("Gifts under $100"), and optionally a code, a deadline and
a short URL. Use the shop's own photos; ask before generating any image with `openmotion_media_use`
then `openmotion_assets_use`, and get consent before paid generation. Keep the title honest: a "under
$100" title needs every sale price under 100.

## 2. Write carousel.json and check it

Use the [schema](references/schema.md), then:

```sh
node scripts/build.mjs --check carousel.json
```

The check refuses fewer than 3 or more than 7 products, a product without a photo file, prices that
do not add up, a malformed code, a deadline already past `postDate`, and text too long to fit. It
prints each computed price; read them back to the user.

## 3. Generate and render

```sh
node scripts/build.mjs carousel.json out/ [--aspect 9:16] [--no-credit]
cd out && npx hyperframes check && npx hyperframes render -o carousel.mp4
```

| Beat | What happens |
| --- | --- |
| Title | Occasion, title and "N picks" |
| Product × N | The row swings so this card comes forward; the regular price is struck through beside the sale price, the discount tag pops, the counter reads "01 / 05" |
| End | Every card fans into an arc; code, deadline, call to action, sign-off |

Card size follows the frame. The badge shows a percentage
unless the saving is small, where a flat amount reads better. `theme`, `brand.accent`, `locale` and
`labels` work as in the sale-promo Skill. The film is silent; add music in the editor and cut the
cards on the beat.

The generator uses the GSAP and Geist font installed with OpenMotion; when this Skill is installed on
its own, set `OPENMOTION_HOME` to the OpenMotion checkout or run `npm install gsap`. In OpenMotion,
import or open `out/` as a project and continue through the usual editor preview and export.

## 4. Review

Walk [references/review.md](references/review.md) and report what you checked.

## Provenance

The product-by-product structure with one template rendered from a list of items follows the
MIT-licensed [ecommerce-video-skills](https://github.com/iart-ai/ecommerce-video-skills) collection by
iart.ai (Copyright (c) 2026 iart.ai): its photo-slideshow and promo-video Skills. Those target Remotion;
this one is rewritten for OpenMotion's HTML compositions in our own words and code. This Skill is
Apache-2.0, like the rest of the repository.
