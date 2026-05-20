#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate black-and-white SVG patent reference drawings from structured JSON.

The script uses only the Python standard library. It is intentionally template
based: drawings must be faithful to the patent text and should not introduce
new technical modules or steps.
"""

from __future__ import annotations


import argparse
import json
import math
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


FIGURE_RE = re.compile(r"图\s*(\d+)")
STEP_RE = re.compile(r"(S\d{3})[，,:：、\s]*(.*?)(?=；|;|。|$)")
CONTENT_RATIO_TARGET = 0.80
CONTENT_RATIO_FLOOR = 0.78


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object.")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def as_paragraphs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(as_paragraphs(item))
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(as_paragraphs(item))
        return result
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?:\r?\n){1,}", text) if part.strip()]


def xml(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def default_prefix(input_path: Path) -> str:
    stem = input_path.stem
    for suffix in ("_patent_content", "_专利申请书"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def compact_label(text: str, limit: int = 28) -> str:
    label = re.sub(r"\s+", "", text)
    label = re.sub(r"[。；;，,：:]+$", "", label)
    if len(label) <= limit:
        return label
    return label[: limit - 1] + "…"


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def wrap_label(text: str, max_chars: int = 12) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines[:3]


def title_from_spec(spec: str, figure_no: int) -> str:
    first = as_paragraphs(spec)[0] if as_paragraphs(spec) else spec
    first = re.sub(r"^图\s*\d+\s*[：:]\s*", "", first).strip()
    return compact_label(first or f"图{figure_no}")


def figure_no_from_spec(spec: str, fallback: int) -> int:
    match = FIGURE_RE.search(spec)
    return int(match.group(1)) if match else fallback


def drawing_type_from_spec(spec: str) -> str:
    if "流程" in spec or "步骤" in spec:
        return "method_flow"
    if "数据流" in spec or "候选动作" in spec or "策略参数" in spec:
        return "data_flow"
    if "系统" in spec or "模块" in spec or "结构" in spec:
        return "system_block"
    return "method_flow"


def canvas_length(content_length: int) -> int:
    return max(content_length, math.ceil(content_length / CONTENT_RATIO_TARGET))


def centered_offset(canvas_length_value: int, content_length: int) -> int:
    return max(0, (canvas_length_value - content_length) // 2)


def validate_canvas(width: int, height: int, bbox: tuple[int, int, int, int]) -> dict[str, Any]:
    left, top, right, bottom = bbox
    content_width = max(0, right - left)
    content_height = max(0, bottom - top)
    width_ratio = content_width / width if width else 0
    height_ratio = content_height / height if height else 0
    return {
        "canvas_width": width,
        "canvas_height": height,
        "content_width_ratio": round(width_ratio, 3),
        "content_height_ratio": round(height_ratio, 3),
        "max_margin_ratio": round(
            max(
                left / width if width else 1,
                (width - right) / width if width else 1,
                top / height if height else 1,
                (height - bottom) / height if height else 1,
            ),
            3,
        ),
        "internal_title": False,
        "passes": width_ratio >= CONTENT_RATIO_FLOOR and height_ratio >= CONTENT_RATIO_FLOOR,
    }


def normalize_source_figures(data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    raw_items = data.get("source_figures")
    if not isinstance(raw_items, list):
        return {}
    normalized: dict[int, dict[str, Any]] = {}
    for index, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            continue
        figure_no = int(item.get("figure_no") or index)
        normalized[figure_no] = {
            "figure_no": figure_no,
            "source_label": str(item.get("source_label") or f"Figure {figure_no}").strip(),
            "caption": str(item.get("caption") or "").strip(),
            "page": item.get("page"),
            "notes": str(item.get("notes") or "").strip(),
        }
    return normalized


def source_generation_text(source_figure: dict[str, Any] | None) -> str:
    if not isinstance(source_figure, dict):
        return ""
    parts: list[str] = []
    if source_figure.get("notes"):
        parts.extend(as_paragraphs(source_figure["notes"]))
    if source_figure.get("caption"):
        parts.extend(as_paragraphs(source_figure["caption"]))
    return "\n".join(parts).strip()


def merge_source_figure(asset: dict[str, Any], source_map: dict[int, dict[str, Any]]) -> dict[str, Any]:
    merged = dict(asset)
    figure_no = int(merged.get("figure_no") or 0)
    source_figure = source_map.get(figure_no)
    if source_figure:
        merged["source_figure"] = source_figure
    return merged


def generation_spec(asset: dict[str, Any]) -> str:
    parts: list[str] = []
    source_text = source_generation_text(asset.get("source_figure"))
    if source_text:
        parts.extend(as_paragraphs(source_text))
    spec = str(asset.get("spec") or "").strip()
    if spec:
        parts.extend(as_paragraphs(spec))
    deduped = list(dict.fromkeys(parts))
    return "\n".join(deduped).strip()


def infer_assets(data: dict[str, Any], output_dir: Path, prefix: str) -> list[dict[str, Any]]:
    source_map = normalize_source_figures(data)
    existing = data.get("drawing_assets")
    if isinstance(existing, list) and existing:
        return [
            merge_source_figure(asset, source_map)
            for asset in existing
            if isinstance(asset, dict)
        ]

    raw_drawings = data.get("drawings")
    if isinstance(raw_drawings, list):
        drawings = [str(item).strip() for item in raw_drawings if str(item).strip()]
    else:
        drawings = as_paragraphs(raw_drawings)
    assets: list[dict[str, Any]] = []
    for index, spec in enumerate(drawings, start=1):
        figure_no = figure_no_from_spec(spec, index)
        title = title_from_spec(spec, figure_no)
        svg_name = f"{prefix}_图{figure_no}.svg"
        assets.append(
            {
                "figure_no": figure_no,
                "title": title,
                "type": drawing_type_from_spec(spec),
                "spec": spec,
                "svg_path": str(output_dir / svg_name),
                "caption": f"图{figure_no} {title}",
                "abstract_candidate": figure_no == 1,
            }
        )
    if not assets and source_map:
        for figure_no, source_figure in sorted(source_map.items()):
            source_text = source_generation_text(source_figure)
            if not source_text:
                continue
            title = title_from_spec(source_text, figure_no)
            assets.append(
                {
                    "figure_no": figure_no,
                    "title": title,
                    "type": drawing_type_from_spec(source_text),
                    "spec": source_text,
                    "svg_path": str(output_dir / f"{prefix}_图{figure_no}.svg"),
                    "caption": f"图{figure_no} {title}",
                    "abstract_candidate": figure_no == 1,
                }
            )
    return [merge_source_figure(asset, source_map) for asset in assets]


def svg_header(width: int, height: int) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000000"/></marker></defs>',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
    ]


def svg_footer() -> str:
    return "</svg>\n"


def text_block(
    x: int,
    y: int,
    label: str,
    anchor: str = "middle",
    size: int = 24,
    max_chars: int = 12,
) -> str:
    lines = wrap_label(label, max_chars=max_chars)
    line_height = int(size * 1.25)
    start_y = y - (len(lines) - 1) * line_height // 2
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{xml(line)}</tspan>')
    return (
        f'<text x="{x}" y="{start_y}" text-anchor="{anchor}" '
        f'font-family="SimSun, Songti SC, serif" font-size="{size}" fill="#000000">'
        f'{"".join(tspans)}</text>'
    )


def rect_node(x: int, y: int, width: int, height: int, label: str, max_chars: int = 12) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="0" ry="0" '
        'fill="#ffffff" stroke="#000000" stroke-width="2"/>'
        f"{text_block(x + width // 2, y + height // 2 + 8, label, max_chars=max_chars)}"
    )


def arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="#000000" stroke-width="2" marker-end="url(#arrow)"/>'
    )


def polyline_arrow(points: list[tuple[int, int]]) -> str:
    point_text = " ".join(f"{x},{y}" for x, y in points)
    return (
        f'<polyline points="{point_text}" fill="none" stroke="#000000" '
        'stroke-width="2" marker-end="url(#arrow)"/>'
    )


def box_arrow_points(
    first: tuple[int, int],
    second: tuple[int, int],
    node_w: int,
    node_h: int,
) -> tuple[int, int, int, int]:
    x1, y1 = first
    x2, y2 = second
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        direction = 1 if dx >= 0 else -1
        return (
            x1 + direction * (node_w // 2 + 6),
            y1,
            x2 - direction * (node_w // 2 + 8),
            y2,
        )
    direction = 1 if dy >= 0 else -1
    return (
        x1,
        y1 + direction * (node_h // 2 + 6),
        x2,
        y2 - direction * (node_h // 2 + 8),
    )


def orthogonal_points(
    first: tuple[int, int],
    second: tuple[int, int],
    node_h: int,
) -> list[tuple[int, int]]:
    x1, y1 = first
    x2, y2 = second
    direction = 1 if y2 >= y1 else -1
    start = (x1, y1 + direction * (node_h // 2 + 6))
    end = (x2, y2 - direction * (node_h // 2 + 8))
    mid_y = (start[1] + end[1]) // 2
    return [start, (x1, mid_y), (x2, mid_y), end]


def extract_steps(spec: str) -> list[str]:
    steps = []
    for step_no, label in STEP_RE.findall(spec):
        label = compact_label(label, 20)
        steps.append(f"{step_no} {label}")
    return steps


def extract_modules(spec: str) -> list[str]:
    match = re.search(r"包含(.+?)(?:。|\.|$)", spec)
    source = match.group(1) if match else spec
    source = source.replace("和", "、")
    parts = [compact_label(part, 12) for part in re.split(r"[、,，；;]", source)]
    modules = [part for part in parts if part and "箭头" not in part and "图" not in part]
    return modules[:8]


def require_items(items: list[str], asset: dict[str, Any], kind: str, minimum: int = 2) -> None:
    if len(items) < minimum:
        figure_no = asset.get("figure_no", "?")
        raise ValueError(
            f"Cannot generate figure {figure_no}: {kind} are not explicit enough in the drawing specification."
        )


def method_flow_layout(steps: list[str]) -> dict[str, Any]:
    node_w = 560
    node_h = 82
    gap = 48
    content_w = node_w
    content_h = len(steps) * node_h + max(0, len(steps) - 1) * gap
    width = canvas_length(content_w)
    height = canvas_length(content_h)
    x = centered_offset(width, content_w)
    top = centered_offset(height, content_h)
    positions = [(x, top + index * (node_h + gap)) for index in range(len(steps))]
    return {
        "width": width,
        "height": height,
        "node_w": node_w,
        "node_h": node_h,
        "gap": gap,
        "positions": positions,
        "bbox": (x, top, x + content_w, top + content_h),
    }


def vertical_block_layout(items: list[str]) -> dict[str, Any]:
    node_w = 430
    node_h = 72
    gap = 52
    content_w = node_w
    content_h = len(items) * node_h + max(0, len(items) - 1) * gap
    width = canvas_length(content_w)
    height = canvas_length(content_h)
    x = centered_offset(width, content_w)
    top = centered_offset(height, content_h)
    positions = [(x, top + index * (node_h + gap)) for index in range(len(items))]
    return {
        "width": width,
        "height": height,
        "node_w": node_w,
        "node_h": node_h,
        "positions": positions,
        "bbox": (x, top, x + content_w, top + content_h),
    }


def data_flow_layout(nodes: list[str]) -> dict[str, Any]:
    node_w = 190
    node_h = 78
    gap_x = 54
    gap_y = 64
    rows = 1 if len(nodes) <= 3 else 2
    cols = math.ceil(len(nodes) / rows)
    content_w = cols * node_w + max(0, cols - 1) * gap_x
    content_h = rows * node_h + max(0, rows - 1) * gap_y
    width = canvas_length(content_w)
    height = canvas_length(content_h)
    left = centered_offset(width, content_w)
    top = centered_offset(height, content_h)
    positions = []
    for index in range(len(nodes)):
        row = index // cols
        col = index % cols
        if row % 2 == 1:
            col = cols - 1 - col
        x = left + col * (node_w + gap_x)
        y = top + row * (node_h + gap_y)
        positions.append((x, y))
    return {
        "width": width,
        "height": height,
        "node_w": node_w,
        "node_h": node_h,
        "positions": positions,
        "bbox": (left, top, left + content_w, top + content_h),
    }


def node_index(nodes: list[str], keyword: str) -> int | None:
    for index, label in enumerate(nodes):
        if keyword in label:
            return index
    return None


def data_flow_edges(nodes: list[str]) -> list[tuple[int, int]]:
    return [(index, index + 1) for index in range(len(nodes) - 1)]


def data_flow_extra_edges(spec: str, nodes: list[str]) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    base_edges = set(data_flow_edges(nodes))

    def add_edge(source: int | None, target: int | None) -> None:
        if source is None or target is None or source == target:
            return
        edge = (source, target)
        if edge not in base_edges and edge not in edges:
            edges.append(edge)

    if "共同输入" in spec and "冻结价值环境模型" in spec:
        add_edge(node_index(nodes, "离线状态"), node_index(nodes, "冻结价值环境模型"))
        add_edge(node_index(nodes, "候选动作"), node_index(nodes, "冻结价值环境模型"))
    if "反向作用于策略模型" in spec or "反向作用于所述策略模型" in spec:
        add_edge(node_index(nodes, "策略参数更新"), node_index(nodes, "策略模型"))
    return edges


def method_flow_svg(asset: dict[str, Any]) -> str:
    steps = extract_steps(generation_spec(asset))
    require_items(steps, asset, "method steps")
    layout = method_flow_layout(steps)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    gap = layout["gap"]
    asset["validation"] = validate_canvas(width, height, layout["bbox"])
    parts = svg_header(width, height)
    for index, (label, (x, y)) in enumerate(zip(steps, layout["positions"])):
        parts.append(rect_node(x, y, node_w, node_h, label))
        if index < len(steps) - 1:
            parts.append(arrow(width // 2, y + node_h + 6, width // 2, y + node_h + gap - 8))
    parts.append(svg_footer())
    return "\n".join(parts)


def system_block_svg(asset: dict[str, Any]) -> str:
    modules = extract_modules(generation_spec(asset))
    require_items(modules, asset, "system modules", minimum=2)
    layout = vertical_block_layout(modules)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    asset["validation"] = validate_canvas(width, height, layout["bbox"])
    parts = svg_header(width, height)
    centers = []
    for (x, y), label in zip(layout["positions"], modules):
        parts.append(rect_node(x, y, node_w, node_h, label, max_chars=10))
        centers.append((x + node_w // 2, y + node_h // 2))
    for index in range(len(centers) - 1):
        x1, y1 = centers[index]
        x2, y2 = centers[index + 1]
        parts.append(arrow(x1, y1 + node_h // 2 + 6, x2, y2 - node_h // 2 - 8))
    parts.append(svg_footer())
    return "\n".join(parts)


def data_flow_svg(asset: dict[str, Any]) -> str:
    spec = generation_spec(asset)
    nodes = extract_modules(spec)
    require_items(nodes, asset, "data-flow nodes", minimum=2)
    layout = data_flow_layout(nodes)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    asset["validation"] = validate_canvas(width, height, layout["bbox"])
    parts = svg_header(width, height)
    centers: list[tuple[int, int]] = []
    for label, (x, y) in zip(nodes, layout["positions"]):
        parts.append(rect_node(x, y, node_w, node_h, label, max_chars=8))
        centers.append((x + node_w // 2, y + node_h // 2))
    for source, target in data_flow_edges(nodes):
        parts.append(arrow(*box_arrow_points(centers[source], centers[target], node_w, node_h)))
    for source, target in data_flow_extra_edges(spec, nodes):
        parts.append(polyline_arrow(orthogonal_points(centers[source], centers[target], node_h)))
    parts.append(svg_footer())
    return "\n".join(parts)


def render_svg(asset: dict[str, Any]) -> str:
    drawing_type = str(asset.get("type") or "")
    if drawing_type == "system_block":
        return system_block_svg(asset)
    if drawing_type == "data_flow":
        return data_flow_svg(asset)
    return method_flow_svg(asset)


def load_font(size: int):
    try:
        from PIL import ImageFont
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError("Pillow is required for PNG fallback generation.") from exc

    candidates = [
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_center_text(draw: Any, x: int, y: int, label: str, font: Any, max_chars: int = 12) -> None:
    lines = wrap_label(label, max_chars=max_chars)
    metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        metrics.append((line, bbox[2] - bbox[0], bbox[3] - bbox[1]))
    line_height = max((height for _, _, height in metrics), default=24) + 8
    top = y - (line_height * len(metrics)) // 2
    for index, (line, width, _) in enumerate(metrics):
        draw.text((x - width // 2, top + index * line_height), line, fill="black", font=font)


def draw_rect_node(
    draw: Any,
    x: int,
    y: int,
    width: int,
    height: int,
    label: str,
    font: Any,
    max_chars: int = 12,
) -> None:
    draw.rectangle((x, y, x + width, y + height), outline="black", width=2, fill="white")
    draw_center_text(draw, x + width // 2, y + height // 2, label, font, max_chars=max_chars)


def draw_arrow(draw: Any, x1: int, y1: int, x2: int, y2: int) -> None:
    draw.line((x1, y1, x2, y2), fill="black", width=2)
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 16
    spread = 0.45
    p1 = (
        x2 - length * math.cos(angle - spread),
        y2 - length * math.sin(angle - spread),
    )
    p2 = (
        x2 - length * math.cos(angle + spread),
        y2 - length * math.sin(angle + spread),
    )
    draw.polygon([(x2, y2), p1, p2], fill="black")


def draw_polyline_arrow(draw: Any, points: list[tuple[int, int]]) -> None:
    for first, second in zip(points, points[1:]):
        draw.line((*first, *second), fill="black", width=2)
    if len(points) >= 2:
        x1, y1 = points[-2]
        x2, y2 = points[-1]
        angle = math.atan2(y2 - y1, x2 - x1)
        length = 16
        spread = 0.45
        p1 = (
            x2 - length * math.cos(angle - spread),
            y2 - length * math.sin(angle - spread),
        )
        p2 = (
            x2 - length * math.cos(angle + spread),
            y2 - length * math.sin(angle + spread),
        )
        draw.polygon([(x2, y2), p1, p2], fill="black")


def png_canvas(width: int, height: int):
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError("Pillow is required for PNG fallback generation.") from exc

    image = Image.new("RGB", (width, height), "white")
    return image, ImageDraw.Draw(image)


def method_flow_png(asset: dict[str, Any], output: Path) -> None:
    steps = extract_steps(generation_spec(asset))
    require_items(steps, asset, "method steps")
    layout = method_flow_layout(steps)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    gap = layout["gap"]
    image, draw = png_canvas(width, height)
    body_font = load_font(24)
    for index, (label, (x, y)) in enumerate(zip(steps, layout["positions"])):
        draw_rect_node(draw, x, y, node_w, node_h, label, body_font)
        if index < len(steps) - 1:
            draw_arrow(draw, width // 2, y + node_h + 6, width // 2, y + node_h + gap - 8)
    image.save(output)


def system_block_png(asset: dict[str, Any], output: Path) -> None:
    modules = extract_modules(generation_spec(asset))
    require_items(modules, asset, "system modules", minimum=2)
    layout = vertical_block_layout(modules)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    image, draw = png_canvas(width, height)
    body_font = load_font(23)
    centers = []
    for (x, y), label in zip(layout["positions"], modules):
        draw_rect_node(draw, x, y, node_w, node_h, label, body_font, max_chars=10)
        centers.append((x + node_w // 2, y + node_h // 2))
    for index in range(len(centers) - 1):
        x1, y1 = centers[index]
        x2, y2 = centers[index + 1]
        draw_arrow(draw, x1, y1 + node_h // 2 + 6, x2, y2 - node_h // 2 - 8)
    image.save(output)


def data_flow_png(asset: dict[str, Any], output: Path) -> None:
    spec = generation_spec(asset)
    nodes = extract_modules(spec)
    require_items(nodes, asset, "data-flow nodes", minimum=2)
    layout = data_flow_layout(nodes)
    width = layout["width"]
    height = layout["height"]
    node_w = layout["node_w"]
    node_h = layout["node_h"]
    image, draw = png_canvas(width, height)
    body_font = load_font(22)
    centers: list[tuple[int, int]] = []
    for label, (x, y) in zip(nodes, layout["positions"]):
        draw_rect_node(draw, x, y, node_w, node_h, label, body_font, max_chars=8)
        centers.append((x + node_w // 2, y + node_h // 2))
    for source, target in data_flow_edges(nodes):
        draw_arrow(draw, *box_arrow_points(centers[source], centers[target], node_w, node_h))
    for source, target in data_flow_extra_edges(spec, nodes):
        draw_polyline_arrow(draw, orthogonal_points(centers[source], centers[target], node_h))
    image.save(output)


def render_png(asset: dict[str, Any], output: Path) -> None:
    drawing_type = str(asset.get("type") or "")
    if drawing_type == "system_block":
        system_block_png(asset, output)
    elif drawing_type == "data_flow":
        data_flow_png(asset, output)
    else:
        method_flow_png(asset, output)


def stored_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.relative_to(base_dir.resolve()))
    except ValueError:
        return str(path)


def image_model_prompt(asset: dict[str, Any]) -> str:
    figure_no = int(asset.get("figure_no") or 0)
    spec = generation_spec(asset) or str(asset.get("caption") or "").strip()
    validation = asset.get("validation") if isinstance(asset.get("validation"), dict) else {}
    width_ratio = validation.get("content_width_ratio", "约0.80")
    height_ratio = validation.get("content_height_ratio", "约0.80")
    source_figure = asset.get("source_figure") if isinstance(asset.get("source_figure"), dict) else {}
    source_bits = []
    if source_figure.get("source_label"):
        source_bits.append(str(source_figure["source_label"]))
    if source_figure.get("page") not in (None, ""):
        source_bits.append(f"page {source_figure['page']}")
    if source_figure.get("caption"):
        source_bits.append(f"caption: {source_figure['caption']}")
    source_context = f"原始参考来源：{'；'.join(source_bits)}。\n" if source_bits else ""
    return (
        f"请生成中国发明专利申请的说明书附图图{figure_no}，严格依据参考附图结构和以下附图规格重绘：{spec}\n"
        f"{source_context}"
        "硬性要求：纯黑白线条图，纯白背景；不得使用彩色、灰度、渐变、阴影、照片、三维渲染、装饰元素、logo或水印；"
        "图片内部不得出现图号、附图标题、说明性段落或与技术方案无关的文字；"
        "仅保留说明书和权利要求支持的步骤编号、模块名称、关键术语、标号和箭头；"
        f"主体内容应填充画布，目标内容宽度占比不低于{width_ratio}、高度占比不低于{height_ratio}，不得留下大面积空白；"
        "不得新增、删除或改变任何模块、步骤、连接关系和流程方向。"
    )


def generate(
    data: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    prefix: str,
    png_fallback: bool = True,
) -> list[dict[str, Any]]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    assets = infer_assets(data, output_dir, prefix)
    normalized: list[dict[str, Any]] = []
    for asset in sorted(assets, key=lambda item: int(item.get("figure_no") or 0)):
        figure_no = int(asset.get("figure_no") or len(normalized) + 1)
        asset["figure_no"] = figure_no
        preferred_title = title_from_spec(generation_spec(asset) or str(asset.get("spec") or ""), figure_no)
        current_title = str(asset.get("title") or "").strip()
        if (
            not current_title
            or current_title == f"图{figure_no}"
            or (not has_cjk(current_title) and has_cjk(preferred_title))
        ):
            asset["title"] = preferred_title
        else:
            asset["title"] = current_title
        current_caption = str(asset.get("caption") or "").strip()
        preferred_caption = f"图{figure_no} {asset['title']}"
        if (
            not current_caption
            or current_caption == f"图{figure_no} {current_title}"
            or (not has_cjk(current_caption) and has_cjk(asset["title"]))
        ):
            asset["caption"] = preferred_caption
        else:
            asset["caption"] = current_caption
        asset.setdefault("abstract_candidate", figure_no == 1)
        if not asset.get("svg_path"):
            asset["svg_path"] = str(output_dir / f"{prefix}_图{figure_no}.svg")
        svg_path = Path(str(asset["svg_path"]))
        if not svg_path.is_absolute():
            svg_path = (input_path.parent / svg_path).resolve()
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(render_svg(asset), encoding="utf-8")
        asset["svg_path"] = stored_path(svg_path, input_path.parent)
        if png_fallback:
            png_path = svg_path.with_suffix(".png")
            try:
                render_png(asset, png_path)
                asset["png_path"] = stored_path(png_path, input_path.parent)
            except RuntimeError:
                asset.pop("png_path", None)
        asset["image_model_prompt"] = image_model_prompt(asset)
        normalized.append(asset)
    data["drawing_assets"] = normalized
    data["image_model_prompts"] = [
        {"figure_no": asset["figure_no"], "prompt": asset["image_model_prompt"]}
        for asset in normalized
    ]
    data["drawing_validation"] = [
        {"figure_no": asset["figure_no"], **asset.get("validation", {})}
        for asset in normalized
    ]
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate patent drawing SVG files from JSON.")
    parser.add_argument("input", type=Path, help="Path to patent content JSON.")
    parser.add_argument("-o", "--output-dir", type=Path, help="Directory for SVG files.")
    parser.add_argument("--prefix", help="Output filename prefix.")
    parser.add_argument(
        "--no-png-fallback",
        action="store_true",
        help="Do not generate PNG fallback files for DOCX/PDF converters.",
    )
    parser.add_argument(
        "--update-json",
        action="store_true",
        help="Write generated drawing_assets metadata back to the input JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = read_json(args.input)
    output_dir = args.output_dir or args.input.parent
    prefix = args.prefix or default_prefix(args.input)
    assets = generate(data, args.input, output_dir, prefix, png_fallback=not args.no_png_fallback)
    if args.update_json:
        write_json(args.input, data)
    for asset in assets:
        print(f"Wrote {asset['svg_path']}")
        if asset.get("png_path"):
            print(f"Wrote {asset['png_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
