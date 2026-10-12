from contextlib import nullcontext
import json
import os
from pathlib import Path
import runpy
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().with_name("artifact-identity.py")
HELPER = runpy.run_path(str(SCRIPT))
PREFIX = "degardis-artifact-v1:sha256:"
EMPTY = PREFIX + "fce5cc5edc51073e08d48fa124c65fca6164ccd394ad98f0b6ba0a64f03b0354"
UNICODE = PREFIX + "69dbe265308bc526980a00673ed52027970ac70f1c1156df07d73ad58342f3d2"
BINARY = PREFIX + "9316bba7a0df8964b2a8c8930c631ccdd4e9efc467e2fcf136c67ca65a584394"
CONTENTS = [("A", b"\x00\xff\n\r\n"), ("caf\u00e9.txt", b"alpha"),
            ("\ue000", b""), ("\U00010000", b"end")]

# Golden SHA-256 values use the guide's domain and manually framed uint64 fields.
# The Unicode vector separates code-point order from UTF-16 code-unit order.


class MemoryEntry:
    def __init__(self, name, content, chunk_size=1, size=None):
        self.components = name.split("/")
        self.content = content
        self.size = len(content) if size is None else size
        self.chunk_size = chunk_size

    def read(self):
        for offset in range(0, len(self.content), self.chunk_size):
            yield self.content[offset:offset + self.chunk_size]


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="artifact-identity-test-")
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)

    def cli(self, path, *arguments, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), str(path), *arguments],
                              capture_output=True, check=False, env=env)

    def success(self, path, *arguments):
        result = self.cli(path, *arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        return json.loads(result.stdout)

    def failure(self, path, status, reason, *arguments):
        result = self.cli(path, *arguments)
        self.assertEqual(result.returncode, status, result.stderr)
        output = json.loads(result.stdout)
        self.assertIsNone(output["identity"])
        self.assertEqual(output["reason"], reason)
        self.assertIn(b"Try:", result.stderr)

    def folder(self, contents, name="folder"):
        folder = self.base / name
        folder.mkdir()
        for path, content in contents:
            target = folder / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return folder

    def archive(self, contents, name="artifact.zip", compression=zipfile.ZIP_STORED,
                creator=3, timestamp=(2020, 1, 2, 3, 4, 6)):
        path = self.base / name
        with zipfile.ZipFile(path, "w", compression=compression) as archive:
            for entry, content in contents:
                info = zipfile.ZipInfo(entry, date_time=timestamp)
                info.create_system = creator
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, content, compress_type=compression)
        return path

    def rewrite_header_field(self, path, local_offset, central_offset, change):
        data = bytearray(path.read_bytes())
        for signature, offset in ((b"PK\x03\x04", local_offset), (b"PK\x01\x02", central_offset)):
            start = data.index(signature) + offset
            value = int.from_bytes(data[start:start + 2], "little")
            data[start:start + 2] = change(value).to_bytes(2, "little")
        path.write_bytes(bytes(data))
        return path

    def directory_link(self, link, target):
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                    capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.addCleanup(os.rmdir, link)
        else:
            link.symlink_to(target, target_is_directory=True)
            self.addCleanup(link.unlink)
        return link

    def test_empty_content_has_fixed_identity(self):
        folder = self.folder([])
        (folder / "empty").mkdir()
        archive = self.archive([("empty/", b"")])
        for path in (folder, archive):
            with self.subTest(path=path.name):
                output = self.success(path, "--entries")
                self.assertEqual(output["identity"], EMPTY)
                self.assertEqual(output["names"], [])
                self.assertEqual((output["entries"], output["bytes"]), (0, 0))

    def test_success_json_has_platform_independent_bytes(self):
        folder = self.folder([])
        output = self.cli(folder)
        expected = ('{"identity": "' + EMPTY
                    + '", "entries": 0, "bytes": 0, "store": "folder"}\n').encode("utf-8")
        self.assertEqual(output.returncode, 0, output.stderr)
        self.assertEqual(output.stdout, expected)
        self.assertEqual(output.stderr, b"")

    def test_process_encoding_locale_and_hash_seed_do_not_change_json_bytes(self):
        folder = self.folder(CONTENTS)
        expected = self.cli(folder, "--entries")
        self.assertEqual(expected.returncode, 0, expected.stderr)
        self.assertEqual(json.loads(expected.stdout)["identity"], UNICODE)
        for encoding, locale, seed in (("ascii:strict", "C", "1"),
                                      ("utf-16", "tr_TR.UTF-8", "42")):
            with self.subTest(encoding=encoding, locale=locale, seed=seed):
                env = dict(os.environ, PYTHONIOENCODING=encoding, LC_ALL=locale,
                           PYTHONHASHSEED=seed)
                actual = self.cli(folder, "--entries", env=env)
                self.assertEqual((actual.returncode, actual.stdout, actual.stderr),
                                 (0, expected.stdout, b""))

    def test_unicode_names_and_binary_bytes_have_fixed_identity(self):
        decomposed = [(name.replace("\u00e9", "e\u0301"), data)
                      for name, data in reversed(CONTENTS)]
        folder = self.folder(decomposed)
        archive = self.archive(CONTENTS)
        expected_names = [{"name": name, "size": len(data)} for name, data in CONTENTS]
        for path in (folder, archive):
            with self.subTest(path=path.name):
                output = self.success(path, "--entries")
                self.assertEqual(output["identity"], UNICODE)
                self.assertEqual(output["names"], expected_names)
                self.assertEqual((output["entries"], output["bytes"]), (4, 13))

    def test_chunking_and_enumeration_do_not_change_identity(self):
        for order in (CONTENTS, list(reversed(CONTENTS))):
            for chunk_size in (1, 2, 256):
                with self.subTest(order=order[0][0], chunk_size=chunk_size):
                    entries = [MemoryEntry(name, content, chunk_size) for name, content in order]
                    self.assertEqual(HELPER["compute"](entries, False)["identity"], UNICODE)

    def test_uint64_framing_uses_big_endian_and_not_machine_word_size(self):
        entry = MemoryEntry("x", bytes(range(256)), chunk_size=17)
        self.assertEqual(HELPER["compute"]([entry], False)["identity"], BINARY)
        for length, encoded in ((0, b"\0" * 8), (256, b"\0" * 6 + b"\x01\0"),
                                (2**32, b"\0\0\0\x01\0\0\0\0"),
                                (2**64 - 1, b"\xff" * 8)):
            with self.subTest(length=length):
                self.assertEqual(HELPER["encode_length"](length, "x"), encoded)

    def test_metadata_and_zip_container_representation_do_not_change_identity(self):
        folder = self.folder(CONTENTS)
        before = self.success(folder)["identity"]
        for item in folder.iterdir():
            os.utime(item, (1234567890, 1234567890))
            item.chmod(0o600)
        self.assertEqual(self.success(folder)["identity"], before)
        for creator, compression in ((0, zipfile.ZIP_STORED), (3, zipfile.ZIP_DEFLATED)):
            archive = self.archive(list(reversed(CONTENTS)) + [("empty/", b"")],
                                   name=f"{creator}.zip", compression=compression,
                                   creator=creator, timestamp=(2024, 6, 7, 8, 9, 10))
            self.assertEqual(self.success(archive)["identity"], UNICODE)

    def test_selected_root_is_relative_to_artifact(self):
        contents = [("top/nested/" + name, content) for name, content in CONTENTS]
        contents += [("outside", b"excluded")]
        for path in (self.folder(contents), self.archive(contents)):
            for root in ("top/nested", "top/nested/"):
                with self.subTest(store=path.name, root=root):
                    self.assertEqual(self.success(path, "--root", root)["identity"], UNICODE)

    def test_native_and_traversal_roots_are_usage_errors_for_both_stores(self):
        roots = ("/", "/outside", "../outside", "top/../outside", "top//nested", "./top",
                 "C:outside", "C:/outside", "top/C:/outside", "C:\\outside",
                 "..\\outside", "\\\\server\\share", "top\\nested")
        for path in (self.folder([]), self.archive([])):
            for root in roots:
                with self.subTest(store=path.name, root=root):
                    result = self.cli(path, "--root", root)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"--root", result.stderr)

    def test_missing_roots_and_artifacts_are_read_failures(self):
        for path in (self.folder([]), self.archive([])):
            self.failure(path, 4, "root-not-found", "--root", "missing")
        self.failure(self.base / "missing", 4, "not-found")
        plain = self.base / "plain"
        plain.write_bytes(b"not a zip")
        self.failure(plain, 4, "not-an-archive")

    def test_damaged_encrypted_and_unsupported_archives_are_read_failures(self):
        damaged = self.archive([("x", b"alpha")], name="damaged.zip")
        data = damaged.read_bytes()
        self.assertEqual(data.count(b"alpha"), 1)
        damaged.write_bytes(data.replace(b"alpha", b"alphb"))
        self.failure(damaged, 4, "damaged")
        encrypted = self.archive([("x", b"alpha")], name="encrypted.zip")
        self.rewrite_header_field(encrypted, 6, 8, lambda flags: flags | 0x1)
        self.failure(encrypted, 4, "encrypted")
        unsupported = self.archive([("x", b"alpha")], name="unsupported.zip")
        self.rewrite_header_field(unsupported, 8, 10, lambda method: 9)
        self.failure(unsupported, 4, "unreadable")

    def test_special_and_unlistable_folder_entries_have_no_identity(self):
        special = SimpleNamespace(
            name="pipe", path=str(self.base / "pipe"),
            stat=lambda follow_symlinks: SimpleNamespace(st_mode=stat.S_IFIFO, st_reparse_tag=0),
            is_dir=lambda follow_symlinks: False, is_file=lambda follow_symlinks: False)
        for listing, expected in ((dict(return_value=nullcontext([special])), (3, "not-content")),
                                  (dict(side_effect=PermissionError(13, "Permission denied")),
                                   (4, "unreadable"))):
            with self.subTest(expected=expected[1]):
                with patch("os.scandir", **listing):
                    with self.assertRaises(HELPER["Failure"]) as caught:
                        HELPER["walk_folder"](str(self.base))
                self.assertEqual((caught.exception.status, caught.exception.reason), expected)

    def test_root_resolving_outside_the_artifact_is_unavailable(self):
        folder = self.folder([("top/x", b"x")])
        outside = str(self.base / "elsewhere")
        realpath = os.path.realpath
        with patch("os.path.realpath",
                   side_effect=lambda path: outside if path.endswith("top") else realpath(path)):
            with self.assertRaises(HELPER["Failure"]) as caught:
                HELPER["folder_root"](str(folder), "top")
        self.assertEqual((caught.exception.status, caught.exception.reason), (3, "root-outside"))

    def test_duplicate_normalized_names_are_not_discarded(self):
        archive = self.archive([("caf\u00e9", b"one"), ("cafe\u0301", b"two")])
        self.failure(archive, 3, "duplicate-name")

    def test_invalid_names_are_unavailable(self):
        for name in ("/absolute", "a//b", "a/../b", "a/./b", "\ud800"):
            with self.subTest(name=name):
                with self.assertRaises(HELPER["Failure"]) as caught:
                    HELPER["compute"]([MemoryEntry(name, b"x")], False)
                self.assertEqual((caught.exception.status, caught.exception.reason),
                                 (3, "invalid-name"))

    def test_content_changes_including_line_endings_change_identity(self):
        first = HELPER["compute"]([MemoryEntry("x", b"line\n")], False)["identity"]
        for entry in (MemoryEntry("x", b"line\r\n"), MemoryEntry("y", b"line\n")):
            self.assertNotEqual(HELPER["compute"]([entry], False)["identity"], first)

    def test_content_size_mismatch_is_unstable(self):
        with self.assertRaises(HELPER["Failure"]) as caught:
            HELPER["compute"]([MemoryEntry("x", b"actual", size=7)], False)
        self.assertEqual((caught.exception.status, caught.exception.reason), (4, "unstable"))

    def test_unrepresentable_lengths_are_unavailable(self):
        for size in (-1, 2**64):
            with self.subTest(size=size):
                with self.assertRaises(HELPER["Failure"]) as caught:
                    HELPER["compute"]([MemoryEntry("x", b"", size=size)], False)
                self.assertEqual((caught.exception.status, caught.exception.reason), (3, "length"))

    def test_windows_junction_or_posix_symlink_ancestry_is_rejected(self):
        folder = self.folder([])
        outside = self.folder([("sub/file", b"outside")], "outside")
        self.directory_link(folder / "alias", outside)
        self.failure(folder, 3, "link-entry", "--root", "alias/sub")
        self.failure(folder, 3, "link-entry")

    def test_linked_artifact_path_has_its_target_identity(self):
        target = self.folder([("top/nested/" + name, content) for name, content in CONTENTS])
        link = self.directory_link(self.base / "linked", target)
        self.assertEqual(self.success(link)["identity"], self.success(target)["identity"])
        self.assertEqual(self.success(link, "--root", "top/nested")["identity"], UNICODE)

    def test_zip_symlinks_are_rejected(self):
        path = self.base / "link.zip"
        with zipfile.ZipFile(path, "w") as archive:
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, b"elsewhere")
        self.failure(path, 3, "link-entry")

    def test_stat_link_detection_does_not_depend_on_host_platform(self):
        for mode, tag, expected in ((stat.S_IFDIR, 0, False), (stat.S_IFLNK, 0, True),
                                    (stat.S_IFDIR, 0xA0000003, True)):
            status = SimpleNamespace(st_mode=mode, st_reparse_tag=tag)
            self.assertEqual(HELPER["is_link_status"](status), expected)

    def test_folder_snapshot_changes_are_rejected(self):
        folder = self.folder([("x", b"before")])
        compute = HELPER["compute"]

        def mutate(entries, list_names):
            result = compute(entries, list_names)
            (folder / "added").write_bytes(b"after")
            return result

        with patch.dict(HELPER["identify"].__globals__, compute=mutate):
            with self.assertRaises(HELPER["Failure"]) as caught:
                HELPER["identify"](str(folder), "", False)
        self.assertEqual(caught.exception.reason, "unstable")


if __name__ == "__main__":
    unittest.main()
