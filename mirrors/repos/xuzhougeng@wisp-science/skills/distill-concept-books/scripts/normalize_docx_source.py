#!/usr/bin/env python3
"""Deterministically normalize a DOCX source without modifying the input file.

The script intentionally uses only the Python standard library.  It reads the
OOXML package in-place, walks top-level body paragraphs and tables in document
order, and writes a private normalization bundle to an explicit output
directory.

No OCR, spelling correction, scientific-symbol substitution, or semantic
rewriting is performed.  Normalized text is limited to Unicode NFC and a
conservative whitespace policy documented in ``normalization-log.yml``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import struct
import sys
import unicodedata
import urllib.parse
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping, Sequence
from xml.etree import ElementTree as ET


TOOL_NAME = "normalize_docx_source"
TOOL_VERSION = "1.0.0"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DOCUMENT_PART = "word/document.xml"
DOCUMENT_RELS_PART = "word/_rels/document.xml.rels"
STYLES_PART = "word/styles.xml"
CORE_PROPERTIES_PART = "docProps/core.xml"

W = "{%s}" % NS["w"]
M = "{%s}" % NS["m"]
R = "{%s}" % NS["r"]
A = "{%s}" % NS["a"]
V = "{%s}" % NS["v"]

OUTPUT_FILENAMES = (
    "blocks.jsonl",
    "structure.yml",
    "media-map.yml",
    "normalization-log.yml",
    "checksums.yml",
)

_HORIZONTAL_SPACE_RE = re.compile(r" +")
_HEADING_EN_RE = re.compile(r"(?i)(?:^|\b)heading\s*([1-9])(?:\b|$)")
_HEADING_ZH_RE = re.compile(r"(?:标题|標題)\s*([1-9一二三四五六七八九])")
_CHINESE_LEVELS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                   "六": 6, "七": 7, "八": 8, "九": 9}


class NormalizationError(RuntimeError):
    """Raised when the source cannot be normalized safely."""


@dataclass(frozen=True)
class Relationship:
    relationship_id: str
    relationship_type: str
    target: str
    target_mode: str | None
    package_path: str | None

    @property
    def is_external(self) -> bool:
        return (self.target_mode or "").lower() == "external"

    @property
    def is_image(self) -> bool:
        return self.relationship_type.rstrip("/").endswith("/image")


@dataclass(frozen=True)
class StyleInfo:
    style_id: str
    name: str | None
    based_on: str | None
    outline_level: int | None


def qname(prefix: str, local: str) -> str:
    return "{%s}%s" % (NS[prefix], local)


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        # JSON double-quoted strings are valid YAML scalars and handle control
        # characters deterministically without a third-party YAML dependency.
        return json.dumps(value, ensure_ascii=False)
    raise TypeError(f"unsupported YAML scalar: {type(value).__name__}")


def _yaml_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, Mapping):
        if not value:
            return [prefix + "{}"]
        lines: list[str] = []
        for key, item in value.items():
            rendered_key = _yaml_scalar(str(key))
            if isinstance(item, Mapping) or isinstance(item, (list, tuple)):
                if not item:
                    lines.append(f"{prefix}{rendered_key}: " + ("{}" if isinstance(item, Mapping) else "[]"))
                else:
                    lines.append(f"{prefix}{rendered_key}:")
                    lines.extend(_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}{rendered_key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, (list, tuple)):
        if not value:
            return [prefix + "[]"]
        lines = []
        for item in value:
            if isinstance(item, Mapping) or isinstance(item, (list, tuple)):
                if not item:
                    lines.append(prefix + "- " + ("{}" if isinstance(item, Mapping) else "[]"))
                else:
                    lines.append(prefix + "-")
                    lines.extend(_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return lines
    return [prefix + _yaml_scalar(value)]


def write_yaml(path: Path, value: Mapping[str, Any]) -> None:
    text = "---\n" + "\n".join(_yaml_lines(value)) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def _validate_source_id(source_id: str) -> str:
    value = source_id.strip()
    if not value:
        raise NormalizationError("--source-id must not be empty")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise NormalizationError("--source-id must not contain control characters")
    return value


def _prepare_output_directory(output_dir: Path) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise NormalizationError(f"output path exists and is not a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise NormalizationError(
            f"output directory must be new or empty; refusing to overwrite: {output_dir}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "media").mkdir()


def normalize_text(raw_text: str) -> tuple[str, dict[str, Any]]:
    """Apply NFC and conservative whitespace normalization only."""
    nfc_text = unicodedata.normalize("NFC", raw_text)
    nfc_changed = nfc_text != raw_text

    crlf_count = nfc_text.count("\r\n")
    lone_cr_count = nfc_text.count("\r") - crlf_count
    text = nfc_text.replace("\r\n", "\n").replace("\r", "\n")

    replaced_unicode_space_count = 0
    converted: list[str] = []
    for char in text:
        if char in ("\n", "\t"):
            converted.append(char)
        elif char.isspace() and char != " ":
            converted.append(" ")
            replaced_unicode_space_count += 1
        else:
            converted.append(char)
    text = "".join(converted)

    collapsed_space_count = 0
    normalized_lines: list[str] = []
    for line in text.split("\n"):
        pieces = line.split("\t")
        normalized_pieces: list[str] = []
        for piece in pieces:
            runs = _HORIZONTAL_SPACE_RE.findall(piece)
            collapsed_space_count += sum(max(0, len(run) - 1) for run in runs)
            normalized_pieces.append(_HORIZONTAL_SPACE_RE.sub(" ", piece).strip(" "))
        normalized_lines.append("\t".join(normalized_pieces))

    before_outer_trim = "\n".join(normalized_lines)
    # TABs delimit table cells and therefore remain significant even at the
    # start or end of a block (an empty first/last cell).  Only spaces and
    # newlines are trimmed at the outer block boundary.
    normalized = before_outer_trim.strip(" \n")
    stats = {
        "nfc_changed": nfc_changed,
        "crlf_converted": crlf_count,
        "lone_cr_converted": lone_cr_count,
        "unicode_spaces_replaced": replaced_unicode_space_count,
        "redundant_spaces_removed": collapsed_space_count,
        "outer_whitespace_trimmed": normalized != before_outer_trim,
        "changed": normalized != raw_text,
    }
    return normalized, stats


def extract_text(element: ET.Element) -> str:
    """Extract visible run text while preserving tabs and explicit breaks."""
    pieces: list[str] = []
    for node in element.iter():
        if node.tag in (W + "t", M + "t"):
            pieces.append(node.text or "")
        elif node.tag == W + "tab":
            pieces.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            pieces.append("\n")
        elif node.tag == W + "noBreakHyphen":
            pieces.append("\u2011")
        elif node.tag == W + "softHyphen":
            pieces.append("\u00ad")
        elif node.tag == W + "sym":
            char_value = node.get(W + "char")
            if char_value:
                try:
                    pieces.append(chr(int(char_value, 16)))
                except (ValueError, OverflowError):
                    # The occurrence is separately placed into manual review.
                    pass
    return "".join(pieces)


def iter_body_blocks(body: ET.Element) -> Iterator[ET.Element]:
    """Yield body-level paragraphs/tables, including those in content controls.

    Once a table is yielded its cell content is not traversed again: the table
    is one body block and its internal paragraphs belong to that block.
    """
    for child in list(body):
        name = local_name(child.tag)
        if name in ("p", "tbl"):
            yield child
        elif name not in ("sectPr", "pPr", "tblPr"):
            yield from iter_body_blocks(child)


def _wrapped_children_by_local(element: ET.Element, name: str) -> Iterator[ET.Element]:
    """Yield rows or cells through OOXML wrappers without entering nested peers."""
    for child in list(element):
        child_name = local_name(child.tag)
        if child_name == name:
            yield child
        elif child_name not in ("p", "tbl"):
            yield from _wrapped_children_by_local(child, name)


def _container_text_parts(container: ET.Element) -> list[str]:
    """Extract direct cell content without duplicating nested table text."""
    parts: list[str] = []
    for child in list(container):
        name = local_name(child.tag)
        if name == "p":
            parts.append(extract_text(child))
        elif name == "tbl":
            parts.append(extract_table_text(child))
        elif name in ("sdt", "sdtContent", "customXml"):
            parts.extend(_container_text_parts(child))
    return parts


def extract_table_text(table: ET.Element) -> str:
    rows: list[str] = []
    for row in _wrapped_children_by_local(table, "tr"):
        cells: list[str] = []
        for cell in _wrapped_children_by_local(row, "tc"):
            cells.append("\n".join(_container_text_parts(cell)))
        rows.append("\t".join(cells))
    return "\n".join(rows)


def table_dimensions(table: ET.Element) -> tuple[int, int]:
    rows = list(_wrapped_children_by_local(table, "tr"))
    cell_counts = [len(list(_wrapped_children_by_local(row, "tc"))) for row in rows]
    return len(rows), max(cell_counts, default=0)


def paragraph_style_id(paragraph: ET.Element) -> str | None:
    style = paragraph.find("./w:pPr/w:pStyle", NS)
    return style.get(W + "val") if style is not None else None


def table_style_id(table: ET.Element) -> str | None:
    style = table.find("./w:tblPr/w:tblStyle", NS)
    return style.get(W + "val") if style is not None else None


def load_styles(package: zipfile.ZipFile) -> dict[str, StyleInfo]:
    if STYLES_PART not in package.namelist():
        return {}
    root = ET.fromstring(package.read(STYLES_PART))
    styles: dict[str, StyleInfo] = {}
    for style in root.findall("./w:style", NS):
        if style.get(W + "type") != "paragraph":
            continue
        style_id = style.get(W + "styleId")
        if not style_id:
            continue
        name_node = style.find("./w:name", NS)
        based_node = style.find("./w:basedOn", NS)
        outline_node = style.find("./w:pPr/w:outlineLvl", NS)
        outline_level: int | None = None
        if outline_node is not None:
            try:
                parsed = int(outline_node.get(W + "val", ""))
                if 0 <= parsed <= 8:
                    outline_level = parsed + 1
            except ValueError:
                pass
        styles[style_id] = StyleInfo(
            style_id=style_id,
            name=name_node.get(W + "val") if name_node is not None else None,
            based_on=based_node.get(W + "val") if based_node is not None else None,
            outline_level=outline_level,
        )
    return styles


def _heading_level_from_label(label: str | None) -> int | None:
    if not label:
        return None
    match = _HEADING_EN_RE.search(label)
    if match:
        return int(match.group(1))
    match = _HEADING_ZH_RE.search(label)
    if match:
        token = match.group(1)
        return int(token) if token.isdigit() else _CHINESE_LEVELS[token]
    return None


def heading_level(paragraph: ET.Element, style_id: str | None,
                  styles: Mapping[str, StyleInfo]) -> int | None:
    direct_outline = paragraph.find("./w:pPr/w:outlineLvl", NS)
    if direct_outline is not None:
        try:
            value = int(direct_outline.get(W + "val", ""))
            if 0 <= value <= 8:
                return value + 1
        except ValueError:
            pass

    visited: set[str] = set()
    current = style_id
    while current and current not in visited:
        visited.add(current)
        info = styles.get(current)
        if info is None:
            return _heading_level_from_label(current)
        if info.outline_level is not None:
            return info.outline_level
        inferred = _heading_level_from_label(info.name) or _heading_level_from_label(info.style_id)
        if inferred is not None:
            return inferred
        current = info.based_on
    return _heading_level_from_label(style_id)


def _resolve_package_target(target: str, target_mode: str | None) -> str | None:
    if (target_mode or "").lower() == "external":
        return None
    decoded = urllib.parse.unquote(target).replace("\\", "/")
    if decoded.startswith("/"):
        candidate = posixpath.normpath(decoded.lstrip("/"))
    else:
        candidate = posixpath.normpath(posixpath.join(posixpath.dirname(DOCUMENT_PART), decoded))
    if candidate in ("", ".") or candidate == ".." or candidate.startswith("../"):
        raise NormalizationError(f"unsafe relationship target: {target!r}")
    return str(PurePosixPath(candidate))


def load_relationships(package: zipfile.ZipFile) -> dict[str, Relationship]:
    if DOCUMENT_RELS_PART not in package.namelist():
        return {}
    root = ET.fromstring(package.read(DOCUMENT_RELS_PART))
    relationships: dict[str, Relationship] = {}
    for node in root.findall(f"{{{REL_NS}}}Relationship"):
        relationship_id = node.get("Id")
        target = node.get("Target")
        relationship_type = node.get("Type")
        if not relationship_id or target is None or relationship_type is None:
            continue
        target_mode = node.get("TargetMode")
        relationships[relationship_id] = Relationship(
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            target=target,
            target_mode=target_mode,
            package_path=_resolve_package_target(target, target_mode),
        )
    return relationships


def image_relationship_references(element: ET.Element) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    for node in element.iter():
        if node.tag == A + "blip":
            embedded = node.get(R + "embed")
            linked = node.get(R + "link")
            if embedded:
                references.append({"relationship_id": embedded, "reference_kind": "drawingml-embed"})
            if linked:
                references.append({"relationship_id": linked, "reference_kind": "drawingml-link"})
        elif node.tag == V + "imagedata":
            relationship_id = node.get(R + "id")
            if relationship_id:
                references.append({"relationship_id": relationship_id, "reference_kind": "vml-image"})
    return references


def _safe_media_filename(package_path: str, relationship_id: str,
                         used_names: set[str]) -> str:
    base = PurePosixPath(package_path).name or f"{relationship_id}.bin"
    candidate = base
    if candidate.casefold() in used_names:
        stem = Path(base).stem
        suffix = Path(base).suffix
        candidate = f"{stem}-{relationship_id}{suffix}"
        counter = 2
        while candidate.casefold() in used_names:
            candidate = f"{stem}-{relationship_id}-{counter}{suffix}"
            counter += 1
    used_names.add(candidate.casefold())
    return candidate


def image_dimensions(data: bytes) -> dict[str, int] | None:
    """Return common raster pixel dimensions without decoding/re-encoding."""
    if len(data) >= 24 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        width, height = struct.unpack(">II", data[16:24])
        return {"width_px": width, "height_px": height}
    if len(data) >= 10 and data[:6] in (b"GIF87a", b"GIF89a"):
        width, height = struct.unpack("<HH", data[6:10])
        return {"width_px": width, "height_px": height}
    if len(data) >= 26 and data.startswith(b"BM"):
        width, height = struct.unpack("<ii", data[18:26])
        return {"width_px": abs(width), "height_px": abs(height)}
    if len(data) >= 4 and data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            if offset + 2 > len(data):
                break
            segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
            if segment_length < 2 or offset + segment_length > len(data):
                break
            if marker in {
                0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
            } and segment_length >= 7:
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return {"width_px": width, "height_px": height}
            offset += segment_length
    return None


def core_properties(package: zipfile.ZipFile) -> dict[str, str | None]:
    result: dict[str, str | None] = {
        "title": None,
        "creator": None,
        "subject": None,
        "description": None,
        "created": None,
        "modified": None,
        "last_modified_by": None,
    }
    if CORE_PROPERTIES_PART not in package.namelist():
        return result
    root = ET.fromstring(package.read(CORE_PROPERTIES_PART))
    paths = {
        "title": "./dc:title",
        "creator": "./dc:creator",
        "subject": "./dc:subject",
        "description": "./dc:description",
        "created": "./dcterms:created",
        "modified": "./dcterms:modified",
        "last_modified_by": "./cp:lastModifiedBy",
    }
    for key, path in paths.items():
        node = root.find(path, NS)
        if node is not None and node.text is not None:
            result[key] = node.text
    return result


def _manual_review_findings(element: ET.Element, block_id: str,
                            finding_counter: list[int]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def add(category: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        finding_counter[0] += 1
        item: dict[str, Any] = {
            "finding_id": f"review-{finding_counter[0]:06d}",
            "block_id": block_id,
            "category": category,
            "message": message,
            "status": "needs-human-review",
        }
        if details:
            item["details"] = dict(details)
        findings.append(item)

    symbol_nodes = [node for node in element.iter() if node.tag == W + "sym"]
    for node in symbol_nodes:
        add(
            "legacy-symbol",
            "Legacy w:sym value was preserved as its declared code point; verify font semantics manually.",
            {"font": node.get(W + "font"), "char_hex": node.get(W + "char")},
        )
    math_count = sum(1 for node in element.iter() if node.tag in (M + "oMath", M + "oMathPara"))
    if math_count:
        add(
            "office-math",
            "Office Math content was reduced to available text nodes; verify formula structure manually.",
            {"element_count": math_count},
        )
    field_count = sum(1 for node in element.iter() if node.tag in (W + "instrText", W + "fldSimple"))
    if field_count:
        add(
            "field-code",
            "Field codes were not interpreted; only visible text runs were captured.",
            {"element_count": field_count},
        )
    tracked_insertions = sum(1 for node in element.iter() if node.tag == W + "ins")
    tracked_deletions = sum(1 for node in element.iter() if node.tag == W + "del")
    if tracked_insertions or tracked_deletions:
        add(
            "tracked-changes",
            "Tracked changes are present; visible w:t text was captured and deleted w:delText was excluded.",
            {"insertions": tracked_insertions, "deletions": tracked_deletions},
        )
    return findings


def _style_name(style_id: str | None, styles: Mapping[str, StyleInfo]) -> str | None:
    if style_id is None:
        return None
    info = styles.get(style_id)
    return info.name if info is not None else None


def normalize_docx(source_path: Path | str, output_dir: Path | str,
                   source_id: str) -> dict[str, Any]:
    """Normalize ``source_path`` into ``output_dir`` and return a summary."""
    source = Path(source_path)
    output = Path(output_dir)
    source_id = _validate_source_id(source_id)

    if not source.is_file():
        raise NormalizationError(f"DOCX source does not exist or is not a file: {source}")
    if source.suffix.lower() != ".docx":
        raise NormalizationError(f"expected a .docx source: {source}")

    source_stat_before = source.stat()
    source_sha_before = sha256_file(source)
    blocks: list[dict[str, Any]] = []
    structure_blocks: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    media_assets: dict[str, dict[str, Any]] = {}
    media_occurrences: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    review_findings: list[dict[str, Any]] = []
    finding_counter = [0]
    used_media_names: set[str] = set()
    normalization_totals = {
        "blocks_changed": 0,
        "nfc_changed_blocks": 0,
        "crlf_converted": 0,
        "lone_cr_converted": 0,
        "unicode_spaces_replaced": 0,
        "redundant_spaces_removed": 0,
    }

    with zipfile.ZipFile(source, "r") as package:
        names = set(package.namelist())
        if DOCUMENT_PART not in names:
            raise NormalizationError(f"DOCX package is missing {DOCUMENT_PART}")
        try:
            document_root = ET.fromstring(package.read(DOCUMENT_PART))
        except ET.ParseError as exc:
            raise NormalizationError(f"cannot parse {DOCUMENT_PART}: {exc}") from exc

        body = document_root.find("./w:body", NS)
        if body is None:
            raise NormalizationError("DOCX document.xml has no w:body")

        styles = load_styles(package)
        relationships = load_relationships(package)
        properties = core_properties(package)
        _prepare_output_directory(output)
        heading_path: list[str] = []
        global_image_order = 0
        table_order = 0

        body_blocks = list(iter_body_blocks(body))
        for block_index, element in enumerate(body_blocks, start=1):
            block_type = "paragraph" if element.tag == W + "p" else "table"
            raw_text = extract_text(element) if block_type == "paragraph" else extract_table_text(element)
            normalized_text, normalization_stats = normalize_text(raw_text)
            text_sha256 = sha256_bytes(normalized_text.encode("utf-8"))
            short_content_hash = text_sha256[:12]
            block_id = f"{source_id}#b{block_index:06d}-{short_content_hash}"

            style_id: str | None
            style_name: str | None
            level: int | None = None
            table_id: str | None = None
            table_rows: int | None = None
            table_columns: int | None = None
            if block_type == "paragraph":
                style_id = paragraph_style_id(element)
                style_name = _style_name(style_id, styles)
                level = heading_level(element, style_id, styles)
                if level is not None and normalized_text:
                    heading_path = heading_path[:level - 1]
                    heading_path.append(normalized_text)
                    headings.append({
                        "block_id": block_id,
                        "block_index": block_index,
                        "level": level,
                        "title": normalized_text,
                        "heading_path": list(heading_path),
                    })
            else:
                style_id = table_style_id(element)
                style_name = None
                table_order += 1
                table_id = f"table-{table_order:06d}"
                table_rows, table_columns = table_dimensions(element)

            image_refs = image_relationship_references(element)
            figure_ids: list[str] = []
            occurrence_ids: list[str] = []
            for within_block_order, reference in enumerate(image_refs, start=1):
                global_image_order += 1
                occurrence_id = f"image-occurrence-{global_image_order:06d}"
                figure_id = f"figure-{global_image_order:06d}"
                relationship_id = reference["relationship_id"]
                relationship = relationships.get(relationship_id)
                figure_ids.append(figure_id)
                occurrence_ids.append(occurrence_id)
                occurrence: dict[str, Any] = {
                    "occurrence_id": occurrence_id,
                    "figure_id": figure_id,
                    "document_order": global_image_order,
                    "within_block_order": within_block_order,
                    "relationship_id": relationship_id,
                    "reference_kind": reference["reference_kind"],
                    "block_id": block_id,
                    "block_index": block_index,
                    "previous_block_id": None,
                    "next_block_id": None,
                    "asset_id": None,
                    "status": "unresolved",
                }
                if relationship is None:
                    warnings.append({
                        "warning_id": f"warning-{len(warnings) + 1:06d}",
                        "block_id": block_id,
                        "category": "missing-relationship",
                        "message": f"Image relationship {relationship_id} is not present in document.xml.rels.",
                    })
                else:
                    occurrence.update({
                        "relationship_type": relationship.relationship_type,
                        "relationship_target": relationship.target,
                        "target_mode": relationship.target_mode,
                        "package_path": relationship.package_path,
                    })
                    if relationship.is_external:
                        occurrence["status"] = "external-not-downloaded"
                        warnings.append({
                            "warning_id": f"warning-{len(warnings) + 1:06d}",
                            "block_id": block_id,
                            "category": "external-image",
                            "message": f"External image {relationship_id} was recorded but not downloaded.",
                        })
                    elif not relationship.is_image:
                        occurrence["status"] = "non-image-relationship"
                        warnings.append({
                            "warning_id": f"warning-{len(warnings) + 1:06d}",
                            "block_id": block_id,
                            "category": "unexpected-relationship-type",
                            "message": f"Relationship {relationship_id} is referenced as an image but has type {relationship.relationship_type}.",
                        })
                    elif relationship.package_path not in names:
                        occurrence["status"] = "missing-package-part"
                        warnings.append({
                            "warning_id": f"warning-{len(warnings) + 1:06d}",
                            "block_id": block_id,
                            "category": "missing-media-part",
                            "message": f"Image package part is missing: {relationship.package_path}.",
                        })
                    else:
                        asset_id = f"media-{relationship_id}"
                        occurrence["asset_id"] = asset_id
                        occurrence["status"] = "extracted"
                        if asset_id not in media_assets:
                            media_bytes = package.read(relationship.package_path)
                            filename = _safe_media_filename(
                                relationship.package_path, relationship_id, used_media_names
                            )
                            media_path = output / "media" / filename
                            media_path.write_bytes(media_bytes)
                            package_sha = sha256_bytes(media_bytes)
                            extracted_sha = sha256_file(media_path)
                            media_assets[asset_id] = {
                                "asset_id": asset_id,
                                "relationship_id": relationship_id,
                                "relationship_type": relationship.relationship_type,
                                "package_path": relationship.package_path,
                                "original_filename": PurePosixPath(relationship.package_path).name,
                                "extracted_path": f"media/{filename}",
                                "byte_size": len(media_bytes),
                                "sha256_in_package": package_sha,
                                "sha256_extracted": extracted_sha,
                                "byte_for_byte_preserved": package_sha == extracted_sha,
                                "pixel_dimensions": image_dimensions(media_bytes),
                            }
                media_occurrences.append(occurrence)

            locator: dict[str, Any] = {
                "source_id": source_id,
                "heading_path": list(heading_path),
                "ooxml_block_index": block_index,
                "content_hash": short_content_hash,
            }
            if figure_ids:
                locator["figure_ids"] = figure_ids
            if table_id is not None:
                locator["table_id"] = table_id

            block_record: dict[str, Any] = {
                "schema_version": 1,
                "source_id": source_id,
                "block_id": block_id,
                "block_type": block_type,
                "ooxml_block_index": block_index,
                "locator": locator,
                "heading_path": list(heading_path),
                "heading_level": level,
                "style_id": style_id,
                "style_name": style_name,
                "raw_text": raw_text,
                "normalized_text": normalized_text,
                "text_sha256": text_sha256,
                "short_content_hash": short_content_hash,
                "normalization": normalization_stats,
                "figure_ids": figure_ids,
                "media_occurrence_ids": occurrence_ids,
            }
            if table_id is not None:
                block_record["table_id"] = table_id
                block_record["table_rows"] = table_rows
                block_record["table_columns"] = table_columns
            blocks.append(block_record)

            structure_item: dict[str, Any] = {
                "block_id": block_id,
                "ooxml_block_index": block_index,
                "block_type": block_type,
                "heading_path": list(heading_path),
                "heading_level": level,
                "style_id": style_id,
                "style_name": style_name,
                "short_content_hash": short_content_hash,
                "raw_character_count": len(raw_text),
                "normalized_character_count": len(normalized_text),
                "is_empty_text": normalized_text == "",
                "figure_ids": figure_ids,
            }
            if table_id is not None:
                structure_item.update({
                    "table_id": table_id,
                    "table_rows": table_rows,
                    "table_columns": table_columns,
                })
            structure_blocks.append(structure_item)

            review_findings.extend(_manual_review_findings(element, block_id, finding_counter))
            if normalization_stats["changed"]:
                normalization_totals["blocks_changed"] += 1
            if normalization_stats["nfc_changed"]:
                normalization_totals["nfc_changed_blocks"] += 1
            for key in (
                "crlf_converted", "lone_cr_converted", "unicode_spaces_replaced",
                "redundant_spaces_removed",
            ):
                normalization_totals[key] += int(normalization_stats[key])

        block_ids = [block["block_id"] for block in blocks]
        for occurrence in media_occurrences:
            index = int(occurrence["block_index"]) - 1
            occurrence["previous_block_id"] = block_ids[index - 1] if index > 0 else None
            occurrence["next_block_id"] = block_ids[index + 1] if index + 1 < len(block_ids) else None

        section_property_count = sum(1 for node in document_root.iter() if node.tag == W + "sectPr")
        content_types = {
            "paragraphs": sum(block["block_type"] == "paragraph" for block in blocks),
            "tables": sum(block["block_type"] == "table" for block in blocks),
            "headings": len(headings),
            "image_occurrences": len(media_occurrences),
            "unique_image_assets": len(media_assets),
            "sections_detected": section_property_count,
        }

    structure = {
        "schema_version": 1,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "source": {
            "source_id": source_id,
            "filename": source.name,
            "format": "docx",
            "sha256": source_sha_before,
            "core_properties": properties,
        },
        "locator_policy": {
            "canonical_components": [
                "source_id", "heading_path", "ooxml_block_index", "content_hash",
                "optional figure_id/table_id",
            ],
            "page_number_role": "auxiliary-only-not-extracted",
            "block_index_base": 1,
            "content_hash": "first 12 hexadecimal characters of SHA-256(normalized_text UTF-8)",
        },
        "summary": {"total_blocks": len(blocks), **content_types},
        "headings": headings,
        "blocks": structure_blocks,
    }
    media_map = {
        "schema_version": 1,
        "source_id": source_id,
        "policy": {
            "extraction": "original OOXML package bytes; no decoding or re-encoding",
            "resolution": "preserved byte-for-byte; raster dimensions reported when detectable",
            "external_media": "record-only; never downloaded",
        },
        "assets": list(media_assets.values()),
        "occurrences": media_occurrences,
        "warnings": warnings,
    }
    normalization_log = {
        "schema_version": 1,
        "source_id": source_id,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "automatic_policy": {
            "unicode": "NFC",
            "line_endings": "CRLF and CR converted to LF",
            "horizontal_whitespace": "Unicode whitespace except TAB/LF mapped to ASCII space; consecutive ASCII spaces collapsed within TAB-delimited fields",
            "trimming": "leading/trailing ASCII spaces per TAB-delimited field and outer block whitespace removed",
        },
        "not_performed": [
            "OCR",
            "spelling or grammar correction",
            "scientific-symbol substitution",
            "professional-terminology correction",
            "semantic rewriting",
            "field-code evaluation",
            "equation reconstruction",
        ],
        "summary": {"total_blocks": len(blocks), **normalization_totals},
        "manual_review": review_findings,
        "warnings": warnings,
    }

    write_jsonl(output / "blocks.jsonl", blocks)
    write_yaml(output / "structure.yml", structure)
    write_yaml(output / "media-map.yml", media_map)
    write_yaml(output / "normalization-log.yml", normalization_log)

    source_sha_after = sha256_file(source)
    source_stat_after = source.stat()
    generated_files: list[dict[str, Any]] = []
    for path in sorted(
        [output / "blocks.jsonl", output / "structure.yml", output / "media-map.yml",
         output / "normalization-log.yml"] + list((output / "media").iterdir()),
        key=lambda item: item.relative_to(output).as_posix(),
    ):
        generated_files.append({
            "path": path.relative_to(output).as_posix(),
            "byte_size": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    checksum_report = {
        "schema_version": 1,
        "source_id": source_id,
        "source": {
            "filename": source.name,
            "sha256_before": source_sha_before,
            "sha256_after": source_sha_after,
            "sha256_unchanged": source_sha_before == source_sha_after,
            "size_before": source_stat_before.st_size,
            "size_after": source_stat_after.st_size,
            "size_unchanged": source_stat_before.st_size == source_stat_after.st_size,
            "mtime_ns_before": source_stat_before.st_mtime_ns,
            "mtime_ns_after": source_stat_after.st_mtime_ns,
            "mtime_unchanged": source_stat_before.st_mtime_ns == source_stat_after.st_mtime_ns,
        },
        "generated_files": generated_files,
        "self_checksum": "excluded to avoid recursive checksum content",
    }
    write_yaml(output / "checksums.yml", checksum_report)

    if source_sha_before != source_sha_after:
        raise NormalizationError(
            "source checksum changed during normalization; outputs must not be trusted"
        )

    return {
        "source_id": source_id,
        "source_sha256": source_sha_before,
        "source_unchanged": True,
        "output_dir": str(output),
        "block_count": len(blocks),
        "heading_count": len(headings),
        "table_count": content_types["tables"],
        "image_occurrence_count": len(media_occurrences),
        "image_asset_count": len(media_assets),
        "manual_review_count": len(review_findings),
        "warning_count": len(warnings),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a deterministic, private normalization bundle from a DOCX. "
            "The source is opened read-only and the output directory must be new or empty."
        )
    )
    parser.add_argument("source_docx", type=Path, help="Path to the source DOCX (read-only)")
    parser.add_argument(
        "--source-id", required=True,
        help="Stable source_id used in block IDs and locators (normally from manifests/sources.yml)",
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path,
        help="Explicit new or empty directory for the normalization bundle",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = normalize_docx(args.source_docx, args.output_dir, args.source_id)
    except (NormalizationError, zipfile.BadZipFile, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
