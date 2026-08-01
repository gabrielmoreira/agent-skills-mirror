"""
test_scrub.py — unit tests for scrub.py

Run from the scripts/ directory:
    python3 -m unittest -v

Coverage
--------
- Each secret/PII category redacts correctly.
- Normal English prose is left intact (no over-redaction).
- scrub_text() returns correct category counts.
- --fail-on-secret exit-code semantics (subprocess + direct logic).
- All synthetic/fake secrets — no real credentials.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

# Ensure the scripts directory is on sys.path so scrub can be imported directly.
sys.path.insert(0, str(Path(__file__).parent))
from scrub import scrub_text, SECRET_CATEGORIES  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cats(findings: list) -> dict:
    """Return {category: count} from a findings list."""
    return {f["category"]: f["count"] for f in findings}


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

class TestEmailRedaction(unittest.TestCase):
    def test_email_is_replaced(self):
        text, _ = scrub_text("Contact alice@example.com for more info.")
        self.assertIn("[REDACTED:email]", text)
        self.assertNotIn("alice@example.com", text)

    def test_email_category_counted(self):
        _, findings = scrub_text("Send to user@domain.org please.")
        self.assertIn("email", _cats(findings))

    def test_multiple_emails_counted_correctly(self):
        _, findings = scrub_text("a@b.com and c@d.org and e@f.net")
        self.assertEqual(_cats(findings).get("email"), 3)

    def test_email_not_in_secret_categories(self):
        """Emails are PII but not 'secrets' for --fail-on-secret purposes."""
        self.assertNotIn("email", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# GitHub tokens
# ---------------------------------------------------------------------------

class TestGitHubTokens(unittest.TestCase):
    # Each prefix requires 36+ alphanumeric chars after the underscore.
    _TOKENS = {p: f"{p}_{'A' * 20}{'b' * 10}{'1' * 6}" for p in
               ("ghp", "gho", "ghu", "ghs", "ghr")}

    def test_each_prefix_is_redacted(self):
        for prefix, token in self._TOKENS.items():
            with self.subTest(prefix=prefix):
                text, _ = scrub_text(f"token: {token}")
                self.assertIn("[REDACTED:github-token]", text)
                self.assertNotIn(token, text)

    def test_github_token_category(self):
        token = list(self._TOKENS.values())[0]
        _, findings = scrub_text(token)
        self.assertIn("github-token", _cats(findings))

    def test_github_token_in_secret_categories(self):
        self.assertIn("github-token", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# AWS access key IDs
# ---------------------------------------------------------------------------

class TestAWSAccessKey(unittest.TestCase):
    # Standard fake example from AWS docs — 20 chars, starts with AKIA.
    _KEY = "AKIAIOSFODNN7EXAMPLE"

    def test_aws_key_is_redacted(self):
        text, _ = scrub_text(f"aws_access_key_id = {self._KEY}")
        self.assertIn("[REDACTED:aws-access-key]", text)
        self.assertNotIn(self._KEY, text)

    def test_aws_key_category(self):
        _, findings = scrub_text(self._KEY)
        self.assertIn("aws-access-key", _cats(findings))

    def test_aws_key_in_secret_categories(self):
        self.assertIn("aws-access-key", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# Slack tokens
# ---------------------------------------------------------------------------

class TestSlackToken(unittest.TestCase):
    # Slack token format: xox<type>-<workspace_id>-<more_stuff>
    # Assembled from fragments at runtime so the synthetic token is never a
    # contiguous literal in the committed file. This keeps secret scanners
    # (e.g. GitHub push protection) from flagging a deliberately-fake test
    # fixture, while the detector is still exercised on the realistic shape.
    _TOKEN = "xox" + "b-" + ("1" * 12) + "-" + ("2" * 12) + "-examplefaketoken1234"

    def test_xoxb_is_redacted(self):
        text, _ = scrub_text(f"SLACK_TOKEN={self._TOKEN}")
        self.assertIn("[REDACTED:slack-token]", text)
        self.assertNotIn(self._TOKEN, text)

    def test_other_xox_prefixes(self):
        for prefix in ("xoxa", "xoxp", "xoxr", "xoxs"):
            token = f"{prefix}-111-222-faketoken1234567890abc"
            with self.subTest(prefix=prefix):
                text, _ = scrub_text(token)
                self.assertIn("[REDACTED:slack-token]", text)

    def test_slack_token_in_secret_categories(self):
        self.assertIn("slack-token", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# Google API keys
# ---------------------------------------------------------------------------

class TestGoogleAPIKey(unittest.TestCase):
    # Google API keys are exactly 39 chars: "AIza" + 35 url-safe chars.
    _KEY = "AIza" + "B" * 35  # 4 + 35 = 39 chars

    def test_google_key_is_redacted(self):
        text, _ = scrub_text(f"GOOGLE_API_KEY={self._KEY}")
        self.assertIn("[REDACTED:google-api-key]", text)
        self.assertNotIn(self._KEY, text)

    def test_google_key_in_secret_categories(self):
        self.assertIn("google-api-key", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# Bearer / auth header tokens
# ---------------------------------------------------------------------------

class TestBearerToken(unittest.TestCase):
    def test_bearer_keyword_redacts_value(self):
        text, _ = scrub_text("Authorization: Bearer faketoken1234567890abcxyz")
        self.assertIn("[REDACTED:bearer-token]", text)
        self.assertNotIn("faketoken", text)

    def test_x_api_key_header_redacted(self):
        text, _ = scrub_text("X-Api-Key: mysupersecretapikey1234567890")
        self.assertIn("[REDACTED:bearer-token]", text)
        self.assertNotIn("mysupersecretapikey", text)

    def test_bearer_token_in_secret_categories(self):
        self.assertIn("bearer-token", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# PEM private-key blocks
# ---------------------------------------------------------------------------

class TestPEMKey(unittest.TestCase):
    _FAKE_PEM = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEAFAKEDATAFAKEDATAFAKEDATA\n"
        "ANOTHERLINEOFFAKEDATAabcdefghijklmnopqrstu\n"
        "-----END RSA PRIVATE KEY-----"
    )

    def test_pem_block_is_redacted(self):
        text, _ = scrub_text(self._FAKE_PEM)
        self.assertIn("[REDACTED:pem-private-key]", text)
        self.assertNotIn("MIIEowIBAAKCAQEAFAKEDATA", text)

    def test_pem_category(self):
        _, findings = scrub_text(self._FAKE_PEM)
        self.assertIn("pem-private-key", _cats(findings))

    def test_pem_in_secret_categories(self):
        self.assertIn("pem-private-key", SECRET_CATEGORIES)

    def test_ec_private_key_redacted(self):
        pem = (
            "-----BEGIN EC PRIVATE KEY-----\n"
            "FAKEECKEYDATAabcdefghijklmnop==\n"
            "-----END EC PRIVATE KEY-----"
        )
        text, _ = scrub_text(pem)
        self.assertIn("[REDACTED:pem-private-key]", text)


# ---------------------------------------------------------------------------
# JWTs
# ---------------------------------------------------------------------------

class TestJWT(unittest.TestCase):
    # Structurally valid fake JWT: base64url(header).base64url(payload).sig
    # Both header and payload must start with eyJ (base64url of '{"').
    _HEADER  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    _PAYLOAD = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkZha2VVc2VyIn0"
    _SIG     = "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    @property
    def _JWT(self):
        return f"{self._HEADER}.{self._PAYLOAD}.{self._SIG}"

    def test_jwt_is_redacted(self):
        text, _ = scrub_text(f"token: {self._JWT}")
        self.assertIn("[REDACTED:jwt]", text)
        self.assertNotIn(self._HEADER, text)

    def test_jwt_category(self):
        _, findings = scrub_text(self._JWT)
        self.assertIn("jwt", _cats(findings))

    def test_jwt_in_secret_categories(self):
        self.assertIn("jwt", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# High-entropy backstop (hex hashes + mixed-class tokens)
# ---------------------------------------------------------------------------

class TestHighEntropy(unittest.TestCase):
    # 32-char lowercase hex string (MD5-like hash)
    _FAKE_HEX = "a3f2e1d4b5c6a7b8c9d0e1f2a3b4c5d6"
    # 38-char mixed-case+digit token (all unique chars → high entropy)
    _FAKE_TOKEN = "xK9mQr3tZvNpBwY7uH2sAj1dLf4eGi6oCn8kM0"

    def test_hex_hash_is_redacted(self):
        text, _ = scrub_text(f"commit hash: {self._FAKE_HEX}")
        self.assertIn("[REDACTED:high-entropy]", text)
        self.assertNotIn(self._FAKE_HEX, text)

    def test_high_entropy_token_is_redacted(self):
        text, _ = scrub_text(self._FAKE_TOKEN)
        self.assertIn("[REDACTED:high-entropy]", text)
        self.assertNotIn(self._FAKE_TOKEN, text)

    def test_high_entropy_in_secret_categories(self):
        self.assertIn("high-entropy", SECRET_CATEGORIES)

    def test_sha256_hash_is_redacted(self):
        sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        text, _ = scrub_text(f"sha256: {sha256}")
        self.assertIn("[REDACTED:high-entropy]", text)


# ---------------------------------------------------------------------------
# Absolute path redaction
# ---------------------------------------------------------------------------

class TestPathRedaction(unittest.TestCase):
    def test_unix_users_path(self):
        text, _ = scrub_text("file: /Users/alice/projects/app/main.py")
        self.assertIn("[REDACTED:path]", text)
        self.assertNotIn("/Users/alice", text)

    def test_unix_home_path(self):
        text, _ = scrub_text("config at /home/bob/.config/app.yaml was loaded")
        self.assertIn("[REDACTED:path]", text)
        self.assertNotIn("/home/bob", text)

    def test_windows_path(self):
        text, _ = scrub_text(r"open C:\Users\carol\Documents\notes.txt")
        self.assertIn("[REDACTED:path]", text)
        self.assertNotIn("carol", text)

    def test_path_category(self):
        _, findings = scrub_text("see /Users/dave/readme.md")
        self.assertIn("path", _cats(findings))

    def test_path_not_in_secret_categories(self):
        """Paths are PII but not 'secrets' for --fail-on-secret purposes."""
        self.assertNotIn("path", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# IP address redaction
# ---------------------------------------------------------------------------

class TestIPAddressRedaction(unittest.TestCase):
    def test_ipv4_is_redacted(self):
        text, _ = scrub_text("server listening on 192.168.1.100")
        self.assertIn("[REDACTED:ip-address]", text)
        self.assertNotIn("192.168.1.100", text)

    def test_ipv6_full_is_redacted(self):
        text, _ = scrub_text("addr: 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        self.assertIn("[REDACTED:ip-address]", text)

    def test_ip_not_in_secret_categories(self):
        """IP addresses are PII but not 'secrets' for --fail-on-secret purposes."""
        self.assertNotIn("ip-address", SECRET_CATEGORIES)


# ---------------------------------------------------------------------------
# No false positives on normal prose
# ---------------------------------------------------------------------------

class TestNoProseFalsePositives(unittest.TestCase):
    """Normal English text must pass through unmodified."""

    def test_ordinary_sentence(self):
        sentence = "The function loads the configuration file and validates the schema."
        text, findings = scrub_text(sentence)
        self.assertEqual(text, sentence)
        self.assertEqual(findings, [])

    def test_short_words(self):
        phrase = "add the item to the list before returning the result"
        text, _ = scrub_text(phrase)
        self.assertNotIn("[REDACTED", text)

    def test_camelcase_variable_name_not_redacted(self):
        # 25-char camelCase name: entropy ~4.0 bits/char < threshold
        text, _ = scrub_text("getUserAuthenticationToken returns None if expired")
        self.assertNotIn("[REDACTED", text)

    def test_markdown_code_block_not_redacted(self):
        code = "```python\ndef authenticate():\n    return True\n```"
        text, _ = scrub_text(code)
        self.assertNotIn("[REDACTED", text)

    def test_pangram_not_redacted(self):
        # 35-char continuous alnum run — entropy ~4.6 bits/char < threshold
        pangram = "TheQuickBrownFoxJumpsOverTheLazyDog"
        text, _ = scrub_text(pangram)
        self.assertNotIn("[REDACTED", text)

    def test_version_string_words_preserved(self):
        # Even if a version string is misidentified as an IP, the surrounding
        # prose must be preserved.
        text, _ = scrub_text("using library version 0.0.1.0 in production")
        self.assertIn("using library version", text)
        self.assertIn("in production", text)


# ---------------------------------------------------------------------------
# Category count correctness
# ---------------------------------------------------------------------------

class TestCategoryCounts(unittest.TestCase):
    def test_no_findings_for_clean_text(self):
        _, findings = scrub_text("This is perfectly clean prose with no secrets.")
        self.assertEqual(findings, [])

    def test_two_emails_counted(self):
        _, findings = scrub_text("from alpha@test.com to beta@test.com")
        self.assertEqual(_cats(findings).get("email"), 2)

    def test_findings_sorted_alphabetically(self):
        text = "user@test.com and /Users/x/file.txt and 10.0.0.1"
        _, findings = scrub_text(text)
        cats = [f["category"] for f in findings]
        self.assertEqual(cats, sorted(cats))

    def test_finding_structure(self):
        _, findings = scrub_text("user@example.com")
        self.assertEqual(len(findings), 1)
        self.assertIn("category", findings[0])
        self.assertIn("count", findings[0])
        self.assertIsInstance(findings[0]["count"], int)


# ---------------------------------------------------------------------------
# --fail-on-secret exit-code semantics (via subprocess)
# ---------------------------------------------------------------------------

class TestFailOnSecret(unittest.TestCase):
    """CLI --fail-on-secret must exit 1 for secret categories, 0 otherwise."""

    _SCRIPT = str(Path(__file__).parent / "scrub.py")
    # Temp file written adjacent to the test — never /tmp.
    _TMP = Path(__file__).parent / "_scrub_test_input.txt"

    def _run(self, content: str, extra_args: list = None) -> int:
        """Write *content* to a local temp file and run scrub.py; return exit code."""
        self._TMP.write_text(content, encoding="utf-8")
        try:
            cmd = [sys.executable, self._SCRIPT, str(self._TMP)] + (extra_args or [])
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode
        finally:
            if self._TMP.exists():
                self._TMP.unlink()

    def test_github_token_causes_exit_1(self):
        token = "ghp_" + "A" * 20 + "b" * 10 + "1" * 6
        self.assertEqual(self._run(token, ["--fail-on-secret"]), 1)

    def test_aws_key_causes_exit_1(self):
        self.assertEqual(self._run("AKIAIOSFODNN7EXAMPLE", ["--fail-on-secret"]), 1)

    def test_clean_text_exits_0(self):
        self.assertEqual(
            self._run("The build failed due to a missing dependency.", ["--fail-on-secret"]),
            0,
        )

    def test_email_only_exits_0(self):
        """Emails are PII but not secrets — must not trigger --fail-on-secret."""
        self.assertEqual(self._run("contact user@example.com", ["--fail-on-secret"]), 0)

    def test_path_only_exits_0(self):
        """Paths are PII but not secrets — must not trigger --fail-on-secret."""
        self.assertEqual(self._run("see /Users/alice/readme.md", ["--fail-on-secret"]), 0)

    def test_without_flag_always_exits_0(self):
        """Without --fail-on-secret the exit code is always 0 (success)."""
        token = "ghp_" + "A" * 20 + "b" * 10 + "1" * 6
        self.assertEqual(self._run(token), 0)

    # -- Direct logic tests (faster, no subprocess) --------------------------

    def test_secret_category_in_SECRET_CATEGORIES(self):
        token = "ghp_" + "A" * 20 + "b" * 10 + "1" * 6
        _, findings = scrub_text(token)
        hit = any(f["category"] in SECRET_CATEGORIES for f in findings)
        self.assertTrue(hit)

    def test_pii_only_not_in_SECRET_CATEGORIES(self):
        _, findings = scrub_text("user@example.com and /Users/bob/file.txt")
        hit = any(f["category"] in SECRET_CATEGORIES for f in findings)
        self.assertFalse(hit)


if __name__ == "__main__":
    unittest.main()
