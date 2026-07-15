from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillCompatibilityTest(unittest.TestCase):
    def test_shared_skill_entrypoint_stays_portable(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: fireworks-tech-graph", skill)
        self.assertIn("${CLAUDE_SKILL_DIR:-/absolute/path/from-codex-skill-metadata}", skill)
        self.assertNotIn("./scripts/", skill)
        self.assertLessEqual(len(skill.splitlines()), 500)

    def test_runtime_metadata_and_bundled_resources_exist(self) -> None:
        for relative_path in (
            "agents/openai.yaml",
            "references/png-export.md",
            "scripts/generate-diagram.sh",
            "scripts/svg2png.js",
        ):
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

        openai_yaml = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$fireworks-tech-graph", openai_yaml)

    def test_distribution_includes_codex_metadata(self) -> None:
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertRegex(package["version"], r"^\d+\.\d+\.\d+$")
        self.assertIn("agents/", package["files"])
        self.assertIn("schemas/", package["files"])
        self.assertEqual(package["bin"]["fireworks-tech-graph"], "scripts/fireworks.py")
        self.assertNotIn("main", package)

    def test_install_docs_cover_both_discovery_paths(self) -> None:
        for readme in ("README.md", "README.zh.md"):
            content = (ROOT / readme).read_text(encoding="utf-8")
            self.assertIn("~/.agents/skills/fireworks-tech-graph", content)
            self.assertIn("~/.claude/skills/fireworks-tech-graph", content)

    def test_style_regression_exports_a_fixed_1920px_width(self) -> None:
        script = (ROOT / "scripts" / "test-all-styles.sh").read_text(encoding="utf-8")
        self.assertIn("PNG_WIDTH=1920", script)
        self.assertIn("output_width=int(sys.argv[3])", script)
        self.assertNotIn("scale=2", script)

    def test_workflows_pin_actions_and_never_persist_checkout_credentials(self) -> None:
        workflow_dir = ROOT / ".github" / "workflows"
        if not workflow_dir.is_dir():
            self.skipTest("repository-only workflow files are not part of the Skill payload")
        for workflow in ("ci.yml", "release.yml"):
            content = (workflow_dir / workflow).read_text(encoding="utf-8")
            checkouts = content.count("actions/checkout@")
            self.assertGreater(checkouts, 0)
            self.assertEqual(checkouts, content.count("persist-credentials: false"))
            action_refs = re.findall(r"uses:\s+actions/[\w-]+@([^\s#]+)", content)
            self.assertTrue(action_refs)
            self.assertTrue(all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs))

    def test_current_release_notes_are_in_the_distribution(self) -> None:
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        notes = ROOT / "docs" / "releases" / f'v{package["version"]}.md'
        self.assertTrue(notes.is_file(), notes)
        self.assertIn("Node.js 18", notes.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
