#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "autoreview"


def load_helper() -> dict[str, object]:
    return runpy.run_path(str(SCRIPT), run_name="autoreview_under_test")


def git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Autoreview Test",
            "GIT_AUTHOR_EMAIL": "autoreview@example.invalid",
            "GIT_COMMITTER_NAME": "Autoreview Test",
            "GIT_COMMITTER_EMAIL": "autoreview@example.invalid",
        }
    )
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def init_repo(tempdir: Path) -> Path:
    repo = tempdir / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Autoreview Test")
    git(repo, "config", "user.email", "autoreview@example.invalid")
    return repo


class AutoreviewHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.helper = load_helper()

    def test_local_bundle_blocks_sensitive_untracked_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / ".env").write_text("placeholder=true\n", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "untracked sensitive files"):
                self.helper["local_bundle"](repo)

    def test_local_bundle_omits_safe_untracked_binary_content(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / "image.bin").write_bytes(b"\x89PNG\r\n\0binary-content")

            bundle, truncated = self.helper["local_bundle"](repo)

            self.assertIn("## image.bin\n[binary file omitted]", bundle)
            self.assertFalse(truncated)

    def test_branch_bundle_rejects_unsafe_or_unknown_base_before_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
            git(repo, "add", "tracked.txt")
            git(repo, "commit", "-q", "-m", "base")

            with self.assertRaisesRegex(SystemExit, "unsafe base ref"):
                self.helper["branch_bundle"](repo, "--help")
            with self.assertRaisesRegex(SystemExit, "unknown base ref"):
                self.helper["branch_bundle"](repo, "origin/main")

    def test_git_path_list_preserves_newline_filenames(self) -> None:
        if os.name == "nt":
            self.skipTest("Windows filesystems do not support newline path components")
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            rel = "line\nbreak.txt"
            (repo / rel).write_text("content\n", encoding="utf-8")
            git(repo, "add", rel)

            paths = self.helper["git_path_list"](repo, "ls-files", "-z")

            self.assertIn(rel, paths)

    def test_review_patch_rejects_oversized_content(self) -> None:
        with self.assertRaisesRegex(SystemExit, "too large to review safely"):
            self.helper["validate_review_patch"]("local staged diff", ["safe.txt"], "x" * 25, 10)

    def test_tracked_sensitive_paths_are_blocked_in_all_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            git(repo, "add", "base.txt")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD").strip()

            (repo / ".env").write_text("placeholder=true\n", encoding="utf-8")
            git(repo, "add", ".env")
            with self.assertRaisesRegex(SystemExit, "tracked sensitive paths"):
                self.helper["local_bundle"](repo)

            git(repo, "commit", "-q", "-m", "sensitive path")
            with self.assertRaisesRegex(SystemExit, "tracked sensitive paths"):
                self.helper["branch_bundle"](repo, base)
            with self.assertRaisesRegex(SystemExit, "tracked sensitive paths"):
                self.helper["commit_bundle"](repo, "HEAD")

    def test_tracked_source_names_and_env_templates_remain_reviewable(self) -> None:
        for rel in (
            "tokenizer.py",
            "token_count.ts",
            "password_validator.go",
            ".env.example",
            "private/parser.py",
            "design-tokens/colors.json",
            "token_count/generated.py",
            ".docker/Dockerfile",
            ".docker/scripts/build.sh",
        ):
            with self.subTest(rel=rel):
                self.assertIsNone(self.helper["tracked_sensitive_repo_path_risk"](rel))

    def test_tracked_env_variants_remain_sensitive(self) -> None:
        for rel in (
            ".env-local",
            ".env_prod",
            ".env/production",
            ".env/example/production",
            ".env/template/prod",
        ):
            with self.subTest(rel=rel):
                self.assertIsNotNone(
                    self.helper["tracked_sensitive_repo_path_risk"](rel)
                )

    def test_suffixed_credential_data_paths_remain_sensitive(self) -> None:
        for rel in (
            "credentials-prod.json",
            "service-account-dev.yaml",
            "api-key.backup.json",
            "token-prod.json",
            "tokens.json",
            "auth-token.yaml",
            "prod-credentials.json",
            "google-service-account.json",
            "client-secret.yaml",
            "credentials/prod.json",
            "prod-credentials/client.conf",
            "client-secrets/account.ini",
            "credentials.txt",
            "client-secret.csv",
            ".docker/config.json",
            "deployment/.docker/config.json",
        ):
            with self.subTest(rel=rel):
                self.assertIsNotNone(
                    self.helper["tracked_sensitive_repo_path_risk"](rel)
                )

    def test_secret_detector_handles_quoted_json_keys(self) -> None:
        content = '{"' + 'api_key": "' + "a" * 24 + '"}'

        self.assertTrue(self.helper["secret_text_risk"](content))

    def test_secret_detector_handles_punctuation_and_multiline_diff_values(self) -> None:
        value = "Correct-Horse!" + "@Battery$Staple"
        patch = (
            "@@ -1 +1,2 @@\n"
            '+"api_key":\n'
            '+  "' + value + '"\n'
        )

        self.assertTrue(
            any(
                self.helper["secret_text_risk"](content)
                for content in self.helper["unified_diff_contents"](patch)
            )
        )

    def test_secret_detector_does_not_treat_code_expressions_as_values(self) -> None:
        for content in (
            "token = secrets.token_urlsafe(32)",
            'password = payload.get("password")',
            'token_endpoint = "https://accounts.example.com/oauth2/token"',
            'password_policy = "minimum-twelve-characters"',
        ):
            with self.subTest(content=content):
                self.assertFalse(self.helper["secret_text_risk"](content))

    def test_secret_detector_handles_bare_call_keyword_values(self) -> None:
        content = "client(api_key=" + "a" * 24 + ")"

        self.assertTrue(self.helper["secret_text_risk"](content))

    def test_normalized_secret_scan_does_not_cross_hunks(self) -> None:
        patch = (
            "@@ -1 +1 @@\n"
            "+password:\n"
            "@@ -20 +20 @@\n"
            '+"ordinary long string"\n'
        )

        self.assertFalse(
            any(
                self.helper["secret_text_risk"](content)
                for content in self.helper["unified_diff_contents"](patch)
            )
        )

    def test_normalized_secret_scan_handles_combined_diff_prefixes(self) -> None:
        value = "Correct-Horse!" + "@Battery$Staple"
        patch = (
            "diff --cc settings.json\n"
            "@@@ -1,1 -1,1 +1,2 @@@\n"
            '++"api_key":\n'
            '++  "' + value + '"\n'
        )

        self.assertTrue(
            any(
                self.helper["secret_text_risk"](content)
                for content in self.helper["unified_diff_contents"](patch)
            )
        )

    def test_normalized_secret_scan_separates_old_and_new_values(self) -> None:
        value = "Correct-Horse!" + "@Battery$Staple"
        patch = (
            "@@ -1,2 +1,2 @@\n"
            " password:\n"
            "-  placeholder\n"
            '+  "' + value + '"\n'
        )

        self.assertTrue(
            any(
                self.helper["secret_text_risk"](content)
                for content in self.helper["unified_diff_contents"](patch)
            )
        )

    def test_secret_detector_handles_compound_json_keys(self) -> None:
        for key in ("client_secret", "refresh_token"):
            content = '{"' + key + '": "' + "a" * 24 + '"}'
            with self.subTest(key=key):
                self.assertTrue(self.helper["secret_text_risk"](content))

    def test_secret_like_patch_content_is_blocked_in_all_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            path = repo / "settings.txt"
            path.write_text("base\n", encoding="utf-8")
            git(repo, "add", "settings.txt")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD").strip()

            path.write_text("api" + "_key=" + "a" * 24 + "\n", encoding="utf-8")
            git(repo, "add", "settings.txt")
            with self.assertRaisesRegex(SystemExit, "secret-like content"):
                self.helper["local_bundle"](repo)

            git(repo, "commit", "-q", "-m", "secret content")
            with self.assertRaisesRegex(SystemExit, "secret-like content"):
                self.helper["branch_bundle"](repo, base)
            with self.assertRaisesRegex(SystemExit, "secret-like content"):
                self.helper["commit_bundle"](repo, "HEAD")

    def test_pi_refuses_truncated_review_input(self) -> None:
        reviewer = argparse.Namespace(engine="pi", tools=True)

        with self.assertRaisesRegex(SystemExit, "pi engine refused truncated review input"):
            self.helper["ensure_reviewer_input_complete"](
                reviewer,
                True,
            )

        self.helper["ensure_reviewer_input_complete"](
            reviewer,
            False,
        )
        with self.assertRaisesRegex(SystemExit, "codex engine refused truncated review input"):
            self.helper["ensure_reviewer_input_complete"](
                argparse.Namespace(engine="codex", tools=True),
                True,
            )
        with self.assertRaisesRegex(SystemExit, "claude engine refused truncated review input"):
            self.helper["ensure_reviewer_input_complete"](
                argparse.Namespace(engine="claude", tools=True),
                True,
            )
        with self.assertRaisesRegex(SystemExit, "droid engine refused truncated review input"):
            self.helper["ensure_reviewer_input_complete"](
                argparse.Namespace(engine="droid", tools=False),
                True,
            )

    def test_safe_git_env_preserves_trusted_platform_and_helper_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            repo = init_repo(root)
            repo_bin = repo / "bin"
            trusted_bin = root / "trusted-bin"
            repo_bin.mkdir()
            trusted_bin.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "PATH": os.pathsep.join((str(repo_bin), str(trusted_bin))),
                    "SYSTEMROOT": "C:\\Windows",
                    "GIT_DIR": str(repo / ".git"),
                    "OPENAI_API_KEY": "must-not-reach-git",
                },
                clear=False,
            ):
                env = self.helper["safe_git_env"](repo)

        self.assertNotIn(str(repo_bin.resolve()), env["PATH"].split(os.pathsep))
        self.assertIn(str(trusted_bin.resolve()), env["PATH"].split(os.pathsep))
        self.assertEqual(env["SYSTEMROOT"], "C:\\Windows")
        self.assertNotIn("GIT_DIR", env)
        self.assertNotIn("OPENAI_API_KEY", env)

    def test_boolean_environment_values_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {"AUTOREVIEW_TEST_BOOL": "flase"}):
            with self.assertRaisesRegex(SystemExit, "invalid boolean environment value"):
                self.helper["env_truthy"]("AUTOREVIEW_TEST_BOOL")

    def test_droid_fails_closed_without_complete_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / "AGENTS.md").write_text("hostile instructions\n", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "droid engine is unavailable"):
                self.helper["run_droid"](argparse.Namespace(), repo, "prompt")

    def test_prompt_file_keeps_recoverable_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            (repo / "review.md").write_text("review context\n", encoding="utf-8")
            args = argparse.Namespace(prompt=[], prompt_file=["review.md"])

            prompt, truncated = self.helper["load_extra_prompt"](args, repo)

            self.assertIn("# Prompt file: review.md", prompt)
            self.assertFalse(truncated)

    def test_cursor_refuses_global_mcp_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            repo = init_repo(root)
            global_mcp = root / ".cursor" / "mcp.json"
            global_mcp.parent.mkdir()
            global_mcp.write_text("{}\n", encoding="utf-8")
            args = argparse.Namespace(
                thinking=None,
                tools=True,
                web_search=True,
                cursor_allow_workspace_instructions=True,
            )

            with mock.patch.object(Path, "home", return_value=root):
                with self.assertRaisesRegex(SystemExit, "cursor engine refused global MCP config"):
                    self.helper["run_cursor"](args, repo, "prompt")

    def test_read_text_truncates_without_scanning_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "large.txt"
            path.write_bytes(b"x" * 200_000 + b"\0tail")

            text = self.helper["read_text"](path)

            self.assertIn("[truncated at 180000 characters]", text)
            self.assertNotEqual(text, "[binary file omitted]")

    def test_evidence_file_must_be_repo_relative_and_not_symlinked(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            repo = init_repo(root)
            outside = root / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "repo-relative"):
                self.helper["validate_evidence_file"](repo, str(outside), "--prompt-file")

            target = repo / "notes.md"
            target.write_text("notes\n", encoding="utf-8")
            link = repo / "link.md"
            try:
                link.symlink_to(target)
            except OSError as exc:
                if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                    self.skipTest("Windows symlink privilege is not available")
                raise
            with self.assertRaisesRegex(SystemExit, "symlinked"):
                self.helper["validate_evidence_file"](repo, "link.md", "--dataset")

    def test_safe_engine_env_strips_process_injection_variables(self) -> None:
        old = os.environ.copy()
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            try:
                os.environ["GIT_DIR"] = "/tmp/unsafe-git-dir"
                os.environ["GIT_CONFIG_COUNT"] = "99"
                os.environ["DYLD_INSERT_LIBRARIES"] = "/tmp/unsafe.dylib"
                os.environ["NODE_OPTIONS"] = "--require=/tmp/unsafe.js"

                env = self.helper["safe_engine_env"](repo)

                self.assertNotEqual(env.get("GIT_DIR"), "/tmp/unsafe-git-dir")
                self.assertEqual(
                    env["GIT_CONFIG_COUNT"],
                    str(len(self.helper["ENGINE_GIT_CONFIG_OVERRIDES"])),
                )
                self.assertNotIn("DYLD_INSERT_LIBRARIES", env)
                self.assertNotIn("NODE_OPTIONS", env)
            finally:
                os.environ.clear()
                os.environ.update(old)

    def test_safe_engine_env_excludes_repo_local_path_entries(self) -> None:
        old_path = os.environ.get("PATH", "")
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            os.environ["PATH"] = f"{repo}{os.pathsep}{old_path}"
            try:
                env = self.helper["safe_engine_env"](repo)
            finally:
                os.environ["PATH"] = old_path

            self.assertNotIn(str(repo.resolve()), env["PATH"].split(os.pathsep))

    def test_safe_engine_env_ignores_inaccessible_path_entries(self) -> None:
        old_path = os.environ.get("PATH", "")
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            repo = init_repo(root)
            blocked = root / "blocked"
            os.environ["PATH"] = f"{blocked}{os.pathsep}{old_path}"
            original_exists = Path.exists

            def fake_exists(path: Path) -> bool:
                if str(path) == str(blocked):
                    raise PermissionError("access denied")
                return original_exists(path)

            try:
                with mock.patch.object(Path, "exists", fake_exists):
                    env = self.helper["safe_engine_env"](repo)
            finally:
                os.environ["PATH"] = old_path

            self.assertNotIn(str(blocked), env["PATH"].split(os.pathsep))

    def test_run_with_heartbeat_replaces_undecodable_engine_output(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            result = self.helper["run_with_heartbeat"](
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.stdout.buffer.write(b'\\x90\\n')",
                ],
                Path(tempdir),
                label="decode-test",
                heartbeat_seconds=1,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("\ufffd", result.stdout)

    def test_large_repo_relative_evidence_file_is_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = init_repo(Path(tempdir))
            evidence = repo / "evidence.txt"
            evidence.write_text("x" * 600_000, encoding="utf-8")

            _, content, truncated = self.helper["validate_evidence_file"](repo, "evidence.txt", "--dataset")

            self.assertIn("[truncated at 180000 characters]", content)
            self.assertTrue(truncated)

    def test_copilot_allows_web_fetch_only_when_web_search_is_enabled(self) -> None:
        captured: list[list[str]] = []

        def fake_run_with_heartbeat(
            cmd: list[str],
            cwd: Path,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            captured.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, '{"findings":[]}', "")

        self.helper["run_copilot"].__globals__["run_with_heartbeat"] = fake_run_with_heartbeat
        self.helper["run_copilot"].__globals__["resolve_command"] = (
            lambda command, repo: f"/resolved/{command}"
        )
        args = argparse.Namespace(
            copilot_bin="copilot",
            thinking=None,
            tools=True,
            model=None,
            web_search=False,
            stream_engine_output=False,
        )

        self.helper["run_copilot"](args, Path("/repo"), "prompt")

        self.assertNotIn("--allow-tool=web_fetch", captured[-1])
        self.assertFalse(any(arg == "--allow-all-urls" for arg in captured[-1]))

        args.web_search = True
        self.helper["run_copilot"](args, Path("/repo"), "prompt")

        self.assertIn("--allow-tool=web_fetch", captured[-1])
        self.assertIn("--allow-all-urls", captured[-1])

    def test_self_test_shortcut_runs_deterministic_checks(self) -> None:
        command = [str(SCRIPT), "--self-test"]
        if os.name == "nt":
            command = [sys.executable, str(SCRIPT), "--self-test"]
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("autoreview engine isolation self-test: ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
