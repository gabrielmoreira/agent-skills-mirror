#!/usr/bin/env python3
"""Export an interactive deck to a content-complete PDF — one image per slide.

This captures what the audience actually sees. Because the deck is interactive, two
things are handled deliberately:

  1. Wait for render. After moving to each slide it waits for the network to settle
     and for entrance animations to finish, so nothing is captured half-drawn.
  2. Reveal hidden content. Anything hidden by opacity/animation (e.g. step reveals,
     Framer Motion entrances) is forced visible before the screenshot, so click-gated
     content shows up in the PDF without anyone clicking through it.

The output is image-based (no selectable text) by design: the goal is a faithful,
full-content capture, not a text document.

Requires:
    pip install playwright pillow
    playwright install chromium

Usage:
    python export-deck-pdf.py <url-or-file> [-o out.pdf] [--width 1920] [--height 1080] [--wait 0.8]

<url-or-file>:
    React deck  -> the dev-server URL (e.g. http://localhost:5173)
    HTML deck   -> a file path or file:// URL to index.html
"""
import argparse
import io
import os
import re
import sys
import time

# Inject before each screenshot: kill animation timing and force opacity-/visibility-
# hidden content visible. It does NOT force every .slide container open (those are
# navigated one at a time), only intra-slide content that a click would have revealed.
REVEAL_JS = r"""
() => {
  let s = document.getElementById('__deck_export_css__');
  if (!s) {
    s = document.createElement('style');
    s.id = '__deck_export_css__';
    document.head.appendChild(s);
  }
  s.textContent = `
    *, *::before, *::after { animation: none !important; transition: none !important; }
    [style*="opacity:0"], [style*="opacity: 0"],
    .opacity-0, [data-reveal], [hidden] {
      opacity: 1 !important; visibility: visible !important;
    }
    [hidden] { display: revert !important; }
  `;
}
"""


def to_url(target: str) -> str:
    if re.match(r"^https?://", target) or target.startswith("file://"):
        return target
    return "file://" + os.path.abspath(target)


def main() -> int:
    ap = argparse.ArgumentParser(description="Export an interactive deck to a content-complete PDF.")
    ap.add_argument("target", help="dev-server URL (React) or file path / file:// URL (HTML)")
    ap.add_argument("-o", "--output", default="slides.pdf", help="output PDF path (default: slides.pdf)")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--wait", type=float, default=1.5,
                    help="seconds to wait after each slide for render/animation (Framer Motion stagger needs ~1.5s)")
    ap.add_argument("--max-slides", type=int, default=200, help="safety cap for keyboard fallback")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Missing dependency. Run: pip install playwright pillow && playwright install chromium", file=sys.stderr)
        return 2
    try:
        from PIL import Image
    except ImportError:
        print("Missing dependency. Run: pip install pillow", file=sys.stderr)
        return 2

    url = to_url(args.target)
    shots: list[bytes] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=2,
        )
        page.goto(url, wait_until="load")
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # Slides expose one dot per slide. The scaffolds use aria-label "Slide N";
        # older hand-built decks sometimes use a title like "Đến Slide N". Match both.
        def is_dot(el):
            label = el.get_attribute("aria-label") or ""
            title = el.get_attribute("title") or ""
            return bool(re.fullmatch(r"Slide \d+", label) or re.search(r"[Ss]lide \d+", title))
        dots = [d for d in page.query_selector_all('[aria-label], [title]') if is_dot(d)]
        # De-dupe while keeping order (an element could match both attrs).
        seen, uniq = set(), []
        for d in dots:
            key = d.get_attribute("aria-label"), d.get_attribute("title")
            if key not in seen:
                seen.add(key); uniq.append(d)
        dots = uniq

        # Fluid decks fill the viewport, so a full-page screenshot at the configured
        # width/height is already an exact frame. Older fixed-canvas decks expose a
        # #stage element — screenshot that directly for a pixel-exact 1920x1080 frame.
        stage = page.query_selector("#stage")

        def shoot():
            page.evaluate(REVEAL_JS)
            time.sleep(args.wait)
            target_el = stage if stage else None
            return target_el.screenshot() if target_el else page.screenshot()

        if dots:
            for i, dot in enumerate(dots):
                dot.click()
                time.sleep(0.2)
                shots.append(shoot())
                print(f"  captured slide {i + 1}/{len(dots)}")
        else:
            # Fallback: drive with the keyboard until the frame stops changing.
            page.keyboard.press("Home")
            last = None
            for i in range(args.max_slides):
                img = shoot()
                if img == last:
                    break
                shots.append(img)
                last = img
                print(f"  captured slide {i + 1}")
                page.keyboard.press("ArrowRight")
                time.sleep(0.2)

        browser.close()

    if not shots:
        print("No slides captured — check the URL and that the deck rendered.", file=sys.stderr)
        return 1

    images = [Image.open(io.BytesIO(b)).convert("RGB") for b in shots]
    images[0].save(args.output, save_all=True, append_images=images[1:])
    print(f"✅ Wrote {len(images)}-page PDF: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
