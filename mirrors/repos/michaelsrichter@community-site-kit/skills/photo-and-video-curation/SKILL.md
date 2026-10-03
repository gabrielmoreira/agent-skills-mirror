---
name: photo-and-video-curation
description: >-
  Choose, prepare and show photos and short videos on a community website without bad crops or copyright
  problems. Use when the owner shares a folder of photos or videos, asks for a homepage carousel or
  slideshow, says images are "cut off" or "weirdly cropped", asks to import photos from Google reviews or
  Facebook, or needs more pictures of people dancing. Covers rights, picking dancing photos, resizing,
  EXIF stripping, focus points, video trimming, slideshow behavior and the image inventory.
---
> `<kit>` = the folder where the community-site-kit plugin is installed (usually `~/.copilot/installed-plugins/community-site-kit/community-site-kit`; check with `copilot plugin list --json`) or a clone of github.com/michaelsrichter/community-site-kit. Run Node scripts from the site repo folder so they can use its `sharp`, `playwright` and `yaml` packages.


# Photo and video curation

## Rights first

| Source | OK? |
| --- | --- |
| Photos the organization or owner took, or a photographer who agreed | Yes. Record who and when in `docs/image-inventory.md` |
| Owner-provided photos with unknown photographer | Use, but list "permission unconfirmed" in the handoff email until confirmed |
| Google Maps review photos, Facebook members' photos | **No.** Link to them ("Photos & reviews on Google Maps") |
| Wikimedia Commons CC BY / CC BY-SA / CC0 / public domain | Yes, with credit (author, license, link). Label "not at our events" if they are not |
| Stock photos with a paid/unclear license | No |

## Pick the right photos (people dancing first)

1. Make a numbered contact sheet, newest files first (the owner's latest additions win):

   ```powershell
   node <kit>/skills/photo-and-video-curation/scripts/contact-sheet.mjs --dir "<photo folder>" --out sheet.png --cols 6 --newest-first
   ```

   Then **look at** `sheet.png` (view tool). Keep photos where people are clearly dancing, faces are
   flattering, and the image is sharp. Skip empty rooms, food, blurry or awkward shots, children unless the
   owner approved, and anything embarrassing. If the folder has many files, make several sheets (`--start`).
2. Prepare the chosen ones (auto-rotate, strip EXIF/GPS, resize to ≤ 1600 px, never upscale, mozjpeg):

   ```powershell
   node <kit>/skills/photo-and-video-curation/scripts/prepare-photos.mjs --in "<photo folder>" --pick "30,06,05" --out src/assets/uploads/<album> --prefix venue-name
   ```

   Run from the site repo (needs `sharp`). Output file names are lowercase slugs.
3. Videos: short (≤ 20 s), silent, 480 px wide, H.264 + faststart, ≤ ~1 MB, with a poster image:

   ```powershell
   node <kit>/skills/photo-and-video-curation/scripts/prepare-video.mjs --in "<clip.mp4>" --out public/media/videos/<name>.mp4 --start 2 --seconds 16 --width 480
   ```

   Needs ffmpeg: on PATH, or `npm i --no-save ffmpeg-static` in the current folder.
4. Need more photos? Search openly licensed ones and download with credits:

   ```powershell
   node <kit>/skills/photo-and-video-curation/scripts/find-cc-photos.mjs --query "lindy hop dancers" --limit 30 --out cc-candidates.json [--download out-folder --width 1600]
   ```

## Showing photos well

- **Never upscale.** Request widths no larger than the source (`ResponsiveImage` in the starter clamps them).
- **One crop at most.** Don't let the image pipeline crop *and* CSS `object-fit: cover` crop again.
- **Focus points**: store `focus: "50% 30%"` per image (CMS field). The starter's custom Astro image service
  (`src/lib/focus-image-service.mjs`) crops around it at build time; CSS uses `object-position` with the
  same value.
- Very wide banners (e.g. 1920×500) should not be forced into 4:3 or 1:1 boxes; show them wide or pick another photo.
- People photos in tight boxes (teacher cards, slideshow): show the whole image (`object-fit: contain`)
  over a blurred copy as the background, so nobody's head is cut off.
- Alt text describes what matters ("Couples swing dancing under string lights at the lodge"), not
  "image of". No text inside essential images.

## Homepage slideshow (when the owner wants one)

- Album flag `homepageSlideshow: true`; order = album order then item order; cap ~16 slides.
- Autoplay every ~6 s; pause/play button; previous/next buttons; swipe; arrow keys; a counter ("1 / 14")
  instead of dots when there are more than 8 slides; stops autoplay once a person chooses a slide;
  pauses on hover, focus, when off-screen and when `prefers-reduced-motion` is set.
- Slides are focusable `div`s (not a list with interactive descendants, which axe flags).
- Video slides: muted, `playsinline`, loop, `preload="none"`, `data-src` loaded only when the slide is
  near; play only while visible.
- SWA config: add the `.mp4` MIME type and long cache headers for `/media/*`; CSP `media-src 'self'`.

## Inventory

Update `docs/image-inventory.md`: file, source/photographer, permission status, license + credit URL,
where used, focus point. Mention open permission questions in the owner email.
