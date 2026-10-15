#!/usr/bin/env python3
"""Build single-asset or contact-sheet images for vision review."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga", ".gif"}


def resolve_project_path(raw: Union[Path, str], project_root: Path) -> Path:
    """
    Resolve filesystem paths and Godot ``res://`` / ``res:/`` URIs against project_root.
    """
    project_root = Path(project_root).resolve()
    text = str(raw).replace("\\", "/")
    if text.startswith("res://"):
        rel = text[len("res://") :]
        return (project_root / rel).resolve()
    if text.startswith("res:/"):
        rel = text[len("res:/") :]
        return (project_root / rel).resolve()
    p = Path(raw)
    if p.is_absolute():
        return p
    # Prefer cwd-relative if it exists; else project-root-relative
    cwd_candidate = Path.cwd() / p
    if cwd_candidate.exists():
        return cwd_candidate.resolve()
    return (project_root / p).resolve()


def collect_images(
    paths: Sequence[Union[Path, str]],
    *,
    project_root: Optional[Path] = None,
    recursive: bool = True,
) -> List[Path]:
    root = Path(project_root).resolve() if project_root else Path.cwd()
    out: List[Path] = []
    for raw in paths:
        p = resolve_project_path(raw, root)
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            out.append(p)
        elif p.is_dir():
            pattern = "**/*" if recursive else "*"
            for child in sorted(p.glob(pattern)):
                if child.is_file() and child.suffix.lower() in IMAGE_EXTS:
                    out.append(child)
    # Dedupe preserving order
    seen = set()
    unique: List[Path] = []
    for p in out:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def load_rgb(path: Path) -> Image.Image:
    im = Image.open(path)
    im = im.convert("RGBA")
    return im


def single_asset(path: Path) -> Image.Image:
    return load_rgb(path)


def contact_sheet(
    paths: Sequence[Path],
    *,
    max_tiles: int = 4,
    gutter: int = 12,
    label_h: int = 28,
    cell: int = 512,
    labels: Optional[Sequence[str]] = None,
) -> Image.Image:
    """
    Up to 2x2 contact sheet (max_tiles default 4) with filename labels.
    """
    tiles = list(paths)[: max(1, max_tiles)]
    n = len(tiles)
    cols = 1 if n == 1 else (2 if n > 1 else 1)
    rows = (n + cols - 1) // cols
    W = cols * cell + (cols + 1) * gutter
    H = rows * (cell + label_h) + (rows + 1) * gutter
    canvas = Image.new("RGB", (W, H), (28, 28, 32))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i, path in enumerate(tiles):
        r, c = divmod(i, cols)
        x0 = gutter + c * (cell + gutter)
        y0 = gutter + r * (cell + label_h + gutter)
        im = load_rgb(path)
        im.thumbnail((cell, cell), Image.Resampling.LANCZOS)
        ox = x0 + (cell - im.width) // 2
        oy = y0 + (cell - im.height) // 2
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (28, 28, 32))
            bg.paste(im, mask=im.split()[-1])
            canvas.paste(bg, (ox, oy))
        else:
            canvas.paste(im.convert("RGB"), (ox, oy))
        label = labels[i] if labels and i < len(labels) else path.name
        if len(label) > 40:
            label = label[:37] + "..."
        draw.text((x0, y0 + cell + 4), label, fill=(220, 220, 220), font=font)
    return canvas
