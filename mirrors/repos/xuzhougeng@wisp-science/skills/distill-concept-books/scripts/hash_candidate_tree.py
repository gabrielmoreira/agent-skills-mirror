#!/usr/bin/env python3
"""Compute the deterministic SHA-256 identity of one materialized Skill tree.

This module has no third-party dependencies.  It is intentionally strict:
every ordinary file is hashed, while symlinks, non-regular filesystem entries,
Python bytecode caches, unsafe relative paths, and trees that change during the
read are rejected rather than ignored.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


TREE_HASH_PREFIX = b"distill-concept-books:candidate-tree:v1\0"
MAX_U64 = (1 << 64) - 1


class CandidateTreeError(RuntimeError):
    """Raised when a candidate tree cannot be hashed safely and completely."""

    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"


@dataclass(frozen=True)
class _FileRecord:
    relative_path: str
    path_bytes: bytes
    absolute_path: Path
    stat_result: os.stat_result


@dataclass(frozen=True)
class _DirectoryRecord:
    relative_path: str
    absolute_path: Path
    stat_result: os.stat_result


def canonical_candidate_path(value: str) -> str:
    """Return a canonical relative POSIX path or raise CandidateTreeError."""
    display = value if isinstance(value, str) else repr(value)
    if not isinstance(value, str) or not value or value != value.strip():
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", display,
            "candidate path must be a non-empty string without surrounding whitespace",
        )
    if "\\" in value or "\x00" in value:
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", value,
            "candidate path must use POSIX separators and contain no NUL byte",
        )
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", value,
            "candidate path must be canonical and must not contain empty, '.' or '..' components",
        )
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or not candidate.parts:
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", value,
            "candidate path must be relative to the distillation directory",
        )
    canonical = candidate.as_posix()
    if canonical != value:
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", value,
            "candidate path must already be in canonical POSIX form",
        )
    try:
        canonical.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", value,
            "candidate path must be valid UTF-8",
        ) from exc
    return canonical


def _reject_cache_name(name: str, display_path: str, *, directory: bool) -> None:
    if (directory and name == "__pycache__") or (not directory and name.endswith(".pyc")):
        raise CandidateTreeError(
            "CANDIDATE_CACHE_ARTIFACT",
            display_path,
            "Python cache artifacts are forbidden in a materialized candidate tree",
        )


def _same_entry(before: os.stat_result, after: os.stat_result) -> bool:
    """Compare identity and mutation-sensitive metadata for a filesystem entry."""
    return (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
        and before.st_size == after.st_size
        and before.st_mtime_ns == after.st_mtime_ns
    )


def _scan_candidate_tree(
    candidate_root: Path,
) -> tuple[list[_FileRecord], list[_DirectoryRecord]]:
    files: list[_FileRecord] = []
    directories: list[_DirectoryRecord] = []

    def scan(directory: Path, relative_directory: PurePosixPath | None) -> None:
        display_directory = (
            "." if relative_directory is None else relative_directory.as_posix()
        )
        try:
            directory_stat = directory.lstat()
        except OSError as exc:
            raise CandidateTreeError(
                "CANDIDATE_TREE_READ_ERROR", display_directory,
                f"cannot inspect candidate directory: {exc}",
            ) from exc
        if stat.S_ISLNK(directory_stat.st_mode):
            raise CandidateTreeError(
                "CANDIDATE_TREE_SYMLINK", display_directory,
                "symlink directories are forbidden",
            )
        if not stat.S_ISDIR(directory_stat.st_mode):
            raise CandidateTreeError(
                "CANDIDATE_PATH_NOT_DIRECTORY", display_directory,
                "candidate root and all traversed containers must be directories",
            )
        directories.append(_DirectoryRecord(display_directory, directory, directory_stat))
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise CandidateTreeError(
                "CANDIDATE_TREE_READ_ERROR", display_directory,
                f"cannot enumerate candidate directory: {exc}",
            ) from exc

        for entry in entries:
            relative = (
                PurePosixPath(entry.name)
                if relative_directory is None
                else relative_directory / entry.name
            )
            relative_string = relative.as_posix()
            try:
                path_bytes = relative_string.encode("utf-8", errors="strict")
            except UnicodeEncodeError as exc:
                raise CandidateTreeError(
                    "CANDIDATE_TREE_PATH_ENCODING", relative_string,
                    "tree entry path must be valid UTF-8",
                ) from exc
            try:
                entry_stat = os.lstat(entry.path)
            except OSError as exc:
                raise CandidateTreeError(
                    "CANDIDATE_TREE_READ_ERROR", relative_string,
                    f"cannot inspect candidate tree entry: {exc}",
                ) from exc
            mode = entry_stat.st_mode
            if stat.S_ISLNK(mode):
                raise CandidateTreeError(
                    "CANDIDATE_TREE_SYMLINK", relative_string,
                    "symlinks are forbidden in a materialized candidate tree",
                )
            if stat.S_ISDIR(mode):
                _reject_cache_name(entry.name, relative_string, directory=True)
                scan(Path(entry.path), relative)
                continue
            if stat.S_ISREG(mode):
                _reject_cache_name(entry.name, relative_string, directory=False)
                files.append(
                    _FileRecord(relative_string, path_bytes, Path(entry.path), entry_stat)
                )
                continue
            raise CandidateTreeError(
                "CANDIDATE_TREE_NON_REGULAR", relative_string,
                "only ordinary files and directories are allowed",
            )

    scan(candidate_root, None)
    files.sort(key=lambda item: item.path_bytes)
    return files, directories


def _read_stable_file(record: _FileRecord) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(record.absolute_path, flags)
    except OSError as exc:
        raise CandidateTreeError(
            "CANDIDATE_TREE_READ_ERROR", record.relative_path,
            f"cannot open candidate file without following symlinks: {exc}",
        ) from exc
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise CandidateTreeError(
                "CANDIDATE_TREE_NON_REGULAR", record.relative_path,
                "entry stopped being an ordinary file during hashing",
            )
        if not _same_entry(record.stat_result, opened_stat):
            raise CandidateTreeError(
                "CANDIDATE_TREE_CHANGED", record.relative_path,
                "file changed between tree traversal and hashing",
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(descriptor)
    except OSError as exc:
        raise CandidateTreeError(
            "CANDIDATE_TREE_READ_ERROR", record.relative_path,
            f"cannot read candidate file: {exc}",
        ) from exc
    finally:
        os.close(descriptor)
    if not _same_entry(opened_stat, final_stat):
        raise CandidateTreeError(
            "CANDIDATE_TREE_CHANGED", record.relative_path,
            "file changed while it was being hashed",
        )
    content = b"".join(chunks)
    if len(content) != final_stat.st_size:
        raise CandidateTreeError(
            "CANDIDATE_TREE_CHANGED", record.relative_path,
            "bytes read do not match the stable file length",
        )
    try:
        current_path_stat = record.absolute_path.lstat()
    except OSError as exc:
        raise CandidateTreeError(
            "CANDIDATE_TREE_CHANGED", record.relative_path,
            f"file path changed after hashing: {exc}",
        ) from exc
    if not _same_entry(final_stat, current_path_stat):
        raise CandidateTreeError(
            "CANDIDATE_TREE_CHANGED", record.relative_path,
            "file path changed while the tree was being hashed",
        )
    return content


def _resolve_candidate_root(distillation_dir: Path | str, candidate_path: str) -> Path:
    canonical = canonical_candidate_path(candidate_path)
    try:
        root = Path(distillation_dir).resolve(strict=True)
    except OSError as exc:
        raise CandidateTreeError(
            "DISTILLATION_ROOT_INVALID", str(distillation_dir),
            f"distillation directory cannot be resolved: {exc}",
        ) from exc
    try:
        root_stat = root.stat()
    except OSError as exc:
        raise CandidateTreeError(
            "DISTILLATION_ROOT_INVALID", str(root),
            f"distillation directory cannot be inspected: {exc}",
        ) from exc
    if not stat.S_ISDIR(root_stat.st_mode):
        raise CandidateTreeError(
            "DISTILLATION_ROOT_INVALID", str(root),
            "distillation root must be a directory",
        )

    current = root
    for part in PurePosixPath(canonical).parts:
        current = current / part
        try:
            component_stat = current.lstat()
        except OSError as exc:
            raise CandidateTreeError(
                "CANDIDATE_PATH_MISSING", canonical,
                f"candidate path component {part!r} cannot be inspected: {exc}",
            ) from exc
        if stat.S_ISLNK(component_stat.st_mode):
            raise CandidateTreeError(
                "CANDIDATE_TREE_SYMLINK", canonical,
                "candidate path must not contain symlink components",
            )
        if current != root / Path(*PurePosixPath(canonical).parts) and not stat.S_ISDIR(
            component_stat.st_mode
        ):
            raise CandidateTreeError(
                "CANDIDATE_PATH_NOT_DIRECTORY", canonical,
                "intermediate candidate path components must be directories",
            )
    try:
        current.relative_to(root)
    except ValueError as exc:  # defensive: canonical path rules should make this impossible
        raise CandidateTreeError(
            "CANDIDATE_PATH_INVALID", canonical,
            "resolved candidate path escapes the distillation directory",
        ) from exc
    if not stat.S_ISDIR(current.lstat().st_mode):
        raise CandidateTreeError(
            "CANDIDATE_PATH_NOT_DIRECTORY", canonical,
            "candidate path must resolve to a directory",
        )
    return current


def candidate_tree_sha256(
    distillation_dir: Path | str,
    candidate_path: str,
) -> str:
    """Return ``sha256:<64 lowercase hex>`` for a safe candidate directory."""
    candidate_root = _resolve_candidate_root(distillation_dir, candidate_path)
    files, directories = _scan_candidate_tree(candidate_root)
    if len(files) > MAX_U64:
        raise CandidateTreeError(
            "CANDIDATE_TREE_TOO_LARGE", ".", "file count exceeds the v1 framing limit"
        )

    digest = hashlib.sha256()
    digest.update(TREE_HASH_PREFIX)
    digest.update(len(files).to_bytes(8, "big"))
    for record in files:
        content = _read_stable_file(record)
        if len(record.path_bytes) > MAX_U64 or len(content) > MAX_U64:
            raise CandidateTreeError(
                "CANDIDATE_TREE_TOO_LARGE", record.relative_path,
                "path or file length exceeds the v1 framing limit",
            )
        digest.update(b"F\0")
        digest.update(len(record.path_bytes).to_bytes(8, "big"))
        digest.update(record.path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)

    # A file that was already read can still be mutated while later files are
    # being hashed.  File-content writes do not change the parent directory's
    # metadata, so the directory pass below cannot detect that race.  Recheck
    # every hashed path against the stat that was proven stable when it was
    # opened and read before returning an identity for the tree.
    for record in files:
        try:
            final_stat = record.absolute_path.lstat()
        except OSError as exc:
            raise CandidateTreeError(
                "CANDIDATE_TREE_CHANGED", record.relative_path,
                f"file changed after hashing: {exc}",
            ) from exc
        if not _same_entry(record.stat_result, final_stat):
            raise CandidateTreeError(
                "CANDIDATE_TREE_CHANGED", record.relative_path,
                "file changed after it was hashed",
            )

    for directory in directories:
        try:
            final_stat = directory.absolute_path.lstat()
        except OSError as exc:
            raise CandidateTreeError(
                "CANDIDATE_TREE_CHANGED", directory.relative_path,
                f"directory changed after traversal: {exc}",
            ) from exc
        if not _same_entry(directory.stat_result, final_stat):
            raise CandidateTreeError(
                "CANDIDATE_TREE_CHANGED", directory.relative_path,
                "directory contents or metadata changed while the tree was being hashed",
            )
    return f"sha256:{digest.hexdigest()}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the deterministic v1 SHA-256 of a materialized candidate tree."
    )
    parser.add_argument("distillation_dir", help="Distillation directory that owns the candidate")
    parser.add_argument(
        "candidate_path",
        help="Canonical POSIX path to the candidate, relative to the distillation directory",
    )
    args = parser.parse_args(argv)
    try:
        result = candidate_tree_sha256(args.distillation_dir, args.candidate_path)
    except CandidateTreeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
