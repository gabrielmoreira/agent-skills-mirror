#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export a DOCX patent application to PDF.

LibreOffice/headless conversion is preferred. When no converter is available,
the script can render a visual PDF directly from the structured patent JSON
using Pillow. The fallback PDF is image-based and intended as a review copy.
"""

from __future__ import annotations



import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def find_soffice(explicit: str | None = None) -> str | None:
    candidates = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("SOFFICE"):
        candidates.append(os.environ["SOFFICE"])
    candidates.extend(
        [
            "soffice",
            "libreoffice",
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    )
    for candidate in candidates:
        resolved = shutil.which(candidate) if not Path(candidate).exists() else candidate
        if resolved:
            return str(resolved)
    return None


def export_pdf(docx: Path, output: Path, soffice: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output.parent),
        str(docx),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "LibreOffice conversion failed.").strip()
        raise RuntimeError(message)

    produced = output.parent / f"{docx.stem}.pdf"
    if produced != output:
        if output.exists():
            output.unlink()
        produced.replace(output)
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("PDF conversion finished but no non-empty PDF was produced.")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Patent content JSON must be an object.")
    return data


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


def resolve_asset(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    base_candidate = base_dir / path
    if base_candidate.exists():
        return base_candidate.resolve()
    cwd_candidate = Path.cwd() / path
    if cwd_candidate.exists():
        return cwd_candidate.resolve()
    return base_candidate.resolve()


def load_font(size: int):
    try:
        from PIL import ImageFont
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError("Pillow is required for JSON PDF fallback rendering.") from exc

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


class PdfCanvas:
    def __init__(self) -> None:
        from PIL import Image, ImageDraw

        self.Image = Image
        self.ImageDraw = ImageDraw
        self.width = 1240
        self.height = 1754
        self.margin_x = 110
        self.margin_top = 105
        self.margin_bottom = 105
        self.y = self.margin_top
        self.pages: list[Any] = []
        self.page = None
        self.draw = None
        self.body_font = load_font(23)
        self.small_font = load_font(19)
        self.heading_font = load_font(30)
        self.title_font = load_font(36)
        self.new_page()

    def new_page(self) -> None:
        if self.page is not None:
            self.add_page_number()
        self.page = self.Image.new("RGB", (self.width, self.height), "white")
        self.draw = self.ImageDraw.Draw(self.page)
        self.pages.append(self.page)
        self.y = self.margin_top

    def add_page_number(self) -> None:
        number = str(len(self.pages))
        bbox = self.draw.textbbox((0, 0), number, font=self.small_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        self.draw.text((x, self.height - 62), number, fill="black", font=self.small_font)

    def ensure_space(self, needed: int) -> None:
        if self.y + needed > self.height - self.margin_bottom:
            self.new_page()

    def text_width(self, text: str, font: Any) -> int:
        bbox = self.draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def wrap(self, text: str, font: Any, max_width: int, first_indent: int = 0) -> list[str]:
        lines = []
        current = ""
        current_limit = max_width - first_indent
        for char in text:
            candidate = current + char
            if current and self.text_width(candidate, font) > current_limit:
                lines.append(current)
                current = char
                current_limit = max_width
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines or [""]

    def centered(self, text: str, font: Any, before: int = 0, after: int = 16) -> None:
        max_width = self.width - self.margin_x * 2
        lines = self.wrap(text, font, max_width)
        line_height = font.size + 10
        self.ensure_space(before + len(lines) * line_height + after)
        self.y += before
        for line in lines:
            x = (self.width - self.text_width(line, font)) // 2
            self.draw.text((x, self.y), line, fill="black", font=font)
            self.y += line_height
        self.y += after

    def paragraph(self, text: str, font: Any | None = None, first_indent: bool = True) -> None:
        font = font or self.body_font
        max_width = self.width - self.margin_x * 2
        indent = 44 if first_indent else 0
        lines = self.wrap(text, font, max_width, first_indent=indent)
        line_height = font.size + 13
        self.ensure_space(len(lines) * line_height + 12)
        for index, line in enumerate(lines):
            x = self.margin_x + (indent if index == 0 else 0)
            self.draw.text((x, self.y), line, fill="black", font=font)
            self.y += line_height
        self.y += 10

    def heading(self, text: str) -> None:
        self.ensure_space(58)
        self.y += 14
        self.draw.text((self.margin_x, self.y), text, fill="black", font=self.heading_font)
        self.y += 50

    def image(self, image_path: Path, caption: str) -> None:
        from PIL import Image

        source = Image.open(image_path).convert("RGB")
        max_width = self.width - self.margin_x * 2
        max_height = 520
        scale = min(max_width / source.width, max_height / source.height, 1.0)
        rendered = source.resize((int(source.width * scale), int(source.height * scale)))
        needed = rendered.height + 76
        self.ensure_space(needed)
        x = (self.width - rendered.width) // 2
        self.page.paste(rendered, (x, self.y))
        self.y += rendered.height + 16
        self.centered(caption, self.small_font, before=0, after=18)

    def save(self, output: Path) -> None:
        self.add_page_number()
        output.parent.mkdir(parents=True, exist_ok=True)
        first, *rest = self.pages
        first.save(output, "PDF", save_all=True, append_images=rest, resolution=150)


def drawing_images(data: dict[str, Any], base_dir: Path) -> list[dict[str, Any]]:
    assets = data.get("drawing_assets")
    if not isinstance(assets, list):
        return []
    result = []
    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            continue
        raw = str(asset.get("png_path") or asset.get("svg_path") or "").strip()
        if not raw:
            continue
        path = resolve_asset(raw, base_dir)
        if path.suffix.lower() != ".png" or not path.exists():
            continue
        figure_no = int(asset.get("figure_no") or index)
        title = str(asset.get("title") or f"图{figure_no}").strip()
        caption = str(asset.get("caption") or f"图{figure_no} {title}").strip()
        result.append({"figure_no": figure_no, "path": path, "caption": caption, "asset": asset})
    return sorted(result, key=lambda item: item["figure_no"])


def select_abstract_image(data: dict[str, Any], images: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not images:
        return None
    text = str(data.get("abstract_drawing") or "")
    match = re.search(r"图\s*(\d+)", text)
    if match:
        figure_no = int(match.group(1))
        for image in images:
            if image["figure_no"] == figure_no:
                return image
    for image in images:
        if bool(image["asset"].get("abstract_candidate")):
            return image
    return images[0]


def render_pdf_from_json(content_json: Path, output: Path) -> None:
    data = read_json(content_json)
    base_dir = content_json.parent
    canvas = PdfCanvas()
    invention_name = str(data.get("invention_name") or data.get("title") or "【待补充：发明名称】")
    source_title = str(data.get("source_title") or "").strip()
    canvas.centered(invention_name, canvas.title_font, after=18)
    if source_title:
        canvas.centered(f"来源论文：{source_title}", canvas.small_font, after=22)

    canvas.heading("一、说明书摘要")
    for paragraph in as_paragraphs(data.get("abstract")) or ["【待补充：说明书摘要。】"]:
        canvas.paragraph(paragraph)

    images = drawing_images(data, base_dir)
    canvas.heading("二、摘要附图")
    for paragraph in as_paragraphs(data.get("abstract_drawing")) or ["【待补充：摘要附图选择或说明。】"]:
        canvas.paragraph(paragraph)
    abstract = select_abstract_image(data, images)
    if abstract:
        canvas.image(abstract["path"], abstract["caption"])

    canvas.heading("三、权利要求书")
    for claim in as_paragraphs(data.get("claims")) or ["【待补充：权利要求书。】"]:
        canvas.paragraph(claim)

    canvas.heading("四、说明书")
    description = data.get("description")
    if isinstance(description, dict):
        mapping = [
            ("technical_field", "技术领域"),
            ("background", "背景技术"),
            ("invention_content", "发明内容"),
            ("drawing_description", "附图说明"),
            ("embodiments", "具体实施方式"),
        ]
        for key, heading in mapping:
            canvas.heading(heading)
            values = as_paragraphs(description.get(key)) or [f"【待补充：{heading}。】"]
            for paragraph in values:
                canvas.paragraph(paragraph)
    else:
        for paragraph in as_paragraphs(description) or ["【待补充：说明书正文。】"]:
            canvas.paragraph(paragraph)

    canvas.heading("五、说明书附图")
    if images:
        for image in images:
            canvas.image(image["path"], image["caption"])
            spec = str(image["asset"].get("spec") or "").strip()
            for paragraph in as_paragraphs(spec):
                canvas.paragraph(paragraph)
    else:
        for paragraph in as_paragraphs(data.get("drawings")) or ["【待补充：说明书附图。】"]:
            canvas.paragraph(paragraph)

    gaps = as_paragraphs(data.get("gaps"))
    if gaps:
        canvas.heading("材料缺口说明")
        for paragraph in gaps:
            canvas.paragraph(paragraph)

    canvas.save(output)
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("JSON PDF fallback did not produce a non-empty PDF.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a DOCX file to PDF.")
    parser.add_argument("docx", type=Path, help="Path to the input DOCX.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Path to write the output PDF.",
    )
    parser.add_argument("--soffice", help="Explicit path to soffice/libreoffice.")
    parser.add_argument(
        "--content-json",
        type=Path,
        help="Structured patent JSON used for image-based PDF fallback when LibreOffice is unavailable.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.docx.exists():
        raise FileNotFoundError(args.docx)
    soffice = find_soffice(args.soffice)
    if soffice:
        export_pdf(args.docx, args.output, soffice)
        print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")
        return 0
    if args.content_json:
        render_pdf_from_json(args.content_json, args.output)
        print(
            f"Wrote {args.output} ({args.output.stat().st_size} bytes, image_based_fallback=1)"
        )
        return 0
    print(
        "LibreOffice/soffice was not found. Keep the DOCX as the primary deliverable "
        "or pass --content-json to render an image-based PDF fallback."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
