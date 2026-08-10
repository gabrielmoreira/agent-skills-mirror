from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from ocr_book_source import (
    OCRRunError,
    run_docx_bundle,
    run_scanned_pdf,
)
from verify_ocr_locators import verify


TSV = (
    "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
    "5\t1\t1\t1\t1\t1\t10\t20\t30\t12\t91.5\tAlpha\n"
)
EMPTY_TSV = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"


class FakeRunner:
    def __init__(self, *, tsv=TSV, fail_item=False):
        self.tsv = tsv
        self.plain_text = "" if tsv == EMPTY_TSV else "Alpha\r\n"
        self.fail_item = fail_item
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((list(args), dict(kwargs)))
        self.assert_safe(kwargs)
        if args[:2] == ["tesseract", "--version"]:
            return subprocess.CompletedProcess(args, 0, "tesseract 5.3.0\n", "")
        if args[:2] == ["tesseract", "--list-langs"]:
            return subprocess.CompletedProcess(args, 0, "List of available languages (2):\neng\nchi_sim\n", "")
        if args[:2] == ["pdftoppm", "-v"]:
            return subprocess.CompletedProcess(args, 0, "", "pdftoppm version 24.01\n")
        if args[0] == "pdfinfo":
            return subprocess.CompletedProcess(args, 0, "Pages:          2\n", "")
        if args[0] == "pdftoppm":
            Path(args[-1]).with_suffix(".png").write_bytes(
                b"page-" + args[args.index("-f") + 1].encode()
            )
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "tesseract":
            if self.fail_item:
                return subprocess.CompletedProcess(args, 1, "", "synthetic OCR failure")
            if args[-1] == "tsv":
                return subprocess.CompletedProcess(args, 0, self.tsv, "")
            return subprocess.CompletedProcess(args, 0, self.plain_text, "")
        raise AssertionError(args)

    @staticmethod
    def assert_safe(kwargs):
        if kwargs.get("shell") is not False:
            raise AssertionError("OCR runner must never use a shell")


def all_tools(_name):
    return "/usr/bin/fake"


class OCRBookSourceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_id = "book-ocr-001"
        self.raw_source = self.root / "raw" / "book.docx"
        self.raw_source.parent.mkdir()
        self.raw_source.write_bytes(b"synthetic-docx-source")
        self.source_hash = "sha256:" + hashlib.sha256(self.raw_source.read_bytes()).hexdigest()
        self.manifest = self.root / "sources.yml"
        self.write_manifest("book-docx")
        self.bundle = self.root / "normalized" / self.source_id
        (self.bundle / "media").mkdir(parents=True)
        self.image = self.bundle / "media" / "image.png"
        self.image.write_bytes(b"synthetic-image")
        image_hash = hashlib.sha256(self.image.read_bytes()).hexdigest()
        (self.bundle / "media-map.yml").write_text(yaml.safe_dump({
            "schema_version": 1,
            "source_id": self.source_id,
            "assets": [{
                "asset_id": "media-001", "extracted_path": "media/image.png",
                "sha256_extracted": image_hash,
            }],
            "occurrences": [
                {"occurrence_id": "occ-001", "figure_id": "figure-001", "asset_id": "media-001"},
                {"occurrence_id": "occ-002", "figure_id": "figure-002", "asset_id": "media-001"},
            ],
        }, sort_keys=False), encoding="utf-8")
        self.refresh_normalized_checksums()

    def tearDown(self):
        self.tempdir.cleanup()

    def write_manifest(self, source_type):
        coverage = "all-pages" if source_type == "book-pdf-scan" else "all-images"
        self.manifest.write_text(yaml.safe_dump({
            "schema_version": 2,
            "sources": [{
                "id": self.source_id, "type": source_type,
                "source_role": "primary-book", "provenance_role": "method-source",
                "privacy": "private", "checksum": self.source_hash,
                "local_path": self.raw_source.relative_to(self.root).as_posix(),
                "ocr_policy": {
                    "required": True, "coverage": coverage,
                    "execution_mode": "local-only", "engine": "tesseract",
                    "languages": ["eng"],
                    **({"renderer": "poppler-pdftoppm", "dpi": 300} if source_type == "book-pdf-scan" else {}),
                },
            }],
        }, sort_keys=False), encoding="utf-8")

    def set_manifest_languages(self, languages):
        document = yaml.safe_load(self.manifest.read_text(encoding="utf-8"))
        document["sources"][0]["ocr_policy"]["languages"] = list(languages)
        self.manifest.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    def refresh_normalized_checksums(self):
        generated = []
        for path in (self.bundle / "media-map.yml", self.image):
            generated.append({
                "path": path.relative_to(self.bundle).as_posix(),
                "byte_size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
        digest = self.source_hash.removeprefix("sha256:")
        (self.bundle / "checksums.yml").write_text(yaml.safe_dump({
            "schema_version": 1, "source_id": self.source_id,
            "source": {
                "sha256_before": digest, "sha256_after": digest,
                "sha256_unchanged": True,
            },
            "generated_files": generated,
        }, sort_keys=False), encoding="utf-8")

    def test_docx_all_occurrences_are_bound_and_duplicate_asset_runs_once(self):
        self.set_manifest_languages(["chi_sim", "eng"])
        before = {
            path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (self.raw_source, self.image, self.bundle / "media-map.yml", self.bundle / "checksums.yml")
        }
        runner = FakeRunner()
        output = self.root / "ocr" / self.source_id
        summary = run_docx_bundle(
            self.bundle, output, source_id=self.source_id,
            sources_manifest=self.manifest, languages=["chi_sim", "eng"],
            runner=runner, which=all_tools,
        )
        self.assertEqual("completed", summary["status"])
        self.assertEqual(2, summary["coverage"]["occurrence_count"])
        self.assertEqual(1, summary["coverage"]["attempted_items"])
        tesseract_calls = [call for call, _ in runner.calls if call[0] == "tesseract" and call[1] not in {"--version", "--list-langs"}]
        self.assertEqual(2, len(tesseract_calls))
        record = json.loads((output / "ocr-results.jsonl").read_text().strip())
        self.assertEqual(["occ-001", "occ-002"], record["context"]["media_occurrence_ids"])
        self.assertEqual("Alpha\r\n", record["raw_text"])
        self.assertEqual("Alpha\n", record["normalized_text"])
        after = {
            path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (self.raw_source, self.image, self.bundle / "media-map.yml", self.bundle / "checksums.yml")
        }
        self.assertEqual(before, after)

    def test_empty_ocr_is_recorded_not_skipped(self):
        output = self.root / "empty"
        summary = run_docx_bundle(
            self.bundle, output, source_id=self.source_id,
            sources_manifest=self.manifest, languages=["eng"],
            runner=FakeRunner(tsv=EMPTY_TSV), which=all_tools,
        )
        self.assertEqual(1, summary["coverage"]["empty"])
        record = json.loads((output / "ocr-results.jsonl").read_text().strip())
        self.assertEqual("empty", record["status"])
        self.assertIn("ocr-empty", record["quality_flags"])

    def test_ocr_failure_writes_blocked_bundle_and_fails_closed(self):
        output = self.root / "failed"
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, output, source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(fail_item=True), which=all_tools,
            )
        self.assertEqual("OCR_COVERAGE_INCOMPLETE", caught.exception.code)
        self.assertEqual("blocked", yaml.safe_load((output / "ocr-manifest.yml").read_text())["status"])

    def test_missing_engine_and_nonempty_output_are_stable_errors(self):
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, self.root / "missing", source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(), which=lambda _name: None,
            )
        self.assertEqual("OCR_ENGINE_UNAVAILABLE", caught.exception.code)
        output = self.root / "nonempty"; output.mkdir(); (output / "keep").write_text("x")
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, output, source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(), which=all_tools,
            )
        self.assertEqual("OCR_OUTPUT_NOT_EMPTY", caught.exception.code)

    def test_missing_language_pack_and_pdf_renderer_are_stable_errors(self):
        class EnglishOnly(FakeRunner):
            def __call__(self, args, **kwargs):
                if args[:2] == ["tesseract", "--list-langs"]:
                    self.calls.append((list(args), dict(kwargs)))
                    self.assert_safe(kwargs)
                    return subprocess.CompletedProcess(args, 0, "List of available languages (1):\neng\n", "")
                return super().__call__(args, **kwargs)
        self.set_manifest_languages(["chi_sim"])
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, self.root / "missing-language", source_id=self.source_id,
                sources_manifest=self.manifest, languages=["chi_sim"],
                runner=EnglishOnly(), which=all_tools,
            )
        self.assertEqual("OCR_LANGUAGE_MISSING", caught.exception.code)

        pdf = self.root / "missing-renderer.pdf"; pdf.write_bytes(b"pdf")
        self.source_hash = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
        self.write_manifest("book-pdf-scan")
        with self.assertRaises(OCRRunError) as caught:
            run_scanned_pdf(
                pdf, self.root / "missing-renderer", source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(),
                which=lambda name: None if name == "pdftoppm" else "/usr/bin/fake",
            )
        self.assertEqual("PDF_RENDERER_UNAVAILABLE", caught.exception.code)

    def test_source_policy_language_mismatch_fails_before_ocr(self):
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, self.root / "policy-mismatch",
                source_id=self.source_id, sources_manifest=self.manifest,
                languages=["chi_sim"], runner=FakeRunner(), which=all_tools,
            )
        self.assertEqual("OCR_SOURCE_POLICY_MISMATCH", caught.exception.code)

    def test_normalized_media_hash_drift_fails_closed(self):
        self.image.write_bytes(b"drift-after-normalization")
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, self.root / "normalized-drift",
                source_id=self.source_id, sources_manifest=self.manifest,
                languages=["eng"], runner=FakeRunner(), which=all_tools,
            )
        self.assertEqual("OCR_NORMALIZED_BUNDLE_HASH_MISMATCH", caught.exception.code)

    def test_unsupported_image_is_recorded_failed_not_skipped(self):
        unsupported = self.image.with_suffix(".emf")
        self.image.rename(unsupported)
        self.image = unsupported
        media_map = yaml.safe_load((self.bundle / "media-map.yml").read_text())
        media_map["assets"][0]["extracted_path"] = "media/image.emf"
        media_map["assets"][0]["sha256_extracted"] = hashlib.sha256(
            unsupported.read_bytes()
        ).hexdigest()
        (self.bundle / "media-map.yml").write_text(
            yaml.safe_dump(media_map, sort_keys=False), encoding="utf-8"
        )
        self.refresh_normalized_checksums()
        output = self.root / "unsupported"
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, output, source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(), which=all_tools,
            )
        self.assertEqual("OCR_COVERAGE_INCOMPLETE", caught.exception.code)
        record = json.loads((output / "ocr-results.jsonl").read_text().strip())
        self.assertEqual("failed", record["status"])
        self.assertEqual("OCR_IMAGE_FORMAT_UNSUPPORTED", record["error_code"])

    def test_unbound_docx_occurrence_blocks_complete_coverage(self):
        media_map = yaml.safe_load((self.bundle / "media-map.yml").read_text())
        media_map["occurrences"][1]["asset_id"] = "missing-asset"
        (self.bundle / "media-map.yml").write_text(
            yaml.safe_dump(media_map, sort_keys=False), encoding="utf-8"
        )
        self.refresh_normalized_checksums()
        output = self.root / "unbound-occurrence"
        with self.assertRaises(OCRRunError) as caught:
            run_docx_bundle(
                self.bundle, output, source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FakeRunner(), which=all_tools,
            )
        self.assertEqual("OCR_COVERAGE_INCOMPLETE", caught.exception.code)
        manifest = yaml.safe_load((output / "ocr-manifest.yml").read_text())
        self.assertEqual(["occ-002"], manifest["coverage"]["unbound_occurrence_ids"])

    def test_scanned_pdf_renders_every_page_at_fixed_300_dpi(self):
        pdf = self.root / "book.pdf"; pdf.write_bytes(b"synthetic-pdf")
        self.raw_source = pdf
        self.source_hash = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
        self.write_manifest("book-pdf-scan")
        self.set_manifest_languages(["chi_sim", "eng"])
        runner = FakeRunner(); output = self.root / "pdf-ocr"
        summary = run_scanned_pdf(
            pdf, output, source_id=self.source_id, sources_manifest=self.manifest,
            languages=["chi_sim", "eng"], runner=runner, which=all_tools,
        )
        self.assertEqual(2, summary["coverage"]["attempted_items"])
        render_calls = [call for call, _ in runner.calls if call[0] == "pdftoppm" and call[1] != "-v"]
        self.assertEqual(2, len(render_calls))
        self.assertTrue(all(call[call.index("-r") + 1] == "300" for call in render_calls))
        self.assertEqual(self.source_hash, "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest())

    def test_pdf_render_failure_still_records_every_page(self):
        class FailFirstPage(FakeRunner):
            def __call__(self, args, **kwargs):
                if (
                    args[0] == "pdftoppm" and args[1] != "-v"
                    and args[args.index("-f") + 1] == "1"
                ):
                    self.calls.append((list(args), dict(kwargs)))
                    self.assert_safe(kwargs)
                    return subprocess.CompletedProcess(args, 1, "", "synthetic render failure")
                return super().__call__(args, **kwargs)

        pdf = self.root / "render-failure.pdf"; pdf.write_bytes(b"synthetic-pdf")
        self.raw_source = pdf
        self.source_hash = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
        self.write_manifest("book-pdf-scan")
        output = self.root / "render-failure"
        with self.assertRaises(OCRRunError) as caught:
            run_scanned_pdf(
                pdf, output, source_id=self.source_id,
                sources_manifest=self.manifest, languages=["eng"],
                runner=FailFirstPage(), which=all_tools,
            )
        self.assertEqual("OCR_COVERAGE_INCOMPLETE", caught.exception.code)
        records = [json.loads(line) for line in (output / "ocr-results.jsonl").read_text().splitlines()]
        self.assertEqual(2, len(records))
        self.assertEqual("PDF_RENDER_FAILED", records[0]["error_code"])
        self.assertEqual("completed", records[1]["status"])

    def test_pdf_verifier_recomputes_source_and_full_page_count(self):
        pdf = self.root / "verified.pdf"; pdf.write_bytes(b"synthetic-pdf")
        self.raw_source = pdf
        self.source_hash = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
        self.write_manifest("book-pdf-scan")
        output_root = self.root / "pdf-verified"
        run_scanned_pdf(
            pdf, output_root / self.source_id, source_id=self.source_id,
            sources_manifest=self.manifest, languages=["eng"],
            runner=FakeRunner(), which=all_tools,
        )
        distillation = self.root / "pdf-distillation"; distillation.mkdir()
        (distillation / "evidence-ledger.yml").write_text(
            yaml.safe_dump({"schema_version": 1, "evidence": [], "claims": []}),
            encoding="utf-8",
        )
        report = verify(
            distillation, output_root, self.manifest,
            runner=FakeRunner(), which=all_tools,
        )
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        pdf.write_bytes(b"source-drift")
        report = verify(
            distillation, output_root, self.manifest,
            runner=FakeRunner(), which=all_tools,
        )
        self.assertFalse(report.ok)
        self.assertIn("OCR_SOURCE_CHECKSUM_MISMATCH", {item.code for item in report.errors})

    def test_verifier_resolves_region_and_detects_hash_drift(self):
        output = self.root / "ocr-verified" / self.source_id
        run_docx_bundle(
            self.bundle, output, source_id=self.source_id,
            sources_manifest=self.manifest, languages=["eng"],
            runner=FakeRunner(), which=all_tools,
        )
        record = json.loads((output / "ocr-results.jsonl").read_text().strip())
        region = record["regions"][0]
        distillation = self.root / "distillation"; distillation.mkdir()
        (distillation / "evidence-ledger.yml").write_text(yaml.safe_dump({
            "schema_version": 1, "distillation_id": "ocr-test",
            "evidence": [{
                "evidence_id": "ev-ocr-001", "source_id": self.source_id,
                "normalized_text": region["text"],
                "locator": {
                    "source_id": self.source_id, "locator_type": "ocr-region",
                    "anchor": "figure-001#region-001", "carrier": "docx-image",
                    "image_sha256": record["image_sha256"],
                    "ocr_run_id": f"ocr-{self.source_id}-v1",
                    "ocr_record_id": record["ocr_record_id"],
                    "region_id": region["region_id"], "bbox_px": region["bbox_px"],
                    "figure_id": "figure-001", "media_occurrence_id": "occ-001",
                    "content_hash": hashlib.sha256(region["text"].encode()).hexdigest()[:12],
                },
            }], "claims": [],
        }, sort_keys=False), encoding="utf-8")
        report = verify(
            distillation,
            self.root / "ocr-verified",
            self.manifest,
            self.bundle,
        )
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        image_path = output / record["image_path"]
        image_path.write_bytes(b"drift")
        report = verify(
            distillation,
            self.root / "ocr-verified",
            self.manifest,
            self.bundle,
        )
        self.assertFalse(report.ok)
        self.assertIn("OCR_BUNDLE_HASH_MISMATCH", {item.code for item in report.errors})


if __name__ == "__main__":
    unittest.main()
