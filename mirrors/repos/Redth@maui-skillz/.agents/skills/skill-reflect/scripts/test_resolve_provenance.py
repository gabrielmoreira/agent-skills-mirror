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
                             "confidence": "Confirmed", "install_scope": "unknown"})

    def test_frontmatter_returns_safe_ref_and_sha_without_paths(self):
        md = self.write(
            "SKILL.md",
            (
                "---\n"
                "name: my-skill\n"
                "source_repo: acme/skills\n"
                "source_ref: release/v2\n"
                "source_sha: abcdef1234567\n"
                f"version: {self.tmp}/private/version\n"
                "---\n# body\n"
            ),
        )
        r = resolve_provenance(
            "my-skill",
            skill_md_path=md,
            install_scope="user",
        )
        self.assertEqual(r["ref"], "release/v2")
        self.assertEqual(r["sha"], "abcdef1234567")
        self.assertEqual(r["install_scope"], "user")
        self.assertNotIn("version", r)
        self.assertNotIn(str(self.tmp), json.dumps(r))

    def test_invalid_frontmatter_repo_is_ignored(self):
        md = self.write(
            "SKILL.md",
            "---\nname: my-skill\nsource_repo: not a repository\n---\n# body\n",
        )
        r = resolve_provenance(
            "my-skill",
            skill_md_path=md,
            registry_path=str(self.tmp / "nope.json"),
        )
        self.assertEqual(
            r,
            {
                "repo": None,
                "source": "unknown",
                "confidence": "None",
                "install_scope": "unknown",
            },
        )

    def test_flat_manifest_source_repo_confirmed(self):
        mf = self.write("plugin.json", {"source_repo": "acme/skills"})
        r = resolve_provenance("my-skill", manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["confidence"], "Confirmed")

    def test_flat_manifest_repository_object_likely(self):
        mf = self.write(
            "plugin.json",
            {
                "name": "skill-bundle",
                "version": "2.4.1",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/acme/skills.git",
                },
            },
        )
        r = resolve_provenance("my-skill", manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/skills")
        self.assertEqual(r["confidence"], "Likely")
        self.assertEqual(r["plugin"], "skill-bundle")
        self.assertEqual(r["version"], "2.4.1")

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

    def test_marketplace_matches_skill_path_and_top_level_repository(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {
                "name": "acme-market",
                "repository": "https://github.com/acme/marketplace",
                "plugins": [
                    {
                        "name": "skill-bundle",
                        "source": "./",
                        "skills": [
                            "./skills/other-skill",
                            "./skills/my-skill/SKILL.md",
                        ],
                        "version": "3.1.0",
                        "ref": "release/v3",
                        "sha": "abcdef1234567",
                    }
                ],
            },
        )
        r = resolve_provenance("my-skill", manifest_paths=[mp])
        self.assertEqual(r["repo"], "acme/marketplace")
        self.assertEqual(r["source"], "marketplace")
        self.assertEqual(r["plugin"], "skill-bundle")
        self.assertEqual(r["marketplace"], "acme-market")
        self.assertEqual(r["version"], "3.1.0")
        self.assertEqual(r["ref"], "release/v3")
        self.assertEqual(r["sha"], "abcdef1234567")
        self.assertNotIn(str(self.tmp), json.dumps(r))

    def test_marketplace_top_level_repo_does_not_match_unlisted_skill(self):
        mp = self.write(
            ".claude-plugin/marketplace.json",
            {
                "name": "acme-market",
                "repository": "acme/marketplace",
                "plugins": [
                    {
                        "name": "other-bundle",
                        "source": "./",
                        "skills": ["./skills/other-skill"],
                    }
                ],
            },
        )
        r = resolve_provenance(
            "my-skill",
            manifest_paths=[mp],
            registry_path=str(self.tmp / "nope.json"),
        )
        self.assertIsNone(r["repo"])
        self.assertEqual(r["source"], "unknown")

    def test_discovers_marketplace_within_install_root(self):
        root = self.tmp / "installed-plugin"
        skill_md = self.write(
            "installed-plugin/skills/my-skill/SKILL.md",
            "---\nname: my-skill\n---\n# body\n",
        )
        self.write(
            "installed-plugin/.claude-plugin/marketplace.json",
            {
                "name": "acme-market",
                "repository": "acme/marketplace",
                "plugins": [
                    {
                        "name": "skill-bundle",
                        "source": "./",
                        "skills": ["./skills/my-skill"],
                    }
                ],
            },
        )
        r = resolve_provenance(
            "my-skill",
            skill_md_path=skill_md,
            install_root=str(root),
            install_scope="user",
            registry_path=str(self.tmp / "nope.json"),
        )
        self.assertEqual(r["repo"], "acme/marketplace")
        self.assertEqual(r["plugin"], "skill-bundle")
        self.assertEqual(r["install_scope"], "user")
        self.assertNotIn(str(root), json.dumps(r))

    def test_manifest_discovery_does_not_cross_install_root(self):
        root = self.tmp / "installed-plugin"
        skill_md = self.write(
            "installed-plugin/skills/my-skill/SKILL.md",
            "---\nname: my-skill\n---\n# body\n",
        )
        self.write(
            ".claude-plugin/marketplace.json",
            {
                "repository": "acme/wrong-parent",
                "plugins": [
                    {
                        "name": "skill-bundle",
                        "source": "./",
                        "skills": ["./skills/my-skill"],
                    }
                ],
            },
        )
        r = resolve_provenance(
            "my-skill",
            skill_md_path=skill_md,
            install_root=str(root),
            registry_path=str(self.tmp / "nope.json"),
        )
        self.assertIsNone(r["repo"])
        self.assertEqual(r["source"], "unknown")

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
        self.assertEqual(
            resolve_provenance("b", registry_path=reg)["ref"], "main")

    def test_unknown(self):
        r = resolve_provenance("nobody", registry_path=str(self.tmp / "nope.json"))
        self.assertEqual(
            r,
            {
                "repo": None,
                "source": "unknown",
                "confidence": "None",
                "install_scope": "unknown",
            },
        )

    def test_order_frontmatter_beats_manifest(self):
        md = self.write("SKILL.md", "---\nsource_repo: acme/from-fm\n---\n")
        mf = self.write("plugin.json", {"source_repo": "acme/from-manifest"})
        r = resolve_provenance("my-skill", skill_md_path=md, manifest_paths=[mf])
        self.assertEqual(r["repo"], "acme/from-fm")
        self.assertEqual(r["source"], "frontmatter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
