#!/usr/bin/env python3
"""Audit a candidate Skill tree for private bibliographic identity disclosure.

The audit is deterministic and read-only.  It derives forbidden identity terms
from manifest records explicitly classified as a method source or book and/or an
optional UTF-8 line-oriented terms file; unrelated target-material and project-
policy identities are intentionally outside this check.  It never includes the
forbidden values in its report.  It
also detects a small, source-neutral set of attribution phrases.  Candidate
artifacts must be auditable UTF-8 text; binary or otherwise unauditable files
fail closed and must be removed or separately reviewed by an explicit dedicated
mechanism before Gate 3.  A successful result is only a disclosure check; it
does not establish copyright, privacy, or publication permission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency is project-provided
    raise SystemExit(
        "PyYAML is required. Do not install it without the user's approval."
    ) from exc


TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".j2",
    ".jinja",
    ".jinja2",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".properties",
    ".py",
    ".r",
    ".rmd",
    ".rst",
    ".sh",
    ".sql",
    ".svg",
    ".template",
    ".tex",
    ".toml",
    ".ts",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

GENERIC_IDENTITY_VALUES = {
    "author",
    "authors",
    "book",
    "document",
    "edition",
    "file",
    "isbn",
    "publisher",
    "sample",
    "series",
    "source",
    "task",
    "title",
    "unknown",
    "untitled",
}


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


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
                "duplicate mapping key",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class DisclosureInputError(RuntimeError):
    """Fail-closed input error whose public fields cannot disclose identities."""

    def __init__(self, code: str, input_ref: str, message: str):
        super().__init__(message)
        self.code = code
        self.input_ref = input_ref
        self.message = message


@dataclass(frozen=True)
class _FileRecord:
    relative_path: str
    absolute_path: Path
    stat_result: os.stat_result


@dataclass(frozen=True)
class _DirectoryRecord:
    relative_path: str
    absolute_path: Path
    stat_result: os.stat_result


@dataclass(frozen=True)
class _IdentityTerm:
    category: str
    normalized: str
    compact: str
    source_field_refs: tuple[str, ...]


def _same_entry(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
        and before.st_size == after.st_size
        and before.st_mtime_ns == after.st_mtime_ns
    )


def _same_path_component(before: os.stat_result, after: os.stat_result) -> bool:
    # Ancestor directory size/mtime can change when an unrelated process creates
    # a sibling (especially under /tmp). Identity and file type are the relevant
    # no-follow invariants; final files and candidate-contained directories are
    # checked more strictly with _same_entry.
    return (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
    )


def _path_fingerprint(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _entry_input_ref(relative_path: str) -> str:
    return f"candidate-entry:{_path_fingerprint(relative_path)}"


def _inspect_path_components(path: Path, expected: str) -> list[tuple[Path, os.stat_result]]:
    absolute = Path(os.path.abspath(os.fspath(path)))
    current = Path(absolute.anchor)
    components: list[tuple[Path, os.stat_result]] = []
    for part in absolute.parts[1:]:
        current = current / part
        try:
            item_stat = current.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "INPUT_UNREADABLE", expected, "input path cannot be inspected"
            ) from exc
        if stat.S_ISLNK(item_stat.st_mode):
            raise DisclosureInputError(
                "INPUT_SYMLINK", expected, "symlink path components are forbidden"
            )
        components.append((current, item_stat))
    if not components:
        raise DisclosureInputError("INPUT_INVALID", expected, "input path is invalid")
    final_mode = components[-1][1].st_mode
    expected_mode = stat.S_ISDIR if expected == "candidate" else stat.S_ISREG
    if not expected_mode(final_mode):
        raise DisclosureInputError(
            "INPUT_TYPE", expected, "input has the wrong filesystem type"
        )
    return components


def _check_read_permission(mode: int, input_ref: str, *, directory: bool = False) -> None:
    lacks_read_bit = mode & 0o444 == 0
    lacks_search_bit = directory and mode & 0o111 == 0
    if lacks_read_bit or lacks_search_bit:
        raise DisclosureInputError(
            "INPUT_UNREADABLE", input_ref, "input has no readable permission bits"
        )


def _read_stable_input_file(path: Path, input_ref: str) -> bytes:
    components = _inspect_path_components(path, input_ref)
    original = components[-1][1]
    _check_read_permission(original.st_mode, input_ref)
    absolute = components[-1][0]
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as exc:
        raise DisclosureInputError(
            "INPUT_UNREADABLE", input_ref, "input file cannot be opened safely"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not _same_entry(original, opened):
            raise DisclosureInputError(
                "INPUT_CHANGED", input_ref, "input changed before reading"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
    except OSError as exc:
        raise DisclosureInputError(
            "INPUT_UNREADABLE", input_ref, "input file cannot be read safely"
        ) from exc
    finally:
        os.close(descriptor)
    content = b"".join(chunks)
    if not _same_entry(opened, final) or len(content) != final.st_size:
        raise DisclosureInputError(
            "INPUT_CHANGED", input_ref, "input changed while reading"
        )
    for component, original_stat in components:
        try:
            current_stat = component.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "INPUT_CHANGED", input_ref, "input path changed after reading"
            ) from exc
        if stat.S_ISLNK(current_stat.st_mode) or not _same_path_component(
            original_stat, current_stat
        ):
            raise DisclosureInputError(
                "INPUT_CHANGED", input_ref, "input path changed while reading"
            )
    return content


def _load_private_manifest(path: Path) -> tuple[Mapping[str, Any], str]:
    try:
        content = _read_stable_input_file(path, "sources-manifest")
        text = content.decode("utf-8")
        document = yaml.load(text, Loader=_UniqueKeySafeLoader)
    except DisclosureInputError:
        raise
    except (UnicodeError, yaml.YAMLError, RecursionError) as exc:
        # Do not include parser text: it can contain a private scalar.
        raise DisclosureInputError(
            "MANIFEST_INVALID", "sources-manifest", "private manifest is invalid"
        ) from exc
    if not isinstance(document, dict) or not isinstance(document.get("sources"), list):
        raise DisclosureInputError(
            "MANIFEST_SCHEMA",
            "sources-manifest",
            "private manifest must contain a sources list",
        )
    for record in document["sources"]:
        if not isinstance(record, dict):
            raise DisclosureInputError(
                "MANIFEST_SCHEMA",
                "sources-manifest",
                "each private source record must be a mapping",
            )
    return document, hashlib.sha256(content).hexdigest()


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _compact(value: str) -> str:
    return "".join(character for character in value if character.isalnum())


def _contains_non_ascii_alnum(value: str) -> bool:
    return any(character.isalnum() and not character.isascii() for character in value)


def _classify_manifest_field(key: Any) -> str | None:
    if not isinstance(key, str):
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
    tokens = set(normalized.split("_"))
    if normalized in {"author", "authors", "creator", "creators"} or "author" in tokens:
        return "author"
    if normalized in {"publisher", "publisher_name", "publishing_house", "imprint"}:
        return "publisher"
    if normalized == "isbn" or normalized.startswith("isbn_"):
        return "isbn"
    if normalized == "edition" or "edition" in tokens:
        return "edition"
    if normalized in {
        "collection",
        "collection_name",
        "collection_title",
        "series",
    } or "series" in tokens or "collection" in tokens:
        return "series"
    if normalized == "title" or normalized.endswith("_title"):
        return "title"
    return None


def _is_path_field(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
    return normalized in {
        "file",
        "filename",
        "local_file",
        "local_path",
        "path",
        "related_local_paths",
        "source_file",
        "source_path",
    }


def _safe_field_segment(key: Any) -> str:
    category = _classify_manifest_field(key)
    if category is not None:
        return category
    if _is_path_field(key):
        return "path"
    # Arbitrary manifest keys can themselves contain a forbidden title/name.
    # Never reproduce them; a short deterministic fingerprint still preserves
    # the ability to distinguish nested source fields during review.
    encoded = repr(key).encode("utf-8", errors="backslashreplace")
    return f"field-{hashlib.sha256(encoded).hexdigest()[:12]}"


def _flatten_identity_scalars(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, int) and not isinstance(value, bool):
        values.append(str(value))
    elif isinstance(value, list):
        for item in value:
            values.extend(_flatten_identity_scalars(item))
    elif isinstance(value, dict):
        for item in value.values():
            values.extend(_flatten_identity_scalars(item))
    return values


def _canonical_isbn(value: str) -> str:
    candidate = "".join(
        character for character in unicodedata.normalize("NFKC", value).casefold()
        if character.isdigit() or character == "x"
    )
    return candidate if len(candidate) in {10, 13} else ""


def _term_parts(value: str, category: str) -> tuple[str, str] | None:
    normalized = _normalize(value)
    compact = _compact(normalized)
    if not normalized or normalized in GENERIC_IDENTITY_VALUES:
        return None
    if category == "isbn":
        isbn = _canonical_isbn(value)
        return (normalized, isbn) if isbn else None
    # Two- and three-character CJK/non-ASCII names are common and identifying;
    # short ASCII tokens are much more collision-prone and remain stricter.
    minimum_length = 2 if _contains_non_ascii_alnum(compact) else 4
    if len(compact) < minimum_length:
        return None
    return normalized, compact


def _path_basename(value: str) -> tuple[str, str] | None:
    cleaned = value.strip().split("?", 1)[0].split("#", 1)[0].rstrip("/\\")
    if not cleaned:
        return None
    basename = re.split(r"[/\\]", cleaned)[-1]
    if not basename:
        return None
    stem = Path(basename).stem
    return basename, stem


def _is_method_identity_source(record: Mapping[str, Any]) -> bool:
    provenance_role = record.get("provenance_role")
    source_role = record.get("source_role")
    source_type = record.get("type")
    if isinstance(provenance_role, str) and provenance_role.casefold() == "method-source":
        return True
    if isinstance(source_role, str) and source_role.casefold() in {
        "primary-book",
        "method-source",
        "supplementary-book",
    }:
        return True
    if isinstance(source_type, str):
        normalized_type = source_type.casefold()
        return normalized_type == "book" or normalized_type.startswith("book-")
    return False


def _collect_manifest_terms(document: Mapping[str, Any]) -> list[_IdentityTerm]:
    collected: dict[tuple[str, str, str], set[str]] = {}
    active_containers: set[int] = set()

    def add(
        value: str,
        category: str,
        source_ref: str,
        opaque_source_id: tuple[str, str] | None,
    ) -> None:
        parts = _term_parts(value, category)
        if parts is None:
            return
        normalized, compact = parts
        if category in {"path-basename", "path-stem"} and opaque_source_id is not None:
            source_normalized, source_compact = opaque_source_id
            if normalized == source_normalized or compact == source_compact:
                return
        collected.setdefault((category, normalized, compact), set()).add(source_ref)

    def walk(
        value: Any,
        reference: str,
        opaque_source_id: tuple[str, str] | None,
    ) -> None:
        if isinstance(value, dict):
            identity = id(value)
            if identity in active_containers:
                raise DisclosureInputError(
                    "MANIFEST_RECURSIVE",
                    "sources-manifest",
                    "recursive manifest containers are forbidden",
                )
            active_containers.add(identity)
            try:
                for key, item in value.items():
                    segment = _safe_field_segment(key)
                    field_ref = f"{reference}.{segment}"
                    category = _classify_manifest_field(key)
                    if category is not None:
                        try:
                            scalars = _flatten_identity_scalars(item)
                        except RecursionError as exc:
                            raise DisclosureInputError(
                                "MANIFEST_RECURSIVE",
                                "sources-manifest",
                                "recursive manifest containers are forbidden",
                            ) from exc
                        for scalar_index, scalar in enumerate(scalars):
                            suffix = "" if len(scalars) == 1 else f"[{scalar_index}]"
                            add(
                                scalar,
                                category,
                                f"{field_ref}{suffix}",
                                opaque_source_id,
                            )
                    elif _is_path_field(key):
                        try:
                            paths = _flatten_identity_scalars(item)
                        except RecursionError as exc:
                            raise DisclosureInputError(
                                "MANIFEST_RECURSIVE",
                                "sources-manifest",
                                "recursive manifest containers are forbidden",
                            ) from exc
                        for path_index, path_value in enumerate(paths):
                            parts = _path_basename(path_value)
                            if parts is None:
                                continue
                            index_suffix = "" if len(paths) == 1 else f"[{path_index}]"
                            basename, stem = parts
                            add(
                                basename,
                                "path-basename",
                                f"{field_ref}{index_suffix}#basename",
                                opaque_source_id,
                            )
                            if stem != basename:
                                add(
                                    stem,
                                    "path-stem",
                                    f"{field_ref}{index_suffix}#stem",
                                    opaque_source_id,
                                )
                    else:
                        walk(item, field_ref, opaque_source_id)
            finally:
                active_containers.remove(identity)
        elif isinstance(value, list):
            identity = id(value)
            if identity in active_containers:
                raise DisclosureInputError(
                    "MANIFEST_RECURSIVE",
                    "sources-manifest",
                    "recursive manifest containers are forbidden",
                )
            active_containers.add(identity)
            try:
                for index, item in enumerate(value):
                    walk(item, f"{reference}[{index}]", opaque_source_id)
            finally:
                active_containers.remove(identity)

    for source_index, record in enumerate(document["sources"]):
        # The candidate must hide the originating method/book identity, not
        # unrelated project-policy paths or target-material paper identities.
        if not _is_method_identity_source(record):
            continue
        source_id = record.get("id")
        opaque_source_id = None
        if isinstance(source_id, str) and source_id.strip():
            source_normalized = _normalize(source_id)
            source_compact = _compact(source_normalized)
            opaque_source_id = (source_normalized, source_compact)
        walk(record, f"sources[{source_index}]", opaque_source_id)

    return [
        _IdentityTerm(category, normalized, compact, tuple(sorted(references)))
        for (category, normalized, compact), references in sorted(
            collected.items(), key=lambda item: item[0]
        )
    ]


def _load_extra_terms(path: Path) -> tuple[list[_IdentityTerm], str]:
    try:
        content = _read_stable_input_file(path, "extra-terms-file")
        text = content.decode("utf-8")
    except DisclosureInputError:
        raise
    except UnicodeError as exc:
        raise DisclosureInputError(
            "EXTRA_TERMS_INVALID",
            "extra-terms-file",
            "extra terms file must be UTF-8 text",
        ) from exc
    terms: list[_IdentityTerm] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        parts = _term_parts(value, "extra-term")
        if parts is None:
            continue
        normalized, compact = parts
        terms.append(
            _IdentityTerm(
                "extra-term",
                normalized,
                compact,
                (f"extra_terms[line:{line_number}]",),
            )
        )
    return terms, hashlib.sha256(content).hexdigest()


def _merge_terms(terms: Iterable[_IdentityTerm]) -> list[_IdentityTerm]:
    merged: dict[tuple[str, str, str], set[str]] = {}
    for term in terms:
        merged.setdefault((term.category, term.normalized, term.compact), set()).update(
            term.source_field_refs
        )
    return [
        _IdentityTerm(category, normalized, compact, tuple(sorted(references)))
        for (category, normalized, compact), references in sorted(
            merged.items(), key=lambda item: item[0]
        )
    ]


def _scan_candidate_tree(
    candidate_dir: Path,
) -> tuple[list[_FileRecord], list[_DirectoryRecord], list[tuple[Path, os.stat_result]]]:
    root_components = _inspect_path_components(candidate_dir, "candidate")
    root = root_components[-1][0]
    files: list[_FileRecord] = []
    directories: list[_DirectoryRecord] = []

    def scan(directory: Path, relative_directory: str) -> None:
        try:
            directory_stat = directory.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "CANDIDATE_UNREADABLE",
                _entry_input_ref(relative_directory or "."),
                "candidate directory cannot be inspected",
            ) from exc
        if stat.S_ISLNK(directory_stat.st_mode):
            raise DisclosureInputError(
                "CANDIDATE_SYMLINK",
                _entry_input_ref(relative_directory or "."),
                "candidate symlinks are forbidden",
            )
        if not stat.S_ISDIR(directory_stat.st_mode):
            raise DisclosureInputError(
                "CANDIDATE_TYPE",
                _entry_input_ref(relative_directory or "."),
                "candidate containers must be directories",
            )
        _check_read_permission(
            directory_stat.st_mode,
            _entry_input_ref(relative_directory or "."),
            directory=True,
        )
        directories.append(
            _DirectoryRecord(relative_directory or ".", directory, directory_stat)
        )
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: os.fsencode(entry.name))
        except OSError as exc:
            raise DisclosureInputError(
                "CANDIDATE_UNREADABLE",
                _entry_input_ref(relative_directory or "."),
                "candidate directory cannot be enumerated",
            ) from exc
        for entry in entries:
            relative = entry.name if not relative_directory else f"{relative_directory}/{entry.name}"
            try:
                relative.encode("utf-8", errors="strict")
                item_stat = os.lstat(entry.path)
            except (UnicodeEncodeError, OSError) as exc:
                raise DisclosureInputError(
                    "CANDIDATE_UNREADABLE",
                    _entry_input_ref(relative.encode("utf-8", "backslashreplace").decode("utf-8")),
                    "candidate entry cannot be inspected",
                ) from exc
            mode = item_stat.st_mode
            if stat.S_ISLNK(mode):
                raise DisclosureInputError(
                    "CANDIDATE_SYMLINK",
                    _entry_input_ref(relative),
                    "candidate symlinks are forbidden",
                )
            if stat.S_ISDIR(mode):
                if entry.name.casefold() == "__pycache__":
                    raise DisclosureInputError(
                        "CANDIDATE_CACHE_ARTIFACT",
                        _entry_input_ref(relative),
                        "Python cache artifacts are forbidden",
                    )
                scan(Path(entry.path), relative)
            elif stat.S_ISREG(mode):
                if entry.name.casefold().endswith(".pyc"):
                    raise DisclosureInputError(
                        "CANDIDATE_CACHE_ARTIFACT",
                        _entry_input_ref(relative),
                        "Python cache artifacts are forbidden",
                    )
                _check_read_permission(item_stat.st_mode, _entry_input_ref(relative))
                files.append(_FileRecord(relative, Path(entry.path), item_stat))
            else:
                raise DisclosureInputError(
                    "CANDIDATE_NON_REGULAR",
                    _entry_input_ref(relative),
                    "candidate entries must be ordinary files or directories",
                )

    scan(root, "")
    files.sort(key=lambda item: item.relative_path.encode("utf-8"))
    return files, directories, root_components


def _read_candidate_file(record: _FileRecord) -> bytes:
    input_ref = _entry_input_ref(record.relative_path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(record.absolute_path, flags)
    except OSError as exc:
        raise DisclosureInputError(
            "CANDIDATE_UNREADABLE", input_ref, "candidate file cannot be opened"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not _same_entry(record.stat_result, opened):
            raise DisclosureInputError(
                "CANDIDATE_CHANGED", input_ref, "candidate file changed before reading"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
    except OSError as exc:
        raise DisclosureInputError(
            "CANDIDATE_UNREADABLE", input_ref, "candidate file cannot be read"
        ) from exc
    finally:
        os.close(descriptor)
    content = b"".join(chunks)
    if not _same_entry(opened, final) or len(content) != final.st_size:
        raise DisclosureInputError(
            "CANDIDATE_CHANGED", input_ref, "candidate file changed while reading"
        )
    try:
        final_path_stat = record.absolute_path.lstat()
    except OSError as exc:
        raise DisclosureInputError(
            "CANDIDATE_CHANGED", input_ref, "candidate path changed after reading"
        ) from exc
    if stat.S_ISLNK(final_path_stat.st_mode) or not _same_entry(final, final_path_stat):
        raise DisclosureInputError(
            "CANDIDATE_CHANGED", input_ref, "candidate path changed while reading"
        )
    return content


def _recheck_candidate_tree(
    files: Sequence[_FileRecord],
    directories: Sequence[_DirectoryRecord],
    root_components: Sequence[tuple[Path, os.stat_result]],
) -> None:
    for record in files:
        try:
            current = record.absolute_path.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "CANDIDATE_CHANGED",
                _entry_input_ref(record.relative_path),
                "candidate file changed after scanning",
            ) from exc
        if stat.S_ISLNK(current.st_mode) or not _same_entry(record.stat_result, current):
            raise DisclosureInputError(
                "CANDIDATE_CHANGED",
                _entry_input_ref(record.relative_path),
                "candidate file changed after scanning",
            )
    for record in directories:
        try:
            current = record.absolute_path.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "CANDIDATE_CHANGED",
                _entry_input_ref(record.relative_path),
                "candidate directory changed after scanning",
            ) from exc
        if stat.S_ISLNK(current.st_mode) or not _same_entry(record.stat_result, current):
            raise DisclosureInputError(
                "CANDIDATE_CHANGED",
                _entry_input_ref(record.relative_path),
                "candidate directory changed after scanning",
            )
    for component, original in root_components:
        try:
            current = component.lstat()
        except OSError as exc:
            raise DisclosureInputError(
                "CANDIDATE_CHANGED", "candidate", "candidate path changed after scanning"
            ) from exc
        if stat.S_ISLNK(current.st_mode) or not _same_path_component(original, current):
            raise DisclosureInputError(
                "CANDIDATE_CHANGED", "candidate", "candidate path changed while scanning"
            )


def _bounded_normalized_match(haystack: str, needle: str) -> bool:
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            return False
        end = index + len(needle)
        left_ok = index == 0 or not (needle[0].isalnum() and haystack[index - 1].isalnum())
        right_ok = end == len(haystack) or not (
            needle[-1].isalnum() and haystack[end].isalnum()
        )
        if left_ok and right_ok:
            return True
        start = index + 1


def _compact_match(haystack: str, term: _IdentityTerm) -> bool:
    if not term.compact:
        return False
    compact_characters: list[str] = []
    original_positions: list[int] = []
    for position, character in enumerate(haystack):
        if character.isalnum():
            compact_characters.append(character)
            original_positions.append(position)
    compact_haystack = "".join(compact_characters)
    start = 0
    while True:
        index = compact_haystack.find(term.compact, start)
        if index < 0:
            return False
        end = index + len(term.compact)
        if term.category == "isbn":
            left_ok = index == 0 or not compact_haystack[index - 1].isdigit()
            right_ok = end == len(compact_haystack) or not compact_haystack[end].isdigit()
        elif _contains_non_ascii_alnum(term.compact):
            # CJK and other non-ASCII names commonly occur without word separators.
            return True
        else:
            original_start = original_positions[index]
            original_end = original_positions[end - 1] + 1
            left_ok = original_start == 0 or not haystack[original_start - 1].isalnum()
            right_ok = original_end == len(haystack) or not haystack[original_end].isalnum()
        if left_ok and right_ok:
            return True
        start = index + 1


def _match_term(value: str, term: _IdentityTerm) -> str | None:
    normalized = _normalize(value)
    if _bounded_normalized_match(normalized, term.normalized):
        return "normalized-exact"
    # Compact matching is intentionally limited to sufficiently identifying
    # values, except ISBNs whose canonical length is already constrained.
    compact_allowed = (
        term.category == "isbn"
        or (_contains_non_ascii_alnum(term.compact) and len(term.compact) >= 2)
        or len(term.compact) >= 6
    )
    if compact_allowed and _compact_match(normalized, term):
        return "compact"
    return None


ATTRIBUTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "en-according-to-source",
        re.compile(
            r"\baccording\s+to\s+(?:the\s+)?(?:author|book|original\s+author|source(?:\s+(?:text|material))?)\b"
        ),
    ),
    (
        "en-attribution-verb",
        re.compile(
            r"\b(?:the|this|original)\s+(?:author|book|source(?:\s+(?:text|material))?)\s+"
            r"(?:argues?|claims?|states?|says?|notes?|writes?|observes?|proposes?|suggests?|contends?|explains?)\b"
        ),
    ),
    (
        "en-book-author-attribution",
        re.compile(
            r"\b(?:the|this)\s+book(?:'s|’s)\s+author\s+"
            r"(?:argues?|claims?|states?|says?|notes?|writes?|observes?|proposes?|suggests?|contends?|explains?)\b"
        ),
    ),
    (
        "zh-attribution-verb",
        re.compile(
            r"(?:本书|该书|原书|书中|原作者|"
            r"(?<!论文)(?<!文章)(?<!研究)(?<!目标)(?<!材料)作者)\s*"
            r"(?:认为|指出|主张|提出|写道|强调|声称|论证|表明)"
        ),
    ),
    (
        "zh-according-to-source",
        re.compile(r"(?:根据|依据|按照)\s*(?:本书|该书|原书|原作者|作者)"),
    ),
)


def _generic_attribution_matches(value: str) -> list[str]:
    normalized = _normalize(value)
    return [rule_id for rule_id, pattern in ATTRIBUTION_PATTERNS if pattern.search(normalized)]


def _first_multiline_match_line(
    lines: Sequence[str], matcher: Callable[[str], bool]
) -> int:
    # Prefer the shortest matching window so unrelated earlier lines do not
    # become the reported start. The whole-file check remains the fail-closed
    # fallback for longer artificial splits.
    maximum_span = min(8, len(lines))
    for span in range(2, maximum_span + 1):
        for start in range(0, len(lines) - span + 1):
            if matcher("\n".join(lines[start : start + span])):
                return start + 1
    return 1


def _path_contains_identity(relative_path: str, terms: Sequence[_IdentityTerm]) -> bool:
    return any(_match_term(relative_path, term) is not None for term in terms)


def _public_candidate_path(relative_path: str, terms: Sequence[_IdentityTerm]) -> dict[str, str]:
    if _path_contains_identity(relative_path, terms):
        return {
            "path": "<redacted>",
            "path_sha256": _path_fingerprint(relative_path),
        }
    return {"path": relative_path}


def _finding_key(finding: Mapping[str, Any]) -> str:
    return json.dumps(finding, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def audit_candidate_disclosure(
    candidate_dir: Path | str,
    sources_manifest: Path | str | None = None,
    extra_terms_file: Path | str | None = None,
) -> dict[str, Any]:
    """Return a deterministic disclosure report without exposing identity values."""
    terms: list[_IdentityTerm] = []
    manifest_snapshot: tuple[Path, str, str] | None = None
    extra_terms_snapshot: tuple[Path, str, str] | None = None
    if sources_manifest is not None:
        manifest_path = Path(sources_manifest)
        document, manifest_digest = _load_private_manifest(manifest_path)
        manifest_snapshot = (manifest_path, "sources-manifest", manifest_digest)
        terms.extend(_collect_manifest_terms(document))
    if extra_terms_file is not None:
        extra_path = Path(extra_terms_file)
        extra_terms, extra_digest = _load_extra_terms(extra_path)
        extra_terms_snapshot = (extra_path, "extra-terms-file", extra_digest)
        terms.extend(extra_terms)
    terms = _merge_terms(terms)

    files, directories, root_components = _scan_candidate_tree(Path(candidate_dir))
    findings: list[dict[str, Any]] = []
    text_files_scanned = 0

    for record in files:
        public_path = _public_candidate_path(record.relative_path, terms)
        for term in terms:
            mode = _match_term(record.relative_path, term)
            if mode is not None:
                findings.append(
                    {
                        "candidate_location": {"kind": "path", **public_path},
                        "code": "IDENTITY_DISCLOSURE",
                        "identity_category": term.category,
                        "match_mode": mode,
                        "source_field_refs": list(term.source_field_refs),
                    }
                )
        for rule_id in _generic_attribution_matches(record.relative_path):
            findings.append(
                {
                    "attribution_rule": rule_id,
                    "candidate_location": {"kind": "path", **public_path},
                    "code": "GENERIC_SOURCE_ATTRIBUTION",
                    "source_field_refs": [],
                }
            )

        content = _read_candidate_file(record)
        suffix = Path(record.relative_path).suffix.casefold()
        if suffix and suffix not in TEXT_SUFFIXES:
            raise DisclosureInputError(
                "CANDIDATE_BINARY_UNAUDITED",
                _entry_input_ref(record.relative_path),
                "candidate artifact is not an approved UTF-8 text type",
            )
        try:
            text = content.decode("utf-8")
        except UnicodeError as exc:
            raise DisclosureInputError(
                "CANDIDATE_BINARY_UNAUDITED",
                _entry_input_ref(record.relative_path),
                "candidate artifact cannot be audited as UTF-8 text",
            ) from exc
        if "\x00" in text:
            raise DisclosureInputError(
                "CANDIDATE_BINARY_UNAUDITED",
                _entry_input_ref(record.relative_path),
                "candidate artifact cannot be audited as UTF-8 text",
            )
        text_files_scanned += 1
        lines = text.splitlines() or [""]
        term_indexes_seen_on_one_line: set[int] = set()
        attribution_rules_seen_on_one_line: set[str] = set()
        for line_number, line in enumerate(lines, start=1):
            for term_index, term in enumerate(terms):
                mode = _match_term(line, term)
                if mode is not None:
                    term_indexes_seen_on_one_line.add(term_index)
                    findings.append(
                        {
                            "candidate_location": {
                                "kind": "content",
                                **public_path,
                                "line": line_number,
                            },
                            "code": "IDENTITY_DISCLOSURE",
                            "identity_category": term.category,
                            "match_mode": mode,
                            "source_field_refs": list(term.source_field_refs),
                        }
                    )
            for rule_id in _generic_attribution_matches(line):
                attribution_rules_seen_on_one_line.add(rule_id)
                findings.append(
                    {
                        "attribution_rule": rule_id,
                        "candidate_location": {
                            "kind": "content",
                            **public_path,
                            "line": line_number,
                        },
                        "code": "GENERIC_SOURCE_ATTRIBUTION",
                        "source_field_refs": [],
                    }
                )

        # Line-oriented scanning gives precise locations, while the whole-file
        # pass prevents identities or attribution phrases from being hidden by
        # Markdown/YAML line wrapping.
        for term_index, term in enumerate(terms):
            if term_index in term_indexes_seen_on_one_line:
                continue
            mode = _match_term(text, term)
            if mode is None:
                continue
            start_line = _first_multiline_match_line(
                lines, lambda value, current=term: _match_term(value, current) is not None
            )
            findings.append(
                {
                    "candidate_location": {
                        "kind": "content",
                        **public_path,
                        "line": start_line,
                    },
                    "code": "IDENTITY_DISCLOSURE",
                    "identity_category": term.category,
                    "match_mode": mode,
                    "match_scope": "multiline-or-whole-file",
                    "source_field_refs": list(term.source_field_refs),
                }
            )
        for rule_id in _generic_attribution_matches(text):
            if rule_id in attribution_rules_seen_on_one_line:
                continue
            start_line = _first_multiline_match_line(
                lines,
                lambda value, current=rule_id: current
                in _generic_attribution_matches(value),
            )
            findings.append(
                {
                    "attribution_rule": rule_id,
                    "candidate_location": {
                        "kind": "content",
                        **public_path,
                        "line": start_line,
                    },
                    "code": "GENERIC_SOURCE_ATTRIBUTION",
                    "match_scope": "multiline-or-whole-file",
                    "source_field_refs": [],
                }
            )

    _recheck_candidate_tree(files, directories, root_components)
    for snapshot in (manifest_snapshot, extra_terms_snapshot):
        if snapshot is None:
            continue
        input_path, input_ref, initial_digest = snapshot
        final_digest = hashlib.sha256(
            _read_stable_input_file(input_path, input_ref)
        ).hexdigest()
        if final_digest != initial_digest:
            raise DisclosureInputError(
                "INPUT_CHANGED", input_ref, "private audit input changed while scanning"
            )
    unique_findings = {
        _finding_key(finding): finding for finding in findings
    }
    ordered_findings = [unique_findings[key] for key in sorted(unique_findings)]
    return {
        "candidate_files_scanned": len(files),
        "checker_scope": "candidate-bibliographic-identity-disclosure",
        "extra_terms_file_supplied": extra_terms_file is not None,
        "finding_count": len(ordered_findings),
        "findings": ordered_findings,
        "identity_term_count": len(terms),
        "ok": not ordered_findings,
        "sources_manifest_supplied": sources_manifest is not None,
        "status": "pass" if not ordered_findings else "findings",
        "text_files_scanned": text_files_scanned,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a candidate Skill for private bibliographic identity disclosure; "
            "binary or non-UTF-8 candidate artifacts fail closed."
        )
    )
    parser.add_argument("candidate_dir", help="Candidate Skill directory to scan read-only")
    parser.add_argument(
        "--sources-manifest",
        help="Private YAML sources manifest used only to derive forbidden identities",
    )
    parser.add_argument(
        "--extra-terms-file",
        help="Optional UTF-8 file containing one additional forbidden term per line",
    )
    args = parser.parse_args(argv)
    try:
        report = audit_candidate_disclosure(
            args.candidate_dir,
            sources_manifest=args.sources_manifest,
            extra_terms_file=args.extra_terms_file,
        )
    except DisclosureInputError as exc:
        report = {
            "checker_scope": "candidate-bibliographic-identity-disclosure",
            "input_error": {
                "code": exc.code,
                "input_ref": exc.input_ref,
                "message": exc.message,
            },
            "ok": False,
            "status": "input-error",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
