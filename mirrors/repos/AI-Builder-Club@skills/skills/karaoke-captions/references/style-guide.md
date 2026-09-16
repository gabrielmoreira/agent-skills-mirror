# ASS Style Reference Guide

This guide explains each parameter in `style.json` and how to adjust captions based on user requests.

---

## 1. Parameter Definitions

| Parameter | Type | Default | Description |
|---|---|---|---|
| `font` | string | `"Arial Black"` | Font name. |
| `font_size` | number | `64` | Subtitle font size (scaled against `play_res_y`). |
| `bold` | number | `1` | `1` for bold, `0` for regular weight. |
| `primary_color` | string | `"&H00FFFFFF"` | Normal word color (White). |
| `highlight_color` | string | `"&H0000FF00"` | Active reading word color (Neon Green). |
| `outline_color` | string | `"&H00000000"` | Text stroke outline color (Black). |
| `outline` | number | `5` | Outline width in pixels. |
| `shadow` | number | `2` | Drop shadow depth in pixels (`0` for flat stroke). |
| `alignment` | number | `2` | Subtitle position: `2` = Bottom-center, `5` = Center, `8` = Top-center. |
| `margin_v` | number | `60` | Vertical offset in pixels from edge (larger = higher up). |
| `uppercase` | boolean | `true` | Convert English text to all-caps. |
| `max_words_per_line` | number | `4` | Number of words shown simultaneously per screen (3-5 for Shorts/TikTok). |
| `max_gap` | number | `0.8` | Audio silence threshold (seconds) to split onto a new screen. |
| `break_on_punctuation` | boolean | `true` | Whether punctuation marks (`. , ! ?`) trigger a new phrase. |
| `play_res_x` | number | `1280` | Virtual canvas width (default 1280). |
| `play_res_y` | number | `720` | Virtual canvas height (default 720). |

---

## 2. ASS Color Code Quick Reference

ASS colors use **`&HAABBGGRR`** where:
- `AA` is transparency (`00` = opaque, `FF` = fully transparent).
- `BB` is Blue (`00` - `FF`).
- `GG` is Green (`00` - `FF`).
- `RR` is Red (`00` - `FF`).

| Color | ASS Value | Hex (RGB) |
|---|---|---|
| White | `&H00FFFFFF` | `#FFFFFF` |
| Neon Green | `&H0000FF00` | `#00FF00` |
| Yellow | `&H0000FFFF` | `#FFFF00` |
| Cyan / Aqua | `&H00FFFF00` | `#00FFFF` |
| Hot Pink / Magenta | `&H00FF00FF` | `#FF00FF` |
| Orange | `&H0000A5FF` | `#FFA500` |
| Red | `&H000000FF` | `#FF0000` |
| Pure Black | `&H00000000` | `#000000` |

---

## 3. How to Respond to User Customization Requests

- **"Make the captions larger / They are too small"**: Increase `font_size` (e.g. from `64` to `76` or `84`).
- **"Move the captions up / They cover the bottom of the video"**: Increase `margin_v` (e.g. from `60` to `120` or `160`).
- **"Change the highlight to yellow"**: Change `highlight_color` to `"&H0000FFFF"`.
- **"Show more words at a time / The phrases are too short"**: Increase `max_words_per_line` (e.g. from `4` to `6` or `7`).
- **"Show only 2-3 words at a time for a faster pace"**: Decrease `max_words_per_line` to `3` or `2`.
