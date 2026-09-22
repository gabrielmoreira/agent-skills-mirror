import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_figures.py"
SPEC = importlib.util.spec_from_file_location("audit_figures", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


def textured_panel(size=(220, 180), offset=0):
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, size[0] - 3, size[1] - 3), outline="black", width=3)
    for index in range(18):
        x = 12 + ((index * 37 + offset) % (size[0] - 30))
        y = 12 + ((index * 53 + offset * 3) % (size[1] - 30))
        draw.ellipse((x, y, x + 7 + index % 4, y + 7 + index % 5), fill=(30 + index * 7, 20, 120))
    return image


class AuditFiguresTests(unittest.TestCase):
    def test_parse_pages(self):
        self.assertEqual(audit.parse_pages("1-3, 5, 8-9", 10), [1, 2, 3, 5, 8, 9])
        with self.assertRaises(ValueError):
            audit.parse_pages("4-2", 10)
        with self.assertRaises(ValueError):
            audit.parse_pages("11", 10)

    def test_directory_prepare_proposes_gutter_split(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / "inputs"
            inputs.mkdir()
            composite = Image.new("RGB", (500, 220), "white")
            composite.paste(textured_panel((210, 180), 1), (10, 20))
            composite.paste(textured_panel((210, 180), 2), (280, 20))
            composite.save(inputs / "figure.png")
            workspace = root / "audit"

            self.assertEqual(audit.main(["prepare", "--input", str(inputs), "--output", str(workspace)]), 0)
            sources = json.loads((workspace / "sources.json").read_text(encoding="utf-8"))["sources"]
            panels = json.loads((workspace / "panels.json").read_text(encoding="utf-8"))["panels"]
            self.assertEqual(len(sources), 1)
            self.assertEqual(len(panels), 2)
            self.assertTrue((workspace / "sources-contact-sheet.png").is_file())

    def test_exact_duplicate_is_a_candidate_without_opencv(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / "inputs"
            inputs.mkdir()
            image = textured_panel(offset=5)
            image.save(inputs / "a.png")
            image.save(inputs / "b.png")
            workspace = root / "audit"

            audit.main(["prepare", "--input", str(inputs), "--output", str(workspace)])
            audit.main(["materialize", "--workspace", str(workspace)])
            audit.main(["scan", "--workspace", str(workspace), "--features", "off"])
            candidates = json.loads((workspace / "candidates.json").read_text(encoding="utf-8"))["candidates"]
            self.assertEqual(len(candidates), 1)
            self.assertTrue(candidates[0]["exact_pixel_copy"])
            self.assertIn("exact-pixel-copy", candidates[0]["signals"])
            self.assertEqual(
                audit.main([
                    "evidence", "--workspace", str(workspace),
                    "--pair", f"{candidates[0]['panel_a']},{candidates[0]['panel_b']}",
                ]),
                0,
            )
            evidence_dirs = list((workspace / "evidence").iterdir())
            self.assertEqual(len(evidence_dirs), 1)
            self.assertTrue((evidence_dirs[0] / "side-by-side.png").is_file())

    def test_overlapping_same_source_boxes_are_warned_and_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / "inputs"
            inputs.mkdir()
            textured_panel((300, 240), 8).save(inputs / "one.png")
            workspace = root / "audit"
            audit.main(["prepare", "--input", str(inputs), "--output", str(workspace)])
            source_id = json.loads((workspace / "sources.json").read_text(encoding="utf-8"))["sources"][0]["id"]
            manifest = {
                "version": 1,
                "panels": [
                    {"id": "context", "source_id": source_id, "label": "", "bbox": [0, 0, 300, 240], "kind": "unknown", "compare": True, "derivation_group": None, "proposal": False},
                    {"id": "nested", "source_id": source_id, "label": "", "bbox": [40, 30, 260, 210], "kind": "unknown", "compare": True, "derivation_group": None, "proposal": False},
                ],
            }
            (workspace / "panels.json").write_text(json.dumps(manifest), encoding="utf-8")
            audit.main(["materialize", "--workspace", str(workspace)])
            warnings = json.loads((workspace / "manifest-warnings.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["type"] == "overlapping-boxes" for item in warnings))
            audit.main(["scan", "--workspace", str(workspace), "--features", "off"])
            summary = json.loads((workspace / "scan-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["compared_pairs"], 0)
            self.assertEqual(summary["skipped_same_source_overlaps"], 1)

    def test_pdf_large_image_is_extracted_before_render_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pdf_path = root / "paper.pdf"
            textured_panel((640, 480), 3).save(pdf_path, "PDF", resolution=144.0)
            workspace = root / "audit"
            audit.main([
                "prepare", "--input", str(pdf_path), "--output", str(workspace),
                "--pages", "1", "--min-image-pixels", "1000", "--render-fallback", "none",
            ])
            sources = json.loads((workspace / "sources.json").read_text(encoding="utf-8"))["sources"]
            self.assertGreaterEqual(len(sources), 1)
            self.assertEqual(sources[0]["input_type"], "pdf-embedded-image")
            self.assertGreaterEqual(sources[0]["width"] * sources[0]["height"], 1000)

    @unittest.skipUnless(os.environ.get("FIGURE_AUDIT_REGRESSION_PDF"), "set FIGURE_AUDIT_REGRESSION_PDF to run")
    def test_known_cross_figure_reuse_regression(self):
        try:
            import cv2  # noqa: F401
        except ImportError:
            self.skipTest("OpenCV is not installed")
        pdf_path = Path(os.environ["FIGURE_AUDIT_REGRESSION_PDF"])
        fixture = Path(__file__).resolve().parent / "fixtures" / "known-reuse-panels.json"
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "audit"
            audit.main([
                "prepare", "--input", str(pdf_path), "--output", str(workspace),
                "--pages", "32,34", "--render-fallback", "none",
            ])
            shutil.copyfile(fixture, workspace / "panels.json")
            audit.main(["materialize", "--workspace", str(workspace)])
            audit.main([
                "scan", "--workspace", str(workspace), "--features", "required",
                "--min-inliers", "8",
            ])
            candidates = json.loads((workspace / "candidates.json").read_text(encoding="utf-8"))["candidates"]
            pairs = {frozenset((item["panel_a"], item["panel_b"])): item for item in candidates}
            expected = [
                ("F2D-AR-H1WT", "F3F-H1-WT"),
                ("F2D-AR-H1KO", "F3F-H1-shSCRAM"),
                ("F2D-AR-H9WT", "F3F-H9-WT"),
                ("F2D-AR-H9KO", "F3F-H9-shSCRAM"),
            ]
            for first, second in expected:
                item = pairs[frozenset((first, second))]
                self.assertIn("sift-ransac", item["signals"])
                self.assertGreaterEqual(item["feature"]["inliers"], 8)


if __name__ == "__main__":
    unittest.main()
