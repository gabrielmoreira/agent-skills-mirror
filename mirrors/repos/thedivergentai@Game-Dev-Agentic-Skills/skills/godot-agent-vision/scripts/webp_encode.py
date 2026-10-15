#!/usr/bin/env python3
"""WebP encode + vision context budgets (default: short-edge 512)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

# Default analysis: conserve context — short (lowest) edge 512.
DEFAULT_SHORT_EDGE = 512
# Detail / full-layout / OCR: long-edge cap when --detail / --max-edge is used.
DETAIL_MAX_EDGE = 1568
DEFAULT_QUALITY = 80
DEFAULT_METHOD = 4
SOFT_MAX_BYTES = 1_000_000

# Back-compat alias (detail tier)
DEFAULT_MAX_EDGE = DETAIL_MAX_EDGE


def fit_short_edge(im: Image.Image, short_edge: int = DEFAULT_SHORT_EDGE) -> Image.Image:
    """Downscale so the lowest edge is <= short_edge. Never upscale."""
    w, h = im.size
    low = min(w, h)
    if short_edge <= 0 or low <= short_edge:
        return im
    scale = short_edge / float(low)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def fit_max_edge(im: Image.Image, max_edge: int = DETAIL_MAX_EDGE) -> Image.Image:
    """Downscale so the long edge is <= max_edge. Never upscale."""
    w, h = im.size
    long_edge = max(w, h)
    if long_edge <= max_edge or max_edge <= 0:
        return im
    im = im.copy()
    im.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    return im


def save_webp(
    im: Image.Image,
    path: Path,
    *,
    short_edge: int = DEFAULT_SHORT_EDGE,
    max_edge: Optional[int] = None,
    quality: int = DEFAULT_QUALITY,
    method: int = DEFAULT_METHOD,
    lossless: bool = False,
) -> Tuple[Path, int]:
    """
    Resize + save lossy WebP. Returns (path, byte_size).

    Default: fit **short edge** to ``short_edge`` (512) for identity / overview.
    If ``max_edge`` is set (>0), use long-edge cap instead (detail / layout / OCR).
    Re-encodes at quality-10 if over SOFT_MAX_BYTES once.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    if max_edge is not None and max_edge > 0:
        out = fit_max_edge(base, max_edge)
    else:
        out = fit_short_edge(base, short_edge)
    # Prefer RGB for opaque screenshots (smaller).
    if out.mode == "RGBA" and not _has_useful_alpha(out):
        out = out.convert("RGB")

    q = quality
    _save(out, path, quality=q, method=method, lossless=lossless)
    size = path.stat().st_size
    if size > SOFT_MAX_BYTES and not lossless and q > 50:
        q = max(50, q - 10)
        _save(out, path, quality=q, method=method, lossless=False)
        size = path.stat().st_size
    return path, size


def _has_useful_alpha(im: Image.Image) -> bool:
    extrema = im.getextrema()
    if len(extrema) < 4:
        return False
    a_min, a_max = extrema[3]
    return a_min < 255


def _save(im: Image.Image, path: Path, *, quality: int, method: int, lossless: bool) -> None:
    kwargs = {"format": "WEBP", "method": method, "lossless": lossless}
    if not lossless:
        kwargs["quality"] = quality
    im.save(path, **kwargs)
