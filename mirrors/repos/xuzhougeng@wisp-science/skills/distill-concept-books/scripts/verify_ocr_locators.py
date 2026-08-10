#!/usr/bin/env python3
"""Read-only integrity and locator verification for private OCR bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required; do not install it without approval.") from exc


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass
class Report:
    checked_ocr_evidence: int = 0
    verified_sources: int = 0
    errors: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, code: str, path: str, message: str) -> None:
        self.errors.append(Issue(code, path, message))

    def as_dict(self) -> dict[str, Any]:
        return {
            "checker_scope": "integrity-bound-ocr-locator-resolution",
            "truth_assessed": False,
            "ocr_correctness_assessed": False,
            "ok": self.ok,
            "checked_ocr_evidence": self.checked_ocr_evidence,
            "verified_sources": self.verified_sources,
            "errors": [item.as_dict() for item in self.errors],
        }


def _same_entry(before: os.stat_result, after: os.stat_result) -> bool:
    same_identity = (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
    )
    if not same_identity:
        return False
    if stat.S_ISDIR(before.st_mode):
        # Ancestor directory metadata can change when unrelated siblings are
        # created; inode and type preserve the no-follow path identity.
        return True
    return before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns


def _safe_file(path: Path) -> bytes:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    before: list[tuple[Path, os.stat_result]] = []
    for part in absolute.parts[1:]:
        current /= part
        item = current.lstat()
        if stat.S_ISLNK(item.st_mode):
            raise RuntimeError(f"symlink is forbidden: {current}")
        before.append((current, item))
    if not before or not stat.S_ISREG(before[-1][1].st_mode):
        raise RuntimeError(f"not an ordinary file: {absolute}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(absolute, flags)
    try:
        opened = os.fstat(fd)
        chunks = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(fd)
    finally:
        os.close(fd)
    if not _same_entry(before[-1][1], opened) or not _same_entry(opened, final):
        raise RuntimeError(f"file changed while reading: {absolute}")
    payload = b"".join(chunks)
    if len(payload) != final.st_size:
        raise RuntimeError(f"file length changed: {absolute}")
    for component, original in before:
        now = component.lstat()
        if stat.S_ISLNK(now.st_mode) or not _same_entry(original, now):
            raise RuntimeError(f"path changed while reading: {component}")
    return payload


def _load_yaml(path: Path) -> Mapping[str, Any]:
    value = yaml.safe_load(_safe_file(path).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("YAML root must be a mapping")
    return value


def _load_results(path: Path) -> list[Mapping[str, Any]]:
    results = []
    for number, line in enumerate(_safe_file(path).decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"result line {number} is not an object")
        results.append(value)
    return results


def _sha(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _normalize_text(value: str) -> str:
    return unicodedata.normalize(
        "NFC", value.replace("\r\n", "\n").replace("\r", "\n")
    )


def _canonical_relative(value: Any) -> str | None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\\" in value
        or "\x00" in value
    ):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        return None
    return value


def _project_root(manifest_path: Path) -> Path:
    return (
        manifest_path.parent.parent
        if manifest_path.parent.name == "manifests"
        else manifest_path.parent
    )


def _pdf_page_count(
    source: Path,
    *,
    runner=subprocess.run,
    which=shutil.which,
) -> int:
    if which("pdfinfo") is None:
        raise RuntimeError("PDF_RENDERER_UNAVAILABLE: pdfinfo is not installed")
    completed = runner(
        ["pdfinfo", str(source)],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "PDF_INPUT_INVALID: "
            + (completed.stderr.strip() or "pdfinfo failed")
        )
    match = re.search(r"(?m)^Pages:\s*([1-9][0-9]*)\s*$", completed.stdout)
    if match is None:
        raise RuntimeError("PDF_INPUT_INVALID: pdfinfo returned no positive page count")
    return int(match.group(1))


def _bundle_path(root: Path, source_id: str) -> Path:
    if not source_id or source_id != source_id.strip() or "/" in source_id or "\\" in source_id or source_id in {".", ".."}:
        raise RuntimeError(f"unsafe source ID {source_id!r}")
    direct = root / source_id
    return direct if direct.is_dir() else root


def verify(
    distillation_dir: Path | str,
    ocr_root: Path | str,
    sources_manifest: Path | str,
    normalized_root: Path | str | None = None,
    *,
    runner=subprocess.run,
    which=shutil.which,
) -> Report:
    """Recompute live source, bundle, coverage, image, text, region and locator bindings."""
    distillation = Path(distillation_dir)
    ocr_root = Path(ocr_root)
    manifest_path = Path(sources_manifest)
    normalized_root = Path(normalized_root) if normalized_root is not None else None
    report = Report()
    try:
        ledger = _load_yaml(distillation / "evidence-ledger.yml")
        manifest_document = _load_yaml(manifest_path)
    except Exception as exc:
        report.error("OCR_INPUT_INVALID", str(distillation), str(exc))
        return report

    raw_sources = manifest_document.get("sources")
    if not isinstance(raw_sources, list) or any(not isinstance(item, dict) for item in raw_sources):
        report.error("OCR_INPUT_INVALID", str(manifest_path), "sources must be a mapping list")
        return report
    sources: dict[str, Mapping[str, Any]] = {}
    for source in raw_sources:
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id or source_id in sources:
            report.error("OCR_INPUT_INVALID", str(manifest_path), "source IDs must be unique non-empty strings")
            return report
        sources[source_id] = source

    evidence = [
        item for item in ledger.get("evidence", [])
        if isinstance(item, dict)
        and isinstance(item.get("locator"), dict)
        and item["locator"].get("locator_type") == "ocr-region"
    ]
    by_source: dict[str, list[Mapping[str, Any]]] = {}
    for item in evidence:
        by_source.setdefault(str(item.get("source_id")), []).append(item)
    required_sources = {
        source_id for source_id, source in sources.items()
        if source.get("type") in {"book-docx", "book-pdf-scan"}
        and isinstance(source.get("ocr_policy"), dict)
        and source["ocr_policy"].get("required") is True
    }

    for source_id in sorted(set(by_source) | required_sources):
        source = sources.get(source_id)
        if source is None:
            report.error("OCR_SOURCE_UNKNOWN", source_id, "source is missing from manifest")
            continue
        source_errors_before = len(report.errors)
        bundle = _bundle_path(ocr_root, source_id)
        try:
            ocr_manifest = _load_yaml(bundle / "ocr-manifest.yml")
            checksums = _load_yaml(bundle / "checksums.yml")
            records = _load_results(bundle / "ocr-results.jsonl")
        except Exception as exc:
            report.error("OCR_BUNDLE_INVALID", str(bundle), str(exc))
            continue

        # The manifest path is project-relative; recompute the original bytes now.
        local_path = _canonical_relative(source.get("local_path"))
        source_path = None
        source_payload = None
        if local_path is not None:
            source_path = _project_root(manifest_path).joinpath(*PurePosixPath(local_path).parts)
            try:
                source_payload = _safe_file(source_path)
            except Exception as exc:
                report.error("OCR_SOURCE_READ_ERROR", str(source_path), str(exc))
        else:
            report.error("OCR_SOURCE_PATH_REQUIRED", source_id, "a canonical local_path is required")
        live_hash = _sha(source_payload) if source_payload is not None else None
        if (
            live_hash != source.get("checksum")
            or ocr_manifest.get("source_id") != source_id
            or ocr_manifest.get("source_sha256") != source.get("checksum")
            or checksums.get("source_id") != source_id
            or checksums.get("source_sha256") != source.get("checksum")
        ):
            report.error("OCR_SOURCE_CHECKSUM_MISMATCH", str(bundle), "live source and both bundle manifests must bind the same SHA-256")

        # Recompute every listed derivative and reject unlisted extra files.
        generated = checksums.get("generated_files")
        if not isinstance(generated, list):
            report.error("OCR_BUNDLE_INVALID", str(bundle / "checksums.yml"), "generated_files is required")
            continue
        recorded_paths: set[str] = set()
        for index, entry in enumerate(generated):
            relative = _canonical_relative(entry.get("path")) if isinstance(entry, dict) else None
            if relative is None or relative in recorded_paths:
                report.error("OCR_BUNDLE_INVALID", f"checksums.generated_files[{index}]", "invalid/duplicate generated path")
                continue
            recorded_paths.add(relative)
            try:
                payload = _safe_file(bundle.joinpath(*PurePosixPath(relative).parts))
            except Exception as exc:
                report.error("OCR_BUNDLE_INVALID", relative, str(exc))
                continue
            if _sha(payload) != entry.get("sha256") or len(payload) != entry.get("size"):
                report.error("OCR_BUNDLE_HASH_MISMATCH", relative, "generated file hash/size drift")
        actual_paths: set[str] = set()
        try:
            for path in bundle.rglob("*"):
                if path.is_symlink():
                    raise RuntimeError(f"symlink is forbidden: {path}")
                if path.is_file() and path.name != "checksums.yml":
                    actual_paths.add(path.relative_to(bundle).as_posix())
        except Exception as exc:
            report.error("OCR_BUNDLE_INVALID", str(bundle), str(exc))
        if actual_paths != recorded_paths or not {"ocr-manifest.yml", "ocr-results.jsonl"}.issubset(recorded_paths):
            report.error("OCR_BUNDLE_INVALID", str(bundle / "checksums.yml"), "generated file inventory is incomplete or contains extras")

        # Recompute record/image/text/region integrity before resolving locators.
        record_map: dict[str, Mapping[str, Any]] = {}
        item_map: dict[str, Mapping[str, Any]] = {}
        statuses = {"completed": 0, "empty": 0, "failed": 0}
        for index, record in enumerate(records):
            record_id = record.get("ocr_record_id")
            item_id = record.get("item_id")
            if (
                not isinstance(record_id, str) or not isinstance(item_id, str)
                or record_id in record_map or item_id in item_map
            ):
                report.error("OCR_BUNDLE_INVALID", f"ocr-results.jsonl[{index}]", "record/item IDs must be unique strings")
                continue
            record_map[record_id] = record
            item_map[item_id] = record
            status_value = record.get("status")
            if status_value not in statuses:
                report.error("OCR_BUNDLE_INVALID", record_id, "invalid status")
                continue
            statuses[status_value] += 1
            raw_text = record.get("raw_text")
            normalized_text = record.get("normalized_text")
            if (
                not isinstance(raw_text, str) or not isinstance(normalized_text, str)
                or record.get("raw_text_sha256") != _sha(str(raw_text).encode("utf-8"))
                or normalized_text != _normalize_text(raw_text)
                or record.get("text_sha256") != _sha(str(normalized_text).encode("utf-8"))
            ):
                report.error("OCR_TEXT_HASH_MISMATCH", record_id, "raw/normalized text or hash drift")
            image_path = _canonical_relative(record.get("image_path"))
            if image_path is None:
                if status_value != "failed" or record.get("image_sha256") is not None:
                    report.error("OCR_IMAGE_HASH_MISMATCH", record_id, "non-failed record has no bound image")
            else:
                try:
                    image_payload = _safe_file(bundle.joinpath(*PurePosixPath(image_path).parts))
                except Exception as exc:
                    report.error("OCR_IMAGE_HASH_MISMATCH", record_id, str(exc))
                else:
                    if _sha(image_payload) != record.get("image_sha256"):
                        report.error("OCR_IMAGE_HASH_MISMATCH", record_id, "image/page hash drift")
            regions = record.get("regions")
            if not isinstance(regions, list):
                report.error("OCR_BUNDLE_INVALID", record_id, "regions must be a list")
                continue
            region_ids: set[str] = set()
            for region_index, region in enumerate(regions):
                bbox = region.get("bbox_px") if isinstance(region, dict) else None
                region_id = region.get("region_id") if isinstance(region, dict) else None
                text_value = region.get("text") if isinstance(region, dict) else None
                if (
                    not isinstance(region_id, str) or region_id in region_ids
                    or not isinstance(bbox, list) or len(bbox) != 4
                    or any(not isinstance(value, int) or isinstance(value, bool) for value in bbox)
                    or bbox[0] < 0 or bbox[1] < 0 or bbox[2] < 1 or bbox[3] < 1
                    or not isinstance(text_value, str)
                    or region.get("text_sha256") != _sha(str(text_value).encode("utf-8"))
                    or not isinstance(region.get("confidence_raw"), str)
                ):
                    report.error("OCR_REGION_HASH_MISMATCH", f"{record_id}.regions[{region_index}]", "invalid bbox/text/confidence/hash")
                else:
                    region_ids.add(region_id)
            if status_value == "empty" and (regions or str(normalized_text).strip()):
                report.error("OCR_BUNDLE_INVALID", record_id, "empty record contains OCR output")
            if status_value == "failed" and not isinstance(record.get("error_code"), str):
                report.error("OCR_BUNDLE_INVALID", record_id, "failed record lacks stable error_code")

        coverage = ocr_manifest.get("coverage")
        recomputed = {"discovered_items": len(records), "attempted_items": len(records), **statuses}
        if (
            not isinstance(coverage, dict)
            or any(coverage.get(key) != value for key, value in recomputed.items())
            or coverage.get("unbound_occurrence_ids") != []
            or coverage.get("complete") is not True
            or ocr_manifest.get("status") != "completed"
            or statuses["failed"] != 0
        ):
            report.error("OCR_COVERAGE_INCOMPLETE", str(bundle / "ocr-manifest.yml"), "all images/pages must be accounted for without failures")

        binding = ocr_manifest.get("input_binding")
        if not isinstance(binding, dict):
            report.error("OCR_BUNDLE_INVALID", str(bundle / "ocr-manifest.yml"), "input_binding is required")
            binding = {}
        carrier = ocr_manifest.get("carrier")
        raw_policy = source.get("ocr_policy")
        policy = raw_policy if isinstance(raw_policy, dict) else {}
        engine = ocr_manifest.get("engine")
        if (
            not isinstance(raw_policy, dict)
            or not isinstance(engine, dict)
            or policy.get("required") is not True
            or policy.get("execution_mode") != "local-only"
            or policy.get("engine") != "tesseract"
            or engine.get("name") != "tesseract"
            or engine.get("languages") != policy.get("languages")
        ):
            report.error("OCR_SOURCE_POLICY_MISMATCH", source_id, "source and OCR engine/language policy drift")
        if source.get("type") == "book-docx":
            if carrier != "docx-image" or policy.get("coverage") != "all-images":
                report.error("OCR_BUNDLE_INVALID", source_id, "DOCX source requires docx-image carrier")
            if normalized_root is None:
                report.error("OCR_NORMALIZED_BUNDLE_REQUIRED", source_id, "DOCX verification requires --normalized-root")
            else:
                normalized_bundle = _bundle_path(normalized_root, source_id)
                try:
                    media_bytes = _safe_file(normalized_bundle / "media-map.yml")
                    normalized_checksum_bytes = _safe_file(normalized_bundle / "checksums.yml")
                    media_map = yaml.safe_load(media_bytes.decode("utf-8"))
                    normalized_checksums = yaml.safe_load(normalized_checksum_bytes.decode("utf-8"))
                    if not isinstance(media_map, dict) or not isinstance(normalized_checksums, dict):
                        raise RuntimeError("normalized YAML roots must be mappings")
                except Exception as exc:
                    report.error("OCR_NORMALIZED_BUNDLE_INVALID", str(normalized_bundle), str(exc))
                else:
                    normalized_source = normalized_checksums.get("source")
                    before = str(normalized_source.get("sha256_before") or "") if isinstance(normalized_source, dict) else ""
                    before = before if before.startswith("sha256:") else "sha256:" + before
                    if (
                        before != source.get("checksum")
                        or not isinstance(normalized_source, dict)
                        or normalized_source.get("sha256_unchanged") is not True
                        or binding.get("media_map_sha256") != _sha(media_bytes)
                        or binding.get("normalization_checksums_sha256") != _sha(normalized_checksum_bytes)
                    ):
                        report.error("OCR_NORMALIZED_BUNDLE_HASH_MISMATCH", str(normalized_bundle), "normalization/source binding drift")
                    assets = media_map.get("assets")
                    occurrences = media_map.get("occurrences")
                    if (
                        not isinstance(assets, list) or any(not isinstance(item, dict) for item in assets)
                        or not isinstance(occurrences, list) or any(not isinstance(item, dict) for item in occurrences)
                    ):
                        report.error("OCR_NORMALIZED_BUNDLE_INVALID", str(normalized_bundle), "assets/occurrences must be mapping lists")
                    else:
                        by_asset: dict[str, list[Mapping[str, Any]]] = {}
                        for occurrence in occurrences:
                            by_asset.setdefault(str(occurrence.get("asset_id")), []).append(occurrence)
                        expected_assets: set[str] = set()
                        expected_media_paths: set[str] = set()
                        for asset in assets:
                            asset_id = asset.get("asset_id")
                            relative = _canonical_relative(asset.get("extracted_path"))
                            if not isinstance(asset_id, str) or not asset_id or asset_id in expected_assets or relative is None:
                                report.error("OCR_NORMALIZED_BUNDLE_INVALID", source_id, "invalid/duplicate asset identity")
                                continue
                            expected_assets.add(asset_id)
                            expected_media_paths.add(relative)
                            record = item_map.get(asset_id)
                            if record is None:
                                report.error("OCR_COVERAGE_INCOMPLETE", asset_id, "normalized asset has no OCR record")
                                continue
                            try:
                                media_payload = _safe_file(normalized_bundle.joinpath(*PurePosixPath(relative).parts))
                            except Exception as exc:
                                report.error("OCR_IMAGE_HASH_MISMATCH", asset_id, str(exc))
                                continue
                            context = record.get("context") if isinstance(record.get("context"), dict) else {}
                            expected_occurrences = [str(item.get("occurrence_id")) for item in by_asset.get(asset_id, [])]
                            expected_figures = [str(item.get("figure_id")) for item in by_asset.get(asset_id, [])]
                            if (
                                record.get("image_sha256") != _sha(media_payload)
                                or context.get("media_occurrence_ids") != expected_occurrences
                                or context.get("figure_ids") != expected_figures
                            ):
                                report.error("OCR_COVERAGE_INCOMPLETE", asset_id, "media/occurrence binding drift")
                        if set(item_map) != expected_assets or coverage.get("occurrence_count") != len(occurrences):
                            report.error("OCR_COVERAGE_INCOMPLETE", source_id, "OCR asset/occurrence set differs from normalized media map")
                        normalized_generated = normalized_checksums.get("generated_files")
                        generated_media_paths = {
                            str(entry.get("path"))
                            for entry in normalized_generated
                            if isinstance(entry, dict)
                            and isinstance(entry.get("path"), str)
                            and str(entry.get("path")).startswith("media/")
                        } if isinstance(normalized_generated, list) else set()
                        if (
                            not isinstance(normalized_generated, list)
                            or expected_media_paths != generated_media_paths
                        ):
                            report.error(
                                "OCR_NORMALIZED_BUNDLE_INVALID",
                                source_id,
                                "normalized checksums/media-map asset coverage differs",
                            )
        elif source.get("type") == "book-pdf-scan":
            if (
                carrier != "pdf-page"
                or policy.get("coverage") != "all-pages"
                or policy.get("renderer") != "poppler-pdftoppm"
                or policy.get("dpi") != 300
            ):
                report.error("OCR_BUNDLE_INVALID", source_id, "scanned PDF requires pdf-page carrier")
            page_count = None
            if source_path is not None:
                try:
                    page_count = _pdf_page_count(source_path, runner=runner, which=which)
                except Exception as exc:
                    report.error("PDF_PAGE_COUNT_UNVERIFIED", str(source_path), str(exc))
            if page_count is not None:
                expected_pages = {f"page-{number:06d}" for number in range(1, page_count + 1)}
                renderer_contract = ocr_manifest.get("renderer")
                if (
                    set(item_map) != expected_pages
                    or binding.get("pdfinfo_page_count") != page_count
                    or not isinstance(renderer_contract, dict)
                    or renderer_contract.get("dpi") != 300
                    or renderer_contract.get("format") != "png"
                ):
                    report.error("OCR_COVERAGE_INCOMPLETE", source_id, "live PDF page set/300-DPI binding drift")
                for number in range(1, page_count + 1):
                    record = item_map.get(f"page-{number:06d}")
                    context = record.get("context") if isinstance(record, dict) and isinstance(record.get("context"), dict) else {}
                    if context.get("page_number") != number or context.get("dpi") != 300:
                        report.error("OCR_COVERAGE_INCOMPLETE", f"page-{number:06d}", "page identity/DPI drift")
        else:
            report.error("OCR_SOURCE_MANIFEST_INVALID", source_id, "unsupported OCR source type")

        for item in by_source.get(source_id, []):
            report.checked_ocr_evidence += 1
            locator = item["locator"]
            record = record_map.get(locator.get("ocr_record_id"))
            if record is None:
                report.error("OCR_LOCATOR_UNRESOLVED", str(item.get("evidence_id")), "OCR record does not exist")
                continue
            if (
                record.get("status") != "completed"
                or record.get("image_sha256") != locator.get("image_sha256")
                or locator.get("source_id") != source_id
                or locator.get("carrier") != carrier
                or locator.get("ocr_run_id") != ocr_manifest.get("ocr_run_id")
            ):
                report.error("OCR_LOCATOR_UNRESOLVED", str(item.get("evidence_id")), "record/source/run/carrier/image binding mismatch")
                continue
            context = record.get("context") if isinstance(record.get("context"), dict) else {}
            if carrier == "docx-image" and (
                locator.get("media_occurrence_id") not in context.get("media_occurrence_ids", [])
                or locator.get("figure_id") not in context.get("figure_ids", [])
            ):
                report.error("OCR_LOCATOR_UNRESOLVED", str(item.get("evidence_id")), "DOCX figure occurrence mismatch")
                continue
            if carrier == "pdf-page" and locator.get("page_number") != context.get("page_number"):
                report.error("OCR_LOCATOR_UNRESOLVED", str(item.get("evidence_id")), "PDF page mismatch")
                continue
            regions = {
                region.get("region_id"): region for region in record.get("regions", [])
                if isinstance(region, dict)
            }
            region = regions.get(locator.get("region_id"))
            normalized = item.get("normalized_text")
            expected_hash = hashlib.sha256(str(normalized).encode("utf-8")).hexdigest()
            locator_hash = str(locator.get("content_hash", "")).removeprefix("sha256:")
            if (
                region is None
                or region.get("bbox_px") != locator.get("bbox_px")
                or region.get("text") != normalized
                or region.get("text_sha256") != _sha(str(normalized).encode("utf-8"))
                or not locator_hash
                or not expected_hash.startswith(locator_hash)
            ):
                report.error("OCR_LOCATOR_UNRESOLVED", str(item.get("evidence_id")), "bbox/text/content hash mismatch")
        if len(report.errors) == source_errors_before:
            report.verified_sources += 1
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify private OCR bundle integrity and ocr-region evidence locators.")
    parser.add_argument("distillation_dir")
    parser.add_argument("ocr_root")
    parser.add_argument("--sources-manifest", required=True)
    parser.add_argument(
        "--normalized-root",
        help="Required for DOCX OCR: root containing the integrity-bound normalized bundle.",
    )
    args = parser.parse_args(argv)
    report = verify(
        args.distillation_dir,
        args.ocr_root,
        args.sources_manifest,
        args.normalized_root,
    )
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
