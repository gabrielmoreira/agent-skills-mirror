#!/usr/bin/env python3
"""Prepare, split, screen, and document scientific figure-image audits.

This script is deliberately deterministic.  It creates candidates and evidence;
it never assigns a scientific-integrity verdict.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
FIGURE_RE = re.compile(r"(?im)^\s*(?:figure|fig\.)\s*[s]?\d+[a-z]?\b")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def core_modules():
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageOps
    except ImportError as error:
        raise SystemExit(
            "Pillow and NumPy are required. Load local-env-setup and install "
            "python, pillow, numpy, pypdf, pypdfium2, and opencv."
        ) from error
    return np, Image, ImageDraw, ImageOps


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_sha256(image) -> str:
    rgb = image.convert("RGB")
    digest = hashlib.sha256()
    digest.update(f"{rgb.width}x{rgb.height}:RGB\0".encode())
    digest.update(rgb.tobytes())
    return digest.hexdigest()


def slug(value: str, fallback: str = "item") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.")
    return cleaned or fallback


def parse_pages(spec: str | None, total: int) -> list[int]:
    """Return sorted one-based page numbers."""
    if not spec or spec.strip().lower() in {"all", "*"}:
        return list(range(1, total + 1))
    pages: set[int] = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            try:
                start, end = int(start_text), int(end_text)
            except ValueError as error:
                raise ValueError(f"invalid page range: {token!r}") from error
            if start > end:
                raise ValueError(f"descending page range is not allowed: {token!r}")
            pages.update(range(start, end + 1))
        else:
            try:
                pages.add(int(token))
            except ValueError as error:
                raise ValueError(f"invalid page number: {token!r}") from error
    invalid = sorted(page for page in pages if page < 1 or page > total)
    if invalid:
        raise ValueError(f"page(s) outside 1-{total}: {invalid}")
    return sorted(pages)


def require_new_workspace(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty audit workspace: {path}")
    path.mkdir(parents=True, exist_ok=True)


def save_normalized(image, destination: Path):
    _, _, _, ImageOps = core_modules()
    normalized = ImageOps.exif_transpose(image).convert("RGB")
    normalized.save(destination, format="PNG", optimize=True)
    return normalized


def ink_bounds(image) -> tuple[int, int, int, int]:
    np, _, _, _ = core_modules()
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    ink = gray < 248
    ys, xs = np.nonzero(ink)
    if len(xs) < 16:
        return (0, 0, image.width, image.height)
    pad = max(2, int(min(image.size) * 0.004))
    return (
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(image.width, int(xs.max()) + 1 + pad),
        min(image.height, int(ys.max()) + 1 + pad),
    )


def _runs(flags: Iterable[bool]) -> list[tuple[int, int]]:
    values = list(flags)
    result: list[tuple[int, int]] = []
    start = None
    for index, flag in enumerate(values + [False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            result.append((start, index))
            start = None
    return result


def propose_panel_boxes(image, max_panels: int = 64) -> list[list[int]]:
    """Conservatively split at full-width/full-height white gutters.

    These boxes are review proposals, not authoritative segmentation.
    """
    np, _, _, _ = core_modules()
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    root = ink_bounds(image)
    min_w = max(90, int(image.width * 0.07))
    min_h = max(90, int(image.height * 0.07))

    def recurse(box: tuple[int, int, int, int], depth: int) -> list[tuple[int, int, int, int]]:
        x0, y0, x1, y1 = box
        width, height = x1 - x0, y1 - y0
        if depth >= 6 or width < min_w * 2 or height < min_h * 2:
            return [box]
        region = gray[y0:y1, x0:x1]
        ink = region < 248
        row_density = ink.mean(axis=1)
        col_density = ink.mean(axis=0)
        row_runs = _runs(row_density <= 0.002)
        col_runs = _runs(col_density <= 0.002)
        candidates: list[tuple[float, str, int, int]] = []

        for axis, runs, length, minimum in (
            ("row", row_runs, height, min_h),
            ("col", col_runs, width, min_w),
        ):
            min_gap = max(5, int(length * 0.008))
            for start, end in runs:
                if end - start < min_gap:
                    continue
                midpoint = (start + end) // 2
                if midpoint < minimum or length - midpoint < minimum:
                    continue
                balance = min(midpoint, length - midpoint) / max(length, 1)
                score = (end - start) / max(length, 1) + 0.25 * balance
                candidates.append((score, axis, start, end))

        candidates.sort(reverse=True)
        for _, axis, start, end in candidates:
            midpoint = (start + end) // 2
            if axis == "row":
                first = (x0, y0, x1, y0 + midpoint)
                second = (x0, y0 + midpoint, x1, y1)
            else:
                first = (x0, y0, x0 + midpoint, y1)
                second = (x0 + midpoint, y0, x1, y1)
            pieces = [first, second]
            enough_ink = True
            for px0, py0, px1, py1 in pieces:
                part = gray[py0:py1, px0:px1]
                if part.size == 0 or float((part < 248).mean()) < 0.002:
                    enough_ink = False
            if enough_ink:
                return recurse(first, depth + 1) + recurse(second, depth + 1)
        return [box]

    boxes = recurse(root, 0)
    if len(boxes) == 1 or len(boxes) > max_panels:
        return [[0, 0, image.width, image.height]]
    boxes.sort(key=lambda box: (box[1], box[0]))
    return [list(map(int, box)) for box in boxes]


def make_contact_sheet(items: list[tuple[str, Any]], path: Path, cell=(320, 260)) -> None:
    if not items:
        return
    _, Image, ImageDraw, _ = core_modules()
    columns = min(4, max(1, math.ceil(math.sqrt(len(items)))))
    rows = math.ceil(len(items) / columns)
    sheet = Image.new("RGB", (columns * cell[0], rows * cell[1]), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (label, image) in enumerate(items):
        thumb = image.convert("RGB").copy()
        thumb.thumbnail((cell[0] - 16, cell[1] - 42))
        left = (index % columns) * cell[0]
        top = (index // columns) * cell[1]
        x = left + (cell[0] - thumb.width) // 2
        y = top + 28 + (cell[1] - 36 - thumb.height) // 2
        sheet.paste(thumb, (x, y))
        draw.text((left + 6, top + 6), label[:52], fill="black")
        draw.rectangle((left, top, left + cell[0] - 1, top + cell[1] - 1), outline="#bbbbbb")
    sheet.save(path, format="PNG", optimize=True)


def source_record(source_id: str, audit_path: Path, original: Path, image, **extra) -> dict[str, Any]:
    return {
        "id": source_id,
        "path": audit_path.as_posix(),
        "original_path": str(original.resolve()),
        "width": image.width,
        "height": image.height,
        "normalized_pixel_sha256": image_sha256(image),
        **extra,
    }


def prepare_directory(input_path: Path, workspace: Path) -> tuple[list[dict], list[dict]]:
    _, Image, _, ImageOps = core_modules()
    sources_dir = workspace / "sources"
    sources_dir.mkdir()
    sources: list[dict] = []
    skipped: list[dict] = []
    files = sorted(
        path for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    for index, path in enumerate(files, 1):
        try:
            with Image.open(path) as opened:
                normalized = ImageOps.exif_transpose(opened).convert("RGB")
        except Exception as error:  # Pillow exposes format-specific exceptions.
            skipped.append({"path": str(path.resolve()), "reason": f"unreadable image: {error}"})
            continue
        source_id = f"src-{index:04d}-{slug(path.stem)}"
        destination = sources_dir / f"{source_id}.png"
        normalized.save(destination, format="PNG", optimize=True)
        relative = destination.relative_to(workspace)
        sources.append(source_record(
            source_id,
            relative,
            path,
            normalized,
            input_type="directory-image",
            original_sha256=file_sha256(path),
        ))
    return sources, skipped


def render_pdf_page(pdf_path: Path, page_number: int, dpi: int):
    try:
        import pypdfium2 as pdfium
    except ImportError as error:
        raise SystemExit("pypdfium2 is required for PDF rendering fallback") from error
    document = pdfium.PdfDocument(str(pdf_path))
    try:
        page = document[page_number - 1]
        bitmap = page.render(scale=dpi / 72.0)
        return bitmap.to_pil().convert("RGB")
    finally:
        document.close()


def prepare_pdf(
    input_path: Path,
    workspace: Path,
    pages_spec: str | None,
    min_image_pixels: int,
    render_dpi: int,
    render_fallback: str,
) -> tuple[list[dict], list[dict], list[int]]:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise SystemExit("pypdf is required to extract embedded PDF images") from error
    _, Image, _, ImageOps = core_modules()
    reader = PdfReader(str(input_path))
    selected_pages = parse_pages(pages_spec, len(reader.pages))
    sources_dir = workspace / "sources"
    sources_dir.mkdir()
    sources: list[dict] = []
    skipped: list[dict] = []

    for page_number in selected_pages:
        page = reader.pages[page_number - 1]
        extracted_on_page = 0
        try:
            image_objects = list(page.images)
        except Exception as error:
            image_objects = []
            skipped.append({"page": page_number, "reason": f"could not enumerate embedded images: {error}"})
        for image_index, image_object in enumerate(image_objects, 1):
            try:
                if getattr(image_object, "image", None) is not None:
                    opened = image_object.image
                else:
                    opened = Image.open(io.BytesIO(image_object.data))
                normalized = ImageOps.exif_transpose(opened).convert("RGB")
            except Exception as error:
                skipped.append({
                    "page": page_number,
                    "image": image_index,
                    "reason": f"embedded image unreadable: {error}",
                })
                continue
            if min(normalized.size) < 160 or normalized.width * normalized.height < min_image_pixels:
                skipped.append({
                    "page": page_number,
                    "image": image_index,
                    "size": list(normalized.size),
                    "reason": "embedded image below large-image threshold",
                })
                continue
            source_id = f"p{page_number:04d}-img{image_index:02d}"
            destination = sources_dir / f"{source_id}.png"
            normalized.save(destination, format="PNG", optimize=True)
            sources.append(source_record(
                source_id,
                destination.relative_to(workspace),
                input_path,
                normalized,
                input_type="pdf-embedded-image",
                page=page_number,
                embedded_name=getattr(image_object, "name", None),
            ))
            extracted_on_page += 1

        should_render = False
        if extracted_on_page == 0:
            if render_fallback == "all":
                should_render = True
            elif render_fallback == "auto":
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                should_render = bool(FIGURE_RE.search(text))
        if should_render:
            rendered = render_pdf_page(input_path, page_number, render_dpi)
            source_id = f"p{page_number:04d}-render"
            destination = sources_dir / f"{source_id}.png"
            rendered.save(destination, format="PNG", optimize=True)
            sources.append(source_record(
                source_id,
                destination.relative_to(workspace),
                input_path,
                rendered,
                input_type="pdf-page-render",
                page=page_number,
                render_dpi=render_dpi,
            ))
        elif extracted_on_page == 0:
            skipped.append({"page": page_number, "reason": "no qualifying large embedded image; page not rendered"})
    return sources, skipped, selected_pages


def initial_manifest(workspace: Path, sources: list[dict]) -> dict[str, Any]:
    _, Image, _, _ = core_modules()
    panels: list[dict] = []
    for source in sources:
        with Image.open(workspace / source["path"]) as image:
            boxes = propose_panel_boxes(image)
        for index, box in enumerate(boxes, 1):
            panels.append({
                "id": f"{source['id']}-panel-{index:03d}",
                "source_id": source["id"],
                "label": "",
                "bbox": box,
                "kind": "unknown",
                "compare": True,
                "derivation_group": None,
                "proposal": True,
            })
    return {
        "version": 1,
        "instructions": "Review every proposal at full resolution; replace IDs/labels and set proposal=false before strict scanning.",
        "panels": panels,
    }


def command_prepare(args) -> int:
    input_path = Path(args.input).resolve()
    workspace = Path(args.output).resolve()
    if not input_path.exists():
        raise SystemExit(f"input does not exist: {input_path}")
    require_new_workspace(workspace)
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        sources, skipped, selected_pages = prepare_pdf(
            input_path,
            workspace,
            args.pages,
            args.min_image_pixels,
            args.render_dpi,
            args.render_fallback,
        )
        input_meta = {"type": "pdf", "selected_pages": selected_pages}
    elif input_path.is_dir():
        sources, skipped = prepare_directory(input_path, workspace)
        input_meta = {"type": "directory", "selected_pages": None}
    else:
        raise SystemExit("input must be a PDF or a directory")

    write_json(workspace / "sources.json", {
        "version": 1,
        "input": str(input_path),
        **input_meta,
        "sources": sources,
    })
    write_json(workspace / "skipped.json", skipped)
    write_json(workspace / "panels.json", initial_manifest(workspace, sources))
    _, Image, _, _ = core_modules()
    sheet_items = []
    for source in sources:
        with Image.open(workspace / source["path"]) as opened:
            sheet_items.append((f"{source['id']} {source['width']}x{source['height']}", opened.copy()))
    make_contact_sheet(sheet_items, workspace / "sources-contact-sheet.png")
    print(json.dumps({
        "workspace": str(workspace),
        "sources": len(sources),
        "skipped_entries": len(skipped),
        "next": "Review sources-contact-sheet.png and edit panels.json, then run materialize.",
    }, ensure_ascii=False, indent=2))
    return 0


def intersection_ratio(a: list[int], b: list[int]) -> float:
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    overlap = max(0, x1 - x0) * max(0, y1 - y0)
    area_a = max(1, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(1, (b[2] - b[0]) * (b[3] - b[1]))
    return overlap / min(area_a, area_b)


def quality_metrics(image) -> tuple[dict[str, Any], list[str]]:
    np, _, _, _ = core_modules()
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
    probabilities = hist[hist > 0] / gray.size
    entropy = float(-(probabilities * np.log2(probabilities)).sum())
    std = float(gray.std())
    white_fraction = float((gray >= 250).mean())
    black_fraction = float((gray <= 5).mean())
    flags: list[str] = []
    if min(image.size) < 80:
        flags.append("very-small")
    if std < 2.0 or entropy < 0.5:
        flags.append("near-blank")
    if white_fraction > 0.985:
        flags.append("mostly-white-review")
    if black_fraction > 0.985:
        flags.append("mostly-black-review")
    return {
        "width": image.width,
        "height": image.height,
        "stddev": round(std, 4),
        "entropy": round(entropy, 4),
        "white_fraction": round(white_fraction, 6),
        "black_fraction": round(black_fraction, 6),
    }, flags


def validate_and_materialize(workspace: Path) -> tuple[list[dict], list[dict]]:
    _, Image, _, _ = core_modules()
    source_doc = read_json(workspace / "sources.json")
    manifest = read_json(workspace / "panels.json")
    source_map = {source["id"]: source for source in source_doc["sources"]}
    warnings: list[dict] = []
    panels: list[dict] = []
    seen_ids: set[str] = set()
    panel_dir = workspace / "panels"
    panel_dir.mkdir(exist_ok=True)

    for raw in manifest.get("panels", []):
        panel_id = str(raw.get("id", ""))
        source_id = str(raw.get("source_id", ""))
        if not panel_id or not SAFE_ID_RE.fullmatch(panel_id):
            warnings.append({"panel": panel_id, "type": "invalid-id", "detail": "use ASCII letters, digits, dot, underscore, or hyphen"})
            continue
        if panel_id in seen_ids:
            warnings.append({"panel": panel_id, "type": "duplicate-id"})
            continue
        seen_ids.add(panel_id)
        if source_id not in source_map:
            warnings.append({"panel": panel_id, "type": "unknown-source", "source_id": source_id})
            continue
        try:
            box = [int(value) for value in raw["bbox"]]
        except Exception:
            warnings.append({"panel": panel_id, "type": "invalid-bbox"})
            continue
        source = source_map[source_id]
        if len(box) != 4 or box[0] < 0 or box[1] < 0 or box[2] <= box[0] or box[3] <= box[1] or box[2] > source["width"] or box[3] > source["height"]:
            warnings.append({"panel": panel_id, "type": "out-of-bounds", "bbox": box, "source_size": [source["width"], source["height"]]})
            continue
        with Image.open(workspace / source["path"]) as opened:
            crop = opened.convert("RGB").crop(tuple(box))
        destination = panel_dir / f"{panel_id}.png"
        crop.save(destination, format="PNG", optimize=True)
        metrics, flags = quality_metrics(crop)
        panels.append({
            **raw,
            "id": panel_id,
            "source_id": source_id,
            "bbox": box,
            "path": destination.relative_to(workspace).as_posix(),
            "normalized_pixel_sha256": image_sha256(crop),
            "quality": metrics,
            "quality_flags": flags,
        })

    for first, second in itertools.combinations(panels, 2):
        if first["source_id"] != second["source_id"]:
            continue
        ratio = intersection_ratio(first["bbox"], second["bbox"])
        if ratio >= 0.10:
            warnings.append({
                "type": "overlapping-boxes",
                "panels": [first["id"], second["id"]],
                "intersection_over_smaller": round(ratio, 6),
                "detail": "overlapping same-source crops are skipped during scanning",
            })

    write_json(workspace / "panel-index.json", {"version": 1, "panels": panels})
    write_json(workspace / "manifest-warnings.json", warnings)
    sheet_items = []
    for panel in panels:
        with Image.open(workspace / panel["path"]) as opened:
            label = panel["id"] if not panel.get("label") else f"{panel['id']} | {panel['label']}"
            sheet_items.append((label, opened.copy()))
    make_contact_sheet(sheet_items, workspace / "panels-contact-sheet.png")
    with (workspace / "quality-flags.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["panel_id", "source_id", "flags", "width", "height", "stddev", "entropy", "white_fraction", "black_fraction"])
        writer.writeheader()
        for panel in panels:
            writer.writerow({
                "panel_id": panel["id"],
                "source_id": panel["source_id"],
                "flags": ";".join(panel["quality_flags"]),
                **panel["quality"],
            })
    return panels, warnings


def command_materialize(args) -> int:
    workspace = Path(args.workspace).resolve()
    panels, warnings = validate_and_materialize(workspace)
    print(json.dumps({
        "workspace": str(workspace),
        "panels": len(panels),
        "warnings": len(warnings),
        "next": "Inspect panels-contact-sheet.png and manifest-warnings.json before scan.",
    }, ensure_ascii=False, indent=2))
    return 0


def resize_gray(image, size: tuple[int, int]):
    np, Image, _, ImageOps = core_modules()
    gray = ImageOps.autocontrast(image.convert("L"))
    return np.asarray(gray.resize(size, Image.Resampling.LANCZOS), dtype=np.float32)


def hash_bits(image, kind: str, hash_size: int = 16):
    np, Image, _, ImageOps = core_modules()
    gray = ImageOps.autocontrast(image.convert("L"))
    if kind == "ahash":
        values = np.asarray(gray.resize((hash_size, hash_size), Image.Resampling.LANCZOS), dtype=float)
        return values >= values.mean()
    if kind == "dhash":
        values = np.asarray(gray.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS), dtype=float)
        return values[:, 1:] >= values[:, :-1]
    if kind == "phash":
        side = hash_size * 2
        values = np.asarray(gray.resize((side, side), Image.Resampling.LANCZOS), dtype=float)
        coordinates = np.arange(side)
        frequencies = np.arange(hash_size)[:, None]
        transform = np.cos((math.pi / side) * (coordinates + 0.5) * frequencies)
        transform[0, :] *= 1 / math.sqrt(2)
        low = transform @ values @ transform.T
        median = np.median(low[1:, 1:])
        return low >= median
    raise ValueError(f"unknown hash: {kind}")


def hamming(first, second) -> int:
    np, _, _, _ = core_modules()
    return int(np.count_nonzero(first != second))


def normalized_ncc(first, second) -> float:
    np, Image, _, _ = core_modules()
    a = resize_gray(first, (128, 128))
    variants = []
    candidate = second.convert("L")
    for angle in (0, 90, 180, 270):
        rotated = candidate.rotate(angle, expand=True)
        variants.append(rotated)
        variants.append(rotated.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
    best = -1.0
    a = (a - a.mean()) / (a.std() + 1e-6)
    for variant in variants:
        b = resize_gray(variant, (128, 128))
        b = (b - b.mean()) / (b.std() + 1e-6)
        best = max(best, float((a * b).mean()))
    return best


def load_cv2(mode: str):
    if mode == "off":
        return None
    try:
        import cv2
    except ImportError:
        if mode == "required":
            raise SystemExit(
                "OpenCV with SIFT support is required for this scan. Load "
                "local-env-setup and install opencv (or opencv-python-headless)."
            )
        return None
    if not hasattr(cv2, "SIFT_create"):
        if mode == "required":
            raise SystemExit("the installed OpenCV build does not provide SIFT_create")
        return None
    return cv2


def feature_image(image, cv2):
    np, Image, _, _ = core_modules()
    rgb = np.asarray(image.convert("RGB"))
    largest = max(image.size)
    scale = 600 / largest if largest < 600 else (1600 / largest if largest > 1600 else 1.0)
    if scale != 1.0:
        rgb = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    sift = cv2.SIFT_create(nfeatures=1800, contrastThreshold=0.02)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return {"rgb": rgb, "gray": gray, "keypoints": keypoints, "descriptors": descriptors}


def hull_coverage(points, shape, cv2) -> float:
    np, _, _, _ = core_modules()
    if len(points) < 3:
        return 0.0
    hull = cv2.convexHull(np.asarray(points, dtype=np.float32))
    return float(cv2.contourArea(hull) / max(1, shape[0] * shape[1]))


def feature_match(first_feature, second_feature, cv2, details: bool = False) -> dict[str, Any]:
    np, _, _, _ = core_modules()
    kp1, des1 = first_feature["keypoints"], first_feature["descriptors"]
    kp2, des2 = second_feature["keypoints"], second_feature["descriptors"]
    empty = {
        "keypoints_a": len(kp1), "keypoints_b": len(kp2), "good_matches": 0,
        "inliers": 0, "inlier_ratio": 0.0, "coverage_a": 0.0,
        "coverage_b": 0.0, "grid_coverage_a": 0.0, "grid_coverage_b": 0.0,
        "registered_ncc": None, "registered_overlap": 0.0,
    }
    if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
        return empty
    matcher = cv2.BFMatcher()
    raw = matcher.knnMatch(des1, des2, k=2)
    good = [pair[0] for pair in raw if len(pair) == 2 and pair[0].distance < 0.75 * pair[1].distance]
    if len(good) < 4:
        empty["good_matches"] = len(good)
        return empty
    src = np.float32([kp1[item.queryIdx].pt for item in good])
    dst = np.float32([kp2[item.trainIdx].pt for item in good])
    homography, mask = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
    if homography is None or mask is None:
        empty["good_matches"] = len(good)
        return empty
    inlier_mask = mask.ravel().astype(bool)
    src_inliers, dst_inliers = src[inlier_mask], dst[inlier_mask]
    inliers = int(inlier_mask.sum())

    def grid_coverage(points, shape):
        if len(points) == 0:
            return 0.0
        h, w = shape
        cells = set()
        for x, y in points:
            cells.add((min(3, int(4 * x / max(w, 1))), min(3, int(4 * y / max(h, 1)))))
        return len(cells) / 16.0

    gray1, gray2 = first_feature["gray"], second_feature["gray"]
    valid_source = np.full(gray1.shape, 255, dtype=np.uint8)
    warped = cv2.warpPerspective(gray1, homography, (gray2.shape[1], gray2.shape[0]))
    valid = cv2.warpPerspective(valid_source, homography, (gray2.shape[1], gray2.shape[0])) > 0
    overlap = float(valid.mean())
    registered_ncc = None
    if valid.sum() >= 256:
        a = warped[valid].astype(np.float32)
        b = gray2[valid].astype(np.float32)
        if a.std() > 1e-6 and b.std() > 1e-6:
            a = (a - a.mean()) / (a.std() + 1e-6)
            b = (b - b.mean()) / (b.std() + 1e-6)
            registered_ncc = float((a * b).mean())

    result = {
        "keypoints_a": len(kp1),
        "keypoints_b": len(kp2),
        "good_matches": len(good),
        "inliers": inliers,
        "inlier_ratio": round(inliers / max(1, len(good)), 6),
        "coverage_a": round(hull_coverage(src_inliers, gray1.shape, cv2), 6),
        "coverage_b": round(hull_coverage(dst_inliers, gray2.shape, cv2), 6),
        "grid_coverage_a": round(grid_coverage(src_inliers, gray1.shape), 6),
        "grid_coverage_b": round(grid_coverage(dst_inliers, gray2.shape), 6),
        "registered_ncc": None if registered_ncc is None else round(registered_ncc, 6),
        "registered_overlap": round(overlap, 6),
    }
    if details:
        result["_details"] = {
            "good": good,
            "homography": homography,
            "inlier_mask": inlier_mask,
            "first": first_feature,
            "second": second_feature,
        }
    return result


def load_panels(workspace: Path):
    _, Image, _, _ = core_modules()
    document = read_json(workspace / "panel-index.json")
    panels = [panel for panel in document["panels"] if panel.get("compare", True)]
    images = {}
    for panel in panels:
        with Image.open(workspace / panel["path"]) as opened:
            images[panel["id"]] = opened.convert("RGB").copy()
    return panels, images


def candidate_score(exact: bool, distances: dict, ncc: float, feature: dict | None) -> float:
    score = 100.0 if exact else 0.0
    score = max(score, 35.0 - min(distances.values()) * 0.7)
    score = max(score, max(0.0, ncc) * 45.0)
    if feature:
        geometric = min(55.0, feature["inliers"] * 1.8)
        geometric += feature["inlier_ratio"] * 20.0
        geometric += max(feature["coverage_a"], feature["coverage_b"]) * 20.0
        score = max(score, geometric)
    return round(score, 4)


def command_scan(args) -> int:
    workspace = Path(args.workspace).resolve()
    panels, warnings = validate_and_materialize(workspace)
    fatal_warning_types = {"invalid-id", "duplicate-id", "unknown-source", "invalid-bbox", "out-of-bounds"}
    if any(item.get("type") in fatal_warning_types for item in warnings):
        raise SystemExit("manifest has fatal warnings; inspect manifest-warnings.json")
    panels, images = load_panels(workspace)
    cv2 = load_cv2(args.features)
    hashes = {}
    feature_cache = {}
    for panel in panels:
        image = images[panel["id"]]
        hashes[panel["id"]] = {kind: hash_bits(image, kind) for kind in ("ahash", "dhash", "phash")}
        if cv2 is not None:
            feature_cache[panel["id"]] = feature_image(image, cv2)

    candidates: list[dict] = []
    compared = 0
    skipped_overlap = 0
    for first, second in itertools.combinations(panels, 2):
        if first["source_id"] == second["source_id"] and intersection_ratio(first["bbox"], second["bbox"]) >= 0.10:
            skipped_overlap += 1
            continue
        compared += 1
        first_id, second_id = first["id"], second["id"]
        distances = {kind: hamming(hashes[first_id][kind], hashes[second_id][kind]) for kind in hashes[first_id]}
        ncc = normalized_ncc(images[first_id], images[second_id])
        feature = None
        if cv2 is not None:
            feature = feature_match(feature_cache[first_id], feature_cache[second_id], cv2)
        exact = first["normalized_pixel_sha256"] == second["normalized_pixel_sha256"]
        signals = []
        if exact:
            signals.append("exact-pixel-copy")
        if distances["phash"] <= 22 or distances["dhash"] <= 18:
            signals.append("perceptual-hash")
        if ncc >= 0.90:
            signals.append("global-ncc")
        if feature and feature["inliers"] >= args.min_inliers:
            signals.append("sift-ransac")
        if not signals:
            continue
        same_group = bool(first.get("derivation_group")) and first.get("derivation_group") == second.get("derivation_group")
        candidates.append({
            "pair_id": f"{first_id}__{second_id}",
            "panel_a": first_id,
            "panel_b": second_id,
            "source_a": first["source_id"],
            "source_b": second["source_id"],
            "bbox_a": first["bbox"],
            "bbox_b": second["bbox"],
            "kind_a": first.get("kind", "unknown"),
            "kind_b": second.get("kind", "unknown"),
            "same_derivation_group": same_group,
            "signals": signals,
            "exact_pixel_copy": exact,
            "hash_distance": distances,
            "global_ncc": round(ncc, 6),
            "feature": feature,
            "score": candidate_score(exact, distances, ncc, feature),
            "verdict": "unreviewed",
            "review_notes": "",
        })

    candidates.sort(key=lambda item: (-item["score"], item["pair_id"]))
    write_json(workspace / "candidates.json", {"version": 1, "candidates": candidates})
    fields = [
        "pair_id", "panel_a", "panel_b", "source_a", "source_b", "kind_a", "kind_b",
        "same_derivation_group", "signals", "score", "exact_pixel_copy", "ahash_distance",
        "dhash_distance", "phash_distance", "global_ncc", "good_matches", "inliers",
        "inlier_ratio", "coverage_a", "coverage_b", "grid_coverage_a", "grid_coverage_b",
        "registered_ncc", "registered_overlap", "verdict", "review_notes",
    ]
    with (workspace / "candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in candidates:
            feature = item["feature"] or {}
            writer.writerow({
                **{key: item.get(key) for key in fields},
                "signals": ";".join(item["signals"]),
                "ahash_distance": item["hash_distance"]["ahash"],
                "dhash_distance": item["hash_distance"]["dhash"],
                "phash_distance": item["hash_distance"]["phash"],
                **{key: feature.get(key) for key in ["good_matches", "inliers", "inlier_ratio", "coverage_a", "coverage_b", "grid_coverage_a", "grid_coverage_b", "registered_ncc", "registered_overlap"]},
            })
    total_pairs = len(panels) * (len(panels) - 1) // 2
    summary = {
        "panels_in_scan": len(panels),
        "possible_pairs": total_pairs,
        "compared_pairs": compared,
        "skipped_same_source_overlaps": skipped_overlap,
        "candidate_pairs": len(candidates),
        "feature_matching": "sift-ransac" if cv2 is not None else "unavailable",
        "min_inliers_for_candidate": args.min_inliers,
        "warning": "Candidate scores are triage signals, not verdicts.",
    }
    write_json(workspace / "scan-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def labeled_side_by_side(first, second, label_a: str, label_b: str):
    _, Image, ImageDraw, _ = core_modules()
    max_height = 700
    images = []
    for image in (first, second):
        copy = image.convert("RGB").copy()
        if copy.height > max_height:
            scale = max_height / copy.height
            copy = copy.resize((max(1, int(copy.width * scale)), max_height), Image.Resampling.LANCZOS)
        images.append(copy)
    width = images[0].width + images[1].width + 30
    height = max(images[0].height, images[1].height) + 48
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    canvas.paste(images[0], (5, 38))
    canvas.paste(images[1], (images[0].width + 25, 38))
    draw.text((5, 8), label_a[:70], fill="red")
    draw.text((images[0].width + 25, 8), label_b[:70], fill="red")
    return canvas


def evidence_for_pair(workspace: Path, panel_map: dict, images: dict, candidate: dict | None, panel_a: str, panel_b: str) -> Path:
    np, Image, _, _ = core_modules()
    if panel_a not in panel_map or panel_b not in panel_map:
        raise SystemExit(f"unknown panel pair: {panel_a}, {panel_b}")
    pair_dir = workspace / "evidence" / slug(f"{panel_a}__{panel_b}")
    pair_dir.mkdir(parents=True, exist_ok=True)
    first, second = images[panel_a], images[panel_b]
    labeled_side_by_side(first, second, panel_a, panel_b).save(pair_dir / "side-by-side.png")
    metrics = {"panel_a": panel_a, "panel_b": panel_b, "candidate": candidate}
    cv2 = load_cv2("auto")
    if cv2 is not None:
        feature_a, feature_b = feature_image(first, cv2), feature_image(second, cv2)
        result = feature_match(feature_a, feature_b, cv2, details=True)
        details = result.pop("_details", None)
        metrics["recomputed_feature"] = result
        if details and result["inliers"] >= 4:
            inlier_mask = details["inlier_mask"].astype(int).tolist()
            matches = cv2.drawMatches(
                details["first"]["rgb"], details["first"]["keypoints"],
                details["second"]["rgb"], details["second"]["keypoints"],
                details["good"], None, matchesMask=inlier_mask,
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )
            Image.fromarray(matches).save(pair_dir / "inlier-matches.png")
            homography = details["homography"]
            gray_a = details["first"]["gray"]
            gray_b = details["second"]["gray"]
            warped = cv2.warpPerspective(gray_a, homography, (gray_b.shape[1], gray_b.shape[0]))
            valid_source = np.full(gray_a.shape, 255, dtype=np.uint8)
            valid = cv2.warpPerspective(valid_source, homography, (gray_b.shape[1], gray_b.shape[0])) > 0
            overlay = np.zeros((gray_b.shape[0], gray_b.shape[1], 3), dtype=np.uint8)
            overlay[..., 0] = warped
            overlay[..., 1] = gray_b
            overlay[~valid, 2] = 80
            Image.fromarray(overlay).save(pair_dir / "registered-red-green.png")
            difference = np.zeros_like(gray_b)
            difference[valid] = np.abs(warped[valid].astype(np.int16) - gray_b[valid].astype(np.int16)).clip(0, 255).astype(np.uint8)
            Image.fromarray(difference).save(pair_dir / "registered-absolute-difference.png")
    write_json(pair_dir / "metrics.json", metrics)
    return pair_dir


def command_evidence(args) -> int:
    workspace = Path(args.workspace).resolve()
    panels, images = load_panels(workspace)
    panel_map = {panel["id"]: panel for panel in panels}
    candidate_doc = read_json(workspace / "candidates.json") if (workspace / "candidates.json").exists() else {"candidates": []}
    candidate_map = {(item["panel_a"], item["panel_b"]): item for item in candidate_doc["candidates"]}
    selected: list[tuple[str, str, dict | None]] = []
    for value in args.pair or []:
        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 2:
            raise SystemExit("--pair must be PANEL_A,PANEL_B")
        candidate = candidate_map.get((parts[0], parts[1])) or candidate_map.get((parts[1], parts[0]))
        selected.append((parts[0], parts[1], candidate))
    if args.top:
        for item in candidate_doc["candidates"][: args.top]:
            selected.append((item["panel_a"], item["panel_b"], item))
    if not selected:
        raise SystemExit("provide --pair PANEL_A,PANEL_B or --top N")
    outputs = []
    seen = set()
    for first, second, candidate in selected:
        key = tuple(sorted((first, second)))
        if key in seen:
            continue
        seen.add(key)
        outputs.append(str(evidence_for_pair(workspace, panel_map, images, candidate, first, second)))
    print(json.dumps({"evidence_directories": outputs}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="extract PDF figures or inventory a directory")
    prepare.add_argument("--input", required=True, help="PDF path or image directory")
    prepare.add_argument("--output", required=True, help="new audit workspace")
    prepare.add_argument("--pages", help="one-based pages, e.g. 1-40,49-54; default all")
    prepare.add_argument("--min-image-pixels", type=int, default=120_000, help="embedded PDF image area threshold")
    prepare.add_argument("--render-dpi", type=int, default=240)
    prepare.add_argument("--render-fallback", choices=("auto", "all", "none"), default="auto")
    prepare.set_defaults(func=command_prepare)

    materialize = subparsers.add_parser("materialize", help="validate panels.json and write panel crops")
    materialize.add_argument("--workspace", required=True)
    materialize.set_defaults(func=command_materialize)

    scan = subparsers.add_parser("scan", help="run all-pairs candidate screening")
    scan.add_argument("--workspace", required=True)
    scan.add_argument("--features", choices=("auto", "required", "off"), default="required")
    scan.add_argument("--min-inliers", type=int, default=8)
    scan.set_defaults(func=command_scan)

    evidence = subparsers.add_parser("evidence", help="render pair evidence")
    evidence.add_argument("--workspace", required=True)
    evidence.add_argument("--pair", action="append", help="PANEL_A,PANEL_B; may be repeated")
    evidence.add_argument("--top", type=int, default=0, help="also render the top N candidates")
    evidence.set_defaults(func=command_evidence)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "features", None) == "off":
        args.features = "off"
    try:
        return args.func(args)
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
        return 2


if __name__ == "__main__":
    sys.exit(main())
