#!/usr/bin/env python3
"""Unit tests for resolve_provenance.py (stdlib unittest; no third-party deps)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from resolve_provenance import resolve_provenance, _interpret_source


class TmpMixin(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, content) -> str:
        p = self.tmp / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, (dict, list)):
            p.write_text(json.dumps(content), encoding="utf-8")
        else:
            p.write_text(content, encoding="utf-8")
        return str(p)


class TestInterpretSource(unittest.TestCase):
    def test_owner_repo_shorthand(self):
        self.assertEqual(_interpret_source("octo/cat"), ("octo/cat", "repo"))

    def test_github_url(self):
        self.assertEqual(
            _interpret_source("https://github.com/octo/cat.git"), ("octo/cat", "repo")
        )

    def test_relative_paths(self):
        self.assertEqual(_interpret_source("./plugins/x"), (None, "relative"))
        self.assertEqual(_interpret_source("../x"), (None, "relative"))
        self.assertEqual(_interpret_source("/abs/x"), (None, "relative"))

    def test_object_forms(self):
        self.assertEqual(
            _interpret_source({"type": "git", "url": "https://github.com/o/r"}),
            ("o/r", "repo"),
        )
        self.assertEqual(
            _interpret_source({"source": "github", "repo": "o/r"}), ("o/r", "repo")
        )

    def test_none(self):
        self.assertEqual(_interpret_source(""), (None, "none"))
        self.assertEqual(_interpret_source(None), (None, "none"))


class TestResolve(TmpMixin):
    def test_frontmatter_confirmed(self):
        md = self.write(
            "SKILL.md",
            "---\nname: my-skill\nsource_repo: acme/skills\n---\n# body\n",
        )
        r = resolve_provenance("my-skill", skill_md_path=md)
        self.assertEqual(r, {"repo": "acme/skills", "source": "frontmatter",
                             "confidence": "Confirmed"})

    def test_flat_manifest_source_repo_confirmed(self):
        mf = self.write("plugin.json", {"source_repo": "acme/skills"})
        r = resolve_provenance("my-skill", manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["confidence"], "Confirmed")

    def test_flat_manifest_repository_object_likely(self):
        mf = self.write(
            "plugin.json",
            {"repository": {"type": "git", "url": "https://github.com/acme/skills.git"}},
        )
        r = resolve_provenance("my-skill", manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["confidence"], "Likely")

    def test_marketplace_absolute_source(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {"plugins": [
                {"name": "other", "source": "./plugins/other"},
                {"name": "my-skill", "source": "https://github.com/acme/skills"},
            ]},
        )
        r = resolve_provenance("my-skill", manifest_paths=[mp])
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["source"], "manifest")
        self.assertEqual(r["confidence"], "Likely")

    def test_marketplace_relative_with_marketplace_repo(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {"plugins": [{"name": "my-skill", "source": "./plugins/my-skill"}]},
        )
        r = resolve_provenance(
            "my-skill", manifest_paths=[mp], marketplace_repo="acme/marketplace"
        )
        self.assertEqual(r["repo"], "acme/marketplace")
        self.assertEqual(r["source"], "marketplace")
        self.assertEqual(r["confidence"], "Likely")

    def test_marketplace_relative_without_hint_surfaces_possible(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {"plugins": [{"name": "my-skill", "source": "./plugins/my-skill"}]},
        )
        r = resolve_provenance("my-skill", manifest_paths=[mp],
                               registry_path=str(self.tmp / "nope.json"))
        self.assertIsNone(r["repo"])
        self.assertEqual(r["source"], "marketplace-relative")
        self.assertEqual(r["confidence"], "Possible")
        self.assertIn("note", r)

    def test_registry_beats_relative_hint(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {"plugins": [{"name": "my-skill", "source": "./plugins/my-skill"}]},
        )
        reg = self.write("registry.json", {"my-skill": "acme/skills"})
        r = resolve_provenance("my-skill", manifest_paths=[mp], registry_path=reg)
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["source"], "registry")
        self.assertEqual(r["confidence"], "Likely")

    def test_vendored_config_confirmed(self):
        cfg = {"mode": "vendored", "destination": {"repo": "acme/host-plugin"}}
        r = resolve_provenance("my-skill", config=cfg,
                               registry_path=str(self.tmp / "nope.json"))
        self.assertEqual(r["repo"], "acme/host-plugin")
        self.assertEqual(r["source"], "vendored")
        self.assertEqual(r["confidence"], "Confirmed")

    def test_registry_string_and_object(self):
        reg = self.write("registry.json",
                         {"a": "o/a", "b": {"repo": "o/b", "ref": "main"}})
        self.assertEqual(
            resolve_provenance("a", registry_path=reg)["repo"], "o/a")
        self.assertEqual(
            resolve_provenance("b", registry_path=reg)["repo"], "o/b")

    def test_unknown(self):
        r = resolve_provenance("nobody", registry_path=str(self.tmp / "nope.json"))
        self.assertEqual(r, {"repo": None, "source": "unknown", "confidence": "None"})

    def test_order_frontmatter_beats_manifest(self):
        md = self.write("SKILL.md", "---\nsource_repo: acme/from-fm\n---\n")
        mf = self.write("plugin.json", {"source_repo": "acme/from-manifest"})
        r = resolve_provenance("my-skill", skill_md_path=md, manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/from-fm")
        self.assertEqual(r["source"], "frontmatter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
