#!/usr/bin/env python3
"""Resolve OOXML evidence locators against integrity-bound DOCX bundles.

The checker is read-only. It rejects self-asserted or drifted normalization
bundles, binds their recorded source checksum to the explicit source manifest,
and then verifies each OOXML locator and inline excerpt. It does not judge
whether a source statement is true.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Do not install it without the user's approval."
    ) from exc


FULL_SHA256_RE = re.compile(r"^(?:sha256:)?(?P<digest>[0-9a-fA-F]{64})$")
REQUIRED_GENERATED_FILES = {
    "blocks.jsonl",
    "structure.yml",
    "media-map.yml",
    "normalization-log.yml",
}


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate mapping key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass
class Report:
    distillation_dir: str
    normalized_root: str
    sources_manifest: str
    checked: int = 0
    skipped: int = 0
    integrity_verified_sources: int = 0
    manifest_checksum_verified_sources: int = 0
    errors: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, code: str, path: str, message: str) -> None:
        self.errors.append(Issue(code, path, message))

    def as_dict(self) -> dict[str, Any]:
        return {
            "checker_scope": "integrity-bound-normalized-locator-resolution",
            "truth_assessed": False,
            "ok": self.ok,
            "distillation_dir": self.distillation_dir,
            "normalized_root": self.normalized_root,
            "sources_manifest": self.sources_manifest,
            "checked_ooxml_evidence": self.checked,
            "skipped_non_ooxml_evidence": self.skipped,
            "integrity_verified_sources": self.integrity_verified_sources,
            "manifest_checksum_verified_sources": self.manifest_checksum_verified_sources,
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
        return True
    return before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns


def _read_stable_regular_file(path: Path) -> bytes:
    """Read one ordinary file without following symlinks or accepting drift."""
    absolute = Path(os.path.abspath(path))
    components: list[tuple[Path, os.stat_result]] = []
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            entry_stat = current.lstat()
        except OSError as exc:
            raise RuntimeError(f"cannot inspect {current}: {exc}") from exc
        if stat.S_ISLNK(entry_stat.st_mode):
            raise RuntimeError(f"symlink path component is forbidden: {current}")
        components.append((current, entry_stat))
    if not components or not stat.S_ISREG(components[-1][1].st_mode):
        raise RuntimeError(f"path is not an ordinary file: {absolute}")

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as exc:
        raise RuntimeError(f"cannot open ordinary file safely: {absolute}: {exc}") from exc
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode) or not _same_entry(
            components[-1][1], opened_stat
        ):
            raise RuntimeError(f"file changed before reading: {absolute}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    content = b"".join(chunks)
    if not _same_entry(opened_stat, final_stat) or len(content) != final_stat.st_size:
        raise RuntimeError(f"file changed while reading: {absolute}")
    for component, original_stat in components:
        try:
            current_stat = component.lstat()
        except OSError as exc:
            raise RuntimeError(f"path changed after reading: {component}: {exc}") from exc
        if stat.S_ISLNK(current_stat.st_mode) or not _same_entry(
            original_stat, current_stat
        ):
            raise RuntimeError(f"path changed while reading: {component}")
    return content


def _load_yaml(path: Path) -> Mapping[str, Any]:
    try:
        content = _read_stable_regular_file(path)
        data = yaml.load(content.decode("utf-8"), Loader=_UniqueKeySafeLoader)
    except (UnicodeError, yaml.YAMLError, RecursionError, RuntimeError) as exc:
        raise RuntimeError(f"cannot load YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"YAML root must be a mapping: {path}")
    return data


def _load_json_object_strict(line: str, path: Path, line_number: int) -> Mapping[str, Any]:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"non-JSON numeric constant {value!r}")

    try:
        record = json.loads(
            line, object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise RuntimeError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
    if not isinstance(record, dict):
        raise RuntimeError(f"block must be a mapping at {path}:{line_number}")
    return record


def _normalized_sha256(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = FULL_SHA256_RE.fullmatch(value)
    return None if match is None else match.group("digest").lower()


def _canonical_bundle_path(value: Any) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RuntimeError("bundle path must be a non-empty canonical string")
    if "\\" in value or "\x00" in value:
        raise RuntimeError("bundle path must use POSIX separators and contain no NUL")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RuntimeError("bundle path contains an empty, '.' or '..' component")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise RuntimeError("bundle path must be canonical and relative")
    return value


def _load_sources_manifest(path: Path) -> dict[str, Mapping[str, Any]]:
    document = _load_yaml(path)
    records = document.get("sources")
    if not isinstance(records, list):
        raise RuntimeError("sources manifest must contain a sources list")
    result = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise RuntimeError(f"sources[{index}] must be a mapping")
        source_id = record.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise RuntimeError(f"sources[{index}].id must be a non-empty string")
        if source_id in result:
            raise RuntimeError(f"duplicate source ID in manifest: {source_id!r}")
        result[source_id] = record
    return result


def _bundle_dir(normalized_root: Path, source_id: str) -> Path:
    if (
        not source_id
        or source_id != source_id.strip()
        or "\\" in source_id
        or "/" in source_id
        or source_id in {".", ".."}
    ):
        raise RuntimeError(f"unsafe source_id for normalized bundle lookup: {source_id!r}")
    direct = normalized_root / source_id
    if direct.is_dir():
        return direct
    if normalized_root.name == source_id and normalized_root.is_dir():
        return normalized_root
    return direct


def _load_blocks(bundle: Path, source_id: str) -> dict[int, Mapping[str, Any]]:
    blocks_path = bundle / "blocks.jsonl"
    try:
        content = _read_stable_regular_file(blocks_path).decode("utf-8")
    except (UnicodeError, RuntimeError) as exc:
        raise RuntimeError(f"cannot read blocks.jsonl for {source_id}: {exc}") from exc
    blocks = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        record = _load_json_object_strict(line, blocks_path, line_number)
        if record.get("source_id") != source_id:
            raise RuntimeError(
                f"source_id mismatch at {blocks_path}:{line_number}: {record.get('source_id')!r}"
            )
        index = record.get("ooxml_block_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 1:
            raise RuntimeError(f"invalid block index at {blocks_path}:{line_number}")
        if index in blocks:
            raise RuntimeError(f"duplicate block index {index} in {blocks_path}")
        normalized_text = record.get("normalized_text")
        if not isinstance(normalized_text, str):
            raise RuntimeError(f"normalized_text must be a string at {blocks_path}:{line_number}")
        full_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        short_hash = full_hash[:12]
        locator = record.get("locator")
        if (
            record.get("text_sha256") != full_hash
            or record.get("short_content_hash") != short_hash
            or not isinstance(locator, dict)
            or locator.get("content_hash") != short_hash
        ):
            raise RuntimeError(
                f"block content hashes do not match normalized_text at {blocks_path}:{line_number}"
            )
        blocks[index] = record
    return blocks


def _verify_bundle_integrity(report, bundle, source_id, manifest_source):
    checksums_path = bundle / "checksums.yml"
    try:
        checksums = _load_yaml(checksums_path)
    except Exception as exc:
        report.error("BUNDLE_CHECKSUMS", str(checksums_path), str(exc))
        return False
    if checksums.get("source_id") != source_id:
        report.error(
            "BUNDLE_SOURCE_MISMATCH",
            str(checksums_path),
            "checksums source_id does not match evidence source_id",
        )
        return False

    source = checksums.get("source")
    before = _normalized_sha256(source.get("sha256_before")) if isinstance(source, dict) else None
    after = _normalized_sha256(source.get("sha256_after")) if isinstance(source, dict) else None
    manifest_checksum = _normalized_sha256(manifest_source.get("checksum"))
    integrity_ok = True
    if (
        not isinstance(source, dict)
        or source.get("sha256_unchanged") is not True
        or before is None
        or after is None
        or before != after
    ):
        report.error(
            "SOURCE_CHECKSUM_CHANGED",
            str(checksums_path),
            "normalization report must contain equal complete before/after source SHA-256 values",
        )
        integrity_ok = False
    if manifest_checksum is None:
        report.error(
            "MANIFEST_SOURCE_CHECKSUM_MISSING",
            str(checksums_path),
            "manifest source checksum must be a complete SHA-256",
        )
        integrity_ok = False
    elif before is not None and manifest_checksum != before:
        report.error(
            "MANIFEST_SOURCE_CHECKSUM_MISMATCH",
            str(checksums_path),
            "normalization source checksum does not match the explicit source manifest",
        )
        integrity_ok = False
    else:
        report.manifest_checksum_verified_sources += 1

    generated_files = checksums.get("generated_files")
    if not isinstance(generated_files, list):
        report.error(
            "BUNDLE_GENERATED_FILES_INVALID",
            str(checksums_path),
            "checksums.yml must contain a generated_files list",
        )
        return False
    recorded_paths = set()
    for index, record in enumerate(generated_files):
        entry_path = f"{checksums_path}.generated_files[{index}]"
        if not isinstance(record, dict):
            report.error("BUNDLE_GENERATED_FILE_INVALID", entry_path, "entry must be a mapping")
            integrity_ok = False
            continue
        try:
            relative = _canonical_bundle_path(record.get("path"))
        except RuntimeError as exc:
            report.error("BUNDLE_GENERATED_FILE_INVALID", entry_path, str(exc))
            integrity_ok = False
            continue
        if relative in recorded_paths:
            report.error("BUNDLE_GENERATED_FILE_DUPLICATE", entry_path, f"duplicate path {relative!r}")
            integrity_ok = False
            continue
        recorded_paths.add(relative)
        expected = _normalized_sha256(record.get("sha256"))
        if expected is None:
            report.error("BUNDLE_GENERATED_FILE_HASH_INVALID", entry_path, "sha256 must be complete")
            integrity_ok = False
            continue
        try:
            content = _read_stable_regular_file(bundle.joinpath(*PurePosixPath(relative).parts))
        except RuntimeError as exc:
            report.error("BUNDLE_GENERATED_FILE_READ", entry_path, str(exc))
            integrity_ok = False
            continue
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected or record.get("byte_size") != len(content):
            report.error(
                "BUNDLE_GENERATED_FILE_MISMATCH",
                entry_path,
                "recorded byte_size/SHA-256 does not match the current bundle file",
            )
            integrity_ok = False
    missing = sorted(REQUIRED_GENERATED_FILES - recorded_paths)
    if missing:
        report.error(
            "BUNDLE_GENERATED_FILES_INCOMPLETE",
            str(checksums_path),
            "missing required generated-file hashes: " + ", ".join(missing),
        )
        integrity_ok = False
    if integrity_ok:
        report.integrity_verified_sources += 1
    return integrity_ok


def verify(distillation_dir, normalized_root, sources_manifest):
    distillation_dir = Path(distillation_dir)
    normalized_root = Path(normalized_root)
    sources_manifest = Path(sources_manifest)
    report = Report(
        str(distillation_dir.resolve()),
        str(normalized_root.resolve()),
        str(sources_manifest.resolve()),
    )
    ledger = _load_yaml(distillation_dir / "evidence-ledger.yml")
    manifest_sources = _load_sources_manifest(sources_manifest)
    evidence = ledger.get("evidence")
    if not isinstance(evidence, list):
        raise RuntimeError("evidence-ledger.yml must contain an evidence list")

    blocks_by_source = {}
    failed_sources = set()
    for evidence_index, item in enumerate(evidence):
        path = f"evidence-ledger.yml.evidence[{evidence_index}]"
        if not isinstance(item, dict):
            report.error("EVIDENCE_TYPE", path, "evidence must be a mapping")
            continue
        locator = item.get("locator")
        if not isinstance(locator, dict) or locator.get("locator_type") != "ooxml-block":
            report.skipped += 1
            continue
        report.checked += 1
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            report.error("SOURCE_ID", f"{path}.source_id", "must be a non-empty string")
            continue
        manifest_source = manifest_sources.get(source_id)
        if manifest_source is None:
            report.error("UNKNOWN_SOURCE_ID", f"{path}.source_id", "source is absent from manifest")
            failed_sources.add(source_id)
            continue
        if source_id not in blocks_by_source and source_id not in failed_sources:
            try:
                bundle = _bundle_dir(normalized_root, source_id)
                if not _verify_bundle_integrity(report, bundle, source_id, manifest_source):
                    failed_sources.add(source_id)
                    continue
                blocks_by_source[source_id] = _load_blocks(bundle, source_id)
            except Exception as exc:
                failed_sources.add(source_id)
                report.error("BUNDLE_READ", str(normalized_root / source_id), str(exc))
        if source_id in failed_sources:
            continue
        block_index = locator.get("ooxml_block_index")
        block = blocks_by_source[source_id].get(block_index)
        if block is None:
            report.error(
                "LOCATOR_NOT_FOUND",
                f"{path}.locator.ooxml_block_index",
                f"block {block_index!r} is absent from the normalized bundle",
            )
            continue
        expected_hash = block.get("short_content_hash")
        if str(locator.get("content_hash", "")).lower() != str(expected_hash).lower():
            report.error(
                "CONTENT_HASH_MISMATCH",
                f"{path}.locator.content_hash",
                f"recorded {locator.get('content_hash')!r}, bundle has {expected_hash!r}",
            )
        detected_heading = locator.get("detected_heading_path", locator.get("heading_path"))
        if detected_heading != block.get("heading_path"):
            report.error(
                "HEADING_PATH_MISMATCH",
                f"{path}.locator.heading_path",
                "detected heading path does not match the normalized block",
            )
        for field_name in ("raw_text", "normalized_text"):
            excerpt = item.get(field_name)
            block_text = block.get(field_name)
            if isinstance(excerpt, str) and excerpt and (
                not isinstance(block_text, str) or excerpt not in block_text
            ):
                report.error(
                    "EVIDENCE_TEXT_MISMATCH",
                    f"{path}.{field_name}",
                    f"inline {field_name} is not present in the resolved block",
                )
        figure_ids = []
        if isinstance(locator.get("figure_id"), str):
            figure_ids.append(locator["figure_id"])
        if isinstance(locator.get("figure_ids"), list):
            figure_ids.extend(value for value in locator["figure_ids"] if isinstance(value, str))
        block_figures = set(block.get("figure_ids", []))
        for figure_id in figure_ids:
            if figure_id not in block_figures:
                report.error(
                    "FIGURE_NOT_IN_BLOCK",
                    f"{path}.locator",
                    f"figure {figure_id!r} is not associated with the resolved block",
                )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve OOXML evidence locators against integrity-bound DOCX bundles."
    )
    parser.add_argument("distillation_dir")
    parser.add_argument("normalized_root")
    parser.add_argument(
        "--sources-manifest",
        required=True,
        help="Explicit source manifest whose checksum must match each normalized bundle",
    )
    args = parser.parse_args(argv)
    try:
        report = verify(args.distillation_dir, args.normalized_root, args.sources_manifest)
    except Exception as exc:
        print(json.dumps({
            "checker_scope": "integrity-bound-normalized-locator-resolution",
            "truth_assessed": False,
            "ok": False,
            "input_error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
