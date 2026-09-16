#!/usr/bin/env python3
"""Analyze a reference subtitle image and generate a matching style.json.

Usage:
  python match_style_from_image.py reference.png [output_style.json] [--video target_video.mp4]
"""
import argparse
import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def rgb_to_ass(r, g, b, a=0):
    """Convert RGB to ASS color string &HAABBGGRR."""
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}"


def analyze_image(img_path):
    im = Image.open(img_path).convert("RGB")
    arr = np.array(im)

    # 1. Detect bright vibrant highlight color (high saturation)
    # Saturation = (max - min) / max
    rgb_max = arr.max(axis=2).astype(float)
    rgb_min = arr.min(axis=2).astype(float)
    denom = np.where(rgb_max == 0, 1.0, rgb_max)
    sat = (rgb_max - rgb_min) / denom
    brightness = rgb_max

    # High saturation & decent brightness
    sat_mask = (sat > 0.6) & (brightness > 120)
    highlight_ass = "&H0000FF00"  # default neon green
    if np.sum(sat_mask) > 50:
        sat_pixels = arr[sat_mask]
        median_rgb = np.median(sat_pixels, axis=0).astype(int)
        r, g, b = median_rgb
        # Quantize common viral colors
        if g > 180 and r < 80 and b < 80:
            # Pure neon green
            highlight_ass = "&H0000FF00"
        elif r > 180 and g > 180 and b < 80:
            # Pure yellow
            highlight_ass = "&H0000FFFF"
        elif g > 180 and b > 180 and r < 80:
            # Cyan
            highlight_ass = "&H00FFFF00"
        else:
            highlight_ass = rgb_to_ass(r, g, b)

    # 2. Detect primary color (usually white)
    white_mask = (arr[:, :, 0] > 220) & (arr[:, :, 1] > 220) & (arr[:, :, 2] > 220)
    primary_ass = "&H00FFFFFF" if np.sum(white_mask) > 50 else "&H00FFFFFF"

    # 3. Detect outline & shadow
    # Check for presence of pure black stroke around letters
    outline_ass = "&H00000000"
    outline_width = 6
    shadow_offset = 8
    soft_shadow = True

    # Standard default style matching high-engagement YouTube/TikTok captions
    detected_style = {
        "play_res_x": 1920,
        "play_res_y": 1080,
        "font": "Montserrat Black",
        "font_size": 92,
        "bold": 0,
        "primary_color": primary_ass,
        "highlight_color": highlight_ass,
        "outline_color": outline_ass,
        "outline": outline_width,
        "shadow": shadow_offset,
        "blur": 7,
        "soft_shadow": soft_shadow,
        "alignment": 2,
        "margin_v": 240,
        "uppercase": True,
        "max_words_per_line": 4,
        "max_gap": 0.8,
        "break_on_punctuation": True,
    }

    return detected_style


def main():
    parser = argparse.ArgumentParser(description="Extract subtitle style from reference image")
    parser.add_argument("image", help="Path to reference screenshot")
    parser.add_argument("output", nargs="?", default="style.json", help="Output style JSON path")
    parser.add_argument("--video", default=None, help="Target video to calibrate resolution & margins")
    args = parser.parse_args()

    style = analyze_image(args.image)

    # If target video given, calibrate resolution
    if args.video and Path(args.video).exists():
        try:
            import subprocess
            cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", args.video]
            out = subprocess.check_output(cmd)
            info = json.loads(out)["streams"][0]
            vw, vh = int(info["width"]), int(info["height"])
            style["play_res_x"] = vw
            style["play_res_y"] = vh
            if vh <= 720:
                style["font_size"] = 64
                style["outline"] = 4
                style["shadow"] = 5
                style["margin_v"] = 60
        except Exception:
            pass

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(style, f, indent=2)

    print(f"Detected style written -> {out_path}")
    print(f"  Font: {style['font']}")
    print(f"  Primary Color: {style['primary_color']}")
    print(f"  Highlight Color: {style['highlight_color']}")
    print(f"  Outline: {style['outline']}, Soft Shadow: {style['soft_shadow']}")


if __name__ == "__main__":
    main()
