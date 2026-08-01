#!/usr/bin/env python3
"""
scrub.py — deterministic privacy backstop for skill-reflect (M2 milestone).

Runs UNDER the model's own paraphrasing scrub as a defense-in-depth layer.
This script is never the sole line of defense and never emits any redacted value.

Importable API
--------------
    from scrub import scrub_text

    scrubbed, findings = scrub_text(text)
    # scrubbed : str  — text with sensitive spans replaced by typed placeholders
    # findings : list[{"category": str, "count": int}]

CLI
---
    python3 scrub.py <infile> [--out <outfile>] [--report] [--fail-on-secret]

    --out FILE        Write scrubbed output to FILE (default: stdout).
    --report          Print per-category redaction counts to stderr (never values).
    --fail-on-secret  Exit 1 if a high-entropy or known-token secret was found.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# Categories that cause --fail-on-secret to exit 1.
# PII categories (email, path, ip-address) are always redacted but are not
# classified as "secrets" for --fail-on-secret purposes.
# ---------------------------------------------------------------------------
SECRET_CATEGORIES: frozenset = frozenset({
    "bearer-token",
    "github-token",
    "aws-access-key",
    "slack-token",
    "google-api-key",
    "pem-private-key",
    "jwt",
    "high-entropy",
})

# ---------------------------------------------------------------------------
# Pattern definitions.
# Order: most-specific → least-specific so that precise, informative
# placeholders are inserted before the generic high-entropy backstop runs.
# ---------------------------------------------------------------------------

# 1. PEM private-key blocks (may span multiple lines).
_PEM_RE = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"
    r"[\s\S]*?"
    r"-----END (?:[A-Z ]+ )?PRIVATE KEY-----",
    re.MULTILINE,
)

# 2. JWTs: the base64url encoding of any JSON object starts with "eyJ"
#    (i.e. '{"' encodes to eyJ in base64url).  Requiring eyJ in both the
#    header and payload segments minimises false positives.
_JWT_RE = re.compile(
    r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_=]*"
)

# 3. GitHub tokens — personal (ghp_), OAuth (gho_), user-to-server (ghu_),
#    server-to-server (ghs_), refresh (ghr_).  Followed by 36+ alnum chars.
_GITHUB_TOKEN_RE = re.compile(r"\bgh[porsu]_[A-Za-z0-9]{36,}\b")

# 4. AWS access key IDs (always start with AKIA, 20 chars total).
_AWS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# 5. Slack tokens (bot xoxb-, app xoxa-, user xoxp-, refresh xoxr-, shared xoxs-).
_SLACK_TOKEN_RE = re.compile(r"\bxox[baprs]-[0-9A-Za-z][0-9A-Za-z\-]{8,}\b")

# 6. Google API keys (always 39 chars: AIza + 35 url-safe chars).
_GOOGLE_KEY_RE = re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")

# 7. HTTP Bearer tokens ("Bearer <value>").  The "Bearer " keyword is preserved
#    in the output so the reader understands the context.
_BEARER_RE = re.compile(r"\bBearer\s+([A-Za-z0-9\-._~+/]+=*)")

# 8. Generic auth/API-key header values (20+ chars avoids false positives on
#    short values like "admin" or common English words).
_AUTH_HEADER_RE = re.compile(
    r"\b(Authorization|X-Api-Key|Api-Key|X-Auth-Token|X-Access-Token)"
    r"\s*[:=]\s*([A-Za-z0-9+/\-_=]{20,})",
    re.IGNORECASE,
)

# 9. Email addresses.
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# 10. Unix absolute paths containing a user segment (/Users/... or /home/...).
#     Negative lookbehind prevents matching mid-word (e.g. "myapp/Users/...").
_UNIX_PATH_RE = re.compile(
    r"(?<!\w)/(?:Users|home)/[^/\s\"'`<>]+"  # /Users/<name> or /home/<name>
    r"(?:/[^\s\"'`<>]*)?",                    # optional path tail (/ allowed inside)
    re.IGNORECASE,
)

# 11. Windows absolute paths with user segment (C:\Users\...).
_WIN_PATH_RE = re.compile(
    r"[A-Za-z]:\\Users\\[^\\\s\"'<>]+"
    r"(?:\\[^\\\s\"'<>]*)*",
    re.IGNORECASE,
)

# 12. IPv4 addresses (four octets 0–255).
_IPV4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

# 13. IPv6 addresses — covers the full form and all RFC-5952 compressed forms.
_IPV6_RE = re.compile(
    r"(?<![:\w])"
    r"(?:"
    r"(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}"             # full (8 groups)
    r"|(?:[0-9A-Fa-f]{1,4}:){1,7}:"                           # n:: trailing
    r"|:(?::[0-9A-Fa-f]{1,4}){1,7}"                           # ::n leading
    r"|(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}"          # 1-6 groups + :n
    r"|(?:[0-9A-Fa-f]{1,4}:){1,5}(?::[0-9A-Fa-f]{1,4}){2}"  # 1-5 + ::n:n
    r"|(?:[0-9A-Fa-f]{1,4}:){1,4}(?::[0-9A-Fa-f]{1,4}){3}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,3}(?::[0-9A-Fa-f]{1,4}){4}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,2}(?::[0-9A-Fa-f]{1,4}){5}"
    r"|[0-9A-Fa-f]{1,4}:(?::[0-9A-Fa-f]{1,4}){6}"
    r"|::(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4}"        # :: with tail
    r"|::"                                                     # :: alone
    r")"
    r"(?![:\w])"
)

# 14a. Hex-string backstop — 32+ even-length all-hex strings (MD5/SHA hashes,
#      HMAC keys, etc.).  Checked first; if it qualifies we skip the entropy
#      check (hex alphabets have low per-character entropy but are still secrets).
_HEX_CANDIDATE_RE = re.compile(r"\b[0-9A-Fa-f]{32,}\b")
_HEX_CHARS: frozenset = frozenset("0123456789abcdefABCDEF")

# 14b. Generic high-entropy backstop for other encoded secrets (base64, etc.).
#      Min length 20 chars from the base64 / base64url / API-key alphabet.
_ENTROPY_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/\-_=]{20,}")

# Shannon entropy threshold (bits per character).
_ENTROPY_THRESHOLD = 4.8


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _shannon_entropy(s: str) -> float:
    """Return the Shannon entropy of *s* in bits per character."""
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _has_mixed_classes(s: str) -> bool:
    """Return True if *s* contains characters from at least two classes.

    Classes: uppercase letters, lowercase letters, digits, symbols (+/=_-).
    This guard prevents flagging pure-lowercase English words even if long.
    """
    return sum([
        any(c.isupper() for c in s),
        any(c.islower() for c in s),
        any(c.isdigit() for c in s),
        any(c in "+/=_-" for c in s),
    ]) >= 2


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrub_text(s: str) -> tuple:
    """Redact PII and secret material from *s*.

    Returns
    -------
    (scrubbed_text, findings)
        scrubbed_text : str
            The input with sensitive spans replaced by ``[REDACTED:<category>]``
            placeholders.  No redacted *value* ever appears in the output.
        findings : list[dict]
            ``[{"category": str, "count": int}, ...]`` sorted alphabetically;
            only categories with at least one match are included.
    """
    counter: Counter = Counter()
    text = s

    # --- 1. PEM private-key blocks ---
    def _sub_pem(m):
        counter["pem-private-key"] += 1
        return "[REDACTED:pem-private-key]"
    text = _PEM_RE.sub(_sub_pem, text)

    # --- 2. JWTs ---
    def _sub_jwt(m):
        counter["jwt"] += 1
        return "[REDACTED:jwt]"
    text = _JWT_RE.sub(_sub_jwt, text)

    # --- 3. GitHub tokens ---
    def _sub_gh(m):
        counter["github-token"] += 1
        return "[REDACTED:github-token]"
    text = _GITHUB_TOKEN_RE.sub(_sub_gh, text)

    # --- 4. AWS access keys ---
    def _sub_aws(m):
        counter["aws-access-key"] += 1
        return "[REDACTED:aws-access-key]"
    text = _AWS_KEY_RE.sub(_sub_aws, text)

    # --- 5. Slack tokens ---
    def _sub_slack(m):
        counter["slack-token"] += 1
        return "[REDACTED:slack-token]"
    text = _SLACK_TOKEN_RE.sub(_sub_slack, text)

    # --- 6. Google API keys ---
    def _sub_google(m):
        counter["google-api-key"] += 1
        return "[REDACTED:google-api-key]"
    text = _GOOGLE_KEY_RE.sub(_sub_google, text)

    # --- 7. HTTP Bearer tokens (preserve the "Bearer" keyword for context) ---
    def _sub_bearer(m):
        counter["bearer-token"] += 1
        return "Bearer [REDACTED:bearer-token]"
    text = _BEARER_RE.sub(_sub_bearer, text)

    # --- 8. Generic auth/API-key header values ---
    def _sub_auth(m):
        counter["bearer-token"] += 1
        # Preserve the header name; replace only the value (group 2).
        offset = m.start(2) - m.start(0)
        return m.group(0)[:offset] + "[REDACTED:bearer-token]"
    text = _AUTH_HEADER_RE.sub(_sub_auth, text)

    # --- 9. Email addresses ---
    def _sub_email(m):
        counter["email"] += 1
        return "[REDACTED:email]"
    text = _EMAIL_RE.sub(_sub_email, text)

    # --- 10. Unix user paths ---
    def _sub_unix(m):
        counter["path"] += 1
        return "[REDACTED:path]"
    text = _UNIX_PATH_RE.sub(_sub_unix, text)

    # --- 11. Windows user paths ---
    def _sub_win(m):
        counter["path"] += 1
        return "[REDACTED:path]"
    text = _WIN_PATH_RE.sub(_sub_win, text)

    # --- 12. IPv4 addresses ---
    def _sub_ipv4(m):
        counter["ip-address"] += 1
        return "[REDACTED:ip-address]"
    text = _IPV4_RE.sub(_sub_ipv4, text)

    # --- 13. IPv6 addresses ---
    def _sub_ipv6(m):
        counter["ip-address"] += 1
        return "[REDACTED:ip-address]"
    text = _IPV6_RE.sub(_sub_ipv6, text)

    # --- 14a. Hex-string backstop (SHA/MD5 hashes, HMAC keys, etc.) ---
    def _sub_hex(m):
        token = m.group(0)
        # All chars must be strictly hex and length must be even (key/hash shape).
        if frozenset(token.lower()) <= _HEX_CHARS and len(token) % 2 == 0:
            counter["high-entropy"] += 1
            return "[REDACTED:high-entropy]"
        return token
    text = _HEX_CANDIDATE_RE.sub(_sub_hex, text)

    # --- 14b. Generic high-entropy backstop for non-hex encoded secrets ---
    def _sub_entropy(m):
        token = m.group(0)
        if _has_mixed_classes(token) and _shannon_entropy(token) >= _ENTROPY_THRESHOLD:
            counter["high-entropy"] += 1
            return "[REDACTED:high-entropy]"
        return token
    text = _ENTROPY_CANDIDATE_RE.sub(_sub_entropy, text)

    findings = sorted(
        [{"category": cat, "count": cnt} for cat, cnt in counter.items() if cnt > 0],
        key=lambda d: d["category"],
    )
    return text, findings


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list = None) -> int:
    """Run the CLI; returns the process exit code."""
    parser = argparse.ArgumentParser(
        prog="scrub.py",
        description=(
            "Deterministic privacy backstop for skill-reflect. "
            "Redacts PII and secrets from text, Markdown, or JSON. "
            "Runs UNDER the model's own paraphrasing scrub (defense-in-depth). "
            "Never the sole line of defense; never emits any redacted value."
        ),
    )
    parser.add_argument("infile", help="File to scrub (text, Markdown, or JSON).")
    parser.add_argument(
        "--out", metavar="FILE",
        help="Write scrubbed output to FILE (default: stdout).",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print per-category redaction counts to stderr (never values).",
    )
    parser.add_argument(
        "--fail-on-secret", action="store_true",
        help="Exit 1 if a high-entropy or known-token secret category was found.",
    )
    args = parser.parse_args(argv)

    with Path(args.infile).open("r", encoding="utf-8", errors="replace") as fh:
        raw = fh.read()

    scrubbed, findings = scrub_text(raw)

    if args.out:
        Path(args.out).write_text(scrubbed, encoding="utf-8")
    else:
        sys.stdout.write(scrubbed)

    if args.report:
        print("\n=== scrub report ===", file=sys.stderr)
        if findings:
            for f in findings:
                print(f"  {f['category']}: {f['count']} redaction(s)", file=sys.stderr)
        else:
            print("  (no redactions)", file=sys.stderr)

    if args.fail_on_secret:
        if any(f["category"] in SECRET_CATEGORIES for f in findings):
            print(
                "scrub: FAIL — secret-category content detected "
                "(use --report to see categories; no values are shown)",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
