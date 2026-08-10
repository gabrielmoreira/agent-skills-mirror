from __future__ import annotations

import contextlib
import hashlib
import io
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

import hash_candidate_tree as hash_candidate_tree_module
from hash_candidate_tree import (
    TREE_HASH_PREFIX,
    CandidateTreeError,
    candidate_tree_sha256,
    main,
)


class CandidateTreeHashTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.candidate_path = "candidates/test-skill"
        self.candidate = self.root / self.candidate_path
        (self.candidate / "references").mkdir(parents=True)
        (self.candidate / "SKILL.md").write_bytes(b"skill-body\n")
        (self.candidate / "references" / "policy.md").write_bytes(b"policy\x00bytes\n")

    def tearDown(self):
        self.tempdir.cleanup()

    @staticmethod
    def manual_hash(files):
        digest = hashlib.sha256()
        digest.update(TREE_HASH_PREFIX)
        digest.update(len(files).to_bytes(8, "big"))
        for relative_path, content in sorted(
            files, key=lambda item: item[0].encode("utf-8")
        ):
            path_bytes = relative_path.encode("utf-8")
            digest.update(b"F\0")
            digest.update(len(path_bytes).to_bytes(8, "big"))
            digest.update(path_bytes)
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        return f"sha256:{digest.hexdigest()}"

    def test_hash_is_deterministic_prefixed_and_exactly_framed(self):
        first = candidate_tree_sha256(self.root, self.candidate_path)
        second = candidate_tree_sha256(self.root, self.candidate_path)
        expected = self.manual_hash([
            ("SKILL.md", b"skill-body\n"),
            ("references/policy.md", b"policy\x00bytes\n"),
        ])
        self.assertEqual(expected, first)
        self.assertEqual(first, second)
        self.assertRegex(first, r"^sha256:[0-9a-f]{64}$")

    def test_content_and_relative_path_changes_change_hash(self):
        original = candidate_tree_sha256(self.root, self.candidate_path)
        policy = self.candidate / "references" / "policy.md"
        policy.write_bytes(b"changed\n")
        content_changed = candidate_tree_sha256(self.root, self.candidate_path)
        self.assertNotEqual(original, content_changed)

        policy.write_bytes(b"policy\x00bytes\n")
        policy.rename(self.candidate / "references" / "renamed.md")
        path_changed = candidate_tree_sha256(self.root, self.candidate_path)
        self.assertNotEqual(original, path_changed)

    def test_rejects_file_mutated_after_its_read_while_hashing_continues(self):
        target = self.candidate / "SKILL.md"
        mutation_requested = threading.Event()
        mutation_finished = threading.Event()
        original_read = hash_candidate_tree_module._read_stable_file

        def mutate_after_read():
            self.assertTrue(mutation_requested.wait(timeout=5))
            target.write_bytes(b"changed after the stable read\n")
            mutation_finished.set()

        def read_then_wait_for_mutation(record):
            content = original_read(record)
            if record.relative_path == "SKILL.md":
                mutation_requested.set()
                self.assertTrue(mutation_finished.wait(timeout=5))
            return content

        worker = threading.Thread(target=mutate_after_read)
        worker.start()
        try:
            with mock.patch.object(
                hash_candidate_tree_module,
                "_read_stable_file",
                side_effect=read_then_wait_for_mutation,
            ):
                with self.assertRaises(CandidateTreeError) as caught:
                    candidate_tree_sha256(self.root, self.candidate_path)
            self.assertEqual("CANDIDATE_TREE_CHANGED", caught.exception.code)
            self.assertEqual("SKILL.md", caught.exception.path)
        finally:
            mutation_requested.set()
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive())

    def test_cli_outputs_only_prefixed_hash_on_success(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main([str(self.root), self.candidate_path])
        self.assertEqual(0, status)
        self.assertEqual("", stderr.getvalue())
        self.assertEqual(
            candidate_tree_sha256(self.root, self.candidate_path),
            stdout.getvalue().strip(),
        )

    def test_rejects_absolute_parent_and_noncanonical_paths(self):
        for unsafe in (
            "/tmp/test-skill",
            "../test-skill",
            "candidates/../test-skill",
            "candidates//test-skill",
            "candidates/./test-skill",
            "candidates\\test-skill",
        ):
            with self.subTest(candidate_path=unsafe):
                with self.assertRaises(CandidateTreeError) as caught:
                    candidate_tree_sha256(self.root, unsafe)
                self.assertEqual("CANDIDATE_PATH_INVALID", caught.exception.code)

    def test_rejects_symlink_without_following_it(self):
        link = self.candidate / "linked-policy.md"
        try:
            os.symlink(self.candidate / "references" / "policy.md", link)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaises(CandidateTreeError) as caught:
            candidate_tree_sha256(self.root, self.candidate_path)
        self.assertEqual("CANDIDATE_TREE_SYMLINK", caught.exception.code)

    def test_rejects_python_cache_directory_and_pyc_file(self):
        cache = self.candidate / "__pycache__"
        cache.mkdir()
        with self.assertRaises(CandidateTreeError) as caught:
            candidate_tree_sha256(self.root, self.candidate_path)
        self.assertEqual("CANDIDATE_CACHE_ARTIFACT", caught.exception.code)
        cache.rmdir()

        (self.candidate / "compiled.pyc").write_bytes(b"bytecode")
        with self.assertRaises(CandidateTreeError) as caught:
            candidate_tree_sha256(self.root, self.candidate_path)
        self.assertEqual("CANDIDATE_CACHE_ARTIFACT", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
