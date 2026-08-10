#!/usr/bin/env python3
"""Validate distillation YAML structure and traceability, not knowledge truth.

The validator is intentionally read-only. It checks five required governance
YAML files plus a conditionally required correction overlay and never claims
that their scientific or historical contents are correct, current, or
externally accepted.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Iterable, Mapping, Sequence

# Running this validator must not mutate a materialized candidate by creating
# bytecode for its local helper import, even when the caller forgets ``-B``.
sys.dont_write_bytecode = True

from hash_candidate_tree import (
    CandidateTreeError,
    candidate_tree_sha256,
    canonical_candidate_path,
)
from task_contracts import inspect_task_governance

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only in minimal runtimes
    raise SystemExit(
        "PyYAML is required to parse YAML. Do not install it without the user's approval."
    ) from exc


REQUIRED_FILES = {
    "evidence-ledger.yml": ("evidence", "claims"),
    "concept-map.yml": ("relations",),
    "capability-rules.yml": ("capability_rules",),
    "gate-decisions.yml": ("gate_decisions", "materializations"),
    "eval-runs.yml": ("eval_runs",),
}
RECORD_STATUSES = {
    "candidate", "accepted", "reference-only", "needs-verification", "rejected"
}
SKILL_LIFECYCLES = {
    "draft", "review", "accepted", "deployed", "deprecated", "rejected"
}
TRANSFORMATIONS = {"T0", "T1", "T2", "T3", "T4"}
RELATION_STATUSES = {"explicit", "implicit", "inferred"}
HUMAN_DECISIONS = {"pending", "accepted", "revised", "rejected"}
EVIDENCE_TYPES = {
    "text", "definition", "figure", "figure-caption", "table", "case",
    "footnote", "author-summary", "quoted-source", "formula",
}
CAPTURE_MODES = {"quote", "excerpt", "paraphrase", "visual-observation", "ocr"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
CLAIM_TYPES = {
    "definition", "principle", "empirical-claim", "relation", "distinction",
    "method", "heuristic", "misconception", "limitation", "controversy",
    "analogy", "historical-development",
}
SOURCE_POSITIONS = {
    "book-assertion", "author-view", "teaching-simplification", "quoted-source",
    "project-policy", "distiller-synthesis", "task-transfer",
}
IMPORTANCE_LEVELS = {"important", "supporting"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTENT_HASH_RE = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{12,64}$")
TREE_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
FULL_SHA256_RE = re.compile(r"^(?:sha256:)?(?P<digest>[0-9a-fA-F]{64})$")
ANCHOR_LINE_RE = re.compile(r"^(?P<start>[1-9][0-9]*)(?:-(?P<end>[1-9][0-9]*))?$")
ATX_HEADING_RE = re.compile(r"^\s{0,3}(?P<marks>#{1,6})[ \t]+(?P<title>.+?)\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(?P<marker>`{3,}|~{3,})")
TRAILING_PAREN_RE = re.compile(r"\s*[（(][^（）()]*[）)]\s*$")
PLACEHOLDER_RE = re.compile(
    r"\{\{[^{}]+\}\}|(?:^|[\s._:-])(?:todo|tbd|placeholder|replace[-_ ]?me)(?:$|[\s._:-])",
    re.IGNORECASE,
)
EXAMPLE_IDENTIFIER_RE = re.compile(
    r"(?:^|[._:-])(?:example|sample)(?:$|[._:-])", re.IGNORECASE
)

GATES = {"gate-1", "gate-2", "gate-3", "gate-4", "gate-5"}
GATE_DECISIONS = {
    "pending", "approved", "approved-with-conditions", "approved-for-eval",
    "accepted", "revise", "rejected", "blocked",
}
GATE_DECISIONS_BY_GATE = {
    "gate-1": {"pending", "approved", "approved-with-conditions", "revise", "rejected", "blocked"},
    "gate-2": {"pending", "approved", "approved-with-conditions", "revise", "rejected", "blocked"},
    "gate-3": {"pending", "approved-for-eval", "revise", "rejected", "blocked"},
    "gate-4": {"pending", "accepted", "revise", "rejected", "blocked"},
    "gate-5": {"pending", "approved", "approved-with-conditions", "revise", "rejected", "blocked"},
}
HUMAN_REVIEWER_TYPES = {"user", "human-delegate"}
EVAL_STATUSES = {"planned", "blocked", "completed", "invalidated"}
EVAL_OUTCOMES = {None, "pass", "fail", "inconclusive"}
EVAL_CASE_TYPES = {"trigger", "nontrigger", "task"}
SEMANTIC_SUPPORT_KEYS = ("checks", "action", "output", "stop_conditions")
RULE_GATE_DECISIONS = {"accepted", "revised", "rejected"}
MATERIALIZATION_STATUSES = {
    "planned", "completed", "failed", "invalidated", "legacy-quarantined"
}
QUICK_VALIDATION_STATUSES = {"not-run", "pass", "fail"}
POSITIVE_GATE_DECISIONS = {
    "gate-1": {"approved", "approved-with-conditions"},
    "gate-2": {"approved", "approved-with-conditions"},
    "gate-3": {"approved-for-eval"},
    "gate-4": {"accepted"},
    "gate-5": {"approved", "approved-with-conditions"},
}

GATE3_APPROVAL_SNAPSHOT_CONTRACT = "gate3-approval-snapshot:v2"
GATE3_APPROVAL_SNAPSHOT_LEGACY_CONTRACT = "gate3-approval-snapshot:v1"
APPROVAL_SNAPSHOT_GOVERNANCE_FILES = (
    "evidence-ledger.yml",
    "concept-map.yml",
    "capability-rules.yml",
)

RECORD_TRANSITIONS = {
    "candidate": {"accepted", "reference-only", "needs-verification", "rejected"},
    "accepted": {"candidate"},
    "reference-only": {"candidate"},
    "needs-verification": {"candidate"},
    "rejected": {"candidate"},
}
LIFECYCLE_TRANSITIONS = {
    "draft": {"review", "rejected"},
    "review": {"accepted", "rejected"},
    "accepted": {"deployed", "deprecated"},
    "deployed": {"deprecated"},
    "deprecated": set(),
    "rejected": set(),
}


class DistillationInputError(RuntimeError):
    """Raised when required input files cannot be read or parsed."""

    def __init__(self, code: str, path: Path, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


class _DuplicateYamlKeyError(yaml.YAMLError):
    """Raised when a YAML mapping contains the same key more than once."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            location = f"line {key_node.start_mark.line + 1}, column {key_node.start_mark.column + 1}"
            raise _DuplicateYamlKeyError(f"duplicate mapping key {key!r} at {location}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class _ArtifactFileError(RuntimeError):
    """A candidate or evaluation artifact cannot be read safely."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass
class ValidationReport:
    root: str
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, code: str, path: str, message: str) -> None:
        self.errors.append(Issue(code, path, message))

    def add_warning(self, code: str, path: str, message: str) -> None:
        self.warnings.append(Issue(code, path, message))

    def as_dict(self) -> dict[str, Any]:
        return {
            "validator_scope": "structure-and-traceability-only",
            "truth_assessed": False,
            "behavior_effectiveness_assessed": False,
            "root": self.root,
            "ok": self.ok,
            "errors": [item.as_dict() for item in self.errors],
            "warnings": [item.as_dict() for item in self.warnings],
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class MarkdownAnchor:
    repository_path: str
    start_line: int
    end_line: int
    heading: str | None


@dataclass(frozen=True)
class MarkdownSection:
    start_line: int
    end_line: int
    level: int
    title: str
    slug_variants: frozenset[str]


@dataclass(frozen=True)
class TextOccurrence:
    start_offset: int
    end_offset: int
    start_line: int
    end_line: int


@dataclass(frozen=True)
class EvalCaseContract:
    case_type: str
    case_id: str
    request: str
    definition_hash: str
    holdout: bool
    prompt_leakage_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalRubricContract:
    rubric_id: str
    dimensions: tuple[str, ...]
    score_min: float
    score_max_per_dimension: float
    pass_threshold: float
    fatal_failures: frozenset[str]

    @property
    def max_score(self) -> float:
        return len(self.dimensions) * self.score_max_per_dimension


@dataclass(frozen=True)
class CandidateEvalContract:
    """Versioned cases and rubric parsed from one materialized candidate tree."""

    case_ids: Mapping[str, frozenset[str]]
    task_holdout: Mapping[str, bool]
    cases: Mapping[str, Mapping[str, EvalCaseContract]]
    rubric: EvalRubricContract | None
    definitions_valid: bool


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DistillationInputError("MISSING_FILE", path, "required YAML file is missing")
    try:
        data = yaml.load(
            path.read_text(encoding="utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except (OSError, UnicodeError) as exc:
        raise DistillationInputError("READ_ERROR", path, str(exc)) from exc
    except _DuplicateYamlKeyError as exc:
        raise DistillationInputError("YAML_DUPLICATE_KEY", path, str(exc)) from exc
    except (yaml.YAMLError, RecursionError) as exc:
        raise DistillationInputError("YAML_PARSE", path, str(exc)) from exc
    if not isinstance(data, dict):
        raise DistillationInputError("ROOT_TYPE", path, "YAML root must be a mapping")
    return data


def _canonical_relative_artifact_path(value: Any) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise _ArtifactFileError(
            "PATH_INVALID",
            "artifact path must be a non-empty string without surrounding whitespace",
        )
    if "\\" in value or "\x00" in value:
        raise _ArtifactFileError(
            "PATH_INVALID",
            "artifact path must use POSIX separators and contain no NUL byte",
        )
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise _ArtifactFileError(
            "PATH_INVALID",
            "artifact path must be canonical and contain no empty, '.' or '..' components",
        )
    relative = PurePosixPath(value)
    if relative.is_absolute() or not relative.parts or relative.as_posix() != value:
        raise _ArtifactFileError(
            "PATH_INVALID",
            "artifact path must be a canonical relative POSIX path",
        )
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise _ArtifactFileError(
            "PATH_INVALID", "artifact path must be valid UTF-8"
        ) from exc
    return value


def _same_filesystem_entry(before: os.stat_result, after: os.stat_result) -> bool:
    same_identity = (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
    )
    if not same_identity:
        return False
    # Directory size/mtime changes when unrelated siblings are created. Identity
    # and no-follow checks are sufficient for path components; ordinary file
    # bytes still require stable size and mtime.
    if stat.S_ISDIR(before.st_mode):
        return True
    return before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns


def _read_distillation_artifact(root: Path, relative_path: Any) -> tuple[str, bytes]:
    """Read one root-confined regular file without accepting symlink components."""
    canonical = _canonical_relative_artifact_path(relative_path)
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise _ArtifactFileError(
            "ROOT_INVALID", f"distillation root cannot be resolved: {exc}"
        ) from exc
    try:
        if not stat.S_ISDIR(resolved_root.stat().st_mode):
            raise _ArtifactFileError("ROOT_INVALID", "distillation root is not a directory")
    except OSError as exc:
        raise _ArtifactFileError(
            "ROOT_INVALID", f"distillation root cannot be inspected: {exc}"
        ) from exc

    components: list[tuple[Path, os.stat_result]] = []
    current = resolved_root
    parts = PurePosixPath(canonical).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            entry_stat = current.lstat()
        except FileNotFoundError as exc:
            raise _ArtifactFileError("MISSING", "artifact file does not exist") from exc
        except OSError as exc:
            raise _ArtifactFileError(
                "READ_ERROR", f"artifact path cannot be inspected: {exc}"
            ) from exc
        if stat.S_ISLNK(entry_stat.st_mode):
            raise _ArtifactFileError("SYMLINK", "artifact path contains a symlink")
        is_last = index == len(parts) - 1
        if not is_last and not stat.S_ISDIR(entry_stat.st_mode):
            raise _ArtifactFileError(
                "NOT_REGULAR", "an intermediate artifact path component is not a directory"
            )
        if is_last and not stat.S_ISREG(entry_stat.st_mode):
            raise _ArtifactFileError("NOT_REGULAR", "artifact is not an ordinary file")
        components.append((current, entry_stat))

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(current, flags)
    except OSError as exc:
        raise _ArtifactFileError(
            "READ_ERROR", f"artifact file cannot be opened safely: {exc}"
        ) from exc
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise _ArtifactFileError("NOT_REGULAR", "artifact is not an ordinary file")
        if not _same_filesystem_entry(components[-1][1], opened_stat):
            raise _ArtifactFileError("CHANGED", "artifact changed before it was read")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(descriptor)
    except OSError as exc:
        raise _ArtifactFileError(
            "READ_ERROR", f"artifact file cannot be read: {exc}"
        ) from exc
    finally:
        os.close(descriptor)
    if not _same_filesystem_entry(opened_stat, final_stat):
        raise _ArtifactFileError("CHANGED", "artifact changed while it was read")
    content = b"".join(chunks)
    if len(content) != final_stat.st_size:
        raise _ArtifactFileError(
            "CHANGED", "artifact bytes do not match the stable file length"
        )
    for component, original_stat in components:
        try:
            current_stat = component.lstat()
        except OSError as exc:
            raise _ArtifactFileError(
                "CHANGED", f"artifact path changed after reading: {exc}"
            ) from exc
        if stat.S_ISLNK(current_stat.st_mode) or not _same_filesystem_entry(
            original_stat, current_stat
        ):
            raise _ArtifactFileError("CHANGED", "artifact path changed while it was read")
    return canonical, content


@contextlib.contextmanager
def distillation_read_snapshot(root: Path | str) -> Iterator[Path]:
    """Yield a private byte snapshot of a distillation tree.

    Every ordinary file is copied from one stable, no-follow read. Symlinks and
    non-regular entries fail closed. The immutable copy lets routing, parsing,
    artifact validation, and candidate hashing all observe the same bytes even
    if another process rewrites and restores the source tree concurrently.
    """
    source = Path(root)
    try:
        resolved_source = source.resolve(strict=True)
        source_stat = resolved_source.lstat()
    except OSError as exc:
        raise DistillationInputError(
            "DISTILLATION_SNAPSHOT_INVALID",
            source,
            f"distillation root cannot be inspected: {exc}",
        ) from exc
    if not stat.S_ISDIR(source_stat.st_mode):
        raise DistillationInputError(
            "DISTILLATION_SNAPSHOT_INVALID",
            source,
            "distillation root must be a directory",
        )

    with tempfile.TemporaryDirectory(prefix="distillation-read-snapshot-") as tempdir:
        snapshot_root = Path(tempdir) / "distillation"
        snapshot_root.mkdir()
        directories: list[tuple[Path, os.stat_result, str]] = []

        def capture(directory: Path, relative: PurePosixPath | None) -> None:
            display = "." if relative is None else relative.as_posix()
            try:
                directory_stat = directory.lstat()
            except OSError as exc:
                raise DistillationInputError(
                    "DISTILLATION_SNAPSHOT_CHANGED",
                    directory,
                    f"directory cannot be inspected: {exc}",
                ) from exc
            if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(
                directory_stat.st_mode
            ):
                raise DistillationInputError(
                    "DISTILLATION_SNAPSHOT_INVALID",
                    directory,
                    "snapshot traversal accepts only ordinary directories",
                )
            directories.append((directory, directory_stat, display))
            destination_directory = (
                snapshot_root
                if relative is None
                else snapshot_root.joinpath(*relative.parts)
            )
            try:
                entries = sorted(os.scandir(directory), key=lambda item: item.name)
            except OSError as exc:
                raise DistillationInputError(
                    "DISTILLATION_SNAPSHOT_READ_ERROR",
                    directory,
                    f"directory cannot be enumerated: {exc}",
                ) from exc
            for entry in entries:
                relative_entry = (
                    PurePosixPath(entry.name)
                    if relative is None
                    else relative / entry.name
                )
                relative_string = relative_entry.as_posix()
                try:
                    entry_stat = entry.stat(follow_symlinks=False)
                except OSError as exc:
                    raise DistillationInputError(
                        "DISTILLATION_SNAPSHOT_READ_ERROR",
                        Path(entry.path),
                        f"entry cannot be inspected: {exc}",
                    ) from exc
                destination = destination_directory / entry.name
                if stat.S_ISLNK(entry_stat.st_mode):
                    # Preserve the link itself without reading its target. Any
                    # referenced governance/artifact/candidate path will then
                    # be rejected by its existing no-follow validation. Map an
                    # in-root target into the private snapshot; replace an
                    # out-of-root target with a self-loop so parsing cannot
                    # accidentally follow it outside the snapshot.
                    try:
                        raw_target = os.readlink(entry.path)
                        source_target = Path(
                            os.path.abspath(
                                raw_target
                                if os.path.isabs(raw_target)
                                else os.path.join(directory, raw_target)
                            )
                        )
                        try:
                            target_relative = source_target.relative_to(resolved_source)
                        except ValueError:
                            snapshot_target = entry.name
                        else:
                            snapshot_target = str(snapshot_root / target_relative)
                        os.symlink(snapshot_target, destination)
                    except OSError as exc:
                        raise DistillationInputError(
                            "DISTILLATION_SNAPSHOT_WRITE_ERROR",
                            destination,
                            f"symlink metadata cannot be snapshotted: {exc}",
                        ) from exc
                    continue
                if stat.S_ISDIR(entry_stat.st_mode):
                    destination.mkdir()
                    capture(Path(entry.path), relative_entry)
                    continue
                if not stat.S_ISREG(entry_stat.st_mode):
                    raise DistillationInputError(
                        "DISTILLATION_SNAPSHOT_NON_REGULAR",
                        Path(entry.path),
                        "only ordinary files and directories may enter a validation snapshot",
                    )
                try:
                    _, content = _read_distillation_artifact(
                        resolved_source, relative_string
                    )
                    destination.write_bytes(content)
                except _ArtifactFileError as exc:
                    raise DistillationInputError(
                        "DISTILLATION_SNAPSHOT_CHANGED",
                        Path(entry.path),
                        f"{exc.code}: {exc.message}",
                    ) from exc
                except OSError as exc:
                    raise DistillationInputError(
                        "DISTILLATION_SNAPSHOT_WRITE_ERROR",
                        destination,
                        str(exc),
                    ) from exc

        capture(resolved_source, None)
        for directory, original_stat, display in directories:
            try:
                final_stat = directory.lstat()
            except OSError as exc:
                raise DistillationInputError(
                    "DISTILLATION_SNAPSHOT_CHANGED",
                    directory,
                    f"directory changed after capture: {exc}",
                ) from exc
            if not _same_filesystem_entry(original_stat, final_stat):
                raise DistillationInputError(
                    "DISTILLATION_SNAPSHOT_CHANGED",
                    directory,
                    f"directory {display!r} changed during snapshot capture",
                )
        yield snapshot_root


def _read_stable_external_file(path: Path | str) -> tuple[Path, bytes]:
    """Read one absolute ordinary file while rejecting every symlink component."""
    requested = Path(path)
    absolute = Path(os.path.abspath(requested))
    parts = absolute.parts
    if not parts:
        raise _ArtifactFileError("PATH_INVALID", "external file path is empty")
    current = Path(parts[0])
    components: list[tuple[Path, os.stat_result]] = []
    for index, part in enumerate(parts[1:], start=1):
        current = current / part
        try:
            entry_stat = current.lstat()
        except FileNotFoundError as exc:
            raise _ArtifactFileError("MISSING", "external file does not exist") from exc
        except OSError as exc:
            raise _ArtifactFileError(
                "READ_ERROR", f"external path cannot be inspected: {exc}"
            ) from exc
        if stat.S_ISLNK(entry_stat.st_mode):
            raise _ArtifactFileError("SYMLINK", "external path contains a symlink")
        is_last = index == len(parts) - 1
        if not is_last and not stat.S_ISDIR(entry_stat.st_mode):
            raise _ArtifactFileError(
                "NOT_REGULAR", "an intermediate external path is not a directory"
            )
        if is_last and not stat.S_ISREG(entry_stat.st_mode):
            raise _ArtifactFileError("NOT_REGULAR", "external input is not an ordinary file")
        components.append((current, entry_stat))

    if not components:
        raise _ArtifactFileError("NOT_REGULAR", "filesystem root is not a file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as exc:
        raise _ArtifactFileError(
            "READ_ERROR", f"external file cannot be opened safely: {exc}"
        ) from exc
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise _ArtifactFileError("NOT_REGULAR", "external input is not an ordinary file")
        if not _same_filesystem_entry(components[-1][1], opened_stat):
            raise _ArtifactFileError("CHANGED", "external file changed before reading")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(descriptor)
    except OSError as exc:
        raise _ArtifactFileError(
            "READ_ERROR", f"external file cannot be read: {exc}"
        ) from exc
    finally:
        os.close(descriptor)
    if not _same_filesystem_entry(opened_stat, final_stat):
        raise _ArtifactFileError("CHANGED", "external file changed while being read")
    content = b"".join(chunks)
    if len(content) != final_stat.st_size:
        raise _ArtifactFileError("CHANGED", "external file length changed while reading")
    for component, original_stat in components:
        try:
            current_stat = component.lstat()
        except OSError as exc:
            raise _ArtifactFileError(
                "CHANGED", f"external path changed after reading: {exc}"
            ) from exc
        if stat.S_ISLNK(current_stat.st_mode) or not _same_filesystem_entry(
            original_stat, current_stat
        ):
            raise _ArtifactFileError("CHANGED", "external path changed while being read")
    return absolute, content


def _anchor_repository_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    without_heading = value.rsplit("#", 1)[0]
    repository_path, separator, _line_value = without_heading.rpartition(":")
    if not separator:
        return None
    return _canonical_repository_path(repository_path)


def snapshot_validation_inputs(
    distillation_snapshot_root: Path,
    sources_manifest: Path | str | None,
) -> Path | None:
    """Freeze the explicit manifest and every Markdown locator file it can read."""
    if sources_manifest is None:
        return None
    try:
        manifest_path, manifest_bytes = _read_stable_external_file(sources_manifest)
    except _ArtifactFileError as exc:
        raise DistillationInputError(
            f"SOURCES_MANIFEST_{exc.code}", Path(sources_manifest), exc.message
        ) from exc

    input_root = Path(
        tempfile.mkdtemp(prefix=".validation-inputs-", dir=distillation_snapshot_root)
    )
    project_root = input_root / "project"
    snapshot_manifest = project_root / "manifests" / "sources.yml"
    snapshot_manifest.parent.mkdir(parents=True)
    snapshot_manifest.write_bytes(manifest_bytes)

    manifest_document = _load_yaml(snapshot_manifest)
    evidence_document = _load_yaml(distillation_snapshot_root / "evidence-ledger.yml")
    sources = {
        record.get("id"): record
        for record in _records(manifest_document, "sources")
        if _is_nonempty_string(record.get("id"))
    }
    original_project_root = (
        manifest_path.parent.parent
        if manifest_path.parent.name == "manifests"
        else manifest_path.parent
    )
    paths_to_freeze: set[str] = set()
    for evidence in _records(evidence_document, "evidence"):
        locator = evidence.get("locator")
        if not isinstance(locator, dict) or locator.get("locator_type") != "markdown-section":
            continue
        source_id = evidence.get("source_id")
        source = sources.get(source_id) if _is_nonempty_string(source_id) else None
        if source is None:
            continue
        repository_path = _anchor_repository_path(locator.get("anchor"))
        if repository_path is not None and repository_path in _allowed_source_paths(source):
            paths_to_freeze.add(repository_path)

    for repository_path in sorted(paths_to_freeze):
        source_path = original_project_root.joinpath(
            *PurePosixPath(repository_path).parts
        )
        try:
            _absolute_source, source_bytes = _read_stable_external_file(source_path)
        except _ArtifactFileError as exc:
            if exc.code == "MISSING":
                continue
            raise DistillationInputError(
                f"LOCATOR_SOURCE_{exc.code}", source_path, exc.message
            ) from exc
        destination = project_root.joinpath(*PurePosixPath(repository_path).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source_bytes)
    return snapshot_manifest


def _normalized_full_sha256(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = FULL_SHA256_RE.fullmatch(value)
    return None if match is None else match.group("digest").lower()


def _load_json_object_strict(content: bytes) -> dict[str, Any]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"JSON is not UTF-8: {exc}") from exc

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key {key!r}")
            result[key] = value
        return result

    def reject_non_json_constant(value: str) -> None:
        raise ValueError(f"non-JSON numeric constant {value!r}")

    try:
        value = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_non_json_constant,
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _string_items(value: Any) -> list[str]:
    """Return only string members of a list, without ever hashing bad values."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _string_set(value: Any) -> set[str]:
    return set(_string_items(value))


def _is_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(_is_nonempty_string(item) for item in value)
    )


def _safe_member(value: Any, container: Any) -> bool:
    """Membership test that treats unhashable malformed values as non-members."""
    try:
        return value in container
    except (TypeError, ValueError):
        return False


def _candidate_file_bytes(
    report: ValidationReport,
    root: Path,
    relative_path: str,
    report_path: str,
    *,
    kind: str,
) -> bytes | None:
    try:
        _, content = _read_distillation_artifact(root, relative_path)
    except _ArtifactFileError as exc:
        code = (
            f"MATERIALIZATION_{kind}_MISSING"
            if exc.code == "MISSING"
            else f"MATERIALIZATION_{kind}_INVALID"
        )
        report.add_error(code, report_path, f"{exc.code}: {exc.message}")
        return None
    return content


def _validate_materialized_skill_file(
    report: ValidationReport,
    root: Path,
    candidate_path: str,
    candidate_name: Any,
    materialization_path: str,
) -> bool:
    relative_path = f"{candidate_path}/SKILL.md"
    report_path = f"{materialization_path}.candidate_path[{relative_path}]"
    content = _candidate_file_bytes(
        report,
        root,
        relative_path,
        report_path,
        kind="SKILL_FILE",
    )
    if content is None:
        return False
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        report.add_error(
            "MATERIALIZATION_SKILL_FILE_INVALID",
            report_path,
            f"SKILL.md must be UTF-8: {exc}",
        )
        return False

    lines = text.splitlines()
    if not lines or lines[0] != "---":
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "SKILL.md must start with an exact '---' frontmatter delimiter",
        )
        return False
    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "SKILL.md frontmatter must have an exact closing '---' delimiter",
        )
        return False
    if not any(line.strip() for line in lines[closing_index + 1 :]):
        report.add_error(
            "MATERIALIZATION_SKILL_BODY_INVALID",
            report_path,
            "SKILL.md must contain a non-empty body after frontmatter",
        )

    frontmatter_text = "\n".join(lines[1:closing_index])
    try:
        frontmatter = yaml.load(frontmatter_text, Loader=_UniqueKeySafeLoader)
    except _DuplicateYamlKeyError as exc:
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            f"duplicate frontmatter key: {exc}",
        )
        return False
    except (yaml.YAMLError, RecursionError) as exc:
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            f"frontmatter is not valid YAML: {exc}",
        )
        return False
    if not isinstance(frontmatter, dict):
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "frontmatter must be a mapping",
        )
        return False
    allowed_keys = {"name", "description"}
    if set(frontmatter) != allowed_keys:
        missing = sorted(allowed_keys - set(frontmatter))
        extra = sorted(str(key) for key in set(frontmatter) - allowed_keys)
        details: list[str] = []
        if missing:
            details.append(f"missing {missing!r}")
        if extra:
            details.append(f"extra {extra!r}")
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "frontmatter must contain only name and description"
            + (f" ({'; '.join(details)})" if details else ""),
        )
        return False
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    valid = True
    if (
        not _is_nonempty_string(name)
        or name != name.strip()
        or not SKILL_NAME_RE.fullmatch(name)
        or len(name) > 64
    ):
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "frontmatter name must be a canonical hyphen-case Skill name",
        )
        valid = False
    if not _is_nonempty_string(description):
        report.add_error(
            "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            report_path,
            "frontmatter description must be a non-empty string",
        )
        valid = False
    path_name = PurePosixPath(candidate_path).name
    if _is_nonempty_string(name) and name != path_name:
        report.add_error(
            "MATERIALIZATION_SKILL_NAME_MISMATCH",
            report_path,
            f"frontmatter name {name!r} must match candidate directory {path_name!r}",
        )
        valid = False
    if (
        _is_nonempty_string(name)
        and _is_nonempty_string(candidate_name)
        and name != candidate_name
    ):
        report.add_error(
            "MATERIALIZATION_SKILL_NAME_MISMATCH",
            report_path,
            f"frontmatter name {name!r} must match linked candidate name {candidate_name!r}",
        )
        valid = False
    return valid


def _canonical_json_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _parse_eval_definition(
    report: ValidationReport,
    root: Path,
    candidate_path: str,
    candidate_name: str,
    materialization_path: str,
    *,
    filename: str,
    list_keys: Sequence[str],
) -> tuple[
    dict[str, frozenset[str]],
    dict[str, bool],
    dict[str, dict[str, EvalCaseContract]],
    EvalRubricContract | None,
    bool,
]:
    relative_path = f"{candidate_path}/evals/{filename}"
    report_path = f"{materialization_path}.candidate_path[{relative_path}]"
    content = _candidate_file_bytes(
        report,
        root,
        relative_path,
        report_path,
        kind="EVAL_DEFINITION",
    )
    empty_ids = {key: frozenset() for key in list_keys}
    empty_cases = {case_type: {} for case_type in EVAL_CASE_TYPES}
    if content is None:
        return empty_ids, {}, empty_cases, None, False
    try:
        definition = _load_json_object_strict(content)
    except ValueError as exc:
        report.add_error(
            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
            report_path,
            str(exc),
        )
        return empty_ids, {}, empty_cases, None, False

    valid = True
    definition_schema = definition.get("schema_version")
    if (
        not isinstance(definition_schema, int)
        or isinstance(definition_schema, bool)
        or definition_schema not in {1, 2}
    ):
        report.add_error(
            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
            f"{report_path}.schema_version",
            "schema_version must be integer 1 (legacy) or 2 (task contract)",
        )
        valid = False
    if definition.get("skill_name") != candidate_name:
        report.add_error(
            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
            f"{report_path}.skill_name",
            f"skill_name must equal {candidate_name!r}",
        )
        valid = False

    case_type_by_key = {
        "should_trigger": "trigger",
        "should_not_trigger": "nontrigger",
        "tasks": "task",
    }
    case_ids: dict[str, frozenset[str]] = {}
    task_holdout: dict[str, bool] = {}
    cases: dict[str, dict[str, EvalCaseContract]] = {
        case_type: {} for case_type in EVAL_CASE_TYPES
    }
    for list_key in list_keys:
        records = definition.get(list_key)
        if not isinstance(records, list) or len(records) < 3:
            report.add_error(
                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                f"{report_path}.{list_key}",
                "must be a list containing at least three case definitions",
            )
            case_ids[list_key] = frozenset()
            valid = False
            continue
        seen: set[str] = set()
        case_type = case_type_by_key[list_key]
        for index, record in enumerate(records):
            case_path = f"{report_path}.{list_key}[{index}]"
            if not isinstance(record, dict):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    case_path,
                    "case definition must be an object",
                )
                valid = False
                continue
            _validate_no_placeholder_deep(report, record, case_path)
            case_id = record.get("case_id")
            if (
                not _is_nonempty_string(case_id)
                or case_id != case_id.strip()
                or not ID_RE.fullmatch(case_id)
            ):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{case_path}.case_id",
                    "case_id must be a stable non-empty ID",
                )
                valid = False
                continue
            if case_id in seen:
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{case_path}.case_id",
                    f"duplicate case_id {case_id!r}",
                )
                valid = False
                continue
            seen.add(case_id)
            request_key = "request" if case_type == "task" else "prompt"
            request = record.get(request_key)
            if not _is_nonempty_string(request):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{case_path}.{request_key}",
                    f"{request_key} must be a non-empty string",
                )
                valid = False
                continue
            holdout = False
            if case_type == "task":
                holdout_value = record.get("holdout")
                if not isinstance(holdout_value, bool):
                    report.add_error(
                        "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                        f"{case_path}.holdout",
                        "task case holdout must be a boolean",
                    )
                    valid = False
                    continue
                holdout = holdout_value
                task_holdout[case_id] = holdout
                for field_name in ("title", "input_profile", "rubric_id"):
                    if not _is_nonempty_string(record.get(field_name)):
                        report.add_error(
                            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                            f"{case_path}.{field_name}",
                            f"task case {field_name} must be a non-empty string",
                        )
                        valid = False
                for field_name in ("expected_behaviors", "failure_signals"):
                    if not _is_string_list(record.get(field_name), nonempty=True):
                        report.add_error(
                            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                            f"{case_path}.{field_name}",
                            f"task case {field_name} must be a non-empty string list",
                        )
                        valid = False
            elif not _is_nonempty_string(record.get("expected_reason")):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{case_path}.expected_reason",
                    "trigger boundary case requires a non-empty expected_reason",
                )
                valid = False
            if definition_schema == 2:
                for field_name in ("stable_task_ids", "input_type_ids"):
                    if not _is_string_list(record.get(field_name), nonempty=True):
                        report.add_error(
                            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                            f"{case_path}.{field_name}",
                            f"schema v2 case requires a unique non-empty {field_name} list",
                        )
                        valid = False
                for field_name, must_be_nonempty in (
                    (
                        "positive_example_ids",
                        case_type in {"trigger", "task"},
                    ),
                    (
                        "negative_example_ids",
                        case_type in {"nontrigger", "task"},
                    ),
                ):
                    values = record.get(field_name)
                    if (
                        not _is_string_list(values, nonempty=must_be_nonempty)
                        or len(_string_items(values)) != len(set(_string_items(values)))
                        or (
                            case_type == "trigger"
                            and field_name == "negative_example_ids"
                            and values != []
                        )
                        or (
                            case_type == "nontrigger"
                            and field_name == "positive_example_ids"
                            and values != []
                        )
                    ):
                        report.add_error(
                            "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                            f"{case_path}.{field_name}",
                            "schema v2 requires explicit unique polarity-separated example IDs",
                        )
                        valid = False
            leakage_terms: list[str] = []
            if case_type == "task":
                for field_name in ("expected_behaviors", "failure_signals"):
                    values = record.get(field_name)
                    if isinstance(values, list):
                        leakage_terms.extend(
                            item for item in values if isinstance(item, str) and item.strip()
                        )
            else:
                reason = record.get("expected_reason")
                if isinstance(reason, str) and reason.strip():
                    leakage_terms.append(reason)
            cases[case_type][case_id] = EvalCaseContract(
                case_type=case_type,
                case_id=case_id,
                request=request,
                definition_hash=_canonical_json_sha256(record),
                holdout=holdout,
                prompt_leakage_terms=tuple(leakage_terms),
            )
        case_ids[list_key] = frozenset(seen)

    rubric: EvalRubricContract | None = None
    if "tasks" in list_keys:
        if not any(task_holdout.values()):
            report.add_error(
                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                f"{report_path}.tasks",
                "task definitions must include at least one holdout case",
            )
            valid = False
        protocol = definition.get("comparison_protocol")
        if not isinstance(protocol, dict):
            report.add_error(
                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                f"{report_path}.comparison_protocol",
                "task definitions require a comparison_protocol mapping",
            )
            valid = False
        else:
            if protocol.get("required") is not True:
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{report_path}.comparison_protocol.required",
                    "comparison protocol must be explicitly required",
                )
                valid = False
            for field_name in ("baseline", "with_skill", "leakage_control"):
                if not _is_nonempty_string(protocol.get(field_name)):
                    report.add_error(
                        "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                        f"{report_path}.comparison_protocol.{field_name}",
                        f"{field_name} must be a non-empty string",
                    )
                    valid = False
            dimensions = protocol.get("human_review_dimensions")
            if definition_schema == 1 and (
                not _is_string_list(dimensions, nonempty=True)
                or len(dimensions) != len(set(_string_items(dimensions)))
            ):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{report_path}.comparison_protocol.human_review_dimensions",
                    "human review dimensions must be a unique non-empty string list",
                )
                valid = False
                dimensions = []
            rubric_record = protocol.get("rubric")
            if not isinstance(rubric_record, dict):
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{report_path}.comparison_protocol.rubric",
                    "comparison protocol requires a structured rubric",
                )
                valid = False
            else:
                rubric_id = rubric_record.get("rubric_id")
                score_min = rubric_record.get("score_min")
                score_max = rubric_record.get("score_max_per_dimension")
                threshold = rubric_record.get("pass_threshold")
                fatal_failures = rubric_record.get("fatal_failures")
                if definition_schema == 2:
                    dimension_records = rubric_record.get("dimensions")
                    if not isinstance(dimension_records, list) or not dimension_records:
                        dimensions = []
                    else:
                        dimensions = [
                            item.get("dimension_id")
                            for item in dimension_records
                            if isinstance(item, dict)
                            and _is_nonempty_string(item.get("dimension_id"))
                            and _is_nonempty_string(item.get("description"))
                        ]
                        if len(dimensions) != len(dimension_records) or len(dimensions) != len(set(dimensions)):
                            dimensions = []
                    if not isinstance(fatal_failures, list):
                        fatal_failures = []
                    else:
                        fatal_failures = [
                            item.get("failure_id")
                            for item in fatal_failures
                            if isinstance(item, dict)
                            and _is_nonempty_string(item.get("failure_id"))
                            and _is_nonempty_string(item.get("description"))
                        ]
                rubric_shape_ok = True
                if not _is_nonempty_string(rubric_id) or not ID_RE.fullmatch(rubric_id):
                    rubric_shape_ok = False
                if not _is_number(score_min) or not _is_number(score_max) or score_max <= score_min:
                    rubric_shape_ok = False
                max_score = len(_string_items(dimensions)) * score_max if _is_number(score_max) else None
                if (
                    not _is_number(threshold)
                    or max_score is None
                    or not score_min <= threshold <= max_score
                ):
                    rubric_shape_ok = False
                if not _is_string_list(fatal_failures, nonempty=True) or not dimensions:
                    rubric_shape_ok = False
                if not rubric_shape_ok:
                    report.add_error(
                        "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                        f"{report_path}.comparison_protocol.rubric",
                        "rubric requires ID, numeric score bounds/threshold, and fatal failures",
                    )
                    valid = False
                else:
                    rubric = EvalRubricContract(
                        rubric_id=rubric_id,
                        dimensions=tuple(dimensions),
                        score_min=float(score_min),
                        score_max_per_dimension=float(score_max),
                        pass_threshold=float(threshold),
                        fatal_failures=frozenset(fatal_failures),
                    )
                    for case_id, case in cases["task"].items():
                        raw_case = next(
                            item for item in definition["tasks"]
                            if isinstance(item, dict) and item.get("case_id") == case_id
                        )
                        if raw_case.get("rubric_id") != rubric.rubric_id:
                            report.add_error(
                                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                                f"{report_path}.tasks[{case_id}].rubric_id",
                                "task rubric_id must match comparison_protocol rubric",
                            )
                            valid = False

    return case_ids, task_holdout, cases, rubric, valid


def _validate_candidate_contract(
    report: ValidationReport,
    root: Path,
    candidate_path: str,
    candidate_name: Any,
    materialization_path: str,
) -> CandidateEvalContract:
    expected_name = (
        candidate_name
        if _is_nonempty_string(candidate_name)
        else PurePosixPath(candidate_path).name
    )
    _validate_materialized_skill_file(
        report, root, candidate_path, candidate_name, materialization_path
    )
    trigger_cases, _, trigger_contracts, _, trigger_valid = _parse_eval_definition(
        report,
        root,
        candidate_path,
        expected_name,
        materialization_path,
        filename="trigger-cases.json",
        list_keys=("should_trigger", "should_not_trigger"),
    )
    task_cases, task_holdout, task_contracts, rubric, task_valid = _parse_eval_definition(
        report,
        root,
        candidate_path,
        expected_name,
        materialization_path,
        filename="task-cases.json",
        list_keys=("tasks",),
    )
    case_ids = {
        "trigger": trigger_cases.get("should_trigger", frozenset()),
        "nontrigger": trigger_cases.get("should_not_trigger", frozenset()),
        "task": task_cases.get("tasks", frozenset()),
    }
    definitions_valid = trigger_valid and task_valid and rubric is not None
    case_types = tuple(case_ids)
    for left_index, left_type in enumerate(case_types):
        for right_type in case_types[left_index + 1 :]:
            overlap = case_ids[left_type] & case_ids[right_type]
            if overlap:
                report.add_error(
                    "MATERIALIZATION_EVAL_DEFINITION_INVALID",
                    f"{materialization_path}.candidate_path",
                    "case IDs must be unique across eval case types; overlap: "
                    + ", ".join(sorted(overlap)),
                )
                definitions_valid = False
    merged_cases = {case_type: {} for case_type in EVAL_CASE_TYPES}
    for source in (trigger_contracts, task_contracts):
        for case_type, records in source.items():
            merged_cases[case_type].update(records)
    return CandidateEvalContract(
        case_ids={key: frozenset(value) for key, value in case_ids.items()},
        task_holdout=dict(task_holdout),
        cases=merged_cases,
        rubric=rubric,
        definitions_valid=definitions_valid,
    )

def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonempty_value(value: Any) -> bool:
    """Return whether a string/container contains at least one usable value."""
    pending = [value]
    seen: set[int] = set()
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            if item.strip():
                return True
            continue
        if not isinstance(item, (list, dict)):
            continue
        identity = id(item)
        if identity in seen:
            continue
        seen.add(identity)
        pending.extend(item if isinstance(item, list) else item.values())
    return False


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_no_placeholder(
    report: ValidationReport,
    value: Any,
    path: str,
    *,
    identifier: bool = False,
) -> None:
    if not isinstance(value, str):
        return
    if PLACEHOLDER_RE.search(value) or (identifier and EXAMPLE_IDENTIFIER_RE.search(value)):
        report.add_error(
            "PLACEHOLDER_VALUE", path, "replace template/example placeholder before validation"
        )


def _validate_no_placeholder_deep(
    report: ValidationReport,
    value: Any,
    path: str,
) -> None:
    """Reject template markers anywhere inside a strict JSON value."""
    pending: list[tuple[Any, str]] = [(value, path)]
    while pending:
        item, item_path = pending.pop()
        if isinstance(item, str):
            _validate_no_placeholder(report, item, item_path)
        elif isinstance(item, list):
            pending.extend(
                (child, f"{item_path}[{index}]")
                for index, child in enumerate(item)
            )
        elif isinstance(item, dict):
            for key, child in item.items():
                key_label = key if isinstance(key, str) else repr(key)
                if isinstance(key, str):
                    _validate_no_placeholder(report, key, f"{item_path}.<key>")
                pending.append((child, f"{item_path}.{key_label}"))


def _validate_content_hash(report: ValidationReport, value: Any, path: str) -> bool:
    if not isinstance(value, str) or not CONTENT_HASH_RE.fullmatch(value):
        report.add_error(
            "CONTENT_HASH_INVALID",
            path,
            "must be 12-64 hexadecimal characters, optionally prefixed with sha256:",
        )
        return False
    return True


def _require_fields(
    report: ValidationReport,
    record: Mapping[str, Any],
    fields: Iterable[str],
    path: str,
) -> None:
    for key in fields:
        if key not in record:
            report.add_error("MISSING_FIELD", f"{path}.{key}", "required field is missing")


def _require_list(
    report: ValidationReport,
    record: Mapping[str, Any],
    key: str,
    path: str,
    *,
    nonempty: bool = False,
) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list):
        report.add_error("FIELD_TYPE", f"{path}.{key}", "must be a list")
        return []
    if nonempty and not value:
        report.add_error("EMPTY_LIST", f"{path}.{key}", "must not be empty")
    return value


def _validate_string_list(
    report: ValidationReport,
    record: Mapping[str, Any],
    key: str,
    path: str,
    *,
    nonempty: bool = False,
    min_items: int = 0,
) -> list[str]:
    values = _require_list(report, record, key, path, nonempty=nonempty)
    result: list[str] = []
    for index, value in enumerate(values):
        if not _is_nonempty_string(value):
            report.add_error(
                "FIELD_TYPE", f"{path}.{key}[{index}]", "must be a non-empty string"
            )
        else:
            result.append(value)
    if len(values) < min_items:
        report.add_error(
            "MIN_ITEMS", f"{path}.{key}", f"must contain at least {min_items} items"
        )
    return result


def _validate_id(report: ValidationReport, value: Any, path: str) -> str | None:
    if not _is_nonempty_string(value):
        report.add_error("INVALID_ID", path, "ID must be a non-empty string")
        return None
    if value != value.strip():
        report.add_error("INVALID_ID", path, "ID must not contain leading or trailing whitespace")
        return None
    value = value.strip()
    if not ID_RE.fullmatch(value):
        report.add_error(
            "INVALID_ID", path, "ID must contain only letters, digits, dot, underscore, colon, or hyphen"
        )
        return None
    _validate_no_placeholder(report, value, path, identifier=True)
    return value


def _validate_status(
    report: ValidationReport,
    value: Any,
    allowed: set[str],
    path: str,
    code: str = "INVALID_STATUS",
) -> str | None:
    if not _safe_member(value, allowed):
        report.add_error(code, path, f"must be one of: {', '.join(sorted(allowed))}")
        return None
    return value


def _validate_history(
    report: ValidationReport,
    record: Mapping[str, Any],
    *,
    current_key: str,
    history_key: str,
    transitions: Mapping[str, set[str]],
    initial: str,
    path: str,
    require_null_initial: bool = False,
) -> None:
    if history_key not in record:
        return
    history = record.get(history_key)
    if not isinstance(history, list) or not history:
        report.add_error(
            "STATUS_HISTORY_INVALID", f"{path}.{history_key}", "must be a non-empty list"
        )
        return
    previous_to: str | None = None
    for index, event in enumerate(history):
        event_path = f"{path}.{history_key}[{index}]"
        if not isinstance(event, dict):
            report.add_error("STATUS_HISTORY_INVALID", event_path, "event must be a mapping")
            continue
        _require_fields(
            report, event, ("from", "to", "decided_by", "decided_at", "rationale"), event_path
        )
        from_value = event.get("from")
        to_value = event.get("to")
        for key in ("decided_by", "decided_at", "rationale"):
            if not _is_nonempty_string(event.get(key)):
                report.add_error(
                    "STATUS_HISTORY_INVALID", f"{event_path}.{key}", "must be a non-empty string"
                )
        if index == 0:
            if from_value is None:
                if to_value != initial:
                    report.add_error(
                        "STATUS_HISTORY_INVALID", f"{event_path}.to",
                        f"initial transition must enter {initial}"
                    )
            elif require_null_initial:
                report.add_error(
                    "STATUS_HISTORY_INVALID",
                    f"{event_path}.from",
                    f"complete history must start from null and enter {initial}",
                )
            elif (
                not isinstance(from_value, str)
                or from_value not in transitions
                or not _safe_member(to_value, transitions[from_value])
            ):
                report.add_error(
                    "STATUS_HISTORY_INVALID", event_path,
                    f"transition {from_value!r} -> {to_value!r} is not allowed"
                )
        else:
            if from_value != previous_to:
                report.add_error(
                    "STATUS_HISTORY_INVALID", f"{event_path}.from",
                    "does not continue the previous event"
                )
            if (
                not isinstance(from_value, str)
                or from_value not in transitions
                or not _safe_member(to_value, transitions[from_value])
            ):
                report.add_error(
                    "STATUS_HISTORY_INVALID", event_path, f"transition {from_value!r} -> {to_value!r} is not allowed"
                )
        previous_to = to_value if isinstance(to_value, str) else None
    if previous_to != record.get(current_key):
        report.add_error(
            "STATUS_HISTORY_INVALID",
            f"{path}.{history_key}",
            f"final transition does not match current {current_key}",
        )


def _require_accepted_status_history(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    if record.get("status") != "accepted":
        return
    history = record.get("status_history")
    if not isinstance(history, list) or not history:
        report.add_error(
            "STATUS_HISTORY_REQUIRED", f"{path}.status_history",
            "accepted records require a complete, non-empty status_history"
        )


def _require_candidate_lifecycle_history(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    lifecycle = record.get("lifecycle")
    if _safe_member(lifecycle, SKILL_LIFECYCLES - {"draft"}):
        history = record.get("lifecycle_history")
        if not isinstance(history, list) or not history:
            report.add_error(
                "LIFECYCLE_HISTORY_REQUIRED", f"{path}.lifecycle_history",
                f"{lifecycle} candidates require a complete lifecycle_history"
            )


def _validate_human_decision(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
    *,
    require_gate_link: bool = False,
) -> None:
    transformation = record.get("transformation")
    if not _safe_member(transformation, {"T3", "T4"}):
        return
    decision = record.get("human_decision")
    if not isinstance(decision, dict):
        report.add_error(
            "T34_DECISION_MISSING", f"{path}.human_decision", "T3/T4 requires a decision mapping"
        )
        return
    fields = ["decision", "reviewer_type", "reviewer", "decided_at", "rationale"]
    if require_gate_link:
        fields.append("gate_decision_id")
    _require_fields(report, decision, fields, f"{path}.human_decision")
    value = decision.get("decision")
    if not _safe_member(value, HUMAN_DECISIONS):
        report.add_error(
            "T34_DECISION_INVALID", f"{path}.human_decision.decision",
            f"must be one of: {', '.join(sorted(HUMAN_DECISIONS))}"
        )
    reviewer_type = decision.get("reviewer_type")
    if reviewer_type is not None and not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
        report.add_error(
            "T34_DECISION_INVALID",
            f"{path}.human_decision.reviewer_type",
            f"must be null or one of: {', '.join(sorted(HUMAN_REVIEWER_TYPES))}",
        )
    for key in ("reviewer", "decided_at"):
        if decision.get(key) is not None and not _is_nonempty_string(decision.get(key)):
            report.add_error(
                "T34_DECISION_INVALID", f"{path}.human_decision.{key}", "must be null or non-empty string"
            )
    if decision.get("rationale") is not None and not isinstance(decision.get("rationale"), str):
        report.add_error(
            "T34_DECISION_INVALID", f"{path}.human_decision.rationale", "must be null or string"
        )
    gate_decision_id = decision.get("gate_decision_id")
    if require_gate_link and gate_decision_id is not None:
        _validate_id(
            report, gate_decision_id, f"{path}.human_decision.gate_decision_id"
        )
    completed_decision = _safe_member(value, HUMAN_DECISIONS - {"pending"})
    if completed_decision:
        if not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
            report.add_error(
                "T34_DECISION_INCOMPLETE",
                f"{path}.human_decision.reviewer_type",
                "completed T3/T4 decision requires a human reviewer type",
            )
        for key in ("reviewer", "decided_at", "rationale"):
            if not _is_nonempty_string(decision.get(key)):
                report.add_error(
                    "T34_DECISION_INCOMPLETE", f"{path}.human_decision.{key}",
                    "completed T3/T4 decision requires completed human metadata"
                )
    if record.get("status") == "accepted":
        if not _safe_member(value, {"accepted", "revised"}):
            report.add_error(
                "T34_DECISION_NOT_ACCEPTED", f"{path}.human_decision.decision",
                "accepted T3/T4 record requires accepted or revised decision"
            )
        for key in ("reviewer_type", "reviewer", "decided_at", "rationale"):
            if not _is_nonempty_string(decision.get(key)):
                report.add_error(
                    "T34_DECISION_INCOMPLETE", f"{path}.human_decision.{key}",
                    "accepted T3/T4 record requires completed human decision metadata"
                )
        if require_gate_link and not _is_nonempty_string(gate_decision_id):
            report.add_error(
                "T34_GATE_LINK_REQUIRED",
                f"{path}.human_decision.gate_decision_id",
                "accepted T3/T4 rule must link its authorizing Gate 3 decision",
            )


def _validate_locator(
    report: ValidationReport,
    evidence: Mapping[str, Any],
    path: str,
) -> bool:
    locator = evidence.get("locator")
    if not isinstance(locator, dict):
        report.add_error("LOCATOR_INVALID", f"{path}.locator", "must be a mapping")
        return False
    _require_fields(report, locator, ("source_id", "locator_type", "content_hash"), f"{path}.locator")
    valid = True
    if locator.get("source_id") != evidence.get("source_id"):
        report.add_error(
            "LOCATOR_SOURCE_MISMATCH", f"{path}.locator.source_id",
            "must equal evidence source_id"
        )
        valid = False
    if not _validate_content_hash(
        report, locator.get("content_hash"), f"{path}.locator.content_hash"
    ):
        valid = False
    locator_type = locator.get("locator_type")
    if locator_type == "ooxml-block":
        _require_fields(
            report, locator, ("heading_path", "ooxml_block_index"), f"{path}.locator"
        )
        heading_path = locator.get("heading_path")
        if not isinstance(heading_path, list) or not heading_path or not all(
            _is_nonempty_string(item) for item in heading_path
        ):
            report.add_error(
                "LOCATOR_INVALID",
                f"{path}.locator.heading_path",
                "must be a non-empty list of non-empty strings",
            )
            valid = False
        index = locator.get("ooxml_block_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 1:
            report.add_error(
                "LOCATOR_INVALID", f"{path}.locator.ooxml_block_index", "must be a positive integer"
            )
            valid = False
    elif locator_type == "ocr-region":
        _require_fields(
            report,
            locator,
            (
                "anchor", "carrier", "image_sha256", "ocr_run_id",
                "ocr_record_id", "region_id", "bbox_px",
            ),
            f"{path}.locator",
        )
        if not _is_nonempty_string(locator.get("anchor")):
            report.add_error("LOCATOR_INVALID", f"{path}.locator.anchor", "must be non-empty")
            valid = False
        if locator.get("carrier") not in {"docx-image", "pdf-page"}:
            report.add_error(
                "LOCATOR_INVALID", f"{path}.locator.carrier",
                "must be docx-image or pdf-page",
            )
            valid = False
        if not isinstance(locator.get("image_sha256"), str) or not TREE_HASH_RE.fullmatch(
            locator.get("image_sha256", "")
        ):
            report.add_error(
                "LOCATOR_INVALID", f"{path}.locator.image_sha256",
                "must be sha256:<64 lowercase hex>",
            )
            valid = False
        for field_name in ("ocr_run_id", "ocr_record_id", "region_id"):
            if not _is_nonempty_string(locator.get(field_name)):
                report.add_error(
                    "LOCATOR_INVALID", f"{path}.locator.{field_name}",
                    "must be a non-empty stable ID",
                )
                valid = False
        bbox = locator.get("bbox_px")
        if (
            not isinstance(bbox, list) or len(bbox) != 4
            or any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in bbox)
            or bbox[2] < 1 or bbox[3] < 1
        ):
            report.add_error(
                "LOCATOR_INVALID", f"{path}.locator.bbox_px",
                "must be [left, top, width, height] with positive dimensions",
            )
            valid = False
        if locator.get("carrier") == "docx-image":
            for field_name in ("figure_id", "media_occurrence_id"):
                if not _is_nonempty_string(locator.get(field_name)):
                    report.add_error(
                        "LOCATOR_INVALID", f"{path}.locator.{field_name}",
                        "DOCX OCR locator must bind the figure occurrence",
                    )
                    valid = False
        elif locator.get("carrier") == "pdf-page":
            page_number = locator.get("page_number")
            if not isinstance(page_number, int) or isinstance(page_number, bool) or page_number < 1:
                report.add_error(
                    "LOCATOR_INVALID", f"{path}.locator.page_number",
                    "PDF OCR locator requires a positive page number",
                )
                valid = False
    elif _is_nonempty_string(locator_type):
        if not _is_nonempty_string(locator.get("anchor")):
            report.add_error(
                "LOCATOR_INVALID", f"{path}.locator.anchor",
                "non-OOXML locator must provide a non-empty anchor"
            )
            valid = False
    else:
        report.add_error("LOCATOR_INVALID", f"{path}.locator.locator_type", "must be non-empty")
        valid = False
    return valid


def _validate_evidence(report: ValidationReport, record: Mapping[str, Any], path: str) -> bool:
    _require_fields(
        report, record,
        (
            "evidence_id", "source_id", "locator", "evidence_type", "capture_mode",
            "extraction_confidence", "limitations", "quality_flags", "status"
        ),
        path,
    )
    _validate_id(report, record.get("evidence_id"), f"{path}.evidence_id")
    for forbidden_key in ("locators", "related_locators"):
        if forbidden_key in record:
            report.add_error(
                "FORBIDDEN_LOCATOR_FIELD", f"{path}.{forbidden_key}",
                "use exactly one singular locator; split cross-block evidence"
            )
    if not _is_nonempty_string(record.get("source_id")):
        report.add_error("FIELD_TYPE", f"{path}.source_id", "must be a non-empty string")
    else:
        _validate_id(report, record.get("source_id"), f"{path}.source_id")
    locator_valid = _validate_locator(report, record, path)
    if not _safe_member(record.get("evidence_type"), EVIDENCE_TYPES):
        report.add_error("INVALID_ENUM", f"{path}.evidence_type", "unsupported evidence type")
    if not _safe_member(record.get("capture_mode"), CAPTURE_MODES):
        report.add_error("INVALID_ENUM", f"{path}.capture_mode", "unsupported capture mode")
    if record.get("capture_mode") == "ocr":
        if isinstance(record.get("locator"), dict) and record["locator"].get("locator_type") != "ocr-region":
            report.add_error(
                "OCR_LOCATOR_REQUIRED", f"{path}.locator.locator_type",
                "OCR evidence must use an ocr-region locator",
            )
        quality_flags = _string_set(record.get("quality_flags", []))
        if record.get("status") != "accepted" and "ocr-unreviewed" not in quality_flags:
            report.add_error(
                "OCR_EVIDENCE_REVIEW_REQUIRED", f"{path}.quality_flags",
                "non-accepted OCR evidence must retain ocr-unreviewed",
            )
        if record.get("status") == "accepted":
            review = record.get("ocr_review")
            if (
                not isinstance(review, dict)
                or review.get("decision") not in {"accepted", "revised"}
                or review.get("reviewer_type") not in HUMAN_REVIEWER_TYPES
                or not _is_nonempty_string(review.get("reviewer"))
                or not _is_nonempty_string(review.get("decided_at"))
                or not _is_nonempty_string(review.get("rationale"))
            ):
                report.add_error(
                    "OCR_EVIDENCE_REVIEW_REQUIRED", f"{path}.ocr_review",
                    "accepted OCR evidence requires an explicit human review",
                )
    if not _safe_member(record.get("extraction_confidence"), CONFIDENCE_LEVELS):
        report.add_error("INVALID_ENUM", f"{path}.extraction_confidence", "unsupported confidence")
    _require_list(report, record, "limitations", path)
    _validate_string_list(report, record, "quality_flags", path)
    _validate_status(report, record.get("status"), RECORD_STATUSES, f"{path}.status")
    _validate_history(
        report, record, current_key="status", history_key="status_history",
        transitions=RECORD_TRANSITIONS, initial="candidate", path=path,
        require_null_initial=record.get("status") == "accepted",
    )
    _require_accepted_status_history(report, record, path)
    content_fields = ("raw_text", "normalized_text", "content_summary", "visual_observation")
    if not any(_is_nonempty_string(record.get(key)) for key in content_fields):
        report.add_error(
            "EVIDENCE_CONTENT_EMPTY", path,
            "provide raw_text, normalized_text, content_summary, or visual_observation"
        )
    return locator_valid


def _validate_claim(report: ValidationReport, record: Mapping[str, Any], path: str) -> None:
    _require_fields(
        report, record,
        (
            "claim_id", "statement", "claim_type", "source_position", "evidence_ids",
            "transformation", "scope", "limitations", "importance", "status", "human_decision"
        ), path,
    )
    _validate_id(report, record.get("claim_id"), f"{path}.claim_id")
    if not _is_nonempty_string(record.get("statement")):
        report.add_error("FIELD_TYPE", f"{path}.statement", "must be a non-empty string")
    if not _safe_member(record.get("claim_type"), CLAIM_TYPES):
        report.add_error("INVALID_ENUM", f"{path}.claim_type", "unsupported claim type")
    if not _safe_member(record.get("source_position"), SOURCE_POSITIONS):
        report.add_error("INVALID_ENUM", f"{path}.source_position", "unsupported source position")
    _validate_string_list(report, record, "evidence_ids", path, nonempty=True)
    if not _safe_member(record.get("transformation"), TRANSFORMATIONS):
        report.add_error("INVALID_TRANSFORMATION", f"{path}.transformation", "must be T0-T4")
    if not isinstance(record.get("scope"), (str, list, dict)):
        report.add_error("FIELD_TYPE", f"{path}.scope", "must be string, list, or mapping")
    elif not _is_nonempty_value(record.get("scope")):
        report.add_error("EMPTY_FIELD", f"{path}.scope", "must not be empty")
    _require_list(report, record, "limitations", path)
    if "correction_ids" in record:
        _validate_string_list(report, record, "correction_ids", path)
    if not _safe_member(record.get("importance"), IMPORTANCE_LEVELS):
        report.add_error("INVALID_ENUM", f"{path}.importance", "unsupported importance")
    _validate_status(report, record.get("status"), RECORD_STATUSES, f"{path}.status")
    _validate_human_decision(report, record, path)
    _validate_history(
        report, record, current_key="status", history_key="status_history",
        transitions=RECORD_TRANSITIONS, initial="candidate", path=path,
        require_null_initial=record.get("status") == "accepted",
    )
    _require_accepted_status_history(report, record, path)


def _validate_relation(report: ValidationReport, record: Mapping[str, Any], path: str) -> None:
    _require_fields(
        report, record,
        (
            "relation_id", "subject", "predicate", "object", "qualifiers", "claim_ids",
            "evidence_ids", "relation_status", "status"
        ), path,
    )
    _validate_id(report, record.get("relation_id"), f"{path}.relation_id")
    for key in ("subject", "predicate", "object"):
        if not _is_nonempty_string(record.get(key)):
            report.add_error("FIELD_TYPE", f"{path}.{key}", "must be a non-empty string")
    _require_list(report, record, "qualifiers", path)
    _validate_string_list(report, record, "claim_ids", path, nonempty=True)
    _validate_string_list(report, record, "evidence_ids", path)
    if not _safe_member(record.get("relation_status"), RELATION_STATUSES):
        report.add_error("INVALID_ENUM", f"{path}.relation_status", "unsupported relation status")
    _validate_status(report, record.get("status"), RECORD_STATUSES, f"{path}.status")
    if (
        record.get("status") == "accepted"
        and _safe_member(record.get("relation_status"), {"implicit", "inferred"})
    ):
        decision = record.get("human_decision")
        decision_path = f"{path}.human_decision"
        if not isinstance(decision, dict):
            report.add_error(
                "RELATION_HUMAN_DECISION_REQUIRED",
                decision_path,
                "accepted implicit/inferred relation requires a human decision mapping",
            )
        else:
            _require_fields(
                report,
                decision,
                ("decision", "reviewer_type", "reviewer", "decided_at", "rationale"),
                decision_path,
            )
            if not _safe_member(decision.get("decision"), {"accepted", "revised"}):
                report.add_error(
                    "RELATION_HUMAN_DECISION_REQUIRED",
                    f"{decision_path}.decision",
                    "accepted implicit/inferred relation requires accepted or revised decision",
                )
            if decision.get("reviewer_type") != "user":
                report.add_error(
                    "RELATION_HUMAN_DECISION_REQUIRED",
                    f"{decision_path}.reviewer_type",
                    "accepted implicit/inferred relation requires reviewer_type: user",
                )
            for key in ("reviewer", "decided_at", "rationale"):
                if not _is_nonempty_string(decision.get(key)):
                    report.add_error(
                        "RELATION_HUMAN_DECISION_REQUIRED",
                        f"{decision_path}.{key}",
                        "accepted implicit/inferred relation requires complete human metadata",
                    )
    _validate_history(
        report, record, current_key="status", history_key="status_history",
        transitions=RECORD_TRANSITIONS, initial="candidate", path=path,
        require_null_initial=record.get("status") == "accepted",
    )
    _require_accepted_status_history(report, record, path)


def _validate_semantic_support(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    support = record.get("semantic_support")
    required = record.get("status") != "rejected"
    if support is None:
        if required:
            report.add_error(
                "SEMANTIC_SUPPORT_REQUIRED",
                f"{path}.semantic_support",
                "every non-rejected rule requires item-level semantic support",
            )
        return
    if not isinstance(support, dict):
        report.add_error(
            "FIELD_TYPE", f"{path}.semantic_support", "must be a mapping"
        )
        return

    for key in SEMANTIC_SUPPORT_KEYS:
        source_items = record.get(key)
        support_path = f"{path}.semantic_support.{key}"
        if not isinstance(source_items, list) or not all(
            _is_nonempty_string(item) for item in source_items
        ):
            report.add_error(
                "SEMANTIC_SUPPORT_SOURCE_TYPE",
                f"{path}.{key}",
                "semantic support requires a list of non-empty text items",
            )
            continue
        entries = support.get(key)
        if not isinstance(entries, list):
            report.add_error("FIELD_TYPE", support_path, "must be a list")
            continue
        seen_indices: set[int] = set()
        for support_index, entry in enumerate(entries):
            entry_path = f"{support_path}[{support_index}]"
            if not isinstance(entry, dict):
                report.add_error("FIELD_TYPE", entry_path, "must be a mapping")
                continue
            _require_fields(report, entry, ("item_index", "claim_ids", "relation_ids"), entry_path)
            item_index = entry.get("item_index")
            if (
                not isinstance(item_index, int)
                or isinstance(item_index, bool)
                or item_index < 0
                or item_index >= len(source_items)
            ):
                report.add_error(
                    "SEMANTIC_SUPPORT_INDEX",
                    f"{entry_path}.item_index",
                    "must be a valid zero-based index into the corresponding rule field",
                )
            elif item_index in seen_indices:
                report.add_error(
                    "SEMANTIC_SUPPORT_DUPLICATE",
                    f"{entry_path}.item_index",
                    "each rule item may be mapped only once",
                )
            else:
                seen_indices.add(item_index)
            claim_ids = _validate_string_list(report, entry, "claim_ids", entry_path)
            relation_ids = _validate_string_list(report, entry, "relation_ids", entry_path)
            if not claim_ids and not relation_ids:
                report.add_error(
                    "SEMANTIC_SUPPORT_EMPTY",
                    entry_path,
                    "each supported item must cite at least one claim or relation",
                )
        if required and seen_indices != set(range(len(source_items))):
            report.add_error(
                "SEMANTIC_SUPPORT_INCOMPLETE",
                support_path,
                "every non-rejected rule must cover every item exactly once",
            )


def _validate_rule(report: ValidationReport, record: Mapping[str, Any], path: str) -> None:
    _require_fields(
        report, record,
        (
            "rule_id", "trigger", "required_context", "checks", "action", "output",
            "stop_conditions", "claim_ids", "relation_ids", "transformation", "status",
            "human_decision"
        ), path,
    )
    _validate_id(report, record.get("rule_id"), f"{path}.rule_id")
    if not isinstance(record.get("trigger"), (str, list, dict)):
        report.add_error("FIELD_TYPE", f"{path}.trigger", "must be string, list, or mapping")
    elif not _is_nonempty_value(record.get("trigger")):
        report.add_error("EMPTY_FIELD", f"{path}.trigger", "must not be empty")
    for key in ("required_context", "checks", "action", "stop_conditions"):
        _validate_string_list(report, record, key, path, nonempty=True)
    if not isinstance(record.get("output"), (str, list, dict)):
        report.add_error("FIELD_TYPE", f"{path}.output", "must be string, list, or mapping")
    elif not _is_nonempty_value(record.get("output")):
        report.add_error("EMPTY_FIELD", f"{path}.output", "must not be empty")
    _validate_string_list(report, record, "claim_ids", path)
    _validate_string_list(report, record, "relation_ids", path)
    if not _safe_member(record.get("transformation"), TRANSFORMATIONS):
        report.add_error("INVALID_TRANSFORMATION", f"{path}.transformation", "must be T0-T4")
    _validate_status(report, record.get("status"), RECORD_STATUSES, f"{path}.status")
    _validate_human_decision(report, record, path, require_gate_link=True)
    _validate_history(
        report, record, current_key="status", history_key="status_history",
        transitions=RECORD_TRANSITIONS, initial="candidate", path=path,
        require_null_initial=record.get("status") == "accepted",
    )
    _require_accepted_status_history(report, record, path)
    _validate_semantic_support(report, record, path)


def _validate_candidate(report: ValidationReport, record: Mapping[str, Any], path: str) -> None:
    _require_fields(
        report, record,
        (
            "candidate_id", "name", "stable_task", "should_trigger", "should_not_trigger",
            "inputs", "outputs", "rule_ids", "stop_conditions", "risks", "lifecycle"
        ), path,
    )
    _validate_id(report, record.get("candidate_id"), f"{path}.candidate_id")
    name = record.get("name")
    if not _is_nonempty_string(name) or not SKILL_NAME_RE.fullmatch(name):
        report.add_error("INVALID_SKILL_NAME", f"{path}.name", "must be a hyphen-case Skill name")
    elif len(name) > 64:
        report.add_error(
            "INVALID_SKILL_NAME", f"{path}.name", "must not exceed 64 characters"
        )
    else:
        _validate_no_placeholder(report, name, f"{path}.name", identifier=True)
    if not _is_nonempty_string(record.get("stable_task")):
        report.add_error("FIELD_TYPE", f"{path}.stable_task", "must be a non-empty string")
    should_trigger = _validate_string_list(report, record, "should_trigger", path, min_items=3)
    should_not_trigger = _validate_string_list(
        report, record, "should_not_trigger", path, min_items=3
    )
    normalized_trigger = [item.strip().casefold() for item in should_trigger]
    normalized_nontrigger = [item.strip().casefold() for item in should_not_trigger]
    if len(normalized_trigger) != len(set(normalized_trigger)):
        report.add_error(
            "DUPLICATE_TRIGGER_CASE", f"{path}.should_trigger",
            "should_trigger entries must be unique"
        )
    if len(normalized_nontrigger) != len(set(normalized_nontrigger)):
        report.add_error(
            "DUPLICATE_NONTRIGGER_CASE", f"{path}.should_not_trigger",
            "should_not_trigger entries must be unique"
        )
    overlap = sorted(set(normalized_trigger) & set(normalized_nontrigger))
    if overlap:
        report.add_error(
            "TRIGGER_BOUNDARY_OVERLAP", path,
            "should_trigger and should_not_trigger must not overlap"
        )
    for key in ("inputs", "outputs", "rule_ids", "stop_conditions", "risks"):
        values = _validate_string_list(report, record, key, path, nonempty=True)
        if key == "rule_ids" and len(values) != len(set(values)):
            report.add_error(
                "DUPLICATE_RULE_REFERENCE",
                f"{path}.rule_ids",
                "candidate rule_ids must not contain duplicates",
            )
    _validate_status(
        report, record.get("lifecycle"), SKILL_LIFECYCLES, f"{path}.lifecycle",
        code="INVALID_LIFECYCLE"
    )
    _validate_history(
        report, record, current_key="lifecycle", history_key="lifecycle_history",
        transitions=LIFECYCLE_TRANSITIONS, initial="draft", path=path,
        require_null_initial=_safe_member(
            record.get("lifecycle"), {"accepted", "deployed", "deprecated"}
        ),
    )
    _require_candidate_lifecycle_history(report, record, path)


def _validate_human_reviewer(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
    *,
    required: bool,
    date_key: str,
) -> None:
    reviewer_type = record.get("reviewer_type")
    if reviewer_type is not None and not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
        report.add_error(
            "HUMAN_REVIEW_REQUIRED",
            f"{path}.reviewer_type",
            f"must be null or one of: {', '.join(sorted(HUMAN_REVIEWER_TYPES))}",
        )
    for key in ("reviewer", date_key):
        if record.get(key) is not None and not _is_nonempty_string(record.get(key)):
            report.add_error(
                "FIELD_TYPE", f"{path}.{key}", "must be null or a non-empty string"
            )
    if required:
        if not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
            report.add_error(
                "HUMAN_REVIEW_REQUIRED",
                f"{path}.reviewer_type",
                "completed decision/run requires a user or human delegate",
            )
        for key in ("reviewer", date_key):
            if not _is_nonempty_string(record.get(key)):
                report.add_error(
                    "HUMAN_REVIEW_REQUIRED",
                    f"{path}.{key}",
                    "completed decision/run requires non-empty human review metadata",
                )


def _validate_gate_decision(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    _require_fields(
        report,
        record,
        (
            "decision_id", "sequence", "supersedes", "is_current", "gate",
            "candidate_id", "decision", "scope",
            "reviewer_type", "reviewer", "decided_at", "rationale", "conditions",
            "eval_run_ids", "rule_decisions",
        ),
        path,
    )
    _validate_id(report, record.get("decision_id"), f"{path}.decision_id")
    sequence = record.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        report.add_error(
            "GATE_SEQUENCE_INVALID", f"{path}.sequence", "must be a positive integer"
        )
    supersedes = record.get("supersedes")
    if supersedes is not None:
        _validate_id(report, supersedes, f"{path}.supersedes")
    if not isinstance(record.get("is_current"), bool):
        report.add_error(
            "GATE_CURRENT_INVALID", f"{path}.is_current", "must be a boolean"
        )
    gate = record.get("gate")
    if not _safe_member(gate, GATES):
        report.add_error("INVALID_GATE", f"{path}.gate", "must be gate-1 through gate-5")
    candidate_id = record.get("candidate_id")
    if candidate_id is not None:
        _validate_id(report, candidate_id, f"{path}.candidate_id")
    if _safe_member(gate, {"gate-3", "gate-4"}) and not _is_nonempty_string(candidate_id):
        report.add_error(
            "GATE_CANDIDATE_REQUIRED",
            f"{path}.candidate_id",
            "Gate 3 and Gate 4 decisions must identify a candidate",
        )
    decision = record.get("decision")
    if not _safe_member(decision, GATE_DECISIONS):
        report.add_error(
            "INVALID_GATE_DECISION",
            f"{path}.decision",
            f"must be one of: {', '.join(sorted(GATE_DECISIONS))}",
        )
    elif _safe_member(gate, GATE_DECISIONS_BY_GATE) and not _safe_member(
        decision, GATE_DECISIONS_BY_GATE[gate]
    ):
        report.add_error(
            "INVALID_GATE_DECISION",
            f"{path}.decision",
            f"{decision!r} is not valid for {gate}",
        )
    _validate_string_list(report, record, "scope", path)
    _validate_string_list(report, record, "conditions", path)
    eval_run_ids = _validate_string_list(report, record, "eval_run_ids", path)
    rule_decisions = _require_list(report, record, "rule_decisions", path)
    if gate != "gate-3" and rule_decisions:
        report.add_error(
            "RULE_DECISIONS_NOT_ALLOWED",
            f"{path}.rule_decisions",
            "rule_decisions are allowed only on Gate 3 records",
        )
    seen_rule_ids: set[str] = set()
    for index, item in enumerate(rule_decisions):
        item_path = f"{path}.rule_decisions[{index}]"
        if not isinstance(item, dict):
            report.add_error("FIELD_TYPE", item_path, "must be a mapping")
            continue
        _require_fields(report, item, ("rule_id", "decision", "rationale"), item_path)
        rule_id = _validate_id(report, item.get("rule_id"), f"{item_path}.rule_id")
        if rule_id is not None:
            if rule_id in seen_rule_ids:
                report.add_error(
                    "DUPLICATE_RULE_DECISION",
                    f"{item_path}.rule_id",
                    "each rule may be decided only once per Gate 3 record",
                )
            seen_rule_ids.add(rule_id)
        if not _safe_member(item.get("decision"), RULE_GATE_DECISIONS):
            report.add_error(
                "INVALID_RULE_DECISION",
                f"{item_path}.decision",
                f"must be one of: {', '.join(sorted(RULE_GATE_DECISIONS))}",
            )
        if not _is_nonempty_string(item.get("rationale")):
            report.add_error(
                "INVALID_RULE_DECISION",
                f"{item_path}.rationale",
                "rule decision requires a non-empty rationale",
            )
    if not isinstance(record.get("rationale"), str):
        report.add_error("FIELD_TYPE", f"{path}.rationale", "must be a string")
    completed_decision = decision != "pending" and _safe_member(decision, GATE_DECISIONS)
    _validate_human_reviewer(
        report, record, path, required=completed_decision, date_key="decided_at"
    )
    if completed_decision and not _is_nonempty_string(record.get("rationale")):
        report.add_error(
            "HUMAN_REVIEW_REQUIRED",
            f"{path}.rationale",
            "completed gate decision requires a non-empty rationale",
        )
    if gate == "gate-4" and decision == "accepted" and not eval_run_ids:
        report.add_error(
            "GATE4_EVAL_REQUIRED",
            f"{path}.eval_run_ids",
            "accepted Gate 4 decision must cite at least one eval run",
        )
    if gate == "gate-3" and decision == "approved-for-eval":
        if record.get("reviewer_type") != "user":
            report.add_error(
                "GATE3_USER_APPROVAL_REQUIRED",
                f"{path}.reviewer_type",
                "Gate 3 approved-for-eval requires reviewer_type: user",
            )
        if not rule_decisions:
            report.add_error(
                "GATE3_RULE_DECISIONS_REQUIRED",
                f"{path}.rule_decisions",
                "Gate 3 approved-for-eval must decide every candidate rule",
            )


def _validate_materialization(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    _require_fields(
        report,
        record,
        (
            "materialization_id", "candidate_id", "gate3_decision_id", "status",
            "candidate_path", "candidate_hash", "materialized_at", "rule_ids",
            "quick_validation",
        ),
        path,
    )
    _validate_id(report, record.get("materialization_id"), f"{path}.materialization_id")
    _validate_id(report, record.get("candidate_id"), f"{path}.candidate_id")
    gate3_decision_id = record.get("gate3_decision_id")
    if gate3_decision_id is not None:
        _validate_id(report, gate3_decision_id, f"{path}.gate3_decision_id")
    status = record.get("status")
    if not _safe_member(status, MATERIALIZATION_STATUSES):
        report.add_error(
            "INVALID_MATERIALIZATION_STATUS",
            f"{path}.status",
            f"must be one of: {', '.join(sorted(MATERIALIZATION_STATUSES))}",
        )
    for key in ("candidate_path", "materialized_at"):
        value = record.get(key)
        if value is not None and not _is_nonempty_string(value):
            report.add_error(
                "FIELD_TYPE", f"{path}.{key}", "must be null or a non-empty string"
            )
    candidate_hash = record.get("candidate_hash")
    if candidate_hash is not None:
        _validate_content_hash(report, candidate_hash, f"{path}.candidate_hash")
    rule_ids = _validate_string_list(report, record, "rule_ids", path)
    if len(rule_ids) != len(set(rule_ids)):
        report.add_error(
            "DUPLICATE_RULE_REFERENCE",
            f"{path}.rule_ids",
            "materialization rule_ids must not contain duplicates",
        )
    quick_validation = record.get("quick_validation")
    if not isinstance(quick_validation, dict):
        report.add_error(
            "MATERIALIZATION_QUICK_VALIDATION_INVALID",
            f"{path}.quick_validation",
            "must be a mapping",
        )
        quick_validation = {}
    else:
        _require_fields(
            report,
            quick_validation,
            ("status", "validator", "validated_at", "candidate_hash"),
            f"{path}.quick_validation",
        )
    quick_status = quick_validation.get("status")
    if not _safe_member(quick_status, QUICK_VALIDATION_STATUSES):
        report.add_error(
            "MATERIALIZATION_QUICK_VALIDATION_INVALID",
            f"{path}.quick_validation.status",
            f"must be one of: {', '.join(sorted(QUICK_VALIDATION_STATUSES))}",
        )
    for key in ("validator", "validated_at"):
        value = quick_validation.get(key)
        if value is not None and not _is_nonempty_string(value):
            report.add_error(
                "FIELD_TYPE",
                f"{path}.quick_validation.{key}",
                "must be null or a non-empty string",
            )
    quick_validator = quick_validation.get("validator")
    if quick_validator is not None and quick_validator != "quick_validate.py":
        report.add_error(
            "MATERIALIZATION_QUICK_VALIDATION_INVALID",
            f"{path}.quick_validation.validator",
            "validator must be null or exactly 'quick_validate.py'",
        )
    quick_candidate_hash = quick_validation.get("candidate_hash")
    if quick_candidate_hash is not None and not TREE_HASH_RE.fullmatch(
        quick_candidate_hash if isinstance(quick_candidate_hash, str) else ""
    ):
        report.add_error(
            "MATERIALIZATION_QUICK_VALIDATION_HASH_INVALID",
            f"{path}.quick_validation.candidate_hash",
            "quick-validation candidate_hash must use sha256:<64 lowercase hex>",
        )
    if quick_status == "pass" or status == "completed":
        if not TREE_HASH_RE.fullmatch(
            quick_candidate_hash if isinstance(quick_candidate_hash, str) else ""
        ):
            report.add_error(
                "MATERIALIZATION_QUICK_VALIDATION_REQUIRED",
                f"{path}.quick_validation.candidate_hash",
                "passing/completed materialization requires the full validated candidate hash",
            )
        elif quick_candidate_hash != candidate_hash:
            report.add_error(
                "MATERIALIZATION_QUICK_VALIDATION_HASH_MISMATCH",
                f"{path}.quick_validation.candidate_hash",
                "quick-validation candidate_hash must exactly match materialization candidate_hash",
            )
    if status == "completed":
        if not _is_nonempty_string(gate3_decision_id):
            report.add_error(
                "MATERIALIZATION_GATE3_REQUIRED",
                f"{path}.gate3_decision_id",
                "completed materialization must reference its Gate 3 approval",
            )
        for key in ("candidate_path", "candidate_hash", "materialized_at"):
            if not _is_nonempty_string(record.get(key)):
                report.add_error(
                    "MATERIALIZATION_INCOMPLETE",
                    f"{path}.{key}",
                    "completed materialization requires a non-empty value",
                )
        if not rule_ids:
            report.add_error(
                "MATERIALIZATION_INCOMPLETE",
                f"{path}.rule_ids",
                "completed materialization requires at least one approved rule",
            )
        if quick_status != "pass":
            report.add_error(
                "MATERIALIZATION_QUICK_VALIDATION_REQUIRED",
                f"{path}.quick_validation.status",
                "completed materialization requires quick-validation status pass",
            )
        for key in ("validator", "validated_at", "candidate_hash"):
            if not _is_nonempty_string(quick_validation.get(key)):
                report.add_error(
                    "MATERIALIZATION_QUICK_VALIDATION_REQUIRED",
                    f"{path}.quick_validation.{key}",
                    "completed materialization requires quick-validation metadata",
                )


def _validate_eval_run(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
) -> None:
    _require_fields(
        report,
        record,
        (
            "eval_run_id", "candidate_id", "materialization_id", "case_type", "case_id",
            "case_definition_hash", "status", "outcome", "fixture_id",
            "fixture_path", "fixture_hash", "source_ids", "holdout", "rule_ids",
            "candidate_hash", "execution_environment", "baseline_output_path",
            "baseline_output_hash", "with_skill_output_path", "with_skill_output_hash", "rubric_id", "score",
            "max_score", "pass_threshold", "dimension_scores",
            "fatal_failures_observed", "leakage_controls",
            "reviewer_type", "reviewer", "completed_at", "limitations",
        ),
        path,
    )
    _validate_id(report, record.get("eval_run_id"), f"{path}.eval_run_id")
    _validate_id(report, record.get("candidate_id"), f"{path}.candidate_id")
    materialization_id = record.get("materialization_id")
    if materialization_id is not None:
        _validate_id(report, materialization_id, f"{path}.materialization_id")
    if not _safe_member(record.get("case_type"), EVAL_CASE_TYPES):
        report.add_error(
            "INVALID_EVAL_CASE_TYPE",
            f"{path}.case_type",
            f"must be one of: {', '.join(sorted(EVAL_CASE_TYPES))}",
        )
    _validate_id(report, record.get("case_id"), f"{path}.case_id")
    case_definition_hash = record.get("case_definition_hash")
    if case_definition_hash is not None and _normalized_full_sha256(case_definition_hash) is None:
        report.add_error(
            "EVAL_CASE_DEFINITION_HASH_INVALID",
            f"{path}.case_definition_hash",
            "must be null or a complete SHA-256",
        )
    status = record.get("status")
    if not _safe_member(status, EVAL_STATUSES):
        report.add_error(
            "INVALID_EVAL_STATUS",
            f"{path}.status",
            f"must be one of: {', '.join(sorted(EVAL_STATUSES))}",
        )
    outcome = record.get("outcome")
    if not _safe_member(outcome, EVAL_OUTCOMES):
        report.add_error(
            "INVALID_EVAL_OUTCOME",
            f"{path}.outcome",
            "must be null, pass, fail, or inconclusive",
        )
    _validate_id(report, record.get("fixture_id"), f"{path}.fixture_id")
    for key in ("fixture_path", "baseline_output_path", "with_skill_output_path"):
        if record.get(key) is not None and not _is_nonempty_string(record.get(key)):
            report.add_error("FIELD_TYPE", f"{path}.{key}", "must be null or a non-empty string")
    source_ids = _validate_string_list(report, record, "source_ids", path, nonempty=True)
    for index, source_id in enumerate(source_ids):
        _validate_id(report, source_id, f"{path}.source_ids[{index}]")
    if not isinstance(record.get("holdout"), bool):
        report.add_error("FIELD_TYPE", f"{path}.holdout", "must be a boolean")
    _validate_string_list(report, record, "rule_ids", path, nonempty=True)
    _validate_id(report, record.get("rubric_id"), f"{path}.rubric_id")
    _validate_string_list(report, record, "limitations", path)
    _validate_string_list(report, record, "fatal_failures_observed", path)
    dimension_scores = record.get("dimension_scores")
    if dimension_scores is not None and not isinstance(dimension_scores, dict):
        report.add_error(
            "FIELD_TYPE", f"{path}.dimension_scores", "must be null or a mapping"
        )
    leakage_controls = record.get("leakage_controls")
    if leakage_controls is not None and not isinstance(leakage_controls, dict):
        report.add_error(
            "FIELD_TYPE", f"{path}.leakage_controls", "must be null or a mapping"
        )
    environment = record.get("execution_environment")
    if environment is not None and not isinstance(environment, (str, list, dict)):
        report.add_error(
            "FIELD_TYPE",
            f"{path}.execution_environment",
            "must be null, string, list, or mapping",
        )

    for key in (
        "fixture_hash", "candidate_hash", "baseline_output_hash", "with_skill_output_hash"
    ):
        value = record.get(key)
        if value is not None:
            _validate_content_hash(report, value, f"{path}.{key}")
    for key in ("score", "max_score", "pass_threshold"):
        value = record.get(key)
        if value is not None and not _is_number(value):
            report.add_error("FIELD_TYPE", f"{path}.{key}", "must be null or numeric")

    completed = status == "completed"
    _validate_human_reviewer(
        report, record, path, required=completed, date_key="completed_at"
    )
    if completed:
        if not _is_nonempty_string(materialization_id):
            report.add_error(
                "EVAL_MATERIALIZATION_REQUIRED",
                f"{path}.materialization_id",
                "completed eval run must identify its completed materialization",
            )
        if not _safe_member(outcome, {"pass", "fail", "inconclusive"}):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.outcome",
                "completed eval run requires a non-null outcome",
            )
        if not _is_nonempty_string(record.get("case_definition_hash")):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.case_definition_hash",
                "completed eval run requires a case-definition hash",
            )
        if not isinstance(record.get("dimension_scores"), dict) or not record.get("dimension_scores"):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.dimension_scores",
                "completed eval run requires per-dimension scores",
            )
        if not isinstance(record.get("fatal_failures_observed"), list):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.fatal_failures_observed",
                "completed eval run requires a fatal-failures list",
            )
        if not isinstance(record.get("leakage_controls"), dict) or not record.get("leakage_controls"):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.leakage_controls",
                "completed eval run requires leakage-control metadata",
            )
        for key in (
            "fixture_hash", "candidate_hash", "baseline_output_hash", "with_skill_output_hash"
        ):
            if not _is_nonempty_string(record.get(key)):
                report.add_error(
                    "EVAL_RUN_INCOMPLETE",
                    f"{path}.{key}",
                    "completed eval run requires a content hash",
                )
        for key in ("fixture_path", "baseline_output_path", "with_skill_output_path"):
            if not _is_nonempty_string(record.get(key)):
                report.add_error(
                    "EVAL_RUN_INCOMPLETE",
                    f"{path}.{key}",
                    "completed eval run requires a replayable artifact path",
                )
        if not _is_nonempty_value(record.get("execution_environment")):
            report.add_error(
                "EVAL_RUN_INCOMPLETE",
                f"{path}.execution_environment",
                "completed eval run requires execution environment metadata",
            )
        for key in ("score", "max_score", "pass_threshold"):
            if not _is_number(record.get(key)):
                report.add_error(
                    "EVAL_RUN_INCOMPLETE",
                    f"{path}.{key}",
                    "completed eval run requires a numeric value",
                )
    elif outcome is not None:
        report.add_error(
            "EVAL_RUN_STATE_MISMATCH",
            f"{path}.outcome",
            "non-completed eval run must not declare an outcome",
        )

    score = record.get("score")
    max_score = record.get("max_score")
    threshold = record.get("pass_threshold")
    if _is_number(max_score) and max_score <= 0:
        report.add_error("EVAL_SCORE_INVALID", f"{path}.max_score", "must be greater than zero")
    if _is_number(score) and _is_number(max_score) and not 0 <= score <= max_score:
        report.add_error("EVAL_SCORE_INVALID", f"{path}.score", "must be between 0 and max_score")
    if _is_number(threshold) and _is_number(max_score) and not 0 <= threshold <= max_score:
        report.add_error(
            "EVAL_SCORE_INVALID",
            f"{path}.pass_threshold",
            "must be between 0 and max_score",
        )
    if outcome == "pass" and _is_number(score) and _is_number(threshold) and score < threshold:
        report.add_error(
            "EVAL_SCORE_INVALID", f"{path}.score", "pass outcome requires score >= pass_threshold"
        )
    if outcome == "fail" and _is_number(score) and _is_number(threshold) and score >= threshold:
        report.add_error(
            "EVAL_SCORE_INVALID", f"{path}.score", "fail outcome requires score < pass_threshold"
        )


def _validate_correction(
    report: ValidationReport,
    record: Mapping[str, Any],
    path: str,
    *,
    overlay_source_id: Any,
) -> bool:
    _require_fields(
        report,
        record,
        (
            "correction_id", "evidence_id", "locator", "issue_type", "raw_value",
            "proposed_value", "basis", "status", "human_decision",
            "applies_to_claim_ids", "resolved_quality_flags", "resulting_value",
        ),
        path,
    )
    _validate_id(report, record.get("correction_id"), f"{path}.correction_id")
    _validate_id(report, record.get("evidence_id"), f"{path}.evidence_id")
    if not _is_nonempty_string(record.get("issue_type")):
        report.add_error("FIELD_TYPE", f"{path}.issue_type", "must be a non-empty string")
    if not isinstance(record.get("raw_value"), str):
        report.add_error("FIELD_TYPE", f"{path}.raw_value", "must be a string")
    for key in ("proposed_value", "resulting_value"):
        if record.get(key) is not None and not isinstance(record.get(key), str):
            report.add_error("FIELD_TYPE", f"{path}.{key}", "must be null or a string")
    if not _is_nonempty_string(record.get("basis")):
        report.add_error("FIELD_TYPE", f"{path}.basis", "must be a non-empty string")
    _validate_string_list(report, record, "applies_to_claim_ids", path)
    _validate_string_list(report, record, "resolved_quality_flags", path)
    _validate_status(report, record.get("status"), RECORD_STATUSES, f"{path}.status")

    locator_valid = _validate_locator(
        report,
        {"source_id": overlay_source_id, "locator": record.get("locator")},
        path,
    )
    decision = record.get("human_decision")
    if not isinstance(decision, dict):
        report.add_error(
            "CORRECTION_DECISION_INVALID",
            f"{path}.human_decision",
            "must be a decision mapping",
        )
        return locator_valid
    _require_fields(
        report,
        decision,
        ("decision", "reviewer_type", "reviewer", "decided_at", "rationale"),
        f"{path}.human_decision",
    )
    reviewer_type = decision.get("reviewer_type")
    if reviewer_type is not None and not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
        report.add_error(
            "CORRECTION_DECISION_INVALID",
            f"{path}.human_decision.reviewer_type",
            "must be null, user, or human-delegate",
        )
    decision_value = decision.get("decision")
    if not _safe_member(decision_value, HUMAN_DECISIONS):
        report.add_error(
            "CORRECTION_DECISION_INVALID",
            f"{path}.human_decision.decision",
            f"must be one of: {', '.join(sorted(HUMAN_DECISIONS))}",
        )
    decided = _safe_member(decision_value, {"accepted", "revised", "rejected"})
    if decided:
        if not _safe_member(reviewer_type, HUMAN_REVIEWER_TYPES):
            report.add_error(
                "CORRECTION_DECISION_INVALID",
                f"{path}.human_decision.reviewer_type",
                "completed correction decision requires an explicit human reviewer type",
            )
        for key in ("reviewer", "decided_at", "rationale"):
            if not _is_nonempty_string(decision.get(key)):
                report.add_error(
                    "CORRECTION_DECISION_INVALID",
                    f"{path}.human_decision.{key}",
                    "completed correction decision requires non-empty metadata",
                )
    if record.get("status") == "accepted":
        if not _safe_member(decision_value, {"accepted", "revised"}):
            report.add_error(
                "CORRECTION_NOT_ACCEPTED",
                f"{path}.human_decision.decision",
                "accepted correction requires accepted or revised human decision",
            )
        if not _is_nonempty_string(record.get("resulting_value")):
            report.add_error(
                "CORRECTION_RESULT_MISSING",
                f"{path}.resulting_value",
                "accepted correction requires a resulting value",
            )
    return locator_valid


def _gate_series_key(record: Mapping[str, Any]) -> tuple[str, str | None]:
    gate = record.get("gate")
    candidate_id = record.get("candidate_id")
    safe_gate = gate if isinstance(gate, str) else f"<invalid-gate:{gate!r}>"
    safe_candidate = (
        candidate_id
        if isinstance(candidate_id, str) or candidate_id is None
        else f"<invalid-candidate:{candidate_id!r}>"
    )
    return (safe_gate, safe_candidate)


def _validate_gate_decision_chains(
    report: ValidationReport,
    gate_decisions: Sequence[Mapping[str, Any]],
) -> dict[tuple[Any, Any], Mapping[str, Any]]:
    """Validate one linear, explicitly current decision chain per gate/candidate."""
    sequences = [record.get("sequence") for record in gate_decisions]
    if all(isinstance(item, int) and not isinstance(item, bool) for item in sequences):
        if sequences != sorted(sequences):
            report.add_error(
                "GATE_SEQUENCE_INVALID",
                "gate-decisions.yml.gate_decisions",
                "gate decisions must be stored in strictly increasing sequence order",
            )
        if sequences != list(range(1, len(sequences) + 1)):
            report.add_error(
                "GATE_SEQUENCE_INVALID",
                "gate-decisions.yml.gate_decisions",
                "gate decision sequence must be unique, contiguous, and start at 1",
            )

    decision_by_id = {
        record.get("decision_id"): record
        for record in gate_decisions
        if _is_nonempty_string(record.get("decision_id"))
    }
    groups: dict[tuple[Any, Any], list[Mapping[str, Any]]] = {}
    for record in gate_decisions:
        groups.setdefault(_gate_series_key(record), []).append(record)
        supersedes = record.get("supersedes")
        if _is_nonempty_string(supersedes) and supersedes not in decision_by_id:
            report.add_error(
                "GATE_SUPERSEDES_INVALID",
                f"gate_decisions.{record.get('decision_id')}.supersedes",
                f"superseded decision {supersedes!r} does not exist",
            )

    current: dict[tuple[Any, Any], Mapping[str, Any]] = {}
    for key, records in groups.items():
        ordered = sorted(
            records,
            key=lambda item: item.get("sequence")
            if isinstance(item.get("sequence"), int) and not isinstance(item.get("sequence"), bool)
            else sys.maxsize,
        )
        for index, record in enumerate(ordered):
            expected_supersedes = None if index == 0 else ordered[index - 1].get("decision_id")
            if record.get("supersedes") != expected_supersedes:
                report.add_error(
                    "GATE_SUPERSEDES_INVALID",
                    f"gate_decisions.{record.get('decision_id')}.supersedes",
                    "each decision after the first must supersede the immediately previous "
                    "decision in the same gate/candidate series",
                )
            expected_current = index == len(ordered) - 1
            if record.get("is_current") is not expected_current:
                report.add_error(
                    "GATE_CURRENT_INVALID",
                    f"gate_decisions.{record.get('decision_id')}.is_current",
                    "only the terminal decision in a gate/candidate series may be current",
                )
        declared_current = [item for item in ordered if item.get("is_current") is True]
        if len(declared_current) != 1:
            report.add_error(
                "GATE_CURRENT_INVALID",
                f"gate-decisions.yml.gate_decisions[{key!r}]",
                "each gate/candidate series must have exactly one current decision",
            )
        elif declared_current[0] is ordered[-1]:
            current[key] = declared_current[0]
    return current


def _applicable_current_gate(
    current: Mapping[tuple[Any, Any], Mapping[str, Any]],
    gate: str,
    candidate_id: Any,
) -> Mapping[str, Any] | None:
    exact = (
        current.get((gate, candidate_id))
        if isinstance(candidate_id, str) or candidate_id is None
        else None
    )
    if exact is not None:
        return exact
    return current.get((gate, None))


def _validate_gate_prerequisites(
    report: ValidationReport,
    current: Mapping[tuple[Any, Any], Mapping[str, Any]],
) -> None:
    required_gates = {
        "gate-2": ("gate-1",),
        "gate-3": ("gate-1", "gate-2"),
        "gate-4": ("gate-3",),
        "gate-5": ("gate-4",),
    }
    for record in current.values():
        gate = record.get("gate")
        candidate_id = record.get("candidate_id")
        for required_gate in required_gates.get(gate, ()) if isinstance(gate, str) else ():
            prerequisite = _applicable_current_gate(current, required_gate, candidate_id)
            allowed = POSITIVE_GATE_DECISIONS[required_gate]
            if prerequisite is None or not _safe_member(
                prerequisite.get("decision"), allowed
            ):
                report.add_error(
                    "GATE_PREREQUISITE_MISSING",
                    f"gate_decisions.{record.get('decision_id')}",
                    f"current {gate} requires a current positive {required_gate} decision",
                )
                continue
            prerequisite_sequence = prerequisite.get("sequence")
            sequence = record.get("sequence")
            if (
                isinstance(prerequisite_sequence, int)
                and isinstance(sequence, int)
                and prerequisite_sequence >= sequence
            ):
                report.add_error(
                    "GATE_SEQUENCE_INVALID",
                    f"gate_decisions.{record.get('decision_id')}.sequence",
                    f"{required_gate} must precede {gate}",
                )


def _approved_rule_ids(gate3_decision: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    raw_rule_decisions = gate3_decision.get("rule_decisions", [])
    for item in raw_rule_decisions if isinstance(raw_rule_decisions, list) else []:
        if (
            isinstance(item, dict)
            and _safe_member(item.get("decision"), {"accepted", "revised"})
            and _is_nonempty_string(item.get("rule_id"))
        ):
            result.append(item["rule_id"])
    return result


def _validate_exact_mapping_fields(
    report: ValidationReport,
    record: Mapping[Any, Any],
    expected_fields: Iterable[str],
    path: str,
    *,
    code: str,
) -> None:
    """Require an exact mapping shape for security-sensitive snapshot data."""
    expected = set(expected_fields)
    for key in expected:
        if key not in record:
            report.add_error(code, f"{path}.{key}", "required field is missing")
    for key in record:
        if key not in expected:
            report.add_error(
                code,
                f"{path}.{key!r}",
                "unexpected field is not allowed in this versioned contract",
            )


def _validate_gate3_approval_snapshots(
    report: ValidationReport,
    distillation_root: Path,
    gate_decisions: Sequence[Mapping[str, Any]],
    candidates_by_id: Mapping[str, Mapping[str, Any]],
) -> None:
    """Bind every declared current Gate 3 approval to immutable input bytes.

    Historical/superseded approvals intentionally remain compatible with the
    pre-snapshot schema. Only a decision that declares itself current and
    approved-for-eval must satisfy this contract.
    """
    for index, decision in enumerate(gate_decisions):
        if not (
            decision.get("gate") == "gate-3"
            and decision.get("is_current") is True
            and decision.get("decision") == "approved-for-eval"
        ):
            continue

        path = f"gate-decisions.yml.gate_decisions[{index}].approval_snapshot"
        snapshot = decision.get("approval_snapshot")
        if not isinstance(snapshot, dict):
            report.add_error(
                "GATE3_APPROVAL_SNAPSHOT_REQUIRED",
                path,
                "current approved-for-eval Gate 3 decision requires an approval_snapshot mapping",
            )
            continue

        snapshot_contract = snapshot.get("contract")
        expected_snapshot_fields = (
            "contract", "candidate_path", "candidate_hash", "governance_hashes",
            "current_gate1_decision_id", "task_contract", "task_coverage",
            "candidate_stable_task_ids",
        ) if snapshot_contract == GATE3_APPROVAL_SNAPSHOT_CONTRACT else (
            "contract", "candidate_path", "candidate_hash", "governance_hashes",
        )
        _validate_exact_mapping_fields(
            report,
            snapshot,
            expected_snapshot_fields,
            path,
            code="GATE3_APPROVAL_SNAPSHOT_INVALID",
        )

        if snapshot_contract not in {
            GATE3_APPROVAL_SNAPSHOT_CONTRACT,
            GATE3_APPROVAL_SNAPSHOT_LEGACY_CONTRACT,
        }:
            report.add_error(
                "GATE3_APPROVAL_SNAPSHOT_CONTRACT_INVALID",
                f"{path}.contract",
                "must be a recognized Gate 3 approval snapshot contract",
            )

        candidate_path = snapshot.get("candidate_path")
        canonical_path: str | None = None
        try:
            canonical_path = canonical_candidate_path(candidate_path)
        except CandidateTreeError as exc:
            report.add_error(
                "GATE3_APPROVAL_CANDIDATE_PATH_INVALID",
                f"{path}.candidate_path",
                str(exc),
            )

        candidate_id = decision.get("candidate_id")
        candidate = (
            candidates_by_id.get(candidate_id)
            if _is_nonempty_string(candidate_id)
            else None
        )
        if canonical_path is not None and candidate is not None:
            candidate_name = candidate.get("name")
            if (
                _is_nonempty_string(candidate_name)
                and PurePosixPath(canonical_path).name != candidate_name
            ):
                report.add_error(
                    "GATE3_APPROVAL_CANDIDATE_PATH_MISMATCH",
                    f"{path}.candidate_path",
                    "candidate_path final component must exactly match the approved "
                    f"candidate name {candidate_name!r}",
                )

        recorded_candidate_hash = snapshot.get("candidate_hash")
        recorded_candidate_hash_valid = isinstance(
            recorded_candidate_hash, str
        ) and bool(TREE_HASH_RE.fullmatch(recorded_candidate_hash))
        if not recorded_candidate_hash_valid:
            report.add_error(
                "GATE3_APPROVAL_CANDIDATE_HASH_INVALID",
                f"{path}.candidate_hash",
                "must use sha256:<64 lowercase hex> from candidate-tree:v1",
            )

        if canonical_path is not None:
            try:
                actual_candidate_hash = candidate_tree_sha256(
                    distillation_root, canonical_path
                )
            except CandidateTreeError as exc:
                report.add_error(
                    "GATE3_APPROVAL_CANDIDATE_TREE_INVALID",
                    f"{path}.candidate_path",
                    str(exc),
                )
            else:
                if (
                    recorded_candidate_hash_valid
                    and recorded_candidate_hash != actual_candidate_hash
                ):
                    report.add_error(
                        "GATE3_APPROVAL_CANDIDATE_HASH_MISMATCH",
                        f"{path}.candidate_hash",
                        f"recorded hash {recorded_candidate_hash!r} does not match "
                        f"the current candidate tree {actual_candidate_hash!r}",
                    )

        governance_hashes = snapshot.get("governance_hashes")
        if not isinstance(governance_hashes, dict):
            report.add_error(
                "GATE3_APPROVAL_GOVERNANCE_HASHES_INVALID",
                f"{path}.governance_hashes",
                "must be a mapping containing exactly the three frozen governance files",
            )
            continue

        _validate_exact_mapping_fields(
            report,
            governance_hashes,
            APPROVAL_SNAPSHOT_GOVERNANCE_FILES,
            f"{path}.governance_hashes",
            code="GATE3_APPROVAL_GOVERNANCE_HASHES_INVALID",
        )
        for filename in APPROVAL_SNAPSHOT_GOVERNANCE_FILES:
            hash_path = f"{path}.governance_hashes.{filename}"
            expected_hash = governance_hashes.get(filename)
            expected_hash_valid = isinstance(expected_hash, str) and bool(
                TREE_HASH_RE.fullmatch(expected_hash)
            )
            if not expected_hash_valid:
                report.add_error(
                    "GATE3_APPROVAL_GOVERNANCE_HASH_INVALID",
                    hash_path,
                    "must use sha256:<64 lowercase hex> over the complete raw file bytes",
                )
            try:
                _, raw_bytes = _read_distillation_artifact(
                    distillation_root, filename
                )
            except _ArtifactFileError as exc:
                report.add_error(
                    "GATE3_APPROVAL_GOVERNANCE_FILE_INVALID",
                    hash_path,
                    f"{exc.code}: {exc.message}",
                )
                continue
            actual_hash = f"sha256:{hashlib.sha256(raw_bytes).hexdigest()}"
            if expected_hash_valid and expected_hash != actual_hash:
                report.add_error(
                    "GATE3_APPROVAL_GOVERNANCE_HASH_MISMATCH",
                    hash_path,
                    f"recorded hash {expected_hash!r} does not match the complete "
                    f"raw file hash {actual_hash!r}",
                )


def _validate_gate3_rule_alignment(
    report: ValidationReport,
    gate_decisions: Sequence[Mapping[str, Any]],
    current: Mapping[tuple[Any, Any], Mapping[str, Any]],
    candidates_by_id: Mapping[str, Mapping[str, Any]],
    rules_by_id: Mapping[str, Mapping[str, Any]],
    rule_paths: Mapping[str, str],
) -> None:
    gate_by_id = {
        record.get("decision_id"): record
        for record in gate_decisions
        if _is_nonempty_string(record.get("decision_id"))
    }
    current_ids = {
        record.get("decision_id") for record in current.values()
        if _is_nonempty_string(record.get("decision_id"))
    }
    for decision in gate_decisions:
        if decision.get("gate") != "gate-3":
            continue
        decision_path = f"gate_decisions.{decision.get('decision_id')}"
        rule_decisions = decision.get("rule_decisions", [])
        if not isinstance(rule_decisions, list):
            continue
        for index, item in enumerate(rule_decisions):
            if not isinstance(item, dict):
                continue
            rule_id = item.get("rule_id")
            if _is_nonempty_string(rule_id) and rule_id not in rules_by_id:
                report.add_error(
                    "MISSING_FOREIGN_KEY",
                    f"{decision_path}.rule_decisions[{index}].rule_id",
                    f"referenced ID {rule_id!r} does not exist",
                )

        if decision.get("decision") != "approved-for-eval":
            continue
        is_current = _safe_member(decision.get("decision_id"), current_ids)
        if not is_current:
            continue
        candidate_id = decision.get("candidate_id")
        candidate = (
            candidates_by_id.get(candidate_id)
            if _is_nonempty_string(candidate_id)
            else None
        )
        if candidate is None:
            continue
        candidate_rule_ids = candidate.get("rule_ids", [])
        candidate_rule_strings = _string_items(candidate_rule_ids)
        decided_rule_ids = [
            item.get("rule_id")
            for item in rule_decisions
            if isinstance(item, dict) and isinstance(item.get("rule_id"), str)
        ]
        if (
            not _is_string_list(candidate_rule_ids)
            or len(decided_rule_ids) != len(rule_decisions)
            or len(decided_rule_ids) != len(set(decided_rule_ids))
            or set(decided_rule_ids) != set(candidate_rule_strings)
        ):
            report.add_error(
                "GATE3_RULE_COVERAGE",
                f"{decision_path}.rule_decisions",
                "current approved Gate 3 must decide every current candidate rule exactly once",
            )

        for item in rule_decisions:
            if not isinstance(item, dict):
                continue
            rule_id = item.get("rule_id")
            rule = rules_by_id.get(rule_id) if _is_nonempty_string(rule_id) else None
            if rule is None:
                continue
            rule_path = rule_paths.get(rule_id, f"rules.{rule_id}")
            rule_decision = item.get("decision")
            expected_status = (
                "accepted"
                if _safe_member(rule_decision, {"accepted", "revised"})
                else "rejected"
            )
            if rule.get("status") != expected_status:
                report.add_error(
                    "GATE3_RULE_STATE_MISMATCH",
                    f"{rule_path}.status",
                    f"Gate 3 {rule_decision!r} requires status {expected_status!r}",
                )
            human_decision = rule.get("human_decision")
            expected_metadata = {
                "decision": rule_decision,
                "reviewer_type": "user",
                "reviewer": decision.get("reviewer"),
                "decided_at": decision.get("decided_at"),
                "rationale": item.get("rationale"),
                "gate_decision_id": decision.get("decision_id"),
            }
            if not isinstance(human_decision, dict):
                report.add_error(
                    "GATE3_RULE_DECISION_MISMATCH",
                    f"{rule_path}.human_decision",
                    "Gate 3 rule decision must be written back to the rule",
                )
            else:
                for key, expected in expected_metadata.items():
                    if human_decision.get(key) != expected:
                        report.add_error(
                            "GATE3_RULE_DECISION_MISMATCH",
                            f"{rule_path}.human_decision.{key}",
                            "rule decision metadata must match the current Gate 3 record",
                        )
            history = rule.get("status_history")
            if not isinstance(history, list) or not history:
                report.add_error(
                    "GATE3_RULE_HISTORY_MISMATCH",
                    f"{rule_path}.status_history",
                    "decided Gate 3 rule requires a complete status history",
                )
                continue
            first = history[0] if isinstance(history[0], dict) else {}
            last = history[-1] if isinstance(history[-1], dict) else {}
            if first.get("from") is not None or first.get("to") != "candidate":
                report.add_error(
                    "GATE3_RULE_HISTORY_MISMATCH",
                    f"{rule_path}.status_history[0]",
                    "Gate 3-decided rule history must start from null into candidate",
                )
            expected_last = {
                "to": expected_status,
                "decided_by": decision.get("reviewer"),
                "decided_at": decision.get("decided_at"),
                "rationale": item.get("rationale"),
            }
            for key, expected in expected_last.items():
                if last.get(key) != expected:
                    report.add_error(
                        "GATE3_RULE_HISTORY_MISMATCH",
                        f"{rule_path}.status_history[-1].{key}",
                        "final rule history event must match the current Gate 3 rule decision",
                    )

    for rule_id, rule in rules_by_id.items():
        if not _safe_member(rule.get("status"), {"accepted", "rejected"}):
            continue
        if not _safe_member(rule.get("transformation"), {"T3", "T4"}):
            continue
        rule_path = rule_paths.get(rule_id, f"rules.{rule_id}")
        human_decision = rule.get("human_decision")
        gate_id = human_decision.get("gate_decision_id") if isinstance(human_decision, dict) else None
        gate = gate_by_id.get(gate_id) if _is_nonempty_string(gate_id) else None
        if (
            gate is None
            or gate.get("gate") != "gate-3"
            or gate.get("decision") != "approved-for-eval"
            or not _safe_member(gate_id, current_ids)
        ):
            report.add_error(
                "RULE_CURRENT_GATE3_REQUIRED",
                f"{rule_path}.human_decision.gate_decision_id",
                "accepted/rejected T3/T4 rule must link the current approved Gate 3 decision",
            )


def _validate_materialization_links(
    report: ValidationReport,
    distillation_root: Path,
    materializations: Sequence[Mapping[str, Any]],
    current: Mapping[tuple[Any, Any], Mapping[str, Any]],
    gate_by_id: Mapping[str, Mapping[str, Any]],
    candidates_by_id: Mapping[str, Mapping[str, Any]],
    rules_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, CandidateEvalContract]:
    contracts: dict[str, CandidateEvalContract] = {}
    for index, record in enumerate(materializations):
        path = f"gate-decisions.yml.materializations[{index}]"
        candidate_id = record.get("candidate_id")
        if _is_nonempty_string(candidate_id) and candidate_id not in candidates_by_id:
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"{path}.candidate_id",
                f"referenced ID {candidate_id!r} does not exist",
            )
        gate3_id = record.get("gate3_decision_id")
        if _is_nonempty_string(gate3_id) and gate3_id not in gate_by_id:
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"{path}.gate3_decision_id",
                f"referenced ID {gate3_id!r} does not exist",
            )
        raw_rule_ids = record.get("rule_ids", [])
        for rule_index, rule_id in enumerate(
            raw_rule_ids if isinstance(raw_rule_ids, list) else []
        ):
            if isinstance(rule_id, str) and rule_id not in rules_by_id:
                report.add_error(
                    "MISSING_FOREIGN_KEY",
                    f"{path}.rule_ids[{rule_index}]",
                    f"referenced ID {rule_id!r} does not exist",
                )
        if record.get("status") != "completed":
            continue
        candidate = (
            candidates_by_id.get(candidate_id)
            if _is_nonempty_string(candidate_id)
            else None
        )
        candidate_path = record.get("candidate_path")
        recorded_hash = record.get("candidate_hash")
        canonical_path: str | None = None
        if _is_nonempty_string(candidate_path):
            try:
                canonical_path = canonical_candidate_path(candidate_path)
            except CandidateTreeError as exc:
                report.add_error(
                    "MATERIALIZATION_CANDIDATE_PATH_INVALID",
                    f"{path}.candidate_path",
                    str(exc),
                )
        if canonical_path is not None and candidate is not None:
            candidate_name = candidate.get("name")
            if (
                _is_nonempty_string(candidate_name)
                and PurePosixPath(canonical_path).name != candidate_name
            ):
                report.add_error(
                    "MATERIALIZATION_CANDIDATE_PATH_MISMATCH",
                    f"{path}.candidate_path",
                    "candidate_path final component must exactly match the linked "
                    f"candidate name {candidate_name!r}",
                )
        if canonical_path is not None:
            contract = _validate_candidate_contract(
                report,
                distillation_root,
                canonical_path,
                candidate.get("name") if candidate is not None else None,
                path,
            )
            materialization_id = record.get("materialization_id")
            if _is_nonempty_string(materialization_id):
                contracts[materialization_id] = contract
        recorded_hash_valid = isinstance(recorded_hash, str) and bool(
            TREE_HASH_RE.fullmatch(recorded_hash)
        )
        if not recorded_hash_valid:
            report.add_error(
                "MATERIALIZATION_CANDIDATE_HASH_INVALID",
                f"{path}.candidate_hash",
                "completed materialization candidate_hash must use "
                "sha256:<64 lowercase hex>",
            )
        if canonical_path is not None:
            try:
                actual_hash = candidate_tree_sha256(distillation_root, canonical_path)
            except CandidateTreeError as exc:
                path_codes = {
                    "CANDIDATE_PATH_INVALID",
                    "CANDIDATE_PATH_MISSING",
                    "CANDIDATE_PATH_NOT_DIRECTORY",
                    "DISTILLATION_ROOT_INVALID",
                }
                report.add_error(
                    (
                        "MATERIALIZATION_CANDIDATE_PATH_INVALID"
                        if exc.code in path_codes
                        else "MATERIALIZATION_CANDIDATE_TREE_INVALID"
                    ),
                    f"{path}.candidate_path",
                    str(exc),
                )
            else:
                if recorded_hash_valid and recorded_hash != actual_hash:
                    report.add_error(
                        "MATERIALIZATION_CANDIDATE_HASH_MISMATCH",
                        f"{path}.candidate_hash",
                        f"recorded hash {recorded_hash!r} does not match recomputed "
                        f"tree hash {actual_hash!r}",
                    )
        current_gate3 = _applicable_current_gate(current, "gate-3", candidate_id)
        gate3 = gate_by_id.get(gate3_id) if _is_nonempty_string(gate3_id) else None
        if (
            gate3 is None
            or gate3 is not current_gate3
            or gate3.get("decision") != "approved-for-eval"
            or gate3.get("candidate_id") != candidate_id
        ):
            report.add_error(
                "MATERIALIZATION_CURRENT_GATE3_REQUIRED",
                f"{path}.gate3_decision_id",
                "completed materialization must reference the current approved Gate 3 decision",
            )
            continue
        approval_snapshot = gate3.get("approval_snapshot")
        if not isinstance(approval_snapshot, dict):
            report.add_error(
                "MATERIALIZATION_APPROVAL_SNAPSHOT_REQUIRED",
                f"{path}.gate3_decision_id",
                "completed materialization requires a valid current Gate 3 approval snapshot",
            )
        else:
            if record.get("candidate_path") != approval_snapshot.get("candidate_path"):
                report.add_error(
                    "MATERIALIZATION_APPROVAL_PATH_MISMATCH",
                    f"{path}.candidate_path",
                    "completed materialization candidate_path must exactly match the "
                    "current Gate 3 approval snapshot",
                )
            if record.get("candidate_hash") != approval_snapshot.get("candidate_hash"):
                report.add_error(
                    "MATERIALIZATION_APPROVAL_HASH_MISMATCH",
                    f"{path}.candidate_hash",
                    "completed materialization candidate_hash must exactly match the "
                    "current Gate 3 approval snapshot",
                )
        approved_rule_ids = _approved_rule_ids(gate3)
        materialized_rule_ids = record.get("rule_ids", [])
        materialized_rule_strings = _string_items(materialized_rule_ids)
        if (
            not _is_string_list(materialized_rule_ids)
            or len(materialized_rule_strings) != len(set(materialized_rule_strings))
            or set(materialized_rule_strings) != set(approved_rule_ids)
        ):
            report.add_error(
                "MATERIALIZATION_RULE_MISMATCH",
                f"{path}.rule_ids",
                "completed materialization must contain exactly the accepted/revised Gate 3 rules",
            )
        for rule_id in materialized_rule_strings:
            rule = rules_by_id.get(rule_id)
            if rule is not None and rule.get("status") != "accepted":
                report.add_error(
                    "MATERIALIZATION_RULE_NOT_ACCEPTED",
                    f"{path}.rule_ids",
                    f"materialized rule {rule_id!r} is not accepted",
                )
    return contracts


def _validate_completed_eval_artifact(
    report: ValidationReport,
    root: Path,
    run: Mapping[str, Any],
    run_path: str,
    path_key: str,
    hash_key: str,
) -> bytes | None:
    recorded_digest = _normalized_full_sha256(run.get(hash_key))
    if recorded_digest is None:
        report.add_error(
            "EVAL_ARTIFACT_HASH_INVALID",
            f"{run_path}.{hash_key}",
            "completed eval artifact hash must be a complete 64-hex SHA-256, optionally prefixed with sha256:",
        )
    try:
        canonical_path, content = _read_distillation_artifact(root, run.get(path_key))
    except _ArtifactFileError as exc:
        code_by_reason = {
            "PATH_INVALID": "EVAL_ARTIFACT_PATH_INVALID",
            "MISSING": "EVAL_ARTIFACT_MISSING",
            "SYMLINK": "EVAL_ARTIFACT_SYMLINK",
            "NOT_REGULAR": "EVAL_ARTIFACT_NOT_REGULAR",
            "CHANGED": "EVAL_ARTIFACT_CHANGED",
        }
        report.add_error(
            code_by_reason.get(exc.code, "EVAL_ARTIFACT_READ_ERROR"),
            f"{run_path}.{path_key}",
            f"{exc.code}: {exc.message}",
        )
        return None
    if recorded_digest is None:
        return None
    actual_digest = hashlib.sha256(content).hexdigest()
    if actual_digest != recorded_digest:
        report.add_error(
            "EVAL_ARTIFACT_HASH_MISMATCH",
            f"{run_path}.{hash_key}",
            f"recorded SHA-256 does not match {canonical_path!r}",
        )
        return None
    return content


def _normalize_leak_text(value: str) -> str:
    """Normalize text for deterministic leakage comparison (NFKC + casefold + whitespace collapse)."""
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _validate_fixture_prompt_leakage(
    report: ValidationReport,
    fixture: Mapping[str, Any],
    path: str,
    case: EvalCaseContract,
    rubric: EvalRubricContract | None,
) -> None:
    """Reject fixture prompts that embed case-definition or rubric sensitive text.

    Leaking expected behaviors, failure signals, expected reasons, rubric dimensions, or
    fatal failures into the tested prompt invalidates the baseline/with-Skill comparison
    for that run. The check is deterministic: it flags NFKC-casefolded reuse of sensitive
    terms (length >= 6) as substrings of the prompt.
    """
    sensitive: list[str] = []
    if case.prompt_leakage_terms:
        sensitive.extend(case.prompt_leakage_terms)
    if rubric is not None:
        sensitive.extend(rubric.dimensions)
        sensitive.extend(sorted(rubric.fatal_failures))
    if not sensitive:
        return
    payload = fixture.get("input_payload")
    prompt = payload.get("prompt") if isinstance(payload, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        return
    normalized_prompt = _normalize_leak_text(prompt)
    for term in sensitive:
        normalized_term = _normalize_leak_text(term)
        if len(normalized_term) < 6:
            continue
        if normalized_term in normalized_prompt:
            report.add_error(
                "EVAL_FIXTURE_PROMPT_LEAKAGE",
                f"{path}.input_payload.prompt",
                f"fixture prompt embeds case-definition or rubric sensitive text: {term!r}",
            )
            break


def _validate_eval_fixture_contract(
    report: ValidationReport,
    content: bytes | None,
    run: Mapping[str, Any],
    run_path: str,
    case: EvalCaseContract,
    rubric: EvalRubricContract | None = None,
) -> None:
    if content is None:
        return
    try:
        fixture = _load_json_object_strict(content)
    except ValueError as exc:
        report.add_error(
            "EVAL_FIXTURE_CONTRACT_INVALID",
            f"{run_path}.fixture_path",
            f"fixture must be strict JSON: {exc}",
        )
        return
    _validate_no_placeholder_deep(report, fixture, f"{run_path}.fixture_path")
    _validate_fixture_prompt_leakage(report, fixture, f"{run_path}.fixture_path", case, rubric)
    required = {
        "schema_version", "fixture_id", "case_type", "case_id",
        "case_definition_hash", "request", "source_ids", "holdout",
        "input_payload", "leakage_controls",
    }
    if not required.issubset(fixture):
        report.add_error(
            "EVAL_FIXTURE_CONTRACT_INVALID",
            f"{run_path}.fixture_path",
            "fixture is missing required contract fields",
        )
        return
    mismatches = []
    for key, expected in (
        ("schema_version", 1),
        ("fixture_id", run.get("fixture_id")),
        ("case_type", case.case_type),
        ("case_id", case.case_id),
        ("case_definition_hash", case.definition_hash),
        ("request", case.request),
        ("source_ids", run.get("source_ids")),
        ("holdout", case.holdout),
    ):
        if fixture.get(key) != expected:
            mismatches.append(key)
    if mismatches:
        report.add_error(
            "EVAL_FIXTURE_CONTRACT_MISMATCH",
            f"{run_path}.fixture_path",
            "fixture fields do not match the run/case definition: " + ", ".join(mismatches),
        )
    if not _is_nonempty_value(fixture.get("input_payload")):
        report.add_error(
            "EVAL_FIXTURE_CONTRACT_INVALID",
            f"{run_path}.fixture_path.input_payload",
            "fixture input_payload must be non-empty",
        )
    leakage = fixture.get("leakage_controls")
    if not isinstance(leakage, dict):
        report.add_error(
            "EVAL_FIXTURE_CONTRACT_INVALID",
            f"{run_path}.fixture_path.leakage_controls",
            "fixture leakage_controls must be a mapping",
        )
    elif (
        leakage.get("expected_answer_withheld") is not True
        or leakage.get("context_isolated") is not True
        or not isinstance(leakage.get("exceptions"), list)
    ):
        report.add_error(
            "EVAL_FIXTURE_LEAKAGE_CONTROL_INVALID",
            f"{run_path}.fixture_path.leakage_controls",
            "fixture must record withheld answers, isolated context, and an exceptions list",
        )


def _validate_eval_output_contract(
    report: ValidationReport,
    content: bytes | None,
    run: Mapping[str, Any],
    run_path: str,
    condition: str,
) -> None:
    if content is None:
        return
    try:
        output = _load_json_object_strict(content)
    except ValueError as exc:
        report.add_error(
            "EVAL_OUTPUT_CONTRACT_INVALID",
            f"{run_path}.{condition}_output_path",
            f"output must be strict JSON: {exc}",
        )
        return
    _validate_no_placeholder_deep(
        report, output, f"{run_path}.{condition}_output_path"
    )
    required = {"schema_version", "eval_run_id", "case_id", "condition", "response"}
    if not required.issubset(output):
        report.add_error(
            "EVAL_OUTPUT_CONTRACT_INVALID",
            f"{run_path}.{condition}_output_path",
            "output is missing required contract fields",
        )
        return
    if (
        output.get("schema_version") != 1
        or output.get("eval_run_id") != run.get("eval_run_id")
        or output.get("case_id") != run.get("case_id")
        or output.get("condition") != condition
        or not _is_nonempty_string(output.get("response"))
    ):
        report.add_error(
            "EVAL_OUTPUT_CONTRACT_MISMATCH",
            f"{run_path}.{condition}_output_path",
            "output identity/condition/response does not match the eval run",
        )


def _validate_eval_rubric_contract(
    report: ValidationReport,
    run: Mapping[str, Any],
    run_path: str,
    rubric: EvalRubricContract | None,
) -> None:
    if rubric is None:
        report.add_error(
            "EVAL_RUBRIC_DEFINITION_UNAVAILABLE",
            f"{run_path}.rubric_id",
            "completed eval requires a rubric from the materialized task definition",
        )
        return
    if run.get("rubric_id") != rubric.rubric_id:
        report.add_error(
            "EVAL_RUBRIC_MISMATCH", f"{run_path}.rubric_id",
            "run rubric_id must match the materialized rubric",
        )
    if run.get("max_score") != rubric.max_score or run.get("pass_threshold") != rubric.pass_threshold:
        report.add_error(
            "EVAL_RUBRIC_MISMATCH", f"{run_path}.pass_threshold",
            "run maximum and threshold must match the materialized rubric",
        )
    dimension_scores = run.get("dimension_scores")
    if not isinstance(dimension_scores, dict) or set(dimension_scores) != set(rubric.dimensions):
        report.add_error(
            "EVAL_DIMENSION_SCORES_INVALID", f"{run_path}.dimension_scores",
            "dimension scores must contain exactly the materialized rubric dimensions",
        )
    else:
        valid_scores = True
        for dimension, score in dimension_scores.items():
            if (
                not _is_number(score)
                or score < rubric.score_min
                or score > rubric.score_max_per_dimension
            ):
                report.add_error(
                    "EVAL_DIMENSION_SCORES_INVALID",
                    f"{run_path}.dimension_scores.{dimension}",
                    "dimension score is outside the rubric bounds",
                )
                valid_scores = False
        if valid_scores and run.get("score") != sum(dimension_scores.values()):
            report.add_error(
                "EVAL_DIMENSION_SCORE_TOTAL_MISMATCH", f"{run_path}.score",
                "run score must equal the sum of per-dimension scores",
            )
    observed = run.get("fatal_failures_observed")
    if not _is_string_list(observed):
        return
    unknown = set(observed) - set(rubric.fatal_failures)
    if unknown:
        report.add_error(
            "EVAL_FATAL_FAILURE_UNKNOWN", f"{run_path}.fatal_failures_observed",
            "fatal failures must come from the materialized rubric",
        )
    if run.get("outcome") == "pass" and observed:
        report.add_error(
            "EVAL_FATAL_FAILURE_PRESENT", f"{run_path}.fatal_failures_observed",
            "a passing run cannot contain a fatal failure",
        )
    leakage = run.get("leakage_controls")
    if not isinstance(leakage, dict) or (
        leakage.get("expected_answer_withheld") is not True
        or leakage.get("context_isolated") is not True
        or not isinstance(leakage.get("exceptions"), list)
        or not isinstance(leakage.get("context_differences"), list)
    ):
        report.add_error(
            "EVAL_LEAKAGE_CONTROL_INVALID", f"{run_path}.leakage_controls",
            "run must record withheld answers, isolated context, differences, and exceptions",
        )


def _validate_completed_eval_links(
    report: ValidationReport,
    root: Path,
    eval_runs: Sequence[Mapping[str, Any]],
    current: Mapping[tuple[Any, Any], Mapping[str, Any]],
    materializations_by_id: Mapping[str, Mapping[str, Any]],
    contracts_by_materialization_id: Mapping[str, CandidateEvalContract],
) -> None:
    for index, run in enumerate(eval_runs):
        path = f"eval-runs.yml.eval_runs[{index}]"
        materialization_id = run.get("materialization_id")
        materialization = (
            materializations_by_id.get(materialization_id)
            if _is_nonempty_string(materialization_id)
            else None
        )
        if _is_nonempty_string(materialization_id) and materialization is None:
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"{path}.materialization_id",
                f"referenced ID {materialization_id!r} does not exist",
            )
        if run.get("status") != "completed":
            continue
        artifact_contents: dict[str, bytes | None] = {}
        artifact_pairs = (
            ("fixture_path", "fixture_hash"),
            ("baseline_output_path", "baseline_output_hash"),
            ("with_skill_output_path", "with_skill_output_hash"),
        )
        raw_artifact_paths = [run.get(path_key) for path_key, _ in artifact_pairs]
        if (
            all(_is_nonempty_string(value) for value in raw_artifact_paths)
            and len(set(raw_artifact_paths)) != len(raw_artifact_paths)
        ):
            report.add_error(
                "EVAL_ARTIFACT_PATH_COLLISION",
                path,
                "fixture, baseline, and with-Skill outputs must use distinct files",
            )
        for path_key, hash_key in artifact_pairs:
            artifact_contents[path_key] = _validate_completed_eval_artifact(
                report, root, run, path, path_key, hash_key
            )
        candidate_id = run.get("candidate_id")
        current_gate3 = _applicable_current_gate(current, "gate-3", candidate_id)
        if current_gate3 is None or current_gate3.get("decision") != "approved-for-eval":
            report.add_error(
                "EVAL_CURRENT_GATE3_REQUIRED",
                path,
                "completed eval requires a current Gate 3 approved-for-eval decision",
            )
        else:
            approved_rule_ids = set(_approved_rule_ids(current_gate3))
            run_rule_ids = run.get("rule_ids", [])
            if isinstance(run_rule_ids, list) and any(
                rule_id not in approved_rule_ids
                for rule_id in run_rule_ids
                if isinstance(rule_id, str)
            ):
                report.add_error(
                    "EVAL_RULE_NOT_APPROVED",
                    f"{path}.rule_ids",
                    "completed eval may use only Gate 3 accepted/revised rules",
                )
        if materialization is None:
            continue
        if materialization.get("status") == "legacy-quarantined":
            report.add_error(
                "EVAL_LEGACY_MATERIALIZATION",
                f"{path}.materialization_id",
                "legacy-quarantined materialization cannot support evaluation",
            )
            continue
        if materialization.get("status") != "completed":
            report.add_error(
                "EVAL_MATERIALIZATION_NOT_COMPLETED",
                f"{path}.materialization_id",
                "completed eval requires a completed materialization",
            )
            continue
        contract = contracts_by_materialization_id.get(materialization_id)
        if contract is None or not contract.definitions_valid:
            report.add_error(
                "EVAL_CASE_DEFINITION_UNAVAILABLE",
                f"{path}.case_id",
                "completed eval requires valid case definitions in its materialized candidate",
            )
        else:
            case_type = run.get("case_type")
            case_id = run.get("case_id")
            if (
                isinstance(case_type, str)
                and case_type in EVAL_CASE_TYPES
                and _is_nonempty_string(case_id)
            ):
                expected_case_ids = contract.case_ids.get(case_type, frozenset())
                if case_id not in expected_case_ids:
                    defined_types = sorted(
                        candidate_type
                        for candidate_type, case_ids in contract.case_ids.items()
                        if case_id in case_ids
                    )
                    if defined_types:
                        report.add_error(
                            "EVAL_CASE_TYPE_MISMATCH",
                            f"{path}.case_id",
                            f"case_id {case_id!r} is defined as {', '.join(defined_types)}, not {case_type}",
                        )
                    else:
                        report.add_error(
                            "EVAL_CASE_NOT_DEFINED",
                            f"{path}.case_id",
                            f"case_id {case_id!r} is absent from the linked candidate eval definitions",
                        )
                else:
                    case_contract = contract.cases.get(case_type, {}).get(case_id)
                    if case_contract is None:
                        report.add_error(
                            "EVAL_CASE_DEFINITION_UNAVAILABLE",
                            f"{path}.case_id",
                            "case contract is missing despite a declared case ID",
                        )
                    else:
                        if run.get("case_definition_hash") != case_contract.definition_hash:
                            report.add_error(
                                "EVAL_CASE_DEFINITION_HASH_MISMATCH",
                                f"{path}.case_definition_hash",
                                "run must bind the canonical materialized case definition hash",
                            )
                        if run.get("holdout") is not case_contract.holdout:
                            report.add_error(
                                "EVAL_CASE_HOLDOUT_MISMATCH",
                                f"{path}.holdout",
                                "run holdout must match the linked case definition",
                            )
                        _validate_eval_fixture_contract(
                            report, artifact_contents.get("fixture_path"),
                            run, path, case_contract, contract.rubric,
                        )
                        _validate_eval_output_contract(
                            report, artifact_contents.get("baseline_output_path"),
                            run, path, "baseline",
                        )
                        _validate_eval_output_contract(
                            report, artifact_contents.get("with_skill_output_path"),
                            run, path, "with_skill",
                        )
                        _validate_eval_rubric_contract(
                            report, run, path, contract.rubric
                        )
        if materialization.get("candidate_id") != candidate_id:
            report.add_error(
                "EVAL_MATERIALIZATION_MISMATCH",
                f"{path}.candidate_id",
                "eval candidate must match materialization candidate",
            )
        if materialization.get("candidate_hash") != run.get("candidate_hash"):
            report.add_error(
                "EVAL_MATERIALIZATION_MISMATCH",
                f"{path}.candidate_hash",
                "eval candidate_hash must match the completed materialization",
            )
        run_rule_ids = run.get("rule_ids", [])
        materialized_rule_ids = materialization.get("rule_ids", [])
        run_rule_strings = _string_items(run_rule_ids)
        materialized_rule_strings = _string_items(materialized_rule_ids)
        if (
            not _is_string_list(run_rule_ids)
            or not _is_string_list(materialized_rule_ids)
            or len(run_rule_strings) != len(set(run_rule_strings))
            or set(run_rule_strings) != set(materialized_rule_strings)
        ):
            report.add_error(
                "EVAL_MATERIALIZATION_MISMATCH",
                f"{path}.rule_ids",
                "eval rule_ids must exactly match the completed materialization",
            )
        if (
            current_gate3 is not None
            and materialization.get("gate3_decision_id") != current_gate3.get("decision_id")
        ):
            report.add_error(
                "EVAL_CURRENT_GATE3_REQUIRED",
                f"{path}.materialization_id",
                "eval materialization must derive from the current Gate 3 approval",
            )


def _validate_gate4_acceptance_decisions(
    report: ValidationReport,
    gate_decisions: Sequence[Mapping[str, Any]],
    eval_runs_by_id: Mapping[str, Mapping[str, Any]],
) -> None:
    for decision in gate_decisions:
        if decision.get("gate") != "gate-4" or decision.get("decision") != "accepted":
            continue
        decision_path = f"gate_decisions.{decision.get('decision_id')}.eval_run_ids"
        eval_run_ids = decision.get("eval_run_ids", [])
        if not isinstance(eval_run_ids, list):
            continue
        eval_run_id_strings = _string_items(eval_run_ids)
        if (
            not _is_string_list(eval_run_ids)
            or len(eval_run_id_strings) != len(set(eval_run_id_strings))
        ):
            report.add_error(
                "DUPLICATE_EVAL_REFERENCE",
                decision_path,
                "Gate 4 eval_run_ids must not contain duplicates",
            )
        valid_runs: dict[str, Mapping[str, Any]] = {}
        for eval_run_id in eval_run_id_strings:
            run = eval_runs_by_id.get(eval_run_id)
            if (
                run is None
                or run.get("candidate_id") != decision.get("candidate_id")
                or run.get("status") != "completed"
                or run.get("outcome") != "pass"
                or not _safe_member(run.get("reviewer_type"), HUMAN_REVIEWER_TYPES)
            ):
                report.add_error(
                    "GATE4_EVAL_NOT_PASSED",
                    decision_path,
                    f"eval run {eval_run_id!r} must be a completed pass for the same candidate",
                )
            else:
                valid_runs[eval_run_id] = run

        coverage: dict[str, set[str]] = {key: set() for key in EVAL_CASE_TYPES}
        holdout_task = False
        materialization_ids: set[str] = set()
        for run in valid_runs.values():
            case_type = run.get("case_type")
            case_id = run.get("case_id")
            if isinstance(case_type, str) and case_type in coverage and _is_nonempty_string(case_id):
                coverage[case_type].add(case_id)
            if case_type == "task" and run.get("holdout") is True:
                holdout_task = True
            if _is_nonempty_string(run.get("materialization_id")):
                materialization_ids.add(run["materialization_id"])
        missing_coverage = {
            key: 3 - len(case_ids) for key, case_ids in coverage.items()
            if len(case_ids) < 3
        }
        if missing_coverage:
            report.add_error(
                "GATE4_EVAL_COVERAGE",
                decision_path,
                "Gate 4 requires at least three distinct passing trigger, nontrigger, and task "
                "cases; "
                + ", ".join(
                    f"{key} missing {count}" for key, count in sorted(missing_coverage.items())
                ),
            )
        if not holdout_task:
            report.add_error(
                "GATE4_HOLDOUT_REQUIRED",
                decision_path,
                "Gate 4 requires at least one passing holdout task case",
            )
        if len(materialization_ids) != 1:
            report.add_error(
                "GATE4_MATERIALIZATION_MISMATCH",
                decision_path,
                "all Gate 4 acceptance runs must evaluate one completed materialization",
            )


def _records(data: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _load_sources_manifest(path: Path) -> dict[str, dict[str, Any]]:
    manifest = _load_yaml(path)
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise DistillationInputError(
            "MANIFEST_SCHEMA", path, "sources manifest must contain a sources list"
        )
    source_records: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict) or not _is_nonempty_string(source.get("id")):
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path,
                f"sources[{index}] must be a mapping with a non-empty id"
            )
        source_id = source["id"]
        if source_id != source_id.strip():
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path, f"sources[{index}].id has surrounding whitespace"
            )
        if not ID_RE.fullmatch(source_id):
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path, f"sources[{index}].id is not a stable ID"
            )
        if source_id in source_records:
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path, f"sources[{index}].id duplicates {source_id!r}"
            )
        if not _is_nonempty_string(source.get("source_role")):
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path, f"sources[{index}].source_role must be non-empty"
            )
        if not _is_nonempty_string(source.get("privacy")):
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path, f"sources[{index}].privacy must be non-empty"
            )
        if not isinstance(source.get("allow_public_quotes"), bool):
            raise DistillationInputError(
                "MANIFEST_SCHEMA", path,
                f"sources[{index}].allow_public_quotes must be a boolean",
            )
        source_records[source_id] = source
    return source_records


def _manifest_project_root(path: Path) -> Path:
    """Return the root against which manifest local paths are interpreted."""
    resolved = path.resolve()
    if resolved.parent.name == "manifests":
        return resolved.parent.parent
    # Keep programmatic and temporary fixtures compatible when a manifest is
    # supplied directly beside their distillation files.
    return resolved.parent


def _canonical_repository_path(value: Any) -> str | None:
    """Return a safe project-relative POSIX path, or None when it is unsafe."""
    if not _is_nonempty_string(value) or "\\" in value or ":" in value or "#" in value:
        return None
    candidate = PurePosixPath(value.strip())
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        return None
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        return None
    return normalized


def _parse_markdown_anchor(
    report: ValidationReport,
    value: Any,
    path: str,
) -> MarkdownAnchor | None:
    if not _is_nonempty_string(value):
        report.add_error("LOCATOR_ANCHOR_INVALID", path, "anchor must be a non-empty string")
        return None
    anchor = value.strip()
    heading: str | None = None
    if "#" in anchor:
        anchor, heading = anchor.rsplit("#", 1)
        heading = heading.strip()
        if not heading:
            report.add_error(
                "LOCATOR_ANCHOR_INVALID", path, "heading fragment must not be empty"
            )
            return None
    repository_path, separator, line_value = anchor.rpartition(":")
    match = ANCHOR_LINE_RE.fullmatch(line_value) if separator else None
    canonical_path = _canonical_repository_path(repository_path)
    if match is None or canonical_path is None:
        report.add_error(
            "LOCATOR_ANCHOR_INVALID",
            path,
            "must use a safe project-relative path:N[-M][#heading] anchor",
        )
        return None
    start_line = int(match.group("start"))
    end_line = int(match.group("end") or start_line)
    if end_line < start_line:
        report.add_error(
            "LOCATOR_ANCHOR_INVALID", path, "anchor line range must be increasing"
        )
        return None
    return MarkdownAnchor(canonical_path, start_line, end_line, heading)


def _heading_slug(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    result: list[str] = []
    separator_pending = False
    for character in value:
        if character.isalnum():
            if separator_pending and result:
                result.append("-")
            result.append(character)
            separator_pending = False
        else:
            separator_pending = True
    return "".join(result).strip("-")


def _heading_slug_variants(title: str) -> frozenset[str]:
    variants = {_heading_slug(title)}
    without_trailing_parenthetical = TRAILING_PAREN_RE.sub("", title)
    variants.add(_heading_slug(without_trailing_parenthetical))
    return frozenset(item for item in variants if item)


def _markdown_sections(text: str) -> list[MarkdownSection]:
    lines = text.splitlines()
    headings: list[tuple[int, int, str, frozenset[str]]] = []
    fence_character: str | None = None
    fence_length = 0
    for line_number, line in enumerate(lines, start=1):
        fence_match = FENCE_RE.match(line)
        if fence_character is not None:
            if fence_match:
                marker = fence_match.group("marker")
                if marker[0] == fence_character and len(marker) >= fence_length:
                    fence_character = None
                    fence_length = 0
            continue
        if fence_match:
            marker = fence_match.group("marker")
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        heading_match = ATX_HEADING_RE.match(line)
        if heading_match is None:
            continue
        title = re.sub(r"[ \t]+#+[ \t]*$", "", heading_match.group("title")).strip()
        headings.append((
            line_number,
            len(heading_match.group("marks")),
            title,
            _heading_slug_variants(title),
        ))

    sections: list[MarkdownSection] = []
    line_count = text.count("\n") + 1
    for index, (start_line, level, title, variants) in enumerate(headings):
        end_line = line_count
        for next_start, next_level, _next_title, _next_variants in headings[index + 1:]:
            if next_level <= level:
                end_line = next_start - 1
                break
        sections.append(MarkdownSection(start_line, end_line, level, title, variants))
    return sections


def _find_text_occurrences(text: str, needle: str) -> list[TextOccurrence]:
    occurrences: list[TextOccurrence] = []
    search_from = 0
    while True:
        start_offset = text.find(needle, search_from)
        if start_offset < 0:
            break
        end_offset = start_offset + len(needle)
        final_character = max(start_offset, end_offset - 1)
        occurrences.append(TextOccurrence(
            start_offset=start_offset,
            end_offset=end_offset,
            start_line=text.count("\n", 0, start_offset) + 1,
            end_line=text.count("\n", 0, final_character) + 1,
        ))
        search_from = start_offset + 1
    return occurrences


def _occurrence_in_sections(
    occurrence: TextOccurrence,
    sections: Sequence[MarkdownSection],
) -> bool:
    return any(
        section.start_line <= occurrence.start_line
        and occurrence.end_line <= section.end_line
        for section in sections
    )


def _select_text_occurrence(
    report: ValidationReport,
    occurrences: Sequence[TextOccurrence],
    anchor: MarkdownAnchor,
    path: str,
) -> TextOccurrence | None:
    if len(occurrences) == 1:
        return occurrences[0]
    hinted = [
        occurrence for occurrence in occurrences
        if not (
            occurrence.end_line < anchor.start_line
            or occurrence.start_line > anchor.end_line
        )
    ]
    if len(hinted) == 1:
        return hinted[0]
    report.add_error(
        "LOCATOR_TEXT_AMBIGUOUS",
        path,
        "exact source text occurs multiple times and the line hint does not select one",
    )
    return None


def _allowed_source_paths(source: Mapping[str, Any]) -> set[str]:
    values: list[Any] = [source.get("local_path")]
    related = source.get("related_local_paths")
    if isinstance(related, list):
        values.extend(related)
    result: set[str] = set()
    for value in values:
        canonical = _canonical_repository_path(value)
        if canonical is not None:
            result.add(canonical)
    return result


def _validate_markdown_section_locator(
    report: ValidationReport,
    evidence: Mapping[str, Any],
    path: str,
    source: Mapping[str, Any],
    project_root: Path,
) -> bool:
    """Resolve one local Markdown locator without searching outside its manifest allowlist."""
    locator = evidence.get("locator")
    if not isinstance(locator, dict):
        return False
    anchor = _parse_markdown_anchor(
        report, locator.get("anchor"), f"{path}.locator.anchor"
    )
    if anchor is None:
        return False

    allowed_paths = _allowed_source_paths(source)
    if anchor.repository_path not in allowed_paths:
        report.add_error(
            "LOCATOR_PATH_NOT_ALLOWED",
            f"{path}.locator.anchor",
            "anchor path is not listed in this source's local_path or related_local_paths",
        )
        return False

    resolved_root = project_root.resolve()
    source_path = (resolved_root / Path(*PurePosixPath(anchor.repository_path).parts)).resolve()
    try:
        source_path.relative_to(resolved_root)
    except ValueError:
        report.add_error(
            "LOCATOR_PATH_NOT_ALLOWED",
            f"{path}.locator.anchor",
            "resolved anchor path escapes the manifest project root",
        )
        return False
    if not source_path.is_file():
        report.add_error(
            "LOCATOR_SOURCE_FILE_MISSING",
            f"{path}.locator.anchor",
            f"allowed local source file does not exist: {anchor.repository_path}",
        )
        return False
    try:
        with source_path.open("r", encoding="utf-8", newline=None) as handle:
            source_text = handle.read()
    except (OSError, UnicodeError) as exc:
        report.add_error(
            "LOCATOR_SOURCE_READ_ERROR",
            f"{path}.locator.anchor",
            f"cannot read allowed local source as UTF-8 text: {exc}",
        )
        return False

    valid = True
    line_count = source_text.count("\n") + 1
    if anchor.end_line > line_count:
        report.add_error(
            "LOCATOR_LINE_HINT_OUT_OF_RANGE",
            f"{path}.locator.anchor",
            f"recorded line range ends at {anchor.end_line}, but file has {line_count} lines",
        )
        valid = False

    matching_sections: list[MarkdownSection] | None = None
    if anchor.heading is not None:
        expected_slug = _heading_slug(anchor.heading)
        matching_sections = [
            section for section in _markdown_sections(source_text)
            if expected_slug in section.slug_variants
        ]
        if not expected_slug or not matching_sections:
            report.add_error(
                "LOCATOR_HEADING_NOT_FOUND",
                f"{path}.locator.anchor",
                f"Markdown heading {anchor.heading!r} was not found in the allowed file",
            )
            return False

    selected: dict[str, TextOccurrence] = {}
    for field_name, mismatch_code in (
        ("raw_text", "EVIDENCE_RAW_TEXT_MISMATCH"),
        ("normalized_text", "EVIDENCE_NORMALIZED_TEXT_MISMATCH"),
    ):
        value = evidence.get(field_name)
        field_path = f"{path}.{field_name}"
        if not _is_nonempty_string(value):
            report.add_error(
                "EVIDENCE_TEXT_MISSING",
                field_path,
                "markdown-section evidence requires non-empty raw_text and normalized_text",
            )
            valid = False
            continue
        occurrences = _find_text_occurrences(source_text, value)
        if not occurrences:
            report.add_error(
                mismatch_code,
                field_path,
                "exact text is not present in the anchor's allowed local source file",
            )
            valid = False
            continue
        if matching_sections is not None:
            scoped_occurrences = [
                occurrence for occurrence in occurrences
                if _occurrence_in_sections(occurrence, matching_sections)
            ]
            if not scoped_occurrences:
                report.add_error(
                    "LOCATOR_SECTION_MISMATCH",
                    field_path,
                    "exact text exists in the file but not under the named Markdown heading",
                )
                valid = False
                continue
            occurrences = scoped_occurrences
        occurrence = _select_text_occurrence(
            report, occurrences, anchor, field_path
        )
        if occurrence is None:
            valid = False
            continue
        selected[field_name] = occurrence

    canonical_field = (
        "normalized_text" if "normalized_text" in selected else "raw_text"
    )
    canonical_occurrence = selected.get(canonical_field)
    recorded_hash = locator.get("content_hash")
    if canonical_occurrence is not None and isinstance(recorded_hash, str):
        if CONTENT_HASH_RE.fullmatch(recorded_hash):
            expected_prefix = recorded_hash.removeprefix("sha256:").lower()
            source_slice = source_text[
                canonical_occurrence.start_offset:canonical_occurrence.end_offset
            ]
            actual_hash = hashlib.sha256(source_slice.encode("utf-8")).hexdigest()
            if not actual_hash.startswith(expected_prefix):
                report.add_error(
                    "CONTENT_HASH_MISMATCH",
                    f"{path}.locator.content_hash",
                    "recorded content hash does not match the exact normalized source slice",
                )
                valid = False

    if canonical_occurrence is not None and (
        canonical_occurrence.end_line < anchor.start_line
        or canonical_occurrence.start_line > anchor.end_line
    ):
        report.add_warning(
            "LOCATOR_LINE_HINT_DRIFT",
            f"{path}.locator.anchor",
            "recorded line hint "
            f"{anchor.start_line}-{anchor.end_line} differs from exact source span "
            f"{canonical_occurrence.start_line}-{canonical_occurrence.end_line}",
        )
    return valid


def _validate_distillation_snapshot(
    root: Path | str,
    sources_manifest: Path | str | None = None,
) -> ValidationReport:
    """Return a structural report without modifying the distillation directory."""
    root = Path(root)
    report = ValidationReport(root=str(root.resolve()))
    documents: dict[str, dict[str, Any]] = {}
    for filename, required_lists in REQUIRED_FILES.items():
        document = _load_yaml(root / filename)
        documents[filename] = document
        schema_version = document.get("schema_version")
        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version != 1
        ):
            report.add_error(
                "SCHEMA_VERSION", f"{filename}.schema_version",
                "schema_version must be the integer 1"
            )
        if not _is_nonempty_string(document.get("distillation_id")):
            report.add_error(
                "MISSING_FIELD", f"{filename}.distillation_id",
                "distillation_id must be a non-empty string"
            )
        else:
            _validate_id(
                report, document.get("distillation_id"), f"{filename}.distillation_id"
            )
        for key in required_lists:
            if key not in document:
                report.add_error("MISSING_FIELD", f"{filename}.{key}", "required list is missing")
            elif not isinstance(document.get(key), list):
                report.add_error("FIELD_TYPE", f"{filename}.{key}", "must be a list")
            else:
                for index, item in enumerate(document[key]):
                    if not isinstance(item, dict):
                        report.add_error(
                            "RECORD_TYPE", f"{filename}.{key}[{index}]", "record must be a mapping"
                        )
        if filename != "capability-rules.yml" and "skill_candidates" in document:
            report.add_error(
                "MISPLACED_SKILL_CANDIDATES", f"{filename}.skill_candidates",
                "skill_candidates is allowed only in capability-rules.yml"
            )
        optional_candidates = (
            document.get("skill_candidates") if filename == "capability-rules.yml" else None
        )
        if optional_candidates is not None and not isinstance(optional_candidates, list):
            report.add_error(
                "FIELD_TYPE", f"{filename}.skill_candidates", "must be a list when present"
            )
        elif isinstance(optional_candidates, list):
            for index, item in enumerate(optional_candidates):
                if not isinstance(item, dict):
                    report.add_error(
                        "RECORD_TYPE", f"{filename}.skill_candidates[{index}]",
                        "record must be a mapping"
                    )

    overlay_document: dict[str, Any] | None = None
    overlay_path = root / "correction-overlay.yml"
    if overlay_path.is_file():
        overlay_document = _load_yaml(overlay_path)
        documents["correction-overlay.yml"] = overlay_document
        schema_version = overlay_document.get("schema_version")
        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version != 1
        ):
            report.add_error(
                "SCHEMA_VERSION",
                "correction-overlay.yml.schema_version",
                "schema_version must be the integer 1",
            )
        if not _is_nonempty_string(overlay_document.get("distillation_id")):
            report.add_error(
                "MISSING_FIELD",
                "correction-overlay.yml.distillation_id",
                "distillation_id must be a non-empty string",
            )
        else:
            _validate_id(
                report,
                overlay_document.get("distillation_id"),
                "correction-overlay.yml.distillation_id",
            )
        _require_fields(
            report,
            overlay_document,
            ("overlay_id", "source_id", "policy", "corrections"),
            "correction-overlay.yml",
        )
        _validate_id(
            report, overlay_document.get("overlay_id"), "correction-overlay.yml.overlay_id"
        )
        if not _is_nonempty_string(overlay_document.get("source_id")):
            report.add_error(
                "FIELD_TYPE", "correction-overlay.yml.source_id", "must be a non-empty string"
            )
        else:
            _validate_id(
                report,
                overlay_document.get("source_id"),
                "correction-overlay.yml.source_id",
            )
        policy = overlay_document.get("policy")
        if not isinstance(policy, dict):
            report.add_error(
                "FIELD_TYPE", "correction-overlay.yml.policy", "must be a mapping"
            )
        else:
            for key in (
                "source_remains_read_only",
                "normalized_text_must_remain_semantically_unchanged",
            ):
                if policy.get(key) is not True:
                    report.add_error(
                        "CORRECTION_POLICY_INVALID",
                        f"correction-overlay.yml.policy.{key}",
                        "must be explicitly true",
                    )
        corrections_value = overlay_document.get("corrections")
        if not isinstance(corrections_value, list):
            report.add_error(
                "FIELD_TYPE", "correction-overlay.yml.corrections", "must be a list"
            )
        else:
            for index, item in enumerate(corrections_value):
                if not isinstance(item, dict):
                    report.add_error(
                        "RECORD_TYPE",
                        f"correction-overlay.yml.corrections[{index}]",
                        "record must be a mapping",
                    )

    distillation_ids = {
        document.get("distillation_id") for document in documents.values()
        if _is_nonempty_string(document.get("distillation_id"))
    }
    if len(distillation_ids) > 1:
        report.add_error(
            "DISTILLATION_ID_MISMATCH", "distillation_id",
            "all authoritative YAML files must use the same distillation_id"
        )

    evidence = _records(documents["evidence-ledger.yml"], "evidence")
    claims = _records(documents["evidence-ledger.yml"], "claims")
    relations = _records(documents["concept-map.yml"], "relations")
    rules = _records(documents["capability-rules.yml"], "capability_rules")
    candidates = _records(documents["capability-rules.yml"], "skill_candidates")
    gate_decisions = _records(documents["gate-decisions.yml"], "gate_decisions")
    materializations = _records(documents["gate-decisions.yml"], "materializations")
    eval_runs = _records(documents["eval-runs.yml"], "eval_runs")
    corrections = _records(overlay_document or {}, "corrections")

    overlay_required = any(
        isinstance(record.get("quality_flags"), list) and bool(record.get("quality_flags"))
        for record in evidence
    ) or any(
        isinstance(record.get("correction_ids"), list) and bool(record.get("correction_ids"))
        for record in claims
    )
    if overlay_required and overlay_document is None:
        report.add_error(
            "CORRECTION_OVERLAY_REQUIRED",
            "correction-overlay.yml",
            "non-empty quality_flags or correction_ids require a correction overlay",
        )

    source_records: dict[str, dict[str, Any]] | None = None
    manifest_project_root: Path | None = None
    if sources_manifest is not None:
        manifest_path = Path(sources_manifest)
        source_records = _load_sources_manifest(manifest_path)
        manifest_project_root = _manifest_project_root(manifest_path)
        for index, record in enumerate(evidence):
            source_id = record.get("source_id")
            if _is_nonempty_string(source_id) and source_id not in source_records:
                report.add_error(
                    "UNKNOWN_SOURCE_ID", f"evidence-ledger.yml.evidence[{index}].source_id",
                    f"source_id {source_id!r} is not present in the supplied manifest"
                )
        if overlay_document is not None:
            overlay_source_id = overlay_document.get("source_id")
            if _is_nonempty_string(overlay_source_id) and overlay_source_id not in source_records:
                report.add_error(
                    "UNKNOWN_SOURCE_ID",
                    "correction-overlay.yml.source_id",
                    f"source_id {overlay_source_id!r} is not present in the supplied manifest",
                )
        for run_index, eval_run in enumerate(eval_runs):
            source_ids = eval_run.get("source_ids", [])
            if not isinstance(source_ids, list):
                continue
            for source_index, source_id in enumerate(source_ids):
                if _is_nonempty_string(source_id) and source_id not in source_records:
                    report.add_error(
                        "UNKNOWN_SOURCE_ID",
                        f"eval-runs.yml.eval_runs[{run_index}].source_ids[{source_index}]",
                        f"source_id {source_id!r} is not present in the supplied manifest",
                    )
    if any(
        _safe_member(item.get("lifecycle"), {"accepted", "deployed"})
        for item in candidates
    ):
        if source_records is None:
            report.add_error(
                "SOURCES_MANIFEST_REQUIRED",
                "sources_manifest",
                "accepted/deployed candidate validation requires --sources-manifest",
            )

    markdown_locator_count = sum(
        record.get("locator", {}).get("locator_type") == "markdown-section"
        for record in evidence
        if isinstance(record.get("locator"), dict)
    )
    markdown_locator_resolved = 0
    locator_valid: dict[str, bool] = {}
    for index, record in enumerate(evidence):
        path = f"evidence-ledger.yml.evidence[{index}]"
        valid = _validate_evidence(report, record, path)
        locator = record.get("locator")
        if (
            isinstance(locator, dict)
            and locator.get("locator_type") == "markdown-section"
            and source_records is not None
            and manifest_project_root is not None
        ):
            source_id = record.get("source_id")
            source = (
                source_records.get(source_id)
                if _is_nonempty_string(source_id)
                else None
            )
            if source is None:
                valid = False
            else:
                resolved = _validate_markdown_section_locator(
                    report, record, path, source, manifest_project_root
                )
                valid = valid and resolved
                if resolved:
                    markdown_locator_resolved += 1
        locator_valid[str(record.get("evidence_id"))] = valid
    for index, record in enumerate(claims):
        _validate_claim(report, record, f"evidence-ledger.yml.claims[{index}]")
    for index, record in enumerate(relations):
        _validate_relation(report, record, f"concept-map.yml.relations[{index}]")
    for index, record in enumerate(rules):
        _validate_rule(report, record, f"capability-rules.yml.capability_rules[{index}]")
    for index, record in enumerate(candidates):
        _validate_candidate(report, record, f"capability-rules.yml.skill_candidates[{index}]")
    for index, record in enumerate(gate_decisions):
        _validate_gate_decision(report, record, f"gate-decisions.yml.gate_decisions[{index}]")
    for index, record in enumerate(materializations):
        _validate_materialization(
            report, record, f"gate-decisions.yml.materializations[{index}]"
        )
    for index, record in enumerate(eval_runs):
        _validate_eval_run(report, record, f"eval-runs.yml.eval_runs[{index}]")
    for index, record in enumerate(corrections):
        path = f"correction-overlay.yml.corrections[{index}]"
        _validate_correction(
            report,
            record,
            path,
            overlay_source_id=(overlay_document or {}).get("source_id"),
        )

    typed_records = [
        ("evidence", "evidence_id", evidence),
        ("claim", "claim_id", claims),
        ("relation", "relation_id", relations),
        ("rule", "rule_id", rules),
        ("candidate", "candidate_id", candidates),
        ("gate_decision", "decision_id", gate_decisions),
        ("materialization", "materialization_id", materializations),
        ("eval_run", "eval_run_id", eval_runs),
        ("correction", "correction_id", corrections),
    ]
    if overlay_document is not None:
        typed_records.append(("overlay", "overlay_id", [overlay_document]))
    global_ids: dict[str, str] = {}
    for kind, id_key, items in typed_records:
        for index, record in enumerate(items):
            value = record.get(id_key)
            if not _is_nonempty_string(value):
                continue
            value = value.strip()
            path = f"{kind}[{index}].{id_key}"
            if value in global_ids:
                report.add_error(
                    "DUPLICATE_ID", path, f"duplicates ID already used at {global_ids[value]}"
                )
            else:
                global_ids[value] = path

    evidence_by_id = {
        record["evidence_id"]: record for record in evidence if _is_nonempty_string(record.get("evidence_id"))
    }
    claim_by_id = {
        record["claim_id"]: record for record in claims if _is_nonempty_string(record.get("claim_id"))
    }
    relation_by_id = {
        record["relation_id"]: record for record in relations if _is_nonempty_string(record.get("relation_id"))
    }
    rule_by_id = {
        record["rule_id"]: record for record in rules if _is_nonempty_string(record.get("rule_id"))
    }
    candidate_by_id = {
        record["candidate_id"]: record
        for record in candidates if _is_nonempty_string(record.get("candidate_id"))
    }
    eval_run_by_id = {
        record["eval_run_id"]: record
        for record in eval_runs if _is_nonempty_string(record.get("eval_run_id"))
    }
    gate_decision_by_id = {
        record["decision_id"]: record
        for record in gate_decisions if _is_nonempty_string(record.get("decision_id"))
    }
    materialization_by_id = {
        record["materialization_id"]: record
        for record in materializations
        if _is_nonempty_string(record.get("materialization_id"))
    }
    correction_by_id = {
        record["correction_id"]: record
        for record in corrections if _is_nonempty_string(record.get("correction_id"))
    }

    candidate_names: dict[str, str] = {}
    for index, candidate in enumerate(candidates):
        name = candidate.get("name")
        if not _is_nonempty_string(name):
            continue
        normalized_name = name.casefold()
        path = f"capability-rules.yml.skill_candidates[{index}].name"
        if normalized_name in candidate_names:
            report.add_error(
                "DUPLICATE_SKILL_NAME",
                path,
                f"duplicates candidate name already used at {candidate_names[normalized_name]}",
            )
        else:
            candidate_names[normalized_name] = path

    def foreign_keys(
        records: Sequence[Mapping[str, Any]], key: str, targets: Mapping[str, Any], base: str
    ) -> None:
        for index, record in enumerate(records):
            values = record.get(key, [])
            if not isinstance(values, list):
                continue
            for fk_index, value in enumerate(values):
                if isinstance(value, str) and value not in targets:
                    report.add_error(
                        "MISSING_FOREIGN_KEY", f"{base}[{index}].{key}[{fk_index}]",
                        f"referenced ID {value!r} does not exist"
                    )

    foreign_keys(claims, "evidence_ids", evidence_by_id, "claims")
    foreign_keys(claims, "correction_ids", correction_by_id, "claims")
    foreign_keys(relations, "claim_ids", claim_by_id, "relations")
    foreign_keys(relations, "evidence_ids", evidence_by_id, "relations")
    foreign_keys(rules, "claim_ids", claim_by_id, "rules")
    foreign_keys(rules, "relation_ids", relation_by_id, "rules")
    foreign_keys(candidates, "rule_ids", rule_by_id, "candidates")
    foreign_keys(eval_runs, "rule_ids", rule_by_id, "eval_runs")
    foreign_keys(gate_decisions, "eval_run_ids", eval_run_by_id, "gate_decisions")
    foreign_keys(corrections, "applies_to_claim_ids", claim_by_id, "corrections")

    for index, gate_decision in enumerate(gate_decisions):
        candidate_id = gate_decision.get("candidate_id")
        if _is_nonempty_string(candidate_id) and candidate_id not in candidate_by_id:
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"gate-decisions.yml.gate_decisions[{index}].candidate_id",
                f"referenced ID {candidate_id!r} does not exist",
            )
    for index, eval_run in enumerate(eval_runs):
        candidate_id = eval_run.get("candidate_id")
        path = f"eval-runs.yml.eval_runs[{index}]"
        candidate = (
            candidate_by_id.get(candidate_id)
            if _is_nonempty_string(candidate_id)
            else None
        )
        if candidate is None and _is_nonempty_string(candidate_id):
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"{path}.candidate_id",
                f"referenced ID {candidate_id!r} does not exist",
            )
        elif candidate is not None and isinstance(eval_run.get("rule_ids"), list):
            candidate_rule_ids = _string_set(candidate.get("rule_ids", []))
            for rule_index, rule_id in enumerate(eval_run.get("rule_ids", [])):
                if isinstance(rule_id, str) and rule_id not in candidate_rule_ids:
                    report.add_error(
                        "EVAL_RULE_NOT_IN_CANDIDATE",
                        f"{path}.rule_ids[{rule_index}]",
                        f"rule {rule_id!r} is not part of candidate {candidate_id!r}",
                    )

    current_gate_decisions = _validate_gate_decision_chains(report, gate_decisions)
    _validate_gate_prerequisites(report, current_gate_decisions)
    _validate_gate3_approval_snapshots(
        report,
        root,
        gate_decisions,
        candidate_by_id,
    )
    rule_paths = {
        record["rule_id"]: f"capability-rules.yml.capability_rules[{index}]"
        for index, record in enumerate(rules)
        if _is_nonempty_string(record.get("rule_id"))
    }
    _validate_gate3_rule_alignment(
        report,
        gate_decisions,
        current_gate_decisions,
        candidate_by_id,
        rule_by_id,
        rule_paths,
    )
    materialization_contracts = _validate_materialization_links(
        report,
        root,
        materializations,
        current_gate_decisions,
        gate_decision_by_id,
        candidate_by_id,
        rule_by_id,
    )
    _validate_completed_eval_links(
        report,
        root,
        eval_runs,
        current_gate_decisions,
        materialization_by_id,
        materialization_contracts,
    )
    _validate_gate4_acceptance_decisions(report, gate_decisions, eval_run_by_id)

    for rule_index, rule in enumerate(rules):
        support = rule.get("semantic_support")
        if not isinstance(support, dict):
            continue
        declared_claims = _string_set(rule.get("claim_ids", []))
        declared_relations = _string_set(rule.get("relation_ids", []))
        for key in SEMANTIC_SUPPORT_KEYS:
            entries = support.get(key)
            if not isinstance(entries, list):
                continue
            for support_index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    continue
                entry_path = f"capability-rules.yml.capability_rules[{rule_index}].semantic_support.{key}[{support_index}]"
                raw_claim_ids = entry.get("claim_ids", [])
                for claim_index, claim_id in enumerate(
                    raw_claim_ids if isinstance(raw_claim_ids, list) else []
                ):
                    if isinstance(claim_id, str) and claim_id not in claim_by_id:
                        report.add_error(
                            "MISSING_FOREIGN_KEY",
                            f"{entry_path}.claim_ids[{claim_index}]",
                            f"referenced ID {claim_id!r} does not exist",
                        )
                    elif isinstance(claim_id, str) and claim_id not in declared_claims:
                        report.add_error(
                            "SEMANTIC_SUPPORT_UNDECLARED",
                            f"{entry_path}.claim_ids[{claim_index}]",
                            "semantic support claim must also appear in rule.claim_ids",
                        )
                raw_relation_ids = entry.get("relation_ids", [])
                for relation_index, relation_id in enumerate(
                    raw_relation_ids if isinstance(raw_relation_ids, list) else []
                ):
                    if isinstance(relation_id, str) and relation_id not in relation_by_id:
                        report.add_error(
                            "MISSING_FOREIGN_KEY",
                            f"{entry_path}.relation_ids[{relation_index}]",
                            f"referenced ID {relation_id!r} does not exist",
                        )
                    elif isinstance(relation_id, str) and relation_id not in declared_relations:
                        report.add_error(
                            "SEMANTIC_SUPPORT_UNDECLARED",
                            f"{entry_path}.relation_ids[{relation_index}]",
                            "semantic support relation must also appear in rule.relation_ids",
                        )

    if source_records is not None:
        for claim_index, claim in enumerate(claims):
            if claim.get("source_position") != "project-policy":
                continue
            raw_evidence_ids = claim.get("evidence_ids", [])
            for evidence_index, evidence_id in enumerate(
                raw_evidence_ids if isinstance(raw_evidence_ids, list) else []
            ):
                evidence_record = (
                    evidence_by_id.get(evidence_id)
                    if isinstance(evidence_id, str)
                    else None
                )
                if evidence_record is None:
                    continue
                source_id = evidence_record.get("source_id")
                source = (
                    source_records.get(source_id)
                    if _is_nonempty_string(source_id)
                    else None
                )
                if source is not None and source.get("source_role") != "controlling-requirements":
                    report.add_error(
                        "PROJECT_POLICY_SOURCE_ROLE",
                        f"evidence-ledger.yml.claims[{claim_index}].evidence_ids[{evidence_index}]",
                        "project-policy claim evidence must use source_role controlling-requirements",
                    )

    for correction_index, correction in enumerate(corrections):
        correction_path = f"correction-overlay.yml.corrections[{correction_index}]"
        evidence_id = correction.get("evidence_id")
        evidence_record = (
            evidence_by_id.get(evidence_id)
            if _is_nonempty_string(evidence_id)
            else None
        )
        if evidence_record is None and _is_nonempty_string(evidence_id):
            report.add_error(
                "MISSING_FOREIGN_KEY",
                f"{correction_path}.evidence_id",
                f"referenced ID {evidence_id!r} does not exist",
            )
            continue
        if evidence_record is None:
            continue
        if evidence_record.get("source_id") != (overlay_document or {}).get("source_id"):
            report.add_error(
                "CORRECTION_SOURCE_MISMATCH",
                f"{correction_path}.evidence_id",
                "correction evidence source must equal overlay source_id",
            )
        if correction.get("locator") != evidence_record.get("locator"):
            report.add_error(
                "CORRECTION_LOCATOR_MISMATCH",
                f"{correction_path}.locator",
                "correction locator must exactly match referenced evidence locator",
            )
        resolved_flags = _string_set(correction.get("resolved_quality_flags", []))
        current_flags = _string_set(evidence_record.get("quality_flags", []))
        unresolved = resolved_flags & current_flags
        if correction.get("status") == "accepted" and unresolved:
            report.add_error(
                "CORRECTION_QUALITY_FLAG_UNRESOLVED",
                f"{correction_path}.resolved_quality_flags",
                f"resolved flags remain on evidence: {', '.join(sorted(unresolved))}",
            )

    for claim_index, claim in enumerate(claims):
        correction_ids = claim.get("correction_ids", [])
        if not isinstance(correction_ids, list):
            continue
        for correction_index, correction_id in enumerate(correction_ids):
            correction = (
                correction_by_id.get(correction_id)
                if isinstance(correction_id, str)
                else None
            )
            if correction is None:
                continue
            if claim.get("status") == "accepted":
                decision = correction.get("human_decision")
                decision_value = decision.get("decision") if isinstance(decision, dict) else None
                if correction.get("status") != "accepted" or not _safe_member(
                    decision_value, {"accepted", "revised"}
                ):
                    report.add_error(
                        "BLOCKED_CORRECTION",
                        f"evidence-ledger.yml.claims[{claim_index}].correction_ids[{correction_index}]",
                        "accepted claim may use only an accepted or revised correction",
                    )
                applies_to = correction.get("applies_to_claim_ids", [])
                if not isinstance(applies_to, list) or claim.get("claim_id") not in applies_to:
                    report.add_error(
                        "CORRECTION_CLAIM_MISMATCH",
                        f"evidence-ledger.yml.claims[{claim_index}].correction_ids[{correction_index}]",
                        "correction must explicitly apply to the accepted claim",
                    )

    for claim_index, claim in enumerate(claims):
        if claim.get("status") != "accepted":
            continue
        claim_path = f"evidence-ledger.yml.claims[{claim_index}]"
        raw_evidence_ids = claim.get("evidence_ids", [])
        for evidence_id in raw_evidence_ids if isinstance(raw_evidence_ids, list) else []:
            evidence_record = (
                evidence_by_id.get(evidence_id)
                if isinstance(evidence_id, str)
                else None
            )
            if evidence_record is None:
                continue
            if evidence_record.get("status") != "accepted":
                report.add_error(
                    "BLOCKED_DEPENDENCY",
                    f"{claim_path}.evidence_ids",
                    f"accepted claim depends on non-accepted evidence {evidence_id!r}",
                )
            flags = _string_set(evidence_record.get("quality_flags", []))
            if flags:
                report.add_error(
                    "BLOCKED_DEPENDENCY",
                    f"{claim_path}.evidence_ids",
                    f"accepted claim evidence {evidence_id!r} has quality flags: {', '.join(sorted(flags))}",
                )
            if not locator_valid.get(evidence_id, False):
                report.add_error(
                    "TRACEABILITY_GAP",
                    f"{claim_path}.evidence_ids",
                    f"accepted claim evidence {evidence_id!r} lacks a valid locator",
                )

    for relation_index, relation in enumerate(relations):
        if relation.get("status") != "accepted":
            continue
        relation_path = f"concept-map.yml.relations[{relation_index}]"
        raw_claim_ids = relation.get("claim_ids", [])
        for claim_id in raw_claim_ids if isinstance(raw_claim_ids, list) else []:
            claim = claim_by_id.get(claim_id) if isinstance(claim_id, str) else None
            if claim is not None and claim.get("status") != "accepted":
                report.add_error(
                    "BLOCKED_DEPENDENCY",
                    f"{relation_path}.claim_ids",
                    f"accepted relation depends on non-accepted claim {claim_id!r}",
                )
        raw_evidence_ids = relation.get("evidence_ids", [])
        for evidence_id in raw_evidence_ids if isinstance(raw_evidence_ids, list) else []:
            evidence_record = (
                evidence_by_id.get(evidence_id)
                if isinstance(evidence_id, str)
                else None
            )
            if evidence_record is None:
                continue
            if evidence_record.get("status") != "accepted":
                report.add_error(
                    "BLOCKED_DEPENDENCY",
                    f"{relation_path}.evidence_ids",
                    f"accepted relation cites non-accepted evidence {evidence_id!r}",
                )
            flags = _string_set(evidence_record.get("quality_flags", []))
            if flags:
                report.add_error(
                    "BLOCKED_DEPENDENCY",
                    f"{relation_path}.evidence_ids",
                    f"accepted relation evidence {evidence_id!r} has quality flags: {', '.join(sorted(flags))}",
                )
            if not locator_valid.get(evidence_id, False):
                report.add_error(
                    "TRACEABILITY_GAP",
                    f"{relation_path}.evidence_ids",
                    f"accepted relation evidence {evidence_id!r} lacks a valid locator",
                )

    for index, candidate in enumerate(candidates):
        if not _safe_member(candidate.get("lifecycle"), {"accepted", "deployed"}):
            continue
        candidate_path = f"capability-rules.yml.skill_candidates[{index}]"
        candidate_id = candidate.get("candidate_id")
        candidate_rule_ids = candidate.get("rule_ids")
        if not isinstance(candidate_rule_ids, list) or not candidate_rule_ids:
            report.add_error(
                "CANDIDATE_RULES_REQUIRED",
                f"{candidate_path}.rule_ids",
                "accepted/deployed candidate must retain at least one audited rule",
            )
        gate3_decision = _applicable_current_gate(
            current_gate_decisions, "gate-3", candidate_id
        )
        if gate3_decision is None or gate3_decision.get("decision") != "approved-for-eval":
            report.add_error(
                "GATE3_APPROVAL_REQUIRED",
                f"{candidate_path}.lifecycle",
                "accepted/deployed candidate requires the current Gate 3 approved-for-eval",
            )
        else:
            approved_rule_ids = _approved_rule_ids(gate3_decision)
            if not approved_rule_ids:
                report.add_error(
                    "CANDIDATE_RULES_REQUIRED",
                    f"{candidate_path}.rule_ids",
                    "accepted/deployed candidate requires at least one accepted/revised Gate 3 rule",
                )
            for rule_id in approved_rule_ids:
                rule = rule_by_id.get(rule_id)
                if rule is not None and rule.get("status") != "accepted":
                    report.add_error(
                        "CANDIDATE_RULE_NOT_ACCEPTED",
                        f"{candidate_path}.rule_ids",
                        f"accepted/deployed candidate materializes non-accepted rule {rule_id!r}",
                    )
        gate4_decision = _applicable_current_gate(
            current_gate_decisions, "gate-4", candidate_id
        )
        if gate4_decision is None or gate4_decision.get("decision") != "accepted":
            report.add_error(
                "GATE4_ACCEPTANCE_REQUIRED",
                f"{candidate_path}.lifecycle",
                "accepted/deployed candidate requires the current Gate 4 acceptance",
            )

    important_total = 0
    important_with_locator = 0
    for index, claim in enumerate(claims):
        if claim.get("importance") != "important":
            continue
        important_total += 1
        ids = claim.get("evidence_ids", [])
        if _is_string_list(ids, nonempty=True) and all(
            item in evidence_by_id and locator_valid.get(item, False)
            for item in _string_items(ids)
        ):
            important_with_locator += 1
        else:
            report.add_error(
                "IMPORTANT_CLAIM_LOCATOR", f"claims[{index}].evidence_ids",
                "important claim lacks complete locator coverage"
            )

    accepted_rules = [item for item in rules if item.get("status") == "accepted"]
    traced_rules = 0
    for index, rule in enumerate(rules):
        if rule.get("status") != "accepted":
            continue
        rule_path = f"rules[{index}]"
        raw_direct_claim_ids = rule.get("claim_ids", [])
        raw_relation_ids = rule.get("relation_ids", [])
        direct_claim_ids = _string_items(raw_direct_claim_ids)
        relation_ids = _string_items(raw_relation_ids)
        trace_claim_ids = list(direct_claim_ids)
        trace_ok = _is_string_list(raw_direct_claim_ids) and _is_string_list(
            raw_relation_ids
        )
        for relation_id in relation_ids:
            relation = relation_by_id.get(relation_id)
            if relation is None:
                trace_ok = False
                continue
            if relation.get("status") != "accepted":
                report.add_error(
                    "BLOCKED_DEPENDENCY", f"{rule_path}.relation_ids",
                    f"accepted rule depends on non-accepted relation {relation_id!r}"
                )
                trace_ok = False
            relation_claim_ids = _string_items(relation.get("claim_ids", []))
            for claim_id in relation_claim_ids:
                if claim_id not in trace_claim_ids:
                    trace_claim_ids.append(claim_id)
            relation_evidence_ids = _string_items(relation.get("evidence_ids", []))
            for evidence_id in relation_evidence_ids:
                item = evidence_by_id.get(evidence_id)
                if item is None:
                    trace_ok = False
                    continue
                if item.get("status") != "accepted":
                    report.add_error(
                        "BLOCKED_DEPENDENCY",
                        f"{rule_path}.relation_ids",
                        f"accepted relation cites non-accepted evidence {evidence_id!r}",
                    )
                    trace_ok = False
                flags = _string_set(item.get("quality_flags", []))
                if flags:
                    report.add_error(
                        "BLOCKED_DEPENDENCY",
                        f"{rule_path}.relation_ids",
                        f"relation evidence {evidence_id!r} has quality flags: {', '.join(sorted(flags))}",
                    )
                    trace_ok = False
                if not locator_valid.get(evidence_id, False):
                    report.add_error(
                        "TRACEABILITY_GAP",
                        f"{rule_path}.relation_ids",
                        f"relation evidence {evidence_id!r} lacks a valid locator",
                    )
                    trace_ok = False
        if not trace_claim_ids:
            report.add_error(
                "TRACEABILITY_GAP", f"{rule_path}.claim_ids",
                "accepted rule must trace to at least one claim"
            )
            trace_ok = False
        for claim_id in trace_claim_ids:
            claim = claim_by_id.get(claim_id) if isinstance(claim_id, str) else None
            if claim is None:
                trace_ok = False
                continue
            if claim.get("status") != "accepted":
                report.add_error(
                    "BLOCKED_DEPENDENCY", f"{rule_path}.claim_ids",
                    f"accepted rule depends on non-accepted claim {claim_id!r}"
                )
                trace_ok = False
            evidence_ids = claim.get("evidence_ids", [])
            if not _is_string_list(evidence_ids, nonempty=True):
                report.add_error(
                    "TRACEABILITY_GAP", f"{rule_path}.claim_ids",
                    f"claim {claim_id!r} has no evidence"
                )
                trace_ok = False
                continue
            for evidence_id in _string_items(evidence_ids):
                item = evidence_by_id.get(evidence_id)
                if item is None:
                    trace_ok = False
                    continue
                if item.get("status") != "accepted":
                    report.add_error(
                        "BLOCKED_DEPENDENCY", f"{rule_path}.claim_ids",
                        f"accepted rule traces through non-accepted evidence {evidence_id!r}"
                    )
                    trace_ok = False
                flags = _string_set(item.get("quality_flags", []))
                if flags:
                    report.add_error(
                        "BLOCKED_DEPENDENCY", f"{rule_path}.claim_ids",
                        f"evidence {evidence_id!r} has quality flags: {', '.join(sorted(flags))}"
                    )
                    trace_ok = False
                if not locator_valid.get(evidence_id, False):
                    report.add_error(
                        "TRACEABILITY_GAP", f"{rule_path}.claim_ids",
                        f"evidence {evidence_id!r} lacks a valid locator"
                    )
                    trace_ok = False
        if trace_ok:
            traced_rules += 1

    task_governance = inspect_task_governance(root, sources_manifest)
    for issue in task_governance.errors:
        report.add_error(issue.code, issue.path, issue.message)
    for issue in task_governance.warnings:
        report.add_warning(issue.code, issue.path, issue.message)

    report.metrics = {
        "evidence_count": len(evidence),
        "claim_count": len(claims),
        "relation_count": len(relations),
        "capability_rule_count": len(rules),
        "skill_candidate_count": len(candidates),
        "gate_decision_count": len(gate_decisions),
        "materialization_count": len(materializations),
        "eval_run_count": len(eval_runs),
        "correction_count": len(corrections),
        "markdown_locator_count": markdown_locator_count,
        "markdown_locator_resolution_applicable": source_records is not None,
        "markdown_locator_resolved": (
            markdown_locator_resolved if source_records is not None else None
        ),
        "important_claim_locator_coverage": (
            1.0 if important_total == 0 else important_with_locator / important_total
        ),
        "accepted_rule_traceability": (
            None if not accepted_rules else traced_rules / len(accepted_rules)
        ),
        "accepted_rule_traceability_applicable": bool(accepted_rules),
        "accepted_rule_count": len(accepted_rules),
        "task_governance": task_governance.summary,
    }
    return report


def validate_distillation(
    root: Path | str,
    sources_manifest: Path | str | None = None,
) -> ValidationReport:
    """Validate one immutable, private byte snapshot of the input tree."""
    original_root = Path(root)
    try:
        display_root = str(original_root.resolve())
    except OSError:
        display_root = str(original_root)
    with distillation_read_snapshot(original_root) as snapshot_root:
        snapshot_manifest = snapshot_validation_inputs(
            snapshot_root, sources_manifest
        )
        report = _validate_distillation_snapshot(snapshot_root, snapshot_manifest)
    report.root = display_root
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate distillation YAML structure and traceability only."
    )
    parser.add_argument(
        "distillation_dir",
        help="Directory containing the five required governance YAML records",
    )
    parser.add_argument(
        "--sources-manifest",
        help=(
            "Sources manifest used for source metadata checks; required for accepted/deployed "
            "candidate validation"
        ),
    )
    args = parser.parse_args(argv)
    try:
        report = validate_distillation(
            Path(args.distillation_dir),
            Path(args.sources_manifest) if args.sources_manifest else None,
        )
    except DistillationInputError as exc:
        print(json.dumps({
            "validator_scope": "structure-and-traceability-only",
            "truth_assessed": False,
            "behavior_effectiveness_assessed": False,
            "ok": False,
            "input_error": {
                "code": exc.code, "path": str(exc.path), "message": exc.message
            },
        }, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
