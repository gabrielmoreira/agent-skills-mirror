#!/usr/bin/env python3
"""Generate karaoke-style ASS captions from word-level timestamps.

Input:
  words.json: {"words": [{"word": "TERMS", "start": 1.23, "end": 1.55}, ...]}
  style.json: typography, colors, layout, and phrase grouping configuration

Output:
  captions.ass: Dynamic ASS subtitles with word-by-word sweeping highlights.
  Supports soft blurred drop shadows (two-layer rendering) for high-end TikTok/Shorts aesthetics.

Usage:
  gen_ass.py words.json style.json captions.ass [--video input.mp4]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULTS = {
    "play_res_x": 1920,
    "play_res_y": 1080,
    "font": "Montserrat Black",
    "font_size": 92,
    "bold": 0,
    "primary_color": "&H00FFFFFF",    # white  (ASS = &HAABBGGRR)
    "highlight_color": "&H0000FF00",  # vibrant neon green
    "outline_color": "&H00000000",    # black
    "outline": 6,
    "shadow": 8,
    "blur": 7,
    "soft_shadow": True,
    "alignment": 2,                   # bottom-center
    "margin_v": 240,                  # bottom margin (pixels)
    "uppercase": True,
    "max_words_per_line": 4,
    "max_gap": 0.8,                   # split phrase on silence > this (sec)
    "break_on_punctuation": True,
}

PUNCT_END = re.compile(r"[.!?,;:\u2014\u2026\uff0c\u3002\uff01\uff1f\uff1b\uff1a]+[\"')\]]*$")


def probe_video_res(video_path):
    """Probe video dimensions via ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "json", str(video_path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        info = json.loads(out)
        stream = info["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except Exception:
        return None, None


def is_cjk(text):
    """Check if text contains Chinese/Japanese/Korean characters."""
    return any("\u4e00" <= c <= "\u9fff" or "\u3040" <= c <= "\u30ff" for c in text)


def group_words(words, cfg):
    """Split the word stream into short phrases (one screen each)."""
    phrases, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        full = len(cur) >= cfg.get("max_words_per_line", 4)
        punct = cfg.get("break_on_punctuation", True) and PUNCT_END.search(w["word"])
        gap = nxt and (nxt["start"] - w["end"]) > cfg.get("max_gap", 0.8)
        if full or punct or gap or nxt is None:
            phrases.append(cur)
            cur = []
    return phrases


def esc(text):
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def ts(sec):
    sec = max(sec, 0)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_events(phrases, cfg):
    hi = cfg["highlight_color"].rstrip("&") + "&"
    base = cfg["primary_color"].rstrip("&") + "&"
    events = []

    for phrase in phrases:
        texts = [esc(w["word"]) for w in phrase]
        if cfg.get("uppercase", True):
            texts = [t.upper() for t in texts]

        all_text = "".join(texts)
        sep = "" if is_cjk(all_text) else " "
        plain_text = sep.join(texts)

        for i, w in enumerate(phrase):
            start = w["start"]
            # hold highlight until the next word starts (prevents flicker during minor gaps)
            end = phrase[i + 1]["start"] if i + 1 < len(phrase) else phrase[-1]["end"]
            if end <= start:
                end = start + 0.05
            parts = []
            for j, t in enumerate(texts):
                if j == i:
                    parts.append(f"{{\\1c{hi}}}{t}{{\\1c{base}}}")
                else:
                    parts.append(t)
            events.append((start, end, plain_text, sep.join(parts)))
    return events


def main():
    parser = argparse.ArgumentParser(description="Generate karaoke ASS captions")
    parser.add_argument("words", help="Path to words.json")
    parser.add_argument("style", help="Path to style.json")
    parser.add_argument("ass", help="Path to output captions.ass")
    parser.add_argument("--video", default=None, help="Optional video file to auto-detect PlayResX/PlayResY")
    args = parser.parse_args()

    words_path = Path(args.words)
    style_path = Path(args.style)
    ass_path = Path(args.ass)

    if not words_path.exists():
        sys.exit(f"Error: words file not found: {words_path}")
    if not style_path.exists():
        sys.exit(f"Error: style file not found: {style_path}")

    with open(words_path, "r", encoding="utf-8") as f:
        words = json.load(f).get("words", [])
    with open(style_path, "r", encoding="utf-8") as f:
        custom_cfg = json.load(f)

    cfg = {**DEFAULTS, **custom_cfg}

    # If --video provided and dimensions not explicitly set, auto-detect
    if args.video and "play_res_x" not in custom_cfg:
        vw, vh = probe_video_res(args.video)
        if vw and vh:
            cfg["play_res_x"] = vw
            cfg["play_res_y"] = vh
            # Auto scale font_size and margin if 720p vs 1080p
            if vh <= 720 and "font_size" not in custom_cfg:
                cfg["font_size"] = 64
                cfg["outline"] = 4
                cfg["shadow"] = 5
                cfg["margin_v"] = 60

    words = [w for w in words if str(w.get("word", "")).strip()]
    phrases = group_words(words, cfg)
    events = build_events(phrases, cfg)

    soft_shadow = cfg.get("soft_shadow", True)
    shadow_val = 0 if soft_shadow else cfg.get("shadow", 2)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {cfg['play_res_x']}
PlayResY: {cfg['play_res_y']}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KaraokeShadow,{cfg['font']},{cfg['font_size']},&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,{cfg['outline']},0,{cfg['alignment']},40,40,{cfg['margin_v']},1
Style: Karaoke,{cfg['font']},{cfg['font_size']},{cfg['primary_color']},&H000000FF,{cfg['outline_color']},&H00000000,{cfg['bold']},0,0,0,100,100,0,0,1,{cfg['outline']},{shadow_val},{cfg['alignment']},40,40,{cfg['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    blur_amount = cfg.get("blur", 7)
    shad_y = cfg.get("shadow", 8)

    for start, end, plain_text, hi_text in events:
        if soft_shadow:
            # Layer 0: Gaussian-blurred dark drop shadow
            shadow_tag = f"{{\\alpha&H70&\\blur{blur_amount}\\xshad0\\yshad{shad_y}}}"
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},KaraokeShadow,,0,0,0,,{shadow_tag}{plain_text}\n")
            # Layer 1: Razor-sharp text with high-contrast outline and sweeping highlight
            lines.append(f"Dialogue: 1,{ts(start)},{ts(end)},Karaoke,,0,0,0,,{hi_text}\n")
        else:
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Karaoke,,0,0,0,,{hi_text}\n")

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Generated {len(phrases)} phrases, {len(events)} events -> {ass_path}")


if __name__ == "__main__":
    main()
