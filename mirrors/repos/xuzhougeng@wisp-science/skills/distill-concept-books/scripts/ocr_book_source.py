#!/usr/bin/env python3
"""Run local, provenance-recorded OCR over every DOCX image or scanned-PDF page.

The runner never installs dependencies, invokes a shell, uploads data, or
modifies the source.  Tesseract and (for PDF) Poppler must already be present.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required; do not install it without approval.") from exc


TOOL_NAME = "ocr_book_source"
TOOL_VERSION = "1.0.0"
DEFAULT_DPI = 300


class OCRRunError(RuntimeError):
    def __init__(self, code: str, message: str, summary: Mapping[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.summary = dict(summary or {})


@dataclass(frozen=True)
class OCRItem:
    item_id: str
    input_path: Path | None
    output_relative_path: str
    context: Mapping[str, Any]
    preflight_error_code: str | None = None
    preflight_error_message: str | None = None


SUPPORTED_IMAGE_SUFFIXES = {
    ".bmp", ".gif", ".jpeg", ".jpg", ".pbm", ".pgm", ".png", ".pnm",
    ".ppm", ".tif", ".tiff", ".webp",
}


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _load_yaml(path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise OCRRunError("OCR_INPUT_INVALID", f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OCRRunError("OCR_INPUT_INVALID", f"YAML root must be a mapping: {path}")
    return value


def _write_yaml(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )


def _prepare_output(path: Path) -> None:
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise OCRRunError(
            "OCR_OUTPUT_NOT_EMPTY", f"refusing to overwrite non-empty output: {path}"
        )
    path.mkdir(parents=True, exist_ok=True)


def _manifest_source(path: Path, source_id: str) -> Mapping[str, Any]:
    document = _load_yaml(path)
    matches = [
        item for item in document.get("sources", [])
        if isinstance(item, dict) and item.get("id") == source_id
    ]
    if len(matches) != 1:
        raise OCRRunError(
            "OCR_SOURCE_MANIFEST_INVALID",
            f"source_id {source_id!r} must resolve exactly once in {path}",
        )
    return matches[0]


def _validate_source_ocr_policy(
    source: Mapping[str, Any],
    *,
    carrier: str,
    languages: Sequence[str],
) -> None:
    expected_type = "book-docx" if carrier == "docx-image" else "book-pdf-scan"
    expected_coverage = "all-images" if carrier == "docx-image" else "all-pages"
    policy = source.get("ocr_policy")
    if source.get("type") != expected_type or not isinstance(policy, dict):
        raise OCRRunError(
            "OCR_SOURCE_MANIFEST_INVALID",
            f"source must be {expected_type} with an explicit ocr_policy",
        )
    declared_languages = policy.get("languages")
    if (
        policy.get("required") is not True
        or policy.get("coverage") != expected_coverage
        or policy.get("execution_mode") != "local-only"
        or policy.get("engine") != "tesseract"
        or not isinstance(declared_languages, list)
        or any(not isinstance(item, str) for item in declared_languages)
        or declared_languages != list(languages)
    ):
        raise OCRRunError(
            "OCR_SOURCE_POLICY_MISMATCH",
            "command languages and adapter settings must exactly match the explicit source ocr_policy",
        )
    if carrier == "pdf-page" and (
        policy.get("renderer") != "poppler-pdftoppm"
        or policy.get("dpi") != DEFAULT_DPI
    ):
        raise OCRRunError(
            "PDF_RENDER_CONTRACT_INVALID",
            "scanned PDF source policy must declare poppler-pdftoppm at 300 DPI",
        )


def _languages(value: str) -> list[str]:
    result = [item.strip() for item in value.split("+") if item.strip()]
    if not result or len(result) != len(set(result)) or any(
        not re.fullmatch(r"[A-Za-z0-9_]+", item) for item in result
    ):
        raise OCRRunError("OCR_LANGUAGE_INVALID", "languages must be unique Tesseract IDs joined by +")
    return result


def _run(
    args: Sequence[str],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            list(args),
            check=False,
            capture_output=True,
            text=True,
            shell=False,
        )
    except OSError as exc:
        raise OCRRunError("OCR_SUBPROCESS_FAILED", f"cannot execute {args[0]}: {exc}") from exc


def preflight_tools(
    languages: Sequence[str],
    *,
    pdf: bool,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    required = ["tesseract"] + (["pdfinfo", "pdftoppm"] if pdf else [])
    missing = [name for name in required if which(name) is None]
    if missing:
        code = "PDF_RENDERER_UNAVAILABLE" if any(x in missing for x in ("pdfinfo", "pdftoppm")) else "OCR_ENGINE_UNAVAILABLE"
        raise OCRRunError(code, f"required local executable(s) missing: {', '.join(missing)}")
    version = _run(["tesseract", "--version"], runner=runner)
    if version.returncode != 0:
        raise OCRRunError("OCR_ENGINE_UNAVAILABLE", version.stderr.strip() or "tesseract --version failed")
    listed = _run(["tesseract", "--list-langs"], runner=runner)
    if listed.returncode != 0:
        raise OCRRunError("OCR_ENGINE_UNAVAILABLE", listed.stderr.strip() or "tesseract --list-langs failed")
    installed = {
        line.strip() for line in listed.stdout.splitlines()
        if line.strip() and not line.lower().startswith("list of available")
    }
    absent = sorted(set(languages) - installed)
    if absent:
        raise OCRRunError("OCR_LANGUAGE_MISSING", f"Tesseract language packs missing: {', '.join(absent)}")
    result: dict[str, Any] = {
        "tesseract_version": version.stdout.splitlines()[0].strip(),
        "installed_languages": sorted(installed),
    }
    if pdf:
        poppler = _run(["pdftoppm", "-v"], runner=runner)
        if poppler.returncode not in {0, 1}:
            raise OCRRunError("PDF_RENDERER_UNAVAILABLE", poppler.stderr.strip() or "pdftoppm -v failed")
        pdfinfo = _run(["pdfinfo", "-v"], runner=runner)
        if pdfinfo.returncode not in {0, 1}:
            raise OCRRunError("PDF_RENDERER_UNAVAILABLE", pdfinfo.stderr.strip() or "pdfinfo -v failed")
        result["poppler_version"] = (poppler.stderr or poppler.stdout).splitlines()[0].strip()
        result["pdfinfo_version"] = (pdfinfo.stderr or pdfinfo.stdout).splitlines()[0].strip()
    return result


def _normalize_ocr_text(value: str) -> str:
    """Apply only the contract-permitted NFC and newline normalization."""
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))


def _parse_tsv(tsv: str, record_id: str) -> tuple[str, list[dict[str, Any]]]:
    reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    words: list[tuple[tuple[str, str, str, str], str]] = []
    regions: list[dict[str, Any]] = []
    for row in reader:
        text = _normalize_ocr_text(str(row.get("text") or ""))
        if not text.strip():
            continue
        try:
            left = int(row["left"]); top = int(row["top"])
            width = int(row["width"]); height = int(row["height"])
            confidence = float(row["conf"])
        except (KeyError, TypeError, ValueError) as exc:
            raise OCRRunError("OCR_OUTPUT_INVALID", f"invalid Tesseract TSV row: {exc}") from exc
        if width < 1 or height < 1:
            continue
        region_id = f"{record_id}-region-{len(regions) + 1:06d}"
        regions.append({
            "region_id": region_id,
            "bbox_px": [left, top, width, height],
            "text": text,
            "text_sha256": sha256_bytes(text.encode("utf-8")),
            "confidence": confidence,
            "confidence_raw": str(row.get("conf")),
        })
        line_key = (
            str(row.get("page_num")), str(row.get("block_num")),
            str(row.get("par_num")), str(row.get("line_num")),
        )
        words.append((line_key, text))
    lines: list[str] = []
    last_key = None
    for key, word in words:
        if key != last_key:
            lines.append(word)
            last_key = key
        else:
            lines[-1] += " " + word
    return _normalize_ocr_text("\n".join(lines)), regions


def _ocr_item(
    item: OCRItem,
    *,
    output_root: Path,
    languages: Sequence[str],
    psm: int,
    runner: Callable[..., subprocess.CompletedProcess[str]],
    record_number: int,
) -> dict[str, Any]:
    record_id = f"ocr-record-{record_number:06d}"
    destination = output_root.joinpath(*PurePosixPath(item.output_relative_path).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload: bytes | None = None
    if item.input_path is not None and item.input_path.is_file():
        payload = item.input_path.read_bytes()
        if item.input_path != destination:
            destination.write_bytes(payload)
    image_hash = sha256_bytes(payload) if payload is not None else None
    base = {
        "ocr_record_id": record_id,
        "item_id": item.item_id,
        "image_path": item.output_relative_path if payload is not None else None,
        "image_sha256": image_hash,
        "context": dict(item.context),
    }
    if item.preflight_error_code is not None:
        return {
            **base,
            "status": "failed",
            "error_code": item.preflight_error_code,
            "error": item.preflight_error_message,
            "raw_text": "",
            "raw_text_sha256": sha256_bytes(b""),
            "normalized_text": "",
            "text_sha256": sha256_bytes(b""),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    if payload is None:
        return {
            **base,
            "status": "failed",
            "error_code": "OCR_IMAGE_UNREADABLE",
            "error": "image/page bytes are unavailable or unreadable",
            "raw_text": "",
            "raw_text_sha256": sha256_bytes(b""),
            "normalized_text": "",
            "text_sha256": sha256_bytes(b""),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    if destination.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        return {
            **base,
            "status": "failed",
            "error_code": "OCR_IMAGE_FORMAT_UNSUPPORTED",
            "error": f"unsupported local OCR image format: {destination.suffix or '<none>'}",
            "raw_text": "",
            "raw_text_sha256": sha256_bytes(b""),
            "normalized_text": "",
            "text_sha256": sha256_bytes(b""),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    plain = _run(
        [
            "tesseract", str(destination), "stdout", "-l", "+".join(languages),
            "--psm", str(psm),
        ],
        runner=runner,
    )
    if plain.returncode != 0:
        return {
            **base,
            "status": "failed",
            "error_code": "OCR_IMAGE_UNREADABLE",
            "error": plain.stderr.strip() or f"Tesseract text extraction exited {plain.returncode}",
            "raw_text": "",
            "raw_text_sha256": sha256_bytes(b""),
            "normalized_text": "",
            "text_sha256": sha256_bytes(b""),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    completed = _run(
        [
            "tesseract", str(destination), "stdout", "-l", "+".join(languages),
            "--psm", str(psm), "tsv",
        ],
        runner=runner,
    )
    if completed.returncode != 0:
        return {
            **base,
            "status": "failed",
            "error_code": "OCR_TSV_UNAVAILABLE",
            "error": completed.stderr.strip() or f"Tesseract TSV extraction exited {completed.returncode}",
            "raw_text": plain.stdout,
            "raw_text_sha256": sha256_bytes(plain.stdout.encode("utf-8")),
            "normalized_text": _normalize_ocr_text(plain.stdout),
            "text_sha256": sha256_bytes(_normalize_ocr_text(plain.stdout).encode("utf-8")),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    try:
        _tsv_text, regions = _parse_tsv(completed.stdout, record_id)
    except OCRRunError as exc:
        return {
            **base,
            "status": "failed", "error_code": exc.code, "error": exc.message,
            "raw_text": plain.stdout,
            "raw_text_sha256": sha256_bytes(plain.stdout.encode("utf-8")),
            "normalized_text": _normalize_ocr_text(plain.stdout),
            "text_sha256": sha256_bytes(_normalize_ocr_text(plain.stdout).encode("utf-8")),
            "regions": [],
            "quality_flags": ["ocr-failed", "ocr-unreviewed"],
        }
    raw_text = plain.stdout
    normalized_text = _normalize_ocr_text(raw_text)
    status = "completed" if regions or normalized_text.strip() else "empty"
    flags = ["ocr-unreviewed"] + (["ocr-empty"] if status == "empty" else [])
    return {
        **base,
        "status": status,
        "error_code": None,
        "error": None,
        "raw_text": raw_text,
        "raw_text_sha256": sha256_bytes(raw_text.encode("utf-8")),
        "normalized_text": normalized_text,
        "text_sha256": sha256_bytes(normalized_text.encode("utf-8")),
        "regions": regions,
        "quality_flags": flags,
    }


def _write_bundle(
    output: Path,
    *,
    source_id: str,
    carrier: str,
    source_hash: str,
    languages: Sequence[str],
    psm: int,
    tool_info: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    occurrence_count: int,
    unbound_occurrences: Sequence[str],
    renderer: Mapping[str, Any] | None,
    input_binding: Mapping[str, Any],
) -> dict[str, Any]:
    results_path = output / "ocr-results.jsonl"
    with results_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    counts = {status: sum(item.get("status") == status for item in records) for status in ("completed", "empty", "failed")}
    complete = counts["failed"] == 0 and not unbound_occurrences
    manifest = {
        "schema_version": 1,
        "ocr_run_id": f"ocr-{source_id}-v1",
        "source_id": source_id,
        "carrier": carrier,
        "source_sha256": source_hash,
        "input_binding": dict(input_binding),
        "scope": "all-images" if carrier == "docx-image" else "all-pages",
        "execution_mode": "local-only",
        "runner": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "engine": {
            "name": "tesseract", "version": tool_info.get("tesseract_version"),
            "languages": list(languages), "page_segmentation_mode": psm,
        },
        "renderer": dict(renderer) if renderer else None,
        "coverage": {
            "discovered_items": len(records), "attempted_items": len(records),
            **counts, "occurrence_count": occurrence_count,
            "unbound_occurrence_ids": list(unbound_occurrences),
            "complete": complete,
        },
        "status": "completed" if complete else "blocked",
        "limitations": [
            "OCR captures visible text only; it does not infer arrows, diagram relations, formula semantics, or factual truth.",
            "Every OCR-derived evidence item remains ocr-unreviewed until explicit human review.",
        ],
    }
    _write_yaml(output / "ocr-manifest.yml", manifest)
    generated = []
    for path in sorted(p for p in output.rglob("*") if p.is_file() and p.name != "checksums.yml"):
        generated.append({
            "path": path.relative_to(output).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    _write_yaml(output / "checksums.yml", {
        "schema_version": 1, "source_id": source_id,
        "source_sha256": source_hash, "generated_files": generated,
    })
    return manifest


def _normalized_sha256(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    candidate = value if value.startswith("sha256:") else "sha256:" + value
    return candidate if re.fullmatch(r"sha256:[0-9a-f]{64}", candidate) else None


def _canonical_bundle_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        return None
    return value


def _verify_normalized_bundle(
    bundle: Path,
    *,
    source_id: str,
    manifest_checksum: Any,
) -> tuple[Mapping[str, Any], str, dict[str, Any], set[str]]:
    for required in ("media-map.yml", "checksums.yml"):
        path = bundle / required
        if not path.is_file() or path.is_symlink():
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                f"verified normalized bundle file is missing or unsafe: {path}",
            )
    media_map = _load_yaml(bundle / "media-map.yml")
    checksums = _load_yaml(bundle / "checksums.yml")
    source = checksums.get("source")
    before = _normalized_sha256(source.get("sha256_before")) if isinstance(source, dict) else None
    after = _normalized_sha256(source.get("sha256_after")) if isinstance(source, dict) else None
    expected_source = _normalized_sha256(manifest_checksum)
    if (
        checksums.get("source_id") != source_id
        or media_map.get("source_id") != source_id
        or not isinstance(source, dict)
        or source.get("sha256_unchanged") is not True
        or before is None
        or before != after
        or before != expected_source
    ):
        raise OCRRunError(
            "OCR_SOURCE_CHECKSUM_MISMATCH",
            "normalized bundle source identity/checksum does not match the source manifest",
        )
    generated = checksums.get("generated_files")
    if not isinstance(generated, list):
        raise OCRRunError(
            "OCR_NORMALIZED_BUNDLE_INVALID",
            "normalized checksums.yml requires generated_files",
        )
    recorded: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(generated):
        if not isinstance(entry, dict):
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                f"generated_files[{index}] must be a mapping",
            )
        relative = _canonical_bundle_path(entry.get("path"))
        if relative is None or relative in recorded:
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                f"invalid/duplicate normalized generated path at index {index}",
            )
        path = bundle.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file() or path.is_symlink():
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                f"normalized generated file is missing or unsafe: {relative}",
            )
        actual_hash = sha256_file(path)
        expected_hash = _normalized_sha256(entry.get("sha256"))
        if expected_hash != actual_hash or entry.get("byte_size") != path.stat().st_size:
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_HASH_MISMATCH",
                f"normalized generated file drift: {relative}",
            )
        recorded[relative] = dict(entry)
    if "media-map.yml" not in recorded:
        raise OCRRunError(
            "OCR_NORMALIZED_BUNDLE_INVALID",
            "normalized bundle does not integrity-bind media-map.yml",
        )
    return media_map, before, {
        "normalization_checksums_sha256": sha256_file(bundle / "checksums.yml"),
        "media_map_sha256": sha256_file(bundle / "media-map.yml"),
    }, set(recorded)


def run_docx_bundle(
    bundle: Path | str,
    output_dir: Path | str,
    *,
    source_id: str,
    sources_manifest: Path | str,
    languages: Sequence[str],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    bundle = Path(bundle); output = Path(output_dir)
    source = _manifest_source(Path(sources_manifest), source_id)
    _validate_source_ocr_policy(
        source, carrier="docx-image", languages=languages
    )
    media_map, source_hash, input_binding, normalized_paths = _verify_normalized_bundle(
        bundle, source_id=source_id, manifest_checksum=source.get("checksum")
    )
    tool_info = preflight_tools(languages, pdf=False, runner=runner, which=which)
    raw_assets = media_map.get("assets")
    raw_occurrences = media_map.get("occurrences")
    if (
        not isinstance(raw_assets, list)
        or any(not isinstance(item, dict) for item in raw_assets)
        or not isinstance(raw_occurrences, list)
        or any(not isinstance(item, dict) for item in raw_occurrences)
    ):
        raise OCRRunError(
            "OCR_NORMALIZED_BUNDLE_INVALID",
            "media-map assets/occurrences must be complete mapping lists",
        )
    assets = list(raw_assets)
    occurrences = list(raw_occurrences)
    asset_occurrences: dict[str, list[Mapping[str, Any]]] = {}
    unbound: list[str] = []
    seen_occurrence_ids: set[str] = set()
    for occurrence in occurrences:
        asset_id = occurrence.get("asset_id")
        occurrence_id = occurrence.get("occurrence_id")
        if (
            not isinstance(occurrence_id, str)
            or not occurrence_id
            or occurrence_id in seen_occurrence_ids
        ):
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                "every media occurrence requires a unique stable occurrence_id",
            )
        seen_occurrence_ids.add(occurrence_id)
        if not isinstance(asset_id, str) or not asset_id:
            unbound.append(occurrence_id)
        else:
            asset_occurrences.setdefault(asset_id, []).append(occurrence)
    items: list[OCRItem] = []
    seen_asset_ids: set[str] = set()
    declared_media_paths: set[str] = set()
    for asset in assets:
        asset_id = asset.get("asset_id")
        relative = asset.get("extracted_path")
        canonical_relative = _canonical_bundle_path(relative)
        if (
            not isinstance(asset_id, str)
            or not asset_id
            or asset_id in seen_asset_ids
            or canonical_relative is None
        ):
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                "every media asset requires a unique ID and canonical extracted_path",
            )
        seen_asset_ids.add(asset_id)
        declared_media_paths.add(canonical_relative)
        input_path = bundle.joinpath(*PurePosixPath(canonical_relative).parts)
        if canonical_relative not in normalized_paths:
            raise OCRRunError(
                "OCR_NORMALIZED_BUNDLE_INVALID",
                f"media asset is not integrity-bound by normalized checksums: {canonical_relative}",
            )
        if not input_path.is_file() or input_path.is_symlink():
            unbound.extend(str(item.get("occurrence_id")) for item in asset_occurrences.get(asset_id, []))
            items.append(OCRItem(
                asset_id, None, f"images/{asset_id}{input_path.suffix.lower() or '.bin'}",
                {
                    "figure_ids": [str(item.get("figure_id")) for item in asset_occurrences.get(asset_id, [])],
                    "media_occurrence_ids": [str(item.get("occurrence_id")) for item in asset_occurrences.get(asset_id, [])],
                },
                "OCR_IMAGE_UNREADABLE",
                f"normalized media file is missing or unsafe: {canonical_relative}",
            ))
            continue
        expected = _normalized_sha256(asset.get("sha256_extracted"))
        if sha256_file(input_path) != expected:
            raise OCRRunError("OCR_IMAGE_HASH_MISMATCH", f"media hash drift: {canonical_relative}")
        suffix = input_path.suffix.lower() or ".bin"
        items.append(OCRItem(
            asset_id, input_path, f"images/{asset_id}{suffix}",
            {
                "figure_ids": [str(item.get("figure_id")) for item in asset_occurrences.get(asset_id, [])],
                "media_occurrence_ids": [str(item.get("occurrence_id")) for item in asset_occurrences.get(asset_id, [])],
            },
        ))
    unknown_asset_ids = set(asset_occurrences) - seen_asset_ids
    for asset_id in sorted(unknown_asset_ids):
        unbound.extend(
            str(item.get("occurrence_id"))
            for item in asset_occurrences.get(asset_id, [])
        )
    integrity_bound_media_paths = {
        path for path in normalized_paths if path.startswith("media/")
    }
    if declared_media_paths != integrity_bound_media_paths:
        raise OCRRunError(
            "OCR_NORMALIZED_BUNDLE_INVALID",
            "media-map assets must exactly cover every integrity-bound extracted media file",
        )
    input_binding = {
        **input_binding,
        "normalized_bundle_source_id": source_id,
        "normalized_asset_count": len(assets),
        "normalized_occurrence_count": len(occurrences),
    }
    _prepare_output(output)
    records = [
        _ocr_item(item, output_root=output, languages=languages, psm=11, runner=runner, record_number=index)
        for index, item in enumerate(items, 1)
    ]
    manifest = _write_bundle(
        output, source_id=source_id, carrier="docx-image", source_hash=source_hash,
        languages=languages, psm=11, tool_info=tool_info, records=records,
        occurrence_count=len(occurrences), unbound_occurrences=unbound, renderer=None,
        input_binding=input_binding,
    )
    if manifest["status"] != "completed":
        raise OCRRunError("OCR_COVERAGE_INCOMPLETE", "one or more DOCX images could not be OCR-scanned", manifest)
    return manifest


def _pdf_pages(
    source: Path,
    output: Path,
    *,
    dpi: int,
    runner: Callable[..., subprocess.CompletedProcess[str]],
) -> tuple[list[OCRItem], int]:
    info = _run(["pdfinfo", str(source)], runner=runner)
    if info.returncode != 0:
        raise OCRRunError("PDF_INPUT_INVALID", info.stderr.strip() or "pdfinfo failed")
    match = re.search(r"(?m)^Pages:\s*([1-9][0-9]*)\s*$", info.stdout)
    if match is None:
        raise OCRRunError("PDF_INPUT_INVALID", "pdfinfo did not report a positive page count")
    page_count = int(match.group(1))
    pages_dir = output / "pages"; pages_dir.mkdir(parents=True)
    items: list[OCRItem] = []
    for page_number in range(1, page_count + 1):
        stem = pages_dir / f"page-{page_number:06d}"
        rendered = _run([
            "pdftoppm", "-f", str(page_number), "-l", str(page_number),
            "-singlefile", "-r", str(dpi), "-png", str(source), str(stem),
        ], runner=runner)
        page_path = stem.with_suffix(".png")
        if rendered.returncode != 0 or not page_path.is_file():
            items.append(OCRItem(
                f"page-{page_number:06d}",
                page_path if page_path.is_file() and not page_path.is_symlink() else None,
                f"pages/page-{page_number:06d}.png",
                {"page_number": page_number, "dpi": dpi},
                "PDF_RENDER_FAILED",
                rendered.stderr.strip() or f"page {page_number} was not rendered",
            ))
            continue
        items.append(OCRItem(
            f"page-{page_number:06d}", page_path,
            f"pages/page-{page_number:06d}.png",
            {"page_number": page_number, "dpi": dpi},
        ))
    return items, page_count


def run_scanned_pdf(
    source_path: Path | str,
    output_dir: Path | str,
    *,
    source_id: str,
    sources_manifest: Path | str,
    languages: Sequence[str],
    dpi: int = DEFAULT_DPI,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    if dpi != DEFAULT_DPI:
        raise OCRRunError("PDF_RENDER_CONTRACT_INVALID", f"scanned PDF rendering is fixed at {DEFAULT_DPI} DPI")
    source_path = Path(source_path); output = Path(output_dir)
    source = _manifest_source(Path(sources_manifest), source_id)
    _validate_source_ocr_policy(source, carrier="pdf-page", languages=languages)
    tool_info = preflight_tools(languages, pdf=True, runner=runner, which=which)
    before = sha256_file(source_path)
    if before != source.get("checksum"):
        raise OCRRunError("OCR_SOURCE_CHECKSUM_MISMATCH", "PDF bytes do not match the sources manifest")
    _prepare_output(output)
    items, page_count = _pdf_pages(source_path, output, dpi=dpi, runner=runner)
    records = [
        _ocr_item(item, output_root=output, languages=languages, psm=3, runner=runner, record_number=index)
        for index, item in enumerate(items, 1)
    ]
    after = sha256_file(source_path)
    if before != after:
        raise OCRRunError("OCR_SOURCE_CHANGED", "PDF changed during OCR")
    manifest = _write_bundle(
        output, source_id=source_id, carrier="pdf-page", source_hash=before,
        languages=languages, psm=3, tool_info=tool_info, records=records,
        occurrence_count=len(items), unbound_occurrences=[],
        renderer={
            "name": "poppler-pdftoppm",
            "pdftoppm_version": tool_info.get("poppler_version"),
            "pdfinfo_version": tool_info.get("pdfinfo_version"),
            "dpi": dpi,
            "format": "png",
        },
        input_binding={"pdfinfo_page_count": page_count},
    )
    if manifest["status"] != "completed":
        raise OCRRunError("OCR_COVERAGE_INCOMPLETE", "one or more PDF pages failed OCR", manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local OCR over all DOCX images or scanned-PDF pages.")
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("docx-bundle", "scanned-pdf"):
        item = sub.add_parser(name)
        item.add_argument("input")
        item.add_argument("--source-id", required=True)
        item.add_argument("--sources-manifest", required=True)
        item.add_argument("--output-dir", required=True)
        item.add_argument("--languages", required=True, help="Explicit Tesseract IDs, e.g. chi_sim+eng")
    args = parser.parse_args(argv)
    try:
        languages = _languages(args.languages)
        if args.mode == "docx-bundle":
            summary = run_docx_bundle(
                args.input, args.output_dir, source_id=args.source_id,
                sources_manifest=args.sources_manifest, languages=languages,
            )
        else:
            summary = run_scanned_pdf(
                args.input, args.output_dir, source_id=args.source_id,
                sources_manifest=args.sources_manifest, languages=languages,
            )
    except OCRRunError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "message": exc.message, "summary": exc.summary}, ensure_ascii=False, indent=2))
        return 2
    except (OSError, UnicodeError) as exc:
        print(json.dumps({
            "ok": False,
            "code": "OCR_IO_ERROR",
            "message": str(exc),
            "summary": {},
        }, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps({"ok": True, "summary": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
