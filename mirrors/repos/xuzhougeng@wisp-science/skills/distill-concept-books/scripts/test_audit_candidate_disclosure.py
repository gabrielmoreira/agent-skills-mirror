from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import yaml

from audit_candidate_disclosure import (
    DisclosureInputError,
    audit_candidate_disclosure,
    main,
)


class CandidateDisclosureAuditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.candidate = self.root / "candidate"
        self.candidate.mkdir()
        self.manifest = self.root / "private-sources.yml"
        self.identities = {
            "title": "Velvet Quasar Methods",
            "author": ["Nora Exampleton"],
            "publisher": "Imaginary Meridian Press",
            "isbn": "978-1-23-456789-0",
            "edition": "Synthetic third edition",
            "series_title": "Nightglass Inquiry Series",
            "local_path": "sources/raw/Velvet-Quasar-Methods.docx",
        }
        self._write_manifest()

    def tearDown(self):
        self.tempdir.cleanup()

    def _write_manifest(self, **overrides):
        source = {
            "id": "source-opaque-7f31",
            "type": "book-docx",
            "source_role": "primary-book",
            "provenance_role": "method-source",
            **self.identities,
            **overrides,
            "checksum": "sha256:" + "a" * 64,
            "locator_strategy": {"primary": "ooxml-block"},
        }
        self.manifest.write_text(
            yaml.safe_dump({"schema_version": 2, "sources": [source]}, sort_keys=False),
            encoding="utf-8",
        )

    def _write_candidate(self, relative: str, content: str) -> Path:
        path = self.candidate / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _identity_findings(self, report, category=None):
        findings = [
            finding
            for finding in report.get("findings", [])
            if finding["code"] == "IDENTITY_DISCLOSURE"
        ]
        if category is not None:
            findings = [
                finding
                for finding in findings
                if finding["identity_category"] == category
            ]
        return findings

    def test_passes_source_neutral_candidate_and_exempt_metadata_words(self):
        self._write_manifest(local_path="sources/raw/source-opaque-7f31.docx")
        self._write_candidate(
            "evals/task-cases.json",
            json.dumps(
                {
                    "title": "Synthetic audit task",
                    "source_id": "source-opaque-7f31",
                    "checksum": "sha256:" + "b" * 64,
                    "locator": "section-4",
                    "reviewer": "human-delegate",
                }
            ),
        )
        self._write_candidate(
            "SKILL.md",
            "The authorizing Gate checks lifecycle state.\n"
            "Source files are read as immutable bytes for deterministic validation.\n",
        )
        first = audit_candidate_disclosure(self.candidate, self.manifest)
        second = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual(first, second)
        self.assertTrue(first["ok"])
        self.assertEqual("pass", first["status"])
        self.assertEqual([], first["findings"])

    def test_source_field_references_cannot_echo_identity_bearing_keys(self):
        forbidden_key_part = "ObsidianSyntheticKey"
        source = {
            "id": "source-opaque-key-test",
            "type": "book-docx",
            "source_role": "primary-book",
            "title": forbidden_key_part,
            f"{forbidden_key_part}_author": "Alice Exampleton",
        }
        self.manifest.write_text(
            yaml.safe_dump({"schema_version": 2, "sources": [source]}, sort_keys=False),
            encoding="utf-8",
        )
        self._write_candidate("SKILL.md", "Alice Exampleton supplies the example.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertTrue(self._identity_findings(report, "author"))
        self.assertNotIn(
            forbidden_key_part.casefold(),
            json.dumps(report, ensure_ascii=False).casefold(),
        )

    def test_detects_series_like_book_collection_field(self):
        self._write_manifest(book_collection="Synthetic Aurora Collection")
        self._write_candidate(
            "SKILL.md", "The Synthetic Aurora Collection label is forbidden.\n"
        )
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertTrue(self._identity_findings(report, "series"))

    def test_ignores_unrelated_policy_paths_and_target_identity(self):
        method_record = {
            "id": "method-source-1",
            **self.identities,
            "type": "book-docx",
            "source_role": "primary-book",
        }
        policy_record = {
            "id": "policy-source-1",
            "type": "local-policy-bundle",
            "source_role": "controlling-requirements",
            "title": "Synthetic Project Policy",
            "local_path": "docs/workflow.md",
        }
        target_record = {
            "id": "target-source-1",
            "type": "paper-pdf",
            "source_role": "eval-target",
            "provenance_role": "target-material",
            "title": "Synthetic Target Paper",
        }
        self.manifest.write_text(
            yaml.safe_dump(
                {"schema_version": 2, "sources": [method_record, policy_record, target_record]},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self._write_candidate(
            "docs/workflow.md",
            "Review Synthetic Project Policy and Synthetic Target Paper as task inputs.\n",
        )
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertTrue(report["ok"])
        self.assertEqual([], report["findings"])

    def test_detects_title_without_echoing_value(self):
        self._write_candidate("SKILL.md", "Apply Velvet Quasar Methods to the input.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(report, "title")
        self.assertTrue(findings)
        self.assertIn("sources[0].title", findings[0]["source_field_refs"])
        self.assertNotIn(self.identities["title"].casefold(), json.dumps(report).casefold())

    def test_detects_author(self):
        self._write_candidate("references/policy.md", "Nora Exampleton defines the method.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(report, "author")
        self.assertTrue(findings)
        self.assertIn("sources[0].author", findings[0]["source_field_refs"])

    def test_detects_publisher(self):
        self._write_candidate("references/provenance.md", "Issued by Imaginary Meridian Press.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertTrue(self._identity_findings(report, "publisher"))

    def test_detects_isbn_with_punctuation_variation(self):
        self._write_candidate("references/id.md", "Catalog number: 978 1 23 456789 0.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(report, "isbn")
        self.assertTrue(findings)
        self.assertEqual("compact", findings[0]["match_mode"])

    def test_extra_terms_cover_alias_forms_and_named_case_without_echo(self):
        extra = self.root / "extra-terms.txt"
        forbidden = [
            "星幕译称",                 # synthetic translation
            "Xingmu Synthetic",        # synthetic transliteration
            "star-curtain-protocol",   # synthetic slug
            "霁光丛系",                 # synthetic series alias
            "Project Nightglass Case", # synthetic named case
        ]
        extra.write_text(
            "# synthetic aliases only\n" + "\n".join(forbidden) + "\n",
            encoding="utf-8",
        )
        self._write_candidate(
            "SKILL.md",
            "Apply 星幕译称 and Xingmu Synthetic.\n"
            "Route star-curtain-protocol through 霁光丛系.\n"
            "Use Project Nightglass Case as the worked example.\n",
        )
        report = audit_candidate_disclosure(
            self.candidate, self.manifest, extra_terms_file=extra
        )
        findings = self._identity_findings(report, "extra-term")
        self.assertEqual(5, len(findings))
        refs = {
            reference
            for finding in findings
            for reference in finding["source_field_refs"]
        }
        self.assertEqual(
            {f"extra_terms[line:{line}]" for line in range(2, 7)},
            refs,
        )
        serialized = json.dumps(report, ensure_ascii=False).casefold()
        compact_serialized = "".join(
            character for character in serialized if character.isalnum()
        )
        for value in forbidden:
            with self.subTest(value_type="synthetic-extra-term"):
                self.assertNotIn(value.casefold(), serialized)
                compact_value = "".join(
                    character
                    for character in value.casefold()
                    if character.isalnum()
                )
                self.assertNotIn(compact_value, compact_serialized)

    def test_detects_two_character_cjk_author_with_compact_variation(self):
        author = "霁岚"
        self._write_manifest(author=[author])
        self._write_candidate("SKILL.md", "合成署名：霁-岚。\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(report, "author")
        self.assertTrue(findings)
        self.assertEqual("compact", findings[0]["match_mode"])
        self.assertNotIn(author, json.dumps(report, ensure_ascii=False))

    def test_detects_three_character_cjk_author_with_compact_variation(self):
        author = "霁岚舟"
        self._write_manifest(author=[author])
        self._write_candidate("SKILL.md", "合成署名：霁 岚 舟。\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(report, "author")
        self.assertTrue(findings)
        self.assertEqual("compact", findings[0]["match_mode"])
        self.assertNotIn(author, json.dumps(report, ensure_ascii=False))

    def test_detects_filename_leak_and_redacts_candidate_location(self):
        leaked = "Copper Nebula Handbook"
        self._write_manifest(
            title="Unrelated Synthetic Title",
            local_path="sources/raw/Copper-Nebula-Handbook.pdf",
        )
        self._write_candidate("references/Copper-Nebula-Handbook.md", "Neutral body.\n")
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        path_findings = [
            finding
            for finding in self._identity_findings(report)
            if finding["candidate_location"]["kind"] == "path"
        ]
        self.assertTrue(path_findings)
        self.assertTrue(
            any(
                finding["identity_category"] in {"path-basename", "path-stem"}
                for finding in path_findings
            )
        )
        self.assertEqual("<redacted>", path_findings[0]["candidate_location"]["path"])
        self.assertRegex(
            path_findings[0]["candidate_location"]["path_sha256"],
            r"^sha256:[0-9a-f]{64}$",
        )
        serialized = json.dumps(report).casefold()
        self.assertNotIn(leaked.casefold(), serialized)
        self.assertNotIn("copper-nebula-handbook", serialized)

    def test_detects_generic_attribution_phrase_but_not_authorizing(self):
        self._write_candidate(
            "SKILL.md",
            "The authorizing Gate remains source-neutral.\n"
            "According to the author, the framework has three stages.\n",
        )
        report = audit_candidate_disclosure(self.candidate)
        attribution = [
            finding
            for finding in report["findings"]
            if finding["code"] == "GENERIC_SOURCE_ATTRIBUTION"
        ]
        self.assertEqual(1, len(attribution))
        self.assertEqual(2, attribution[0]["candidate_location"]["line"])

    def test_target_material_author_attribution_is_not_method_source_leak(self):
        self._write_candidate(
            "SKILL.md",
            "先记录论文作者提出的主张，再区分论文作者解释与分析者判断。\n",
        )
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        attribution = [
            finding
            for finding in report["findings"]
            if finding["code"] == "GENERIC_SOURCE_ATTRIBUTION"
        ]
        self.assertEqual([], attribution)

    def test_cli_never_echoes_forbidden_identity(self):
        secret = "Obsidian Zephyr Codex"
        self._write_manifest(title=secret, local_path="sources/raw/Obsidian-Zephyr-Codex.docx")
        self._write_candidate("Obsidian-Zephyr-Codex.md", f"Use {secret} here.\n")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(
                [str(self.candidate), "--sources-manifest", str(self.manifest)]
            )
        self.assertEqual(1, status)
        self.assertEqual("", stderr.getvalue())
        output = stdout.getvalue()
        parsed = json.loads(output)
        self.assertEqual("findings", parsed["status"])
        self.assertNotIn(secret.casefold(), output.casefold())
        compact_output = "".join(character for character in output.casefold() if character.isalnum())
        self.assertNotIn("obsidianzephyrcodex", compact_output)

    def test_fails_closed_on_symlink_and_cache_artifacts(self):
        target = self._write_candidate("references/target.md", "Neutral.\n")
        link = self.candidate / "linked.md"
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaises(DisclosureInputError) as caught:
            audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual("CANDIDATE_SYMLINK", caught.exception.code)
        link.unlink()

        (self.candidate / "__pycache__").mkdir()
        with self.assertRaises(DisclosureInputError) as caught:
            audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual("CANDIDATE_CACHE_ARTIFACT", caught.exception.code)

    def test_fails_closed_on_invalid_utf8_text(self):
        (self.candidate / "SKILL.md").write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(DisclosureInputError) as caught:
            audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual("CANDIDATE_BINARY_UNAUDITED", caught.exception.code)

    def test_cli_blocks_binary_artifact_without_echoing_content_or_identity_path(self):
        secret = "Synthetic Cover Identity"
        self._write_manifest(title=secret)
        binary_path = self.candidate / "Synthetic-Cover-Identity.png"
        binary_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00" + secret.encode("utf-8"))
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(
                [str(self.candidate), "--sources-manifest", str(self.manifest)]
            )
        self.assertEqual(2, status)
        self.assertEqual("", stderr.getvalue())
        report = json.loads(stdout.getvalue())
        self.assertEqual("CANDIDATE_BINARY_UNAUDITED", report["input_error"]["code"])
        serialized = stdout.getvalue().casefold()
        self.assertNotIn(secret.casefold(), serialized)
        self.assertNotIn("synthetic-cover-identity", serialized)
        compact_serialized = "".join(
            character for character in serialized if character.isalnum()
        )
        self.assertNotIn("syntheticcoveridentity", compact_serialized)


    def test_detects_wrapped_identity_and_attribution_phrase(self):
        self._write_candidate(
            "SKILL.md",
            "Apply Velvet\nQuasar Methods to the target.\n"
            "According to the\nauthor, reuse the framework.\n",
        )
        report = audit_candidate_disclosure(self.candidate, self.manifest)
        title_findings = self._identity_findings(report, "title")
        attribution_findings = [
            finding
            for finding in report["findings"]
            if finding["code"] == "GENERIC_SOURCE_ATTRIBUTION"
        ]
        self.assertTrue(title_findings)
        self.assertTrue(attribution_findings)
        self.assertEqual(1, title_findings[0]["candidate_location"]["line"])
        self.assertEqual(3, attribution_findings[0]["candidate_location"]["line"])

    def test_ascii_compact_match_preserves_word_boundaries(self):
        self._write_manifest(title="Signal")
        self._write_candidate("SKILL.md", "Analyze signaling dynamics.\n")
        neutral_report = audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertFalse(self._identity_findings(neutral_report, "title"))

        self._write_candidate("SKILL.md", "Apply Sig-nal to the task.\n")
        disclosure_report = audit_candidate_disclosure(self.candidate, self.manifest)
        findings = self._identity_findings(disclosure_report, "title")
        self.assertTrue(findings)
        self.assertEqual("compact", findings[0]["match_mode"])

    def test_cache_artifact_rejection_is_case_insensitive(self):
        cache_dir = self.candidate / "__PYCACHE__"
        cache_dir.mkdir()
        with self.assertRaises(DisclosureInputError) as caught:
            audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual("CANDIDATE_CACHE_ARTIFACT", caught.exception.code)
        cache_dir.rmdir()

        cache_file = self.candidate / "artifact.PYC"
        cache_file.write_bytes(b"synthetic cache")
        with self.assertRaises(DisclosureInputError) as caught:
            audit_candidate_disclosure(self.candidate, self.manifest)
        self.assertEqual("CANDIDATE_CACHE_ARTIFACT", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
