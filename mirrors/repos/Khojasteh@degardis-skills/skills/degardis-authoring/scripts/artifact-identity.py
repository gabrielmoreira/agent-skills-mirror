#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Compute the version 1 identity of an artifact held as a folder or a ZIP archive."""

import argparse
import hashlib
import json
import ntpath
import os
import stat
import sys
import unicodedata
import zipfile

DOMAIN = b"degardis-artifact-identity-v1\x00"
PREFIX = "degardis-artifact-v1:sha256:"
MAX_LENGTH = 2**64 - 1
CHUNK = 1 << 20

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_UNAVAILABLE = 3
EXIT_UNREADABLE = 4

EPILOG = """\
output:
  On success, standard output is one JSON object:
    {"identity": "degardis-artifact-v1:sha256:<hex>", "store": "folder" or "zip",
     "entries": <count>, "bytes": <total content bytes>}
  --entries adds "names": [{"name": <canonical name>, "size": <bytes>}, ...] in identity order.
  When no identity is computed (exit 3 or 4), standard output is
    {"identity": null, "reason": <code>, "detail": <text>}
  and standard error says what was wrong, what was expected, and what to try.
  Invalid arguments (exit 2) are reported on standard error only.

exit status:
  0  identity computed
  2  invalid arguments
  3  no identity exists under the algorithm: an invalid or duplicate canonical name,
     an entry that is a link or not stable content, or a length beyond eight bytes
  4  the artifact could not be read or held stable: missing path, unreadable file,
     damaged or encrypted archive, a --root that is not there, or content that
     changed while it was read

examples:
  artifact-identity.py ./artifact
  artifact-identity.py artifact.zip
  artifact-identity.py artifact.zip --root top --entries
"""


class Failure(Exception):
    def __init__(self, status, reason, detail, expected, attempt):
        super().__init__(detail)
        self.status = status
        self.reason = reason
        self.detail = detail
        self.expected = expected
        self.attempt = attempt


def unavailable(reason, detail, expected, attempt):
    return Failure(EXIT_UNAVAILABLE, reason, detail, expected, attempt)


def unreadable(reason, detail, expected, attempt):
    return Failure(EXIT_UNREADABLE, reason, detail, expected, attempt)


def canonical_name(components):
    joined = unicodedata.normalize("NFC", "/".join(components))
    for part in joined.split("/"):
        if part in ("", ".", ".."):
            raise unavailable(
                "invalid-name",
                f"entry name {joined!r} has an empty, '.' or '..' component",
                "relative entry names made of non-empty components",
                "report the identity as unavailable; the store holds a name the algorithm rejects",
            )
    try:
        encoded = joined.encode("utf-8")
    except UnicodeEncodeError:
        raise unavailable(
            "invalid-name",
            f"entry name {joined!r} cannot be encoded as UTF-8",
            "entry names that are valid Unicode text",
            "report the identity as unavailable; the store holds an undecodable name",
        ) from None
    return joined, encoded


class FolderEntry:
    def __init__(self, components, path, status):
        self.components = components
        self.path = path
        self.size = status.st_size
        self.mark = (status.st_size, status.st_mtime_ns)

    def read(self):
        with open(self.path, "rb") as stream:
            while chunk := stream.read(CHUNK):
                yield chunk
        status = os.stat(self.path, follow_symlinks=False)
        if (status.st_size, status.st_mtime_ns) != self.mark:
            raise changed("/".join(self.components))


class ZipEntry:
    def __init__(self, components, archive, info):
        self.components = components
        self.archive = archive
        self.info = info
        self.size = info.file_size

    def read(self):
        try:
            with self.archive.open(self.info) as stream:
                while chunk := stream.read(CHUNK):
                    yield chunk
        except (OSError, NotImplementedError):
            raise
        except Exception as error:
            raise unreadable(
                "damaged",
                f"{self.info.orig_filename} cannot be decompressed: {error}",
                "entries whose stored data decompresses to their recorded content",
                "obtain an undamaged copy of the archive",
            ) from None


def changed(name):
    return unreadable(
        "unstable",
        f"{name} changed while it was read",
        "an artifact that stays unchanged while its identity is computed",
        "stop whatever is writing to the artifact, or compute the identity of a stable copy",
    )


MOUNT_POINT_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


def is_link_status(status):
    return (stat.S_ISLNK(status.st_mode)
            or getattr(status, "st_reparse_tag", 0) == MOUNT_POINT_TAG)


def is_link(entry):
    return is_link_status(entry.stat(follow_symlinks=False))


def folder_root(path, root):
    top = os.path.abspath(path)
    base = top
    for component in root.split("/") if root else []:
        base = os.path.join(base, component)
        try:
            status = os.stat(base, follow_symlinks=False)
        except (FileNotFoundError, NotADirectoryError):
            status = None
        if status is not None and is_link_status(status):
            raise unavailable(
                "link-entry",
                f"{base} is a link to content held elsewhere",
                "a --root whose directories below the artifact are not links",
                "report the identity as unavailable, or use an authorized copy without links",
            )
        if status is None or not stat.S_ISDIR(status.st_mode):
            raise unreadable(
                "root-not-found",
                f"{root} is not a directory inside {path}",
                "a --root naming a directory inside the folder",
                "check the path given to --root",
            )
    resolved_top = os.path.normcase(os.path.realpath(top))
    resolved_base = os.path.normcase(os.path.realpath(base))
    try:
        contained = os.path.commonpath([resolved_top, resolved_base]) == resolved_top
    except ValueError:
        contained = False
    if not contained:
        raise unavailable(
            "root-outside",
            f"{root} resolves outside {path}",
            "a --root contained inside the artifact",
            "report the identity as unavailable; do not follow an external root",
        )
    return base


def walk_folder(root):
    found = []

    def visit(directory, components):
        try:
            with os.scandir(directory) as listing:
                items = list(listing)
        except OSError as error:
            raise unreadable(
                "unreadable",
                f"cannot list {directory}: {error.strerror or error}",
                "a readable directory",
                "check the path and read permission",
            ) from None
        for item in items:
            names = components + [item.name]
            shown = "/".join(names)
            if is_link(item):
                raise unavailable(
                    "link-entry",
                    f"{shown} is a link to content held elsewhere",
                    "entries holding their own content",
                    "report the identity as unavailable, or compute it for a copy without links if one is authorized",
                )
            if item.is_dir(follow_symlinks=False):
                visit(item.path, names)
            elif item.is_file(follow_symlinks=False):
                try:
                    status = item.stat(follow_symlinks=False)
                except OSError as error:
                    raise unreadable(
                        "unreadable",
                        f"cannot stat {shown}: {error.strerror or error}",
                        "readable entries",
                        "check read permission",
                    ) from None
                found.append(FolderEntry(names, item.path, status))
            else:
                raise unavailable(
                    "not-content",
                    f"{shown} is neither a regular file nor a directory",
                    "regular files and directories only",
                    "report the identity as unavailable",
                )

    visit(root, [])
    return found


def folder_marks(entries):
    return sorted(("/".join(e.components), e.mark) for e in entries)


def zip_entries(archive, root):
    found = []
    prefix = root + "/" if root else ""
    matched = False
    for info in archive.infolist():
        name = info.orig_filename
        if prefix:
            if not name.startswith(prefix):
                continue
            matched = True
            name = name[len(prefix):]
            if not name:
                continue
        if name.endswith("/") and info.file_size == 0:
            continue
        if info.create_system == 3 and stat.S_ISLNK(info.external_attr >> 16):
            raise unavailable(
                "link-entry",
                f"{info.orig_filename} is a link to content held elsewhere",
                "entries holding their own content",
                "report the identity as unavailable",
            )
        if info.flag_bits & 0x1:
            raise unreadable(
                "encrypted",
                f"{info.orig_filename} is encrypted",
                "unencrypted entries",
                "obtain an unencrypted archive",
            )
        found.append(ZipEntry(name.split("/"), archive, info))
    if prefix and not matched:
        raise unreadable(
            "root-not-found",
            f"no entry lies under {root}/ in the archive",
            "a --root naming a directory inside the archive",
            "run with --entries and no --root to see the archive's names",
        )
    return found


def canonical_entries(entries):
    named = []
    for entry in entries:
        text, encoded = canonical_name(entry.components)
        named.append((text, encoded, entry))
    named.sort(key=lambda item: item[0])
    for previous, current in zip(named, named[1:]):
        if previous[0] == current[0]:
            raise unavailable(
                "duplicate-name",
                f"two entries share the canonical name {current[0]!r}",
                "one entry per canonical name",
                "report the identity as unavailable; do not discard or choose between the entries",
            )
    return named


def encode_length(length, name):
    if not 0 <= length <= MAX_LENGTH:
        raise unavailable(
            "length",
            f"{name} has a length that does not fit in eight bytes",
            "names and contents shorter than 2**64 bytes",
            "report the identity as unavailable",
        )
    return length.to_bytes(8, byteorder="big", signed=False)


def compute(entries, list_names):
    named = canonical_entries(entries)
    digest = hashlib.sha256(DOMAIN)
    total = 0
    names = []
    for text, encoded, entry in named:
        name_length = encode_length(len(encoded), text)
        content_length = encode_length(entry.size, text)
        digest.update(name_length)
        digest.update(encoded)
        digest.update(content_length)
        count = 0
        for chunk in entry.read():
            count += len(chunk)
            digest.update(chunk)
        if count != entry.size:
            raise changed(text)
        total += count
        if list_names:
            names.append({"name": text, "size": count})
    result = {"identity": PREFIX + digest.hexdigest(), "entries": len(named), "bytes": total}
    if list_names:
        result["names"] = names
    return result


def identify_folder(path, root, list_names):
    base = folder_root(path, root)
    entries = walk_folder(base)
    before = folder_marks(entries)
    result = compute(entries, list_names)
    if folder_marks(walk_folder(base)) != before:
        raise changed(path)
    result["store"] = "folder"
    return result


def identify_zip(path, root, list_names):
    mark = os.stat(path)
    try:
        with zipfile.ZipFile(path) as archive:
            result = compute(zip_entries(archive, root), list_names)
    except zipfile.BadZipFile as error:
        raise unreadable(
            "not-an-archive",
            f"{path} is not a readable ZIP archive: {error}",
            "a folder or a ZIP archive",
            "pass the artifact's folder, or a ZIP archive of it",
        ) from None
    after = os.stat(path)
    if (after.st_size, after.st_mtime_ns) != (mark.st_size, mark.st_mtime_ns):
        raise changed(path)
    result["store"] = "zip"
    return result


def identify(path, root, list_names):
    if os.path.isdir(path):
        return identify_folder(path, root, list_names)
    if os.path.isfile(path):
        return identify_zip(path, root, list_names)
    raise unreadable(
        "not-found",
        f"{path} does not exist or is neither a folder nor a file",
        "a folder or a ZIP archive",
        "check the path",
    )


def parse(argv):
    parser = argparse.ArgumentParser(
        prog="artifact-identity.py",
        description=(
            "Compute the degardis-artifact-v1 identity of an artifact held as a folder or a\n"
            "ZIP archive from its entry names and contents. Equal identities mean equal\n"
            "content, so comparing them shows whether two copies match or whether one\n"
            "artifact changed. Reads the artifact and writes nothing."
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="the artifact: a folder or a ZIP archive")
    parser.add_argument(
        "--root",
        metavar="DIR",
        help="treat this relative directory inside the artifact, with '/' separators "
        "and no links among its directories, as its top level "
        "(default: the folder itself or the archive's root)",
    )
    parser.add_argument(
        "--entries",
        action="store_true",
        help="also list every entry's canonical name and size",
    )
    return parser.parse_args(argv)


def relative_root(value):
    supplied_root = value or ""
    root = supplied_root.rstrip("/")
    if (supplied_root.startswith("/") or "\\" in supplied_root
            or (root and any(part in ("", ".", "..") or ntpath.splitdrive(part)[0]
                             for part in root.split("/")))):
        return None
    return root


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="backslashreplace", newline="\n")
    arguments = parse(argv)
    root = relative_root(arguments.root)
    if root is None:
        print(f"artifact-identity.py: --root {arguments.root!r} must name a relative directory "
              "with '/' separators, without drive names or empty, '.' or '..' parts", file=sys.stderr)
        return EXIT_USAGE
    try:
        result = identify(arguments.path, root, arguments.entries)
    except Failure as failure:
        print(json.dumps({"identity": None, "reason": failure.reason, "detail": failure.detail}))
        print(
            f"artifact-identity.py: {failure.detail}. Expected {failure.expected}. Try: {failure.attempt}.",
            file=sys.stderr,
        )
        return failure.status
    except OSError as error:
        detail = f"cannot read the artifact: {error.strerror or error}"
        print(json.dumps({"identity": None, "reason": "unreadable", "detail": detail}))
        print(f"artifact-identity.py: {detail}. Try: check the path and read permission.", file=sys.stderr)
        return EXIT_UNREADABLE
    except RuntimeError as error:
        detail = f"cannot read the archive: {error}"
        print(json.dumps({"identity": None, "reason": "unreadable", "detail": detail}))
        print(f"artifact-identity.py: {detail}. Try: obtain an unencrypted, undamaged archive.", file=sys.stderr)
        return EXIT_UNREADABLE
    print(json.dumps(result))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
