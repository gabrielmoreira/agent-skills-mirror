from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from verify_normalized_locators import verify


class NormalizedLocatorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.distillation = self.root / "distillation"
        self.normalized_root = self.root / "normalized"
        self.bundle = self.normalized_root / "book-001"
        self.manifest = self.root / "manifests" / "sources.yml"
        self.distillation.mkdir()
        self.bundle.mkdir(parents=True)
        self.manifest.parent.mkdir()
        self.source_sha = "a" * 64
        text = "Source text."
        full_hash = hashlib.sha256(text.encode()).hexdigest()
        short_hash = full_hash[:12]
        ledger = {
            "schema_version": 1,
            "distillation_id": "test-v1",
            "evidence": [{
                "evidence_id": "ev-001",
                "source_id": "book-001",
                "locator": {
                    "source_id": "book-001",
                    "locator_type": "ooxml-block",
                    "heading_path": ["Chapter 1"],
                    "ooxml_block_index": 1,
                    "content_hash": short_hash,
                },
                "raw_text": text,
                "normalized_text": text,
            }],
            "claims": [],
        }
        (self.distillation / "evidence-ledger.yml").write_text(
            yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8"
        )
        block = {
            "schema_version": 1,
            "source_id": "book-001",
            "ooxml_block_index": 1,
            "locator": {
                "source_id": "book-001",
                "heading_path": ["Chapter 1"],
                "ooxml_block_index": 1,
                "content_hash": short_hash,
            },
            "heading_path": ["Chapter 1"],
            "raw_text": text,
            "normalized_text": text,
            "text_sha256": full_hash,
            "short_content_hash": short_hash,
            "figure_ids": [],
        }
        (self.bundle / "blocks.jsonl").write_text(
            json.dumps(block) + "\n", encoding="utf-8"
        )
        for filename in ("structure.yml", "media-map.yml", "normalization-log.yml"):
            (self.bundle / filename).write_text(
                yaml.safe_dump({"schema_version": 1, "source_id": "book-001"}),
                encoding="utf-8",
            )
        self._write_checksums()
        self._write_manifest()

    def tearDown(self):
        self.tempdir.cleanup()

    def _write_manifest(self, checksum=None):
        document = {
            "schema_version": 2,
            "sources": [{
                "id": "book-001",
                "checksum": checksum or f"sha256:{self.source_sha}",
            }],
        }
        self.manifest.write_text(yaml.safe_dump(document), encoding="utf-8")

    def _write_checksums(self, *, after=None):
        generated = []
        for filename in (
            "blocks.jsonl", "structure.yml", "media-map.yml", "normalization-log.yml"
        ):
            content = (self.bundle / filename).read_bytes()
            generated.append({
                "path": filename,
                "byte_size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            })
        checksums = {
            "schema_version": 1,
            "source_id": "book-001",
            "source": {
                "sha256_before": self.source_sha,
                "sha256_after": self.source_sha if after is None else after,
                "sha256_unchanged": after is None,
            },
            "generated_files": generated,
        }
        (self.bundle / "checksums.yml").write_text(
            yaml.safe_dump(checksums, sort_keys=False), encoding="utf-8"
        )

    def _verify(self):
        return verify(self.distillation, self.normalized_root, self.manifest)

    def test_resolves_valid_locator_excerpt_and_bundle_integrity(self):
        report = self._verify()
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertEqual(1, report.checked)
        self.assertEqual(1, report.integrity_verified_sources)
        self.assertEqual(1, report.manifest_checksum_verified_sources)

    def test_rejects_hash_and_excerpt_drift(self):
        ledger = yaml.safe_load((self.distillation / "evidence-ledger.yml").read_text())
        ledger["evidence"][0]["locator"]["content_hash"] = "ffffffffffff"
        ledger["evidence"][0]["raw_text"] = "Invented text."
        (self.distillation / "evidence-ledger.yml").write_text(
            yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8"
        )
        report = self._verify()
        self.assertFalse(report.ok)
        self.assertEqual(
            {"CONTENT_HASH_MISMATCH", "EVIDENCE_TEXT_MISMATCH"},
            {item.code for item in report.errors},
        )

    def test_rejects_source_checksum_change(self):
        self._write_checksums(after="b" * 64)
        report = self._verify()
        self.assertIn("SOURCE_CHECKSUM_CHANGED", {item.code for item in report.errors})

    def test_rejects_joint_ledger_and_bundle_tamper_without_checksum_update(self):
        invented = "Invented replacement text."
        full_hash = hashlib.sha256(invented.encode()).hexdigest()
        short_hash = full_hash[:12]
        ledger = yaml.safe_load((self.distillation / "evidence-ledger.yml").read_text())
        evidence = ledger["evidence"][0]
        evidence["raw_text"] = invented
        evidence["normalized_text"] = invented
        evidence["locator"]["content_hash"] = short_hash
        (self.distillation / "evidence-ledger.yml").write_text(
            yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8"
        )
        block = json.loads((self.bundle / "blocks.jsonl").read_text())
        block["raw_text"] = invented
        block["normalized_text"] = invented
        block["text_sha256"] = full_hash
        block["short_content_hash"] = short_hash
        block["locator"]["content_hash"] = short_hash
        (self.bundle / "blocks.jsonl").write_text(json.dumps(block) + "\n")
        report = self._verify()
        self.assertFalse(report.ok)
        self.assertIn(
            "BUNDLE_GENERATED_FILE_MISMATCH", {item.code for item in report.errors}
        )

    def test_rejects_manifest_source_checksum_mismatch(self):
        self._write_manifest(checksum="sha256:" + "c" * 64)
        report = self._verify()
        self.assertIn(
            "MANIFEST_SOURCE_CHECKSUM_MISMATCH", {item.code for item in report.errors}
        )

    def test_rejects_unsafe_source_id_bundle_traversal(self):
        ledger = yaml.safe_load((self.distillation / "evidence-ledger.yml").read_text())
        ledger["evidence"][0]["source_id"] = "../outside"
        ledger["evidence"][0]["locator"]["source_id"] = "../outside"
        (self.distillation / "evidence-ledger.yml").write_text(
            yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8"
        )
        manifest = yaml.safe_load(self.manifest.read_text())
        manifest["sources"][0]["id"] = "../outside"
        self.manifest.write_text(yaml.safe_dump(manifest), encoding="utf-8")
        report = self._verify()
        self.assertFalse(report.ok)
        self.assertIn("BUNDLE_READ", {item.code for item in report.errors})

    def test_rejects_symlinked_bundle_file(self):
        target = self.root / "outside.jsonl"
        target.write_text((self.bundle / "blocks.jsonl").read_text(), encoding="utf-8")
        (self.bundle / "blocks.jsonl").unlink()
        try:
            os.symlink(target, self.bundle / "blocks.jsonl")
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        report = self._verify()
        self.assertFalse(report.ok)
        self.assertIn("BUNDLE_GENERATED_FILE_READ", {item.code for item in report.errors})


if __name__ == "__main__":
    unittest.main()
