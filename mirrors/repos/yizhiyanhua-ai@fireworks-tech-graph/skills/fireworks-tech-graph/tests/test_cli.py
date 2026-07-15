from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "fireworks.py"


class UnifiedCLITest(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_examples_and_validate_are_machine_readable(self) -> None:
        examples = self.run_cli("examples")
        self.assertEqual(examples.returncode, 0, examples.stderr)
        self.assertIn("fixtures/mem0-style1.json", json.loads(examples.stdout)["examples"])
        validated = self.run_cli("validate", "memory", "fixtures/mem0-style1.json")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        validation = json.loads(validated.stdout)
        self.assertTrue(validation["ok"])
        self.assertEqual(validation["style"]["id"], 1)
        self.assertEqual(validation["semantics"]["profile"], "generic")

    def test_render_check_inspect_and_export_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = root / "diagram.svg"
            report = root / "layout.json"
            page = root / "diagram.html"
            rendered = self.run_cli(
                "render", "architecture", "fixtures/api-flow-style7.json", str(svg), "--report", str(report)
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertTrue(svg.is_file())
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["ok"])
            checked = self.run_cli("check", str(svg))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            inspected = self.run_cli("inspect", str(svg))
            inspection = json.loads(inspected.stdout)
            self.assertEqual(inspection["generator"], "fireworks-tech-graph")
            self.assertEqual(inspection["style_id"], "7")
            self.assertEqual(inspection["semantic_profile"], "generic")
            exported = self.run_cli("export-html", str(svg), str(page))
            self.assertEqual(exported.returncode, 0, exported.stderr)
            self.assertIn('data-action="zoom-in"', page.read_text(encoding="utf-8"))

    def test_checked_in_interactive_example_matches_current_cli_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = root / "api-flow.svg"
            page = root / "interactive-architecture.html"
            rendered = self.run_cli("render", "architecture", "fixtures/api-flow-style7.json", str(svg))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            exported = self.run_cli(
                "export-html",
                str(svg),
                str(page),
                "--title",
                "API Integration Flow",
                "--slug",
                "api-integration-flow",
            )
            self.assertEqual(exported.returncode, 0, exported.stderr)
            expected = ROOT / "examples" / "interactive-architecture.html"
            self.assertEqual(page.read_bytes(), expected.read_bytes())

    def test_legacy_generator_writes_a_failure_report_without_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = root / "unsafe.svg"
            report = root / "layout.json"
            invalid = json.dumps({"schema_version": 2, "nodes": [], "arrows": []})
            process = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate-from-template.py"),
                    "architecture",
                    str(svg),
                    invalid,
                    "--layout-report",
                    str(report),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertFalse(svg.exists())
            failure = json.loads(report.read_text(encoding="utf-8"))
            self.assertFalse(failure["ok"])
            self.assertEqual(failure["issues"][0]["code"], "LAYOUT_ERROR")


if __name__ == "__main__":
    unittest.main()
